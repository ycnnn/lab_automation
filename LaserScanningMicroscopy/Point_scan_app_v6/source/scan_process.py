import sys, os, shutil, time
# from source.app import LSMLivePlot
from PySide6 import QtWidgets
import numpy as np
from contextlib import ExitStack
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLabel, QPushButton
from PySide6.QtGui import QGuiApplication, QFontDatabase, QFont, QColor, QPixmap, QPen
from PySide6.QtCore import Qt, QByteArray, QBuffer, QLoggingCategory, QThread, Signal,QRectF
import pyqtgraph as pg
from decimal import Decimal
# import source.instruments as inst_driver
# from source.log_config import setup_logging
# from source.parameters import Scan_paramters, Position_parameters
import source.instruments as inst_driver
from source.log_config import setup_logging
from source.parameters import Scan_paramters, Position_parameters

class LSM_single_scan(QThread):
    data_ready = Signal(list)
    finished = Signal()
    def __init__(self,
                 instruments=[],
                 scan_parameters=None,
                 simulate=False,
                 window_wdith=400,
                 ):
        super().__init__()
        self.scan_parameters = scan_parameters
        self.instruments = instruments
        self.simulate = simulate
        self.is_terminated = False

        self.window_width = window_wdith
        
         # Mandatory code. There MUST be at least one external instrument present dring the scan.
        empty_instr = inst_driver.EmptyInstrument(
            address='',
            scan_parameters=scan_parameters)
        self.instruments.append(empty_instr)

        self.channel_num = 0
        self.channel_names = []

        lockin_exists = any(
            isinstance(instrument, inst_driver.Lockin) for instrument in self.instruments)

        
        if lockin_exists:
            for instr_index, instr in enumerate(self.instruments):
                if isinstance(instr, inst_driver.Lockin):
                        break
            lockin = self.instruments[instr_index]
            self.instruments.pop(instr_index)
            self.instruments.append(lockin)

        for instrument in self.instruments:
            self.channel_num += instrument.channel_num
            for name in instrument.channel_name_list:
                self.channel_names.append(name)
      

        self.data = np.zeros(shape=(self.channel_num, self.scan_parameters.steps))
        # Set up the logging process
        self.logger = setup_logging(self.scan_parameters.save_destination)
        self.set_up_app()
        # self.start_scan()
        # self.save()

        
    def set_up_app(self):

        self.app = QApplication([])
        font_family = load_font('font/SourceCodePro-Medium.ttf')
        if font_family:
            global_font = QFont(font_family)
            global_font.setPixelSize(12)
            self.app.setFont(global_font)


        self.windows = []
        for channel_id in range(self.channel_num):
            window = SubWindow(channel_id=channel_id, name=self.channel_names[channel_id], thread=self, scan_num=self.scan_parameters.steps)
            window.setFixedWidth(self.window_width)
            window.move(channel_id * self.window_width,0)
            self.data_ready.connect(window.update_plot)
            self.windows.append(window)
            
        # Start the data thread
        self.start()

        # Show both windows
        for channel_id in range(self.channel_num):
            self.windows[channel_id].show()

        self.app.exec()
        
    
    def run(self):

        self.logger.info('Scan started.')

        instrument_manager = [
                instrument.initialize_and_quit for instrument in self.instruments]
        
        scan_manager = [instrument.scan for instrument in self.instruments]

        auxiliary_init_info = {'logger': self.logger}

        # self.start_ui()

        with ExitStack() as init_stack:
            _ = [init_stack.enter_context(
                    instr(**auxiliary_init_info)
                    ) for instr in instrument_manager]

            for scan_index in range(self.scan_parameters.steps):
                    
                    if self.is_terminated:
                        raise RuntimeError
                    
                    auxiliary_scan_info = {'scan_index': scan_index}
                        
                    with ExitStack() as scan_stack:
                        _ = [scan_stack.enter_context(
                                instr_scan(**auxiliary_scan_info)
                                ) for instr_scan in scan_manager]
                        
                 
                    instr_data = np.concatenate([
                            resource.data for resource in self.instruments
                            ])
                    self.data[:,scan_index] = instr_data
                    self.data_ready.emit([scan_index, instr_data])
                    # # Update
                    # self.main_window.update_data(scan_index, self.data)
                    # self.app.processEvents()
        self.finished.emit()
        self.logger.info('Scan finished.')
        # self.save()
   
    def close(self):
        self.is_terminated = True
        
        self.screenshots = []
        for window in self.windows:
            self.screenshots.append(window.grab())

        self.save()
        self.app.closeAllWindows()

    def save(self):

        # source_python_file = str(Path(__file__).resolve().parent) + '/start_scan.py'
        # shutil.copy(source_python_file, 
        # self.scan_parameters.save_destination + 'scan_settings.py')
        # screenshot = self.app.grab()
        # screenshot.save(self.scan_parameters.save_destination + 'screenshot.png')
        np.save(self.scan_parameters.save_destination + 'data', self.data)
        np.savetxt(self.scan_parameters.save_destination + 'data.csv', self.data.T,
                   header=",".join(self.channel_names),
                   delimiter=',',
                   comments=''
                   )
        for index, screenshot in enumerate(self.screenshots):
            screenshot.save(self.scan_parameters.save_destination+ self.channel_names[index] + '.png')


class CustomAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        pg.AxisItem.__init__(self, *args, **kwargs)
        # self.setStyle(tickTextOffset=axis_label_ticks_distance)  # Move tick labels inside
    def tickStrings(self, values, scale, spacing):
        # Generate tick strings with scientific notation, 1 digit after decimal, and always show sign
        return [f"{Decimal(value):+.1E}" for value in values]
        
  

def load_font(font_path):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    font_id = QFontDatabase.addApplicationFont(dir_path + '/' +  font_path)
    if font_id == -1:
        print(f"Failed to load font from {font_path}")
        return None
    font_families = QFontDatabase.applicationFontFamilies(font_id)
    if not font_families:
        print(f"No font families found for {font_path}")
        return None

    return font_families[0]

def widget_format(widget):
    widget.hideButtons()
    widget.setMouseEnabled(x=False, y=False)
    widget.setStyleSheet("background-color: black;")
    # widget.setXRange(0, x_range, padding=0)
    # widget.setDefaultPadding(0)

    for axis_label in [
        # 'left', 
                       'right', 
                    #    'bottom', 
                       'top']:
        widget.showAxis(axis_label)
        widget.getAxis(axis_label).setTicks([])
        widget.getAxis(axis_label).setStyle(tickLength=2,showValues=False)
        
      

class SubWindow(QMainWindow):
    def __init__(self, scan_num, thread, name='Channel 0', channel_id=0, window_width=400, font_size=12,):
        super().__init__()

        self.channel_id = channel_id
        self.name = name
        self.thread = thread

        self.setWindowTitle(self.name)
        self.scan_num= (scan_num)
        self.count = None
        self.data = np.zeros(self.scan_num)
        
        # Create a central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Create a layout
        self.layout = QVBoxLayout()
        
        self.central_widget.setLayout(self.layout)
        self.central_widget.setStyleSheet("background-color: black;")

        self.button = QPushButton("Terminate", self)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.set_terminate_flag)
        self.thread.finished.connect(self.finish)

        self.button.setStyleSheet("""
            QPushButton {
                background-color: red;  /* Red background */
                border: 0px solid black;  /* Black border */
                color: white;  /* White text color */
           
                padding: 5px;  /* Padding inside the button */
            }
            QPushButton:hover {
                background-color: darkred;  /* Dark red when hovered */
            }
        """)

       
        self.chart_widget = pg.PlotWidget()
        # self.info_label = QLabel('Currently scanning line 0')
  
        
   
        self.layout.addWidget(self.chart_widget)
   
        self.curve = self.chart_widget.plot()
      
        self.time = time.time()
        self.remaining_time = 0

        self.window_width = window_width
        self.font_size = font_size
        self.ui_format()
    def set_terminate_flag(self):
        self.thread.is_terminated = True
        self.button.clicked.connect(self.thread.close)
        # self.close()
    def finish(self):
        # When the thread finishes, change the button's text and color
        self.button.setText("Scan finished. Click to close all wondows.")
        self.button.setStyleSheet("""
            QPushButton {
                background-color: green;  /* Red background */
                border: 0px solid black;  /* Black border */
                color: white;  /* White text color */
           
                padding: 5px;  /* Padding inside the button */
            }
            QPushButton:hover {
                background-color: darkgreen;  /* Dark red when hovered */
            }
        """)
    def ui_format(self):

        widget_format(self.chart_widget)
        y_axis = CustomAxisItem(orientation='left',)

        # Replace the default y-axis with the custom axis for both the cart and the image
        # self.button.setFixedHeight(60)
        self.chart_widget.setAxisItems({'left': y_axis})
        self.chart_widget.getAxis('left').setTextPen('white')
        self.chart_widget.getAxis('bottom').setTextPen('white')

    def update_plot(self, data_pack):
        self.count, new_data = data_pack
        self.data[self.count] = new_data[self.channel_id]
        
        elapse_time = time.time() - self.time
        if self.count >= 1:
            self.remaining_time = int(elapse_time / self.count * (self.scan_num - self.count))

        self.curve.setData(self.data[:self.count + 1])
        self.setWindowTitle(self.name + f': scanning point {int(self.count)}, ' + f'{self.remaining_time} s remaining')


        








if __name__ == "__main__":
    pass