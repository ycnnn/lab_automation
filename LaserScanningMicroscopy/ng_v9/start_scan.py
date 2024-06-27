
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
    


    position_parameters = Position_parameters(
                                            x_size=30,
                                            y_size=30,
                                            x_pixels=100,
                                            y_pixels=99,
                                            z_center=19,
                                            angle=90)
    
    scan_parameters = Scan_parameters(frequency=25, 
                                      input_mapping=["ai0","ai1"],
                                    #   instrument=instrument,
                                      return_to_zero=True)
    # Setting up the external input instrument(s)
    instrument = External_instrument(instrument_type='Empty_instrument')
    # Setting up the external input instrument(s)
    # Sometimes, the code will ask for additional parameters for setting up the instrument.
    # Even if those parameters are not supplied, the scan will go on, but the system will use default values and issue warning(s).
    Keithley_prop = {'start_volt': -15, 'end_volt': 10}
    instrument2 = External_instrument(instrument_type='Keithley2450', **Keithley_prop)

    instrument3 = External_instrument(instrument_type='Virtual_instrument')
    
    scan_parameters.add_instrument(instrument)
    scan_parameters.add_instrument(instrument2)
    scan_parameters.add_instrument(instrument3)
    
    display_parameters = Display_parameters(
                 scan_id='stressor_square_256_px_90_deg',
                 save_destination=None,
                 colormap=None,
                 channel_min=None,
                 channel_max=None,
                 window_width=None,
                 window_height=None,
                 darkmode=True,
                 save_data=True)

    lsm_scan(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters)