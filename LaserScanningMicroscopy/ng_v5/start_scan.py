
######################################################################
# Custom dependencies
from mp import Data_fetcher, Data_receiver
from params.position_params import Position_parameters
from params.scan_params import Scan_parameters
from params.display_params import Display_parameters
from main import lsm_scan
from inst_driver import Lockin
######################################################################



if __name__ == '__main__':
    # Setting up the external input instrument(s)
    instrument = None
    # instrument = Lockin()
    # sleep(2)

    position_parameters = Position_parameters(
                                            x_size=30,
                                            y_size=30,
                                            x_pixels=127,
                                            y_pixels=20,
                                            z_center=19,
                                            angle=90)
    
    scan_parameters = Scan_parameters(frequency=25, 
                                      input_mapping=["ai0","ai1"],
                                      instrument=instrument,
                                      return_to_zero=True)
    
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