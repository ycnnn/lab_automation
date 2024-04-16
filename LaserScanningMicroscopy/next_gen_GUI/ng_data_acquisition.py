import numpy as np

class Data_acquisitor():
    def __init__(self,line_width, scan_num, channel_num):
        self.line_width = line_width
        self.scan_num = scan_num
        self.channel_num = channel_num
    def run(self):
        data = np.random.normal(size=(self.channel_num, self.line_width))
        return data

