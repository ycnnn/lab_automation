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
    
    display_parameters = Display_parameters(scan_id='MOKE_Test_sample_high_resolution')

    position_parameters = Position_parameters(
                                            x_size=60,
                                            y_size=60,
                                            x_pixels=384,
                                            # y_pixels=127,
                                            z_center=25,
                                            angle=90)
    
    scan_parameters = Scan_parameters(frequency=1, 
                                      input_mapping=["ai0","ai1"],
                                      return_to_zero=True)
    
    # Mandatory code. There MUST be at least one external instrument present dring the scan.
    empty_instr = External_instrument(instrument_type='Empty_instrument')
    scan_parameters.add_instrument(empty_instr)

    # Setting up other external input instrument(s)
    # Uncomment as needed
    #############################################################################################
    #############################################################################################
    #############################################################################################
    


    


    # Setting up the external input instrument(s)
    # Sometimes, the code will ask for additional parameters for setting up the instrument.
    # Even if those parameters are not supplied, the scan will go on, but the system will use default values and issue warning(s).
    
    # Keithley_prop = {'start_volt': -2, 'end_volt': 2}
    # instrument2 = External_instrument(instrument_type='Keithley2450', **Keithley_prop)
    # scan_parameters.add_instrument(instrument2)

    # instrument3 = External_instrument(instrument_type='Virtual_instrument')
    # scan_parameters.add_instrument(instrument3)


    # Lockin_prop = {'time_constant_level': 1, 'sample_count': 128}
    # instrument4 = External_instrument(instrument_type='Lockin', **Lockin_prop)
    # scan_parameters.add_instrument(instrument4)

    
    #############################################################################################
    #############################################################################################
    #############################################################################################


    
    
    
    # scan_parameters.save_params(display_parameters.save_destination + display_parameters.scan_id)
    # position_parameters.save_params(display_parameters.save_destination + display_parameters.scan_id)

    lsm_scan(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters)
    
    