import sys, os
import random
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QTimer,Qt
import pyqtgraph as pg
from PySide6.QtGui import QFontDatabase, QFont
from decimal import Decimal
from pyqtgraph import PlotWidget
import numpy as np
import time


class CustomAxisItem(pg.AxisItem):
    def __init__(self, axis_label_ticks_distance, *args, **kwargs):
        pg.AxisItem.__init__(self, *args, **kwargs)
        self.setStyle(tickTextOffset=axis_label_ticks_distance)  # Move tick labels inside
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

class LSMLivePlot(QtWidgets.QMainWindow):

    def __init__(self, 
                channel_num=3, 
                channel_names=[],
                steps=500, 
                font_size=12, 
                chart_wdith=400,
                show_zero_level=True):
        super().__init__()

        self.channel_num = channel_num
        self.channel_names = channel_names
        if len(self.channel_names) != self.channel_num:
            raise RuntimeError(f'\nChannel number {self.channel_num} and channel names: ' + str(self.channel_names) +' do not match. Check.\n')
        self.steps = steps
        self.count = 0
        self.chart_wdith = chart_wdith
        self.font_size = font_size
        self.show_zero_level = show_zero_level


        self.setWindowTitle("LSM Live Plot")
        self.setStyleSheet("background-color: black;")

        font_family = load_font('font/SourceCodePro-Medium.ttf')
        
        # # if font_family:
        global_font = QFont(font_family)
        global_font.setPixelSize(self.font_size)
        # self.setFont(global_font)
        
        # Layout to arrange the plots
        central_widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QHBoxLayout()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)


        # Initialize data containers for each chart
        self.x = np.arange(self.steps)
        self.y  = np.zeros((self.channel_num, self.steps))

        # Create PlotWidgets 
        # Plot the initial data
        self.plots = []
        self.curves = []
        for channel_id in range(self.channel_num):
            self.plots.append(PlotWidget(title=self.channel_names[channel_id]))
        
        for channel_id in range(self.channel_num):
            self.plots[channel_id].setMinimumWidth(self.chart_wdith)
            self.plots[channel_id].setMaximumWidth(self.chart_wdith)
            
            y_axis = CustomAxisItem(orientation='left',
                                     axis_label_ticks_distance=12)
            self.plots[channel_id].setAxisItems({'left': y_axis})

            for axis_label in [
                       'left','right', 'bottom', 'top']:
                self.plots[channel_id].showAxis(axis_label)
                self.plots[channel_id].getAxis(axis_label).setStyle(tickLength=2,showValues=True)
                self.plots[channel_id].getAxis(axis_label).setStyle(tickFont=global_font)
            self.plots[channel_id].getAxis('top').setStyle(tickLength=2,showValues=False)   
            self.plots[channel_id].getAxis('right').setStyle(tickLength=2,showValues=False)   
            self.plots[channel_id].setLabel('bottom', "Time steps")
            self.plots[channel_id].setLabel('left', "")
            self.plots[channel_id].getAxis('bottom').label.setFont(global_font)
            self.plots[channel_id].getAxis('left').label.setFont(global_font)
            # self.plots[channel_id].setXRange(0, self.steps, padding=0)
            self.plots[channel_id].setDefaultPadding(0)


            item = self.plots[channel_id].getPlotItem()
            item.titleLabel.item.setFont(global_font)
            

        for channel_id in range(self.channel_num):
            self.layout.addWidget(self.plots[channel_id])
        for channel_id in range(self.channel_num):
            zero_line = pg.InfiniteLine(
                pos=0, angle=0, 
                pen=pg.mkPen('r', width=2, style=Qt.DashLine))
            self.curves.append(self.plots[channel_id].plot( (0,0),(0,0) ))
            if self.show_zero_level:
                self.plots[channel_id].addItem(zero_line)

    def update_data(self, count, y_data):
        self.y = y_data
        self.count = count
        for channel_id in range(self.channel_num):
            self.curves[channel_id].setData(self.x[:self.count], self.y[channel_id][:self.count])



def main():

    channel_num, steps = (2, 200)
    app = QtWidgets.QApplication(sys.argv)
    main_window = LSMLivePlot(channel_num=channel_num, steps=steps)
    main_window.show()
    
    for count in range(steps):

        # Random delay between 0.5 and 2 seconds
        time.sleep(random.uniform(0.005, 0.010))
        # Generate new random y-data for the chart
        y = np.random.normal(size=(channel_num, steps))
        

        # Update
        main_window.update_data(count, y)
        app.processEvents()

    app.exit()


if __name__ == "__main__":
    main()
