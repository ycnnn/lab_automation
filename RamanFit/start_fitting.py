import numpy as np
from fit_func import load_helper
from torch_fit import one_peak_map_fit, two_peak_map_fit
import matplotlib.pyplot as plt
import time
import sys
import resource


def start_MoS2_fit(filename,
                   peak_0_center_initial_guess=384.0,
                   peak_1_center_initial_guess=404.0):
    resource.setrlimit(
    resource.RLIMIT_CORE,
    (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    x_input, y_input = load_helper(filename)
    si_params = one_peak_map_fit(x_input, y_input[:,:,:])
    params = two_peak_map_fit(x_input, y_input[:,:,:],
                              peak_0_center_initial_guess=peak_0_center_initial_guess,
                              peak_1_center_initial_guess=peak_1_center_initial_guess)
    return si_params, params

if __name__ == "__main__":
    
    if len(sys.argv) > 2:
        print('Enter the customization.') 
        peak_0_center_initial_guess = float(input('Initial E peak position guess (in cm-1) ? \n'))
        peak_1_center_initial_guess = float(input('Initial A peak position guess (in cm-1) ? \n'))
        save_format = float(input('How to save the result? Enter 0 for .csv file, enter 1 for .npy file. \n'))

        filename = sys.argv[1].split('.txt') + '_'
        si_params, params = start_MoS2_fit(sys.argv[1],
                        peak_0_center_initial_guess=peak_0_center_initial_guess,
                        peak_1_center_initial_guess=peak_1_center_initial_guess)
        if save_format == 0:
            np.savetxt(filename + 'Si_peak_position.csv', si_params['peak_0_centers'])
            np.savetxt(filename + 'E_peak_position.csv', params['peak_0_centers'])
            np.savetxt(filename + 'A_peak_position.csv', params['peak_1_centers'])
        else:
            np.save(filename + 'Si_peak_position', si_params['peak_0_centers'])
            np.save(filename + 'E_peak_position', params['peak_0_centers'])
            np.save(filename + 'A_peak_position', params['peak_1_centers'])
    else:
        si_params, params = start_MoS2_fit(sys.argv[1])
        np.savetxt(filename + 'Si_peak_position.csv', si_params['peak_0_centers'])
        np.savetxt(filename + 'E_peak_position.csv', params['peak_0_centers'])
        np.savetxt(filename + 'A_peak_position.csv', params['peak_1_centers'])
        
  


    # if len(sys.argv) == 4:
    #     peak_0_center_initial_guess = float(sys.argv[2])
    #     peak_1_center_initial_guess = float(sys.argv[3])
    #     si_params, params = start_MoS2_fit(sys.argv[1],
    #                    peak_0_center_initial_guess=peak_0_center_initial_guess,
    #                    peak_1_center_initial_guess=peak_1_center_initial_guess)
    # else:
    #     si_params, params = start_MoS2_fit(sys.argv[1])
    
    # np.savetxt(si_params['peak_0_centers'])
    # np.savetxt(params['peak_1_centers'])
    # np.savetxt(params['peak_1_centers'])
