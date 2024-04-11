import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure
from generate_figure import generate_figure_3ch


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self,parameters):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.setWindowTitle('3 Chanel Scan')
        self.pixels = parameters.pixels
        self.scale=parameters.scale
        self.line_color = 'white' if parameters.dark_mode else 'black'
        self.setFixedWidth(parameters.window_width)
        self.setFixedHeight(parameters.window_height)
        self.colormap = parameters.colormap
        self.auto_scale = parameters.auto_scale
        self.val_range_1 = parameters.val_range_1
        self.val_range_2 = parameters.val_range_2
        self.val_range_3 = parameters.val_range_3
        self.save_destination = parameters.save_destination

        self.l_ch1 = np.zeros(self.pixels)
        self.l_ch2 = np.zeros(self.pixels)
        self.l_ch3 = np.zeros(self.pixels)

        self.i_ch_images = np.zeros((3, self.pixels, self.pixels))

        self.i_ch1 = self.i_ch_images[0]
        self.i_ch2 = self.i_ch_images[1]
        self.i_ch3 = self.i_ch_images[2]



        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(dynamic_canvas)
        self.fig = dynamic_canvas.figure

        (self.top_ch_1, self.chan_1, self.line_ch_1, self.chan_1_image,
        self.top_ch_2, self.chan_2, self.line_ch_2, self.chan_2_image,
        self.top_ch_3, self.chan_3, self.line_ch_3, self.chan_3_image) = generate_figure_3ch(
            fig=self.fig,
            scale=self.scale,
            colormap=self.colormap,
            auto_scale=self.auto_scale,
            val_range_1=self.val_range_1,
            val_range_2=self.val_range_2,
            val_range_3=self.val_range_3,
            line_color=self.line_color,
            l_ch1=self.l_ch1,
            i_ch1=self.i_ch1,

            l_ch2=self.l_ch2,
            i_ch2=self.i_ch2,

            l_ch3=self.l_ch3,
            i_ch3=self.i_ch3)

    def _update_canvas(self,l_ch1,i_ch1,
                       scan_id=1,single_time=0.1):
        
        self.line_ch_1.set_ydata(l_ch1)
        self.chan_1_image.set_data(i_ch1)
        if self.auto_scale:
            self.top_ch_1.relim()
            self.top_ch_1.autoscale_view()
            self.chan_1_image.autoscale()
        else:
            self.chan_1_image.set_clim(self.val_range[0],self.val_range[1])
        
        self.fig.suptitle(f'Scanning line {scan_id+1} out of {self.pixels},\n remaining time = {int(single_time*(self.pixels-scan_id-1))} seconds')
        self.fig.canvas.draw()

    def _update_canvas_3_ch(self,
                            l_ch1,i_ch1,
                            l_ch2,i_ch2,
                            l_ch3,i_ch3,
                       scan_id=1,single_time=0.1):
        
        self.line_ch_1.set_ydata(l_ch1)
        self.chan_1_image.set_data(i_ch1)
        self.line_ch_2.set_ydata(l_ch2)
        self.chan_2_image.set_data(i_ch2)
        self.line_ch_3.set_ydata(l_ch3)
        self.chan_3_image.set_data(i_ch3)

        if self.auto_scale:
            self.top_ch_1.relim()
            self.top_ch_1.autoscale_view()
            self.chan_1_image.autoscale()

            self.top_ch_2.relim()
            self.top_ch_2.autoscale_view()
            self.chan_2_image.autoscale()

            self.top_ch_3.relim()
            self.top_ch_3.autoscale_view()
            self.chan_3_image.autoscale()
        else:
            self.chan_1_image.set_clim(self.val_range_1[0],self.val_range_1[1])
            self.chan_2_image.set_clim(self.val_range_2[0],self.val_range_2[1])
            self.chan_3_image.set_clim(self.val_range_3[0],self.val_range_3[1])
        
        self.fig.suptitle(f'Scanning line {scan_id+1} out of {self.pixels},\n remaining time = {int(single_time*(self.pixels-scan_id-1))} seconds')
        self.fig.canvas.draw()

    def save_data(self):
        self.fig.savefig(self.save_destination + '.svg')
        np.save(self.save_destination, self.i_ch_images)
        for i, image in enumerate(self.i_ch_images):
            np.savetxt(self.save_destination + f'Channel_{i}.csv', image)
        # print('Saved!')