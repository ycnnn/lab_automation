import numpy as np
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel
from PySide6 import QtCore
from PySide6.QtGui import QGuiApplication
import pyqtgraph as pg
import time 
import warnings


# class CustomAxisItem(pg.AxisItem):

#     def tickStrings(self, values, scale, spacing):

#         places = max(0, np.ceil(-np.log10(spacing*scale)))
#         strings = []
#         for v in values:
#             vs = v * scale
#             vstr = ("%%0.%df" % places) % vs
#             strings.append(vstr)
#         return strings
def widget_format(widget):
    widget.hideButtons()
    widget.setStyleSheet("background-color: black;")
    widget.showAxis('top')
    widget.showAxis('bottom')
    widget.showAxis('left')
    widget.showAxis('right')
    

class QPlot(QMainWindow):
    def __init__(self, 
                 line_width, 
                 scan_num,
                 channel_num=3,
                 ):
        
        super().__init__()
        self.line_width = line_width
        self.scan_num = scan_num
        self.channel_num = channel_num
        self.counter = 0
        self.time = time.time()
        self.setWindowTitle(f'{self.channel_num} Channel Scan: Frame {self.counter}')
        self.resize(300*self.channel_num,300)

        # width,height = self.primaryScreen().size().toTuple()
        # self.setMaximumWidth(width)

        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.mainWidget.setStyleSheet("background-color: black;")
        self.layout = QGridLayout(self.mainWidget)
        self.layout.setContentsMargins(5,5,5,5)

        self.widgets = np.zeros(shape=(self.channel_num, 2), dtype=np.object_)
        self.plots = np.zeros(shape=(self.channel_num, 2), dtype=np.object_)

        for row_id in range(self.channel_num):
            self.widgets[row_id,0] = pg.PlotWidget()
            self.widgets[row_id,0].setMouseEnabled(x=False, y=False)
            self.widgets[row_id,1] = pg.PlotWidget()
        
            widget_format(self.widgets[row_id,0])
            widget_format(self.widgets[row_id,1])

    
            self.layout.addWidget(self.widgets[row_id,0], 0, row_id)
            self.layout.addWidget(self.widgets[row_id,1], 1, row_id)
        
        # self.layout.setRowStretch(0,0.5)
        # self.layout.setRowStretch(1,1)
        
        ######################################################################
        # Initialize data
        self.data = np.zeros(shape=(self.channel_num, self.line_width, self.scan_num))

        ######################################################################
        # Initialize plots

      
        for row_id in range(self.channel_num):
            plot = self.widgets[row_id,0].plot(np.zeros(shape=self.line_width))
            img = pg.ImageItem(np.zeros(shape=(self.line_width, self.scan_num)))
            self.widgets[row_id,1].addItem(img)
            self.plots[row_id, 0] = plot
            self.plots[row_id, 1] = img
            img.getViewBox().setAspectLocked()
            self.widgets[row_id,0].setXRange(0, self.line_width, padding=0)
            self.widgets[row_id,1].setXRange(0, self.line_width, padding=0)

        
        self.show()
        # sample_fetch_data = np.random.normal(size=(self.channel_num, self.line_width))

        # for _ in range(self.scan_num):
        #     self.update(sample_fetch_data)

    def update(self, fetched_data):

        self.data[:,:,self.scan_num - self.counter - 1] = fetched_data
        for row_id in range(self.channel_num):
            self.plots[row_id, 0].setData(fetched_data[row_id])
            self.plots[row_id, 1].setImage(self.data[row_id])
        self.counter += 1
        elapse_time = time.time() - self.time
        self.time = time.time()
        self.setWindowTitle(f'{self.channel_num} Channel Scan: Frame {self.counter}, Est time {int(elapse_time*(self.scan_num - self.counter))} s')
        QApplication.processEvents()

