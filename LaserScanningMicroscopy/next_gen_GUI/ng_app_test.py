import numpy as np
import multiprocessing as mp
from PySide6.QtWidgets import QApplication
import time 
import warnings
import sys
######################################################################
# Custom dependencies
from ng_app import QPlot
######################################################################

if __name__ == '__main__':
    line_width = 512
    scan_num = 512
    channel_num = 3
    app = QApplication(sys.argv)
    window = QPlot(line_width=line_width, scan_num=scan_num, channel_num=channel_num)
    window.show()

    sample_fetch_data = np.random.normal(size=(channel_num, line_width))

    for _ in range(scan_num):
        window.update(sample_fetch_data)
    sys.exit(app.exec())
  
