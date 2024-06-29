import sys
import time
import numpy as np
import plot_helper as ph
from daq import (generate_ao_data,
                 generate_ao_data_xy_scan,
                 generate_ao_data_xy_scan_with_sync_channel,
                 daq_interface,
                 daq_interface_sync)
from SRS import (set_lockin_ready, set_lockin_output)
from matplotlib.backends.qt_compat import QtWidgets
import matplotlib.pyplot as plt
from scan_params import params
from app import ApplicationWindow
import qcodes as qc

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

    # Set lockin ready
    lockin = set_lockin_ready()

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
    

    # Move laser from center to the top left corner
    # _, _, _ = daq_interface(ao0_1_write_data=ao0_1_write_data_reverse[:,:2],
    #                                                 frequency=reverse_frequency,
    #                                                 input_mapping=params.input_mapping)
    for i in range(pixels):
        ################################################################
        # How this works:
        # 1. Fetch the x, y coordinates (for whole scan, a pixels x pixels 2D array each) from params.x_coordinates and params.y_coordinates
        # 2. Extract the x,y coordinates for current line (ID array each), and make a np array of shape (pixels,2) to store x y coordinates info
        # 3. Move to center, then move from center to the last
        # 4. Move laser by ao output, and record ai input signal simultaneously, as app.l_ch1 to app.l_ch3
        # 5. Move laser back (use ao0_1_write_data_reverse). This is important to ensure the alignment of the pixelated image.
        # 6. Repeat 1 - 4 for each line.
        # 7. Return to the center.
        ao0_1_write_data = generate_ao_data_xy_scan_with_sync_channel(
            ao_0_data_array=params.x_coordinates,
            ao_1_data_array=params.y_coordinates,
            index=i,pixels=pixels)
    
        app.l_ch1, app.l_ch2, app.l_ch3, x_data, y_data = daq_interface_sync(ao0_1_write_data=ao0_1_write_data,
                                                        frequency=frequency,
                                                        input_mapping=params.input_mapping,
                                                        lockin=lockin)
        # move laser back to original position
        reverse_frequency = min(40*frequency,256)
        ao0_1_write_data_reverse = np.copy(np.flip(ao0_1_write_data,axis=0))
        _, _, _ = daq_interface(ao0_1_write_data=ao0_1_write_data_reverse[:,:2],
                                                    frequency=reverse_frequency,
                                                    input_mapping=params.input_mapping)

        app.l_ch2 = x_data
        app.l_ch3 = y_data
        app.i_ch1[i] = app.l_ch1
        # app.i_ch2[i] = app.l_ch2
        # app.i_ch3[i] = app.l_ch3
        app.i_ch2[i] = x_data
        app.i_ch3[i] = y_data
 
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
    

    _ = daq_interface(ao0_1_write_data=ao_stop,
                           frequency=move_frequency,
                           input_mapping=params.input_mapping)
    qc.Instrument.close_all()
    if close:
        qapp.exec()
    return app.i_ch_images
