import sys
import time
import numpy as np
import plot_helper as ph
from daq import (generate_ao_data,
                 generate_ao_data_xy_scan,
                 daq_interface)
from matplotlib.backends.qt_compat import QtWidgets
import matplotlib.pyplot as plt
from scan_params import params
from app import ApplicationWindow
################################################################
# Keithley prep
from script import set_smu_ready_for_ramp, ramp
################################################################


def scan(params,close=False):

    pixels=params.pixels
    frequency = params.frequency

    if params.dark_mode:
        plt.style.use('dark_background')

    close = close

    ph.font_format()
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow(parameters=params)
    app.show()
    app.activateWindow()
    app.raise_()



    times = []
    single_scan_time = 1/frequency

    ao0_start = params.x_coordinates[0,0]
    ao1_start = params.y_coordinates[0,0]
    ao0_end = params.x_coordinates[-1,-1]
    ao1_end = params.y_coordinates[-1,-1]
    ao_start = np.array([np.linspace(0,ao0_start,num=pixels),np.linspace(0,ao1_start,num=pixels)]).T
    ao_stop = np.array([np.linspace(ao0_end,0,num=pixels),np.linspace(ao1_end,0,num=pixels)]).T
    # Move laser to the starting point
    move_frequency = max(frequency,64)
    _ = daq_interface(ao0_1_write_data=ao_start,
                           frequency=move_frequency,
                           input_mapping=params.input_mapping)
    
    ############################################################################
    # Keithley preparation
    if params.xy_scan:
        print('Error: try to run a linescan, but the scaning parameter is set as xy scan.')
        return
    gate = set_smu_ready_for_ramp()
    gate.write('smu.source.output = smu.ON')
    ramp_voltages = params.theta_val
    ramp(smu=gate, start_volt=0, end_volt=ramp_voltages[0])
    current_voltage = ramp_voltages[0]
    # Important: we assume Keithley is ready at this time. Initialization should be finished.
    # Initialization include: 
    # setting up communication -> setting source level to 0 -> setting output ON 
    
    # Input line scan params for Keithley: a start volt, a finish volt 
    # The step number == pixels
    
    # This line should set up a scan voltage array.
    # This line should ramp up Keithely to starting voltage.
    ############################################################################


    for i in range(pixels):
        ################################################################
        # How this works:
        # 1. Fetch the x, y coordinates (for whole scan, a pixels x pixels 2D array each) from params.x_coordinates and params.y_coordinates
        # 2. Extract the x,y coordinates for current line (ID array each), and make a np array of shape (pixels,2) to store x y coordinates info
        # 3. Move laser by ao output, and record ai input signal simultaneously, as app.l_ch1 to app.l_ch3
        # 4. Move laser back (use ao0_1_write_data_reverse). This is important to ensure the alignment of the pixelated image.
        # 5. Repeat 1 - 4 for each line.
        ao0_1_write_data = generate_ao_data_xy_scan(
            ao_0_data_array=params.x_coordinates,
            ao_1_data_array=params.y_coordinates,
            index=i,pixels=pixels)
        
        ################################################################
        # Keithley prep
        # This line should ramp Keithley to the target source level.
        ramp(smu=gate, start_volt=current_voltage, end_volt=ramp_voltages[i])
        current_voltage = ramp_voltages[i]
        ################################################################
    
        app.l_ch1, app.l_ch2, app.l_ch3 = daq_interface(ao0_1_write_data=ao0_1_write_data,
                                                        frequency=frequency,
                                                        input_mapping=params.input_mapping)
        # move laser back to original position
        reverse_frequency = min(40*frequency,256)
        ao0_1_write_data_reverse = np.copy(np.flip(ao0_1_write_data,axis=0))
        _, _, _ = daq_interface(ao0_1_write_data=ao0_1_write_data_reverse,
                                                    frequency=reverse_frequency,
                                                    input_mapping=params.input_mapping)

        app.i_ch1[i] = app.l_ch1
        app.i_ch2[i] = app.l_ch2
        app.i_ch3[i] = app.l_ch3
 
        app._update_canvas_3_ch(
            app.l_ch1,app.i_ch1,
            app.l_ch2,app.i_ch2,
            app.l_ch3,app.i_ch3,
                           scan_id=i,
                           single_time=single_scan_time)
        qapp.processEvents()

        times.append(time.time())
        if i >= 1:
            single_scan_time = np.mean(np.diff(np.array(times)))

    app.save_data()
    params.save_params()

    ################################################################
    # Keithley prep
    # This line should ramp Keithley to 0.
    ramp(smu=gate, start_volt=ramp_voltages[-1], end_volt=0)
    gate.write('smu.source.output = smu.OFF')
    ################################################################

    _ = daq_interface(ao0_1_write_data=ao_stop,
                           frequency=move_frequency,
                           input_mapping=params.input_mapping)
    if close:
        qapp.exec()
    return app.i_ch_images
