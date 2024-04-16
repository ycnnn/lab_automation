import sys
import time
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel
from PySide6 import QtCore
import numpy as np
import pyqtgraph as pg


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Qt test')
        self.resize(900,300)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QGridLayout(self.main_widget)
        self.layout.setContentsMargins(10,10,10,10) 

        # self.X = np.arange(256)
        # self.Y = np.zeros(shape=(3,2,256))
        self.Y = np.random.normal(size=(3,2,256))

        self.widgets = []
        self.plots = []
        for row in range(3):
            row_widgets = []
            plots = []
            for col in range(2):

                # widget = QWidget()
                widget = pg.PlotWidget()
                plot = widget.plot(self.Y[row,col])
                widget.setMouseEnabled(x=False, y=False)
                widget.setStyleSheet("background-color: grey;")
                widget.setFixedSize(280,280)
                self.layout.addWidget(widget, col, row)
                row_widgets.append(widget)
                plots.append(plot)

            self.widgets.append(row_widgets)
            self.plots.append(plots)
      
        #### Start  #####################
        self.counter = 0
        self._update()

    def _update(self):
        # return
        # time.sleep(1)
        
        self.Y = np.random.normal(size=(3,2,256))
        for row in range(3):
            for col in range(2):
                self.plots[row][col].setData(self.Y[row, col])

        QtCore.QTimer.singleShot(1, self._update)
        
        


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())