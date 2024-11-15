import multiprocessing as mp
# from PySide6.QtWidgets import QApplication
import numpy as np
import os


######################################################################
# Custom dependencies
from source.app import QPlot
######################################################################

class Data_receiver(mp.Process):
    def __init__(self,
                 position_parameters,
                 scan_parameters,
                 display_parameters,
                 channel_num,
                 channel_names,
                 pipe) -> None:
        mp.Process.__init__(self)
        self.position_parameters = position_parameters
        self.scan_parameters = scan_parameters
        self.display_parameters = display_parameters
        self.line_width = self.position_parameters.x_pixels
        self.scan_num = 2 * self.position_parameters.y_pixels
        self.channel_num = channel_num
        self.channel_names = channel_names
        self.pipe = pipe
       


    def run(self):
        counter = 0

        #####################################################################
        # Initilize plots
        # self.app = QApplication(sys.argv)
        # self.window = QPlot(line_width=self.line_width, scan_num=self.scan_num, channel_num=self.scan_parameters.channel_num)
        # self.window.show()
        self.app = QPlot(line_width=self.line_width, 
                         scan_num=self.scan_num, 
                         channel_num=self.channel_num,
                         channel_names=self.channel_names,
                         text_bar_height=self.display_parameters.text_bar_height,
                         window_width_min=self.display_parameters.window_width_min,
                         window_width_max=self.display_parameters.window_width_max,
                         show_zero_level=self.display_parameters.show_zero_level,
                         font_size=self.display_parameters.font_size,
                         axis_label_ticks_distance=self.display_parameters.axis_label_ticks_distance)
        #####################################################################

        for scan_index in range(self.scan_num):



            fetch_data = self.pipe.recv()
            # print('\n\n\n')
            # print(fetch_data.shape)
            # print('\n\n\n')
            if scan_index % 2 == 0:
                # Trace
                self.app.update(fetch_data)
            else:
                # Retrace
                self.app.retrace_update(fetch_data)
            
            # print(f'Scan_index {scan_index} data: Receiver received data')
            
            self.pipe.send(True)
            # print(f'Scan_index {scan_index} data: Receiver sent out confirmation')
            counter += 1
            if counter >= self.scan_num:
                break

        # if self.display_parameters.save_data:
        #     self.app.save_results(
        #         filepath=self.display_parameters.save_destination)
            
        self.pipe.send([self.app.data, self.app.retrace_data])

        self.app.save_screenshot()
        self.pipe.send(self.app.screenshots)


