# import shutil
# import os
import sys
import numpy as np
######################################################################
# Custom dependencies
# from mp import Data_fetcher, Data_receiver
from source.params.position_params import Position_parameters
from source.params.scan_params import Scan_parameters
from source.params.display_params import Display_parameters
from source.scan_process import LSM_scan
import source.inst_driver as inst_driver
# from source.inst_driver import External_instrument, EmptyInstrument
######################################################################



if __name__ == '__main__':
   
    
    try:
        scan_id = sys.argv[1]
    except:
        scan_id = 'linescan_delta_vd'
    
    # Gate bias Vg scan range, in volt
    vg = -40

    # Delta V scan range, in volt
    delta_v = (0,2)

    # Load calibration data for rotating the waveplates in the system.
    # The data will have multiple rows, each row is data for a certain polarization angle of the light shining on the sample.
    # for each row, there will be 4 values, which are rotating angles for:
    # the angle of halfwaveplate(HWP) before the balance detector, the polarization angle of the light shining on the sample, 
    # the angle of quarterwaveplate(QWP) in the upstream of lightpath, and
    # the angle of halfwaveplate(HWP) in the upstream of lightpath.
    # The HWP and QWP in the upstream of the light is used to cancel all birefingent behavior of the optics in the system,
    # such that the light shining on the sample is linearly polarized.
    # All angles in degrees

    angle_correction_file = np.load('utilities/mgo_calibration_zerohwp_pol_qwp_hwp.npy')

    angle_correction = angle_correction_file[0]
    hwp_before_bd_angle, pol_angle, correction_qwp_angle, correction_hwp_angle = angle_correction
    
    display_parameters = Display_parameters(scan_id=scan_id)

    #  Pay attention to scan angle
    position_parameters = Position_parameters(
                                            x_size=60,
                                            y_size=0,
                                            x_pixels=10,
                                            y_pixels=200,
                                            z_center=0,
                                            angle=-35)
  
    
    scan_parameters = Scan_parameters(point_time_constant= 0.12,
                                      retrace_point_time_constant=0.02,
                                      return_to_zero=True,
                                      additional_info=f'Polarization angle = {pol_angle}')

    instruments = []

    daq = inst_driver.DAQ(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    input_mapping=['ai0', 'ai1'],
                    )
    instruments.append(daq)

    smu = inst_driver.SMU(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    **{'voltage':vg},
                    )
    instruments.append(smu)

    laser = inst_driver.LaserDiode(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    **{'current':0.08},
                    )
    instruments.append(laser)


    lockin_prop = {
        # Note the time constant levels
        # Levels and range: 0->1us, 1->3us, 2->10us 3->30us, 4->100us, 5->300us, 6->1ms, 7->3ms, 8->10ms, 
        # 9->30ms, 10->100ms, 11->300ms, 12->1s, 13->3s, 14->10s, 15->30s, 16->100s, 17->300s, 18->1000s, 19->3000s, 20->10000s

        'time_constant_level':10,
        'volt_input_range':2,
        'signal_sensitivity':6,
        'ref_frequency':20170,
        'sine_amplitude':delta_v,}
    
    lockin = inst_driver.Lockin(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    **lockin_prop,
                    )
    instruments.append(lockin)



    correction_hwp = inst_driver.RotationStage(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    name='HWP_for_correction',
                    **{'angle':correction_hwp_angle},
                    )
    instruments.append(correction_hwp)

    correction_qwp = inst_driver.RotationStage(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    name='QWP_for_correction',
                    **{'angle':correction_qwp_angle},
                    )
    instruments.append(correction_qwp)

    hwp_before_bd = inst_driver.RotationStage(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    name='HWP_for_zeroing_BD_output',
                    **{'angle':hwp_before_bd_angle},
                    )
    instruments.append(hwp_before_bd)

    



    
    LSM_scan(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters,
             instruments=instruments)
    
    
