import shutil
import os
######################################################################
# Custom dependencies
# from mp import Data_fetcher, Data_receiver
from params.position_params import Position_parameters
from params.scan_params import Scan_parameters
from params.display_params import Display_parameters
from scan_main_program import lsm_scan
from inst_driver import External_instrument
######################################################################



if __name__ == '__main__':
    
    display_parameters = Display_parameters(scan_id='test')

    position_parameters = Position_parameters(
                                            x_size=21,
                                            y_size=21,
                                            x_center=51,
                                            y_center=51,
                                            x_pixels=200,
                                            y_pixels=150,
                                            z_center=25.5,
                                            angle=-45)
    
    scan_parameters = Scan_parameters(point_time_constant=0.001,
                                      # retrace_point_time_constant=0.000001,
                                      input_mapping=["ai0"],
                                      return_to_zero=True)


  

  

    # Setting up the external input instrument(s)
    # Sometimes, the code will ask for additional parameters for setting up the instrument.
    # Even if those parameters are not supplied, the scan will go on, but the system will use default values and issue warning(s).
    # Uncomment the following code as needed.
    


    # instrument2 = External_instrument(instrument_type='Virtual_instrument')
    # scan_parameters.add_instrument(instrument2)

    # Keithley_prop = {'start_volt': -80, 'end_volt': 80}
    # instrument3 = External_instrument(instrument_type='Keithley2450', **Keithley_prop)
    # scan_parameters.add_instrument(instrument3)

    # Lockin_prop = {
    #                 'time_constant_level':10, 
    #                 'volt_input_range':1, 
    #                 'signal_sensitivity':6,
    #                 'ref_frequency':20170,
    #                 'sine_amplitude':1.5
    #                 }
    # instrument4 = External_instrument(instrument_type='Lockin', **Lockin_prop)
    # scan_parameters.add_instrument(instrument4)


    
    
    lsm_scan(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters)
    
    