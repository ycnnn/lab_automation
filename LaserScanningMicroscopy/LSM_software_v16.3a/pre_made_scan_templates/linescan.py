import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 

import sys
######################################################################
# Custom dependencies
# from mp import Data_fetcher, Data_receiver
from source.params.position_params import Position_parameters
from source.params.scan_params import Scan_parameters
from source.params.display_params import Display_parameters
from source.scan_main_program import lsm_scan
from source.inst_driver import External_instrument
######################################################################



if __name__ == '__main__':
    
   
    try:
      scan_id = sys.argv[1]
    except:
       scan_id = 'linescan'
    

    display_parameters = Display_parameters(scan_id=scan_id)

    position_parameters = Position_parameters(
                                            x_size=10,
                                            y_size=0,
                                            x_pixels=100,
                                            y_pixels=100,
                                            z_center=0,
                                            angle=-35)
    
    scan_parameters = Scan_parameters(point_time_constant=0.32,
                                      retrace_point_time_constant=0.02,
                                      input_mapping=["ai0"],
                                      return_to_zero=True)


  
    Laser_prop = {'current_level': 0.080}
    instrument3 = External_instrument(instrument_type='Laser', **Laser_prop)
    scan_parameters.add_instrument(instrument3)

  

    # Setting up the external input instrument(s)
    # Sometimes, the code will ask for additional parameters for setting up the instrument.
    # Even if those parameters are not supplied, the scan will go on, but the system will use default values and issue warning(s).
    # Uncomment the following code as needed.
    


    # instrument2 = External_instrument(instrument_type='Virtual_instrument')
    # scan_parameters.add_instrument(instrument2)

    Keithley_prop = {'start_volt': -60, 'end_volt': 60}
    instrument3 = External_instrument(instrument_type='Keithley2450', **Keithley_prop)
    scan_parameters.add_instrument(instrument3)

    # Levels and range: 0->1us, 1->3us, 2->10us 3->30us, 4->100us, 5->300us, 6->1ms, 7->3ms, 8->10ms, 
    # 9->30ms, 10->100ms, 11->300ms, 12->1s, 13->3s, 14->10s, 15->30s, 16->100s, 17->300s, 18->1000s, 19->3000s, 20->10000s
    Lockin_prop = {
                    'time_constant_level':11, 
                    'volt_input_range':1, 
                    'signal_sensitivity':6,
                    'ref_frequency':20170,
                    'sine_amplitude':1.0
                    }
    instrument4 = External_instrument(instrument_type='Lockin', **Lockin_prop)
    scan_parameters.add_instrument(instrument4)


    
    
    lsm_scan(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters)
    
    