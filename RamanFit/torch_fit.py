import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from fit_func import load_helper, double_peak_fit
import torch



class Lorentizian(torch.autograd.Function):
    @staticmethod
    def forward(ctx, input):
        ctx.save_for_backward(input)
        return 1/ (input ** 2 +1)

    @staticmethod
    def backward(ctx, grad_output):
        input, = ctx.saved_tensors
        return - (grad_output * 2 * input / ((1 + input **2 ) **2))

class RamanTwoPeaks(torch.nn.Module):
    def __init__(self, 
                 pixels, 
                 x_coordinates_len,
                 peak_0_amplitude_guess,
                 peak_0_center_guess,
                 peak_0_sigma_guess,
                 peak_1_amplitude_guess,
                 peak_1_center_guess,
                 peak_1_sigma_guess,
                 slope_guess,
                 constant_guess,
                 device,
                 dtype,
                 Lorentizian_function=Lorentizian.apply,
                 ):
        
        super().__init__()
        
        self.pixels, self.x_coordinates_len = (pixels, x_coordinates_len)

        self.peak_0_amplitudes = torch.tensor(
            peak_0_amplitude_guess * np.ones(self.pixels).reshape(-1,1),
                    device=device, dtype=dtype, requires_grad=True)
        self.peak_0_centers = torch.tensor(
            peak_0_center_guess * np.ones(self.pixels).reshape(-1,1),
                    device=device, dtype=dtype, requires_grad=True)
        self.peak_0_sigmas = torch.tensor(
            peak_0_sigma_guess * np.ones(self.pixels).reshape(-1,1),
                    device=device, dtype=dtype, requires_grad=True)
        self.peak_1_amplitudes = torch.tensor(
            peak_1_amplitude_guess * np.ones(self.pixels).reshape(-1,1),
                    device=device, dtype=dtype, requires_grad=True)
        self.peak_1_centers = torch.tensor(
            peak_1_center_guess * np.ones(self.pixels).reshape(-1,1),
                    device=device, dtype=dtype, requires_grad=True)
        self.peak_1_sigmas = torch.tensor(
            peak_1_sigma_guess * np.ones(self.pixels).reshape(-1,1),
                    device=device, dtype=dtype, requires_grad=True)
        self.slopes = torch.tensor(
            slope_guess * np.ones(self.pixels).reshape(-1,1),
                    device=device, dtype=dtype, requires_grad=True)
        self.constants = torch.tensor(
            constant_guess * np.ones(self.pixels).reshape(-1,1),
                    device=device, dtype=dtype, requires_grad=True)
        self.train_parameters = [
                                                       self.peak_0_amplitudes, 
                                                       self.peak_0_centers, 
                                                       self.peak_0_sigmas,
                                                       self.peak_1_amplitudes,
                                                       self.peak_1_centers,
                                                       self.peak_1_sigmas,
                                                       self.slopes,
                                                       self.constants
                                                       ]

        self.LP = Lorentizian_function

    def forward(self, x):

        result = (self.constants.repeat(1, self.x_coordinates_len) 
              + torch.matmul(torch.diag(self.slopes.reshape(-1)), x)
              + torch.matmul(torch.diag(self.peak_0_amplitudes.reshape(-1)),
                self.LP((x - self.peak_0_centers.repeat(1,self.x_coordinates_len))/self.peak_0_sigmas.repeat(1,self.x_coordinates_len)))
              + torch.matmul(torch.diag(self.peak_1_amplitudes.reshape(-1)),
                self.LP((x - self.peak_1_centers.repeat(1,self.x_coordinates_len))/self.peak_1_sigmas.repeat(1,self.x_coordinates_len)))
                )
        return result


def two_peak_map_fit(
                    x_input, 
                    y_input,
                    learning_rate=0.1,
                    iterations=40,
                    use_GPU=True,
                    spec_cutoff_range=(350.0,450.0)
                    ):
    if not use_GPU:
        device = torch.device("cpu")
    else:
        if torch.cuda.is_available(): 
            print('CUDA GPU accelaration enabled.')
            device = torch.device("cuda:0" )
        elif torch.backends.mps.is_available():
            print('Apple M series GPU accelaration enabled.')
            device = torch.device("mps")
        else: 
            device = torch.device("cpu")
    dtype = torch.float32


    # x_input, y_input = load_helper('spectrums.txt')
    height, width, _ = y_input.shape
    spec_range = (x_input < spec_cutoff_range[1]) & (x_input > spec_cutoff_range[0])
    pixels = height * width
    x_raw = x_input[spec_range]
    y = y_input.reshape(-1,x_input.shape[0])[:pixels, spec_range]

    x = torch.tensor(x_raw.reshape(1,-1), 
                    device=device, 
                    dtype=dtype).repeat(pixels,1)
    y = torch.tensor(y,  
                    device=device, 
                    dtype=dtype)

    initial_fit_params, _ = double_peak_fit(np.mean(y_input, axis=(0,1))[spec_range], x_input[spec_range])
    init_params = {
        'peak_0_amplitude_guess':
        initial_fit_params['peak_0_amplitude']/(np.pi * initial_fit_params['peak_0_sigma']),
        'peak_0_center_guess':initial_fit_params['peak_0_center'],
        'peak_0_sigma_guess':initial_fit_params['peak_0_sigma'],
        'peak_1_amplitude_guess':
        initial_fit_params['peak_1_amplitude']/(np.pi * initial_fit_params['peak_1_sigma']),
        'peak_1_center_guess':initial_fit_params['peak_1_center'],
        'peak_1_sigma_guess':initial_fit_params['peak_1_sigma'],
        'slope_guess':initial_fit_params['_slope'],
        'constant_guess':initial_fit_params['_intercept'],}


    model = RamanTwoPeaks(pixels=pixels,
                        x_coordinates_len=np.sum(spec_range),
                        **init_params,
                        device=device,
                        dtype=dtype)

    training_indices = tqdm(range(iterations))
    # optimizer = torch.optim.RMSprop(model.train_parameters, lr=learning_rate)
    optimizer = torch.optim.Adam(model.train_parameters, lr=learning_rate)

    for t in training_indices:
        y_pred =  model(x)
        # Compute and print loss
        loss = (y_pred - y).pow(2).sum()
        training_indices.set_description(f'Loss {loss.item()/1E9} ')
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    fitted_params = {}

    fitted_params['peak_0_amplitudes'] = model.train_parameters[0].detach().cpu().numpy().reshape(height, -1)
    fitted_params['peak_0_centers'] = model.train_parameters[1].detach().cpu().numpy().reshape(height, -1)
    fitted_params['peak_0_sigmas'] = model.train_parameters[2].detach().cpu().numpy().reshape(height, -1)
    fitted_params['peak_1_amplitudes'] = model.train_parameters[3].detach().cpu().numpy().reshape(height, -1)
    fitted_params['peak_1_centers'] = model.train_parameters[4].detach().cpu().numpy().reshape(height, -1)
    fitted_params['peak_1_sigmas'] = model.train_parameters[5].detach().cpu().numpy().reshape(height, -1)
    fitted_params['slopes'] = model.train_parameters[6].detach().cpu().numpy().reshape(height, -1)
    fitted_params['intercepts'] = model.train_parameters[7].detach().cpu().numpy().reshape(height, -1)

    return fitted_params