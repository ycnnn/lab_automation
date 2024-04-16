from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel
from PySide6 import QtCore
import multiprocessing as mp
import time
import random
import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
#from pyqtgraph.dockarea import *

class PLT():
    def __init__(self):
        self.win = pg.GraphicsLayoutWidget(title="Basic plotting examples")
        self.win.setWindowTitle('pyqtgraph example: Plotting')
        #self.win.resize(1000,600)
        self.p2 = self.win.addPlot(title="Updating plot")
        self.curve = self.p2.plot(pen='y')
        self.win.show()

        #QtGui.QApplication.instance().exec_()   # ---> if it's in effect, the plotting window shows up, but the data exchange doesn't happen.

    def update(self, data):
        self.curve.setData(data)
        QApplication.processEvents()   # <--- Here is the way to update the window.

class sender(mp.Process):
    def __init__(self, pipe):
        mp.Process.__init__(self)
        self.pipe = pipe

    def run(self):
        print('SENDER PID: ', os.getpid() )
        while True:
            value = random.randint(0, 10)
            self.pipe.send(value)
            time.sleep(.01)

class receiver(mp.Process):
    def __init__(self, pipe):
        mp.Process.__init__(self)
        self.pipe = pipe

    def run(self):
        self.p = PLT()
        print('RECEIVER PID: ', os.getpid() )
        while True:
            integer = self.pipe.recv() 
            print(integer)  

            self.p.update(np.random.normal(size=(10,1000))[integer%10])

if __name__ == '__main__':
    mp.freeze_support()
    print('MAIN PID: ', os.getpid() )

    out_pipe, in_pipe = mp.Pipe() 

    p1 = sender(pipe=in_pipe)
    p2 = receiver(pipe=out_pipe)
    p1.start()
    p2.start()