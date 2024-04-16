import sys
import time
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel
from PySide6 import QtCore
import numpy as np
import pyqtgraph as pg
from matplotlib import cm



def fetch_cmap(cmap_name='bwr'):
    colormap = cm.get_cmap(cmap_name)  
    colormap._init()
    lut = (colormap._lut * 255).view(np.ndarray) 
    return lut

class MainWindow(QMainWindow):
    def __init__(self):

        self.pixels = 512
        super().__init__()
        self.setWindowTitle('0')
        self.resize(900,450)

        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("background-color: black;")
        self.setCentralWidget(self.main_widget)
        self.layout = QGridLayout(self.main_widget)
        self.layout.setContentsMargins(10,10,10,10) 


        self.Y = np.random.normal(size=(3,2,self.pixels))

        self.widgets = []
        self.plots = []
        for row in range(3):
            row_widgets = []
            plots = []
            for col in range(2):
                if col == 0:
                    # widget = QWidget()
                    widget = pg.PlotWidget()
                    plot = widget.plot(self.Y[row,col])
                    widget.setXRange(0, self.pixels, padding=0)
                    widget.setMouseEnabled(x=False, y=False)
                    widget.setStyleSheet("background-color: black;")
                    widget.setFixedSize(280,140)
                    widget.hideButtons()
                    widget.showAxis('top')
                    # widget.getAxis('top').setStyle(showValues=False)
                    widget.showAxis('bottom')
                    # widget.getAxis('bottom').setStyle(showValues=False)
                    widget.showAxis('left')
                    # widget.getAxis('left').setStyle(showValues=False)
                    widget.showAxis('right')
                    # widget.getAxis('right').setStyle(showValues=False)
                
                    
                    self.layout.addWidget(widget, col, row)
                    row_widgets.append(widget)
                    plots.append(plot)
                else:
                    widget = pg.PlotWidget()
                    img = pg.ImageItem(np.random.normal(size=(self.pixels,self.pixels)))
                    img.setLookupTable(fetch_cmap())
                    widget.setXRange(0, self.pixels, padding=0)
                    widget.showAxis('top')
                    widget.showAxis('bottom')
                    widget.showAxis('left')
                    widget.showAxis('right')
                    widget.hideButtons()
                    widget.addItem(img)
                    # widget = pg.image(np.random.normal(size=(self.pixels,self.pixels)))
                    widget.setFixedSize(280,280)
                    self.layout.addWidget(widget, col, row)
                    row_widgets.append(widget)
                    plots.append(img)

            self.widgets.append(row_widgets)
            self.plots.append(plots)
      
        #### Start  #####################
        self.counter = 0
        self._update()
        self.start_time = time.time()

    def _update(self):
        # return
        # time.sleep(1)
        
        self.Y = np.random.normal(size=(3,2,self.pixels))
        for row in range(3):
            for col in range(2):
                if col == 0:
                    self.plots[row][col].setData(self.Y[row, col])
                else:
                    self.plots[row][col].setImage(np.random.normal(size=(self.pixels,self.pixels)))
        self.counter += 1
        self.setWindowTitle(f'Frame: {self.counter}')
        QtCore.QTimer.singleShot(1, self._update)
        if self.counter % 60 == 0:
            print(self.counter/(time.time() - self.start_time))
        
        


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())