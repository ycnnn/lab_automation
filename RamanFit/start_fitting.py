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

    filename = sys.argv[1].split('.txt') + '_'
    
 
    peak_0_center_initial_guess = 384.0
    peak_1_center_initial_guess = 404.0
    
    
    si_params, params = start_MoS2_fit(sys.argv[1],
                    peak_0_center_initial_guess=peak_0_center_initial_guess,
                    peak_1_center_initial_guess=peak_1_center_initial_guess)
    
    correction = si_params['peak_0_centers'] - 520.0
    E_pos_corrected = params['peak_0_centers'] - correction
    A_pos_corrected = params['peak_1_centers'] - correction
    strain = -0.20 * E_pos_corrected + 0.03 * A_pos_corrected
    doping = -0.15 * E_pos_corrected + 0.47 * A_pos_corrected

 
    np.savetxt(filename + 'Si_raw_peak_position.csv', si_params['peak_0_centers'])
    np.savetxt(filename + 'E_raw_peak_position.csv', params['peak_0_centers'])
    np.savetxt(filename + 'A_raw_peak_position.csv', params['peak_1_centers'])
    np.savetxt(filename + 'strain.csv', strain)
    np.savetxt(filename + 'doping.csv', doping)

    np.save(filename + 'Si_raw_peak_position', si_params['peak_0_centers'])
    np.save(filename + 'E_raw_peak_position', params['peak_0_centers'])
    np.save(filename + 'A_raw_peak_position', params['peak_1_centers'])
    np.save(filename + 'strain', strain)
    np.save(filename + 'doping', doping)



