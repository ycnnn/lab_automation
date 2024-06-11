import numpy as np
import multiprocessing as mp
from PySide6.QtWidgets import QApplication
import sys
######################################################################
# Custom dependencies
from ng_app import QPlot
######################################################################

if __name__ == '__main__':
    line_width = 256
    scan_num = 128
    channel_num = 4
    app = QApplication(sys.argv)
    window = QPlot(line_width=line_width, scan_num=scan_num, channel_num=channel_num)
    window.show()

    

    for _ in range(scan_num):
        sample_fetch_data = np.random.normal(size=(channel_num, line_width))
        window.update(sample_fetch_data)
    # sys.exit(app.exec())
