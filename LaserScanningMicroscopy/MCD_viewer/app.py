import sys, os, json
from pathlib import Path
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QWidget, QTabWidget, QLabel
)
import pyqtgraph as pg
from pyqtgraph import ImageView
from position_params import Position_parameters

class ImageViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCD Image Viewer")
        self.resize(800, 600)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout
        self.layout = QVBoxLayout(self.central_widget)

        # Button to load files
        self.load_button = QPushButton("Open MCD data (in .npy format)")
        self.load_button.clicked.connect(self.load_files)
        self.layout.addWidget(self.load_button)

        self.info = QLabel('Move mouse to get location information.')
        self.layout.addWidget(self.info)

        # # Tab widget to hold multiple images
        # self.tab_widget = QTabWidget()
        # self.layout.addWidget(self.tab_widget)

        # self.img_widgets = []
        # self.imgs = []
        self.img_widget = pg.PlotWidget()
        self.layout.addWidget(self.img_widget)
        self.img = pg.ImageItem(np.zeros((100,100)))
        self.img_widget.addItem(self.img)
        self.img_widget.setAspectLocked(True)

        

    def load_files(self):
        # Open file dialog to select multiple .npy files
        file_dialog = QFileDialog(self, "Open MCD data (in .npy format)", "", "NumPy Files (*.npy);;All Files (*)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            for file_path in file_paths:
                self.add_image(file_path)

    def add_image(self, file_path):
        try:
            # Load NumPy array
            self.data = np.flip(np.load(file_path).T, axis=1)
            position_params_folder = str(Path(os.path.dirname(file_path)).parent) + '/parameters/position_params.json'
            # print('\n\n\n' + parent_folder)
            with open(position_params_folder, "r") as file:
                position_params_setup = json.load(file)
                # print(position_params_setup)
                
                self.position_parameters = Position_parameters(
                    x_center=position_params_setup['centers'][0],
                    y_center=position_params_setup['centers'][1],
                    z_center=position_params_setup['centers'][2],
                    x_size=position_params_setup['scan_size'][0],
                    y_size=position_params_setup['scan_size'][1],
                    x_pixels=position_params_setup['pixels'][0],
                    y_pixels=position_params_setup['pixels'][1],
                    angle=position_params_setup['angle_in_degrees'])
                self.x_coordinates = self.position_parameters.x_coordinates
                self.y_coordinates = self.position_parameters.y_coordinates
                self.z_coordinates = position_params_setup['centers'][2]
            
            if self.data.ndim != 2:
                raise ValueError(f"File {file_path} does not contain a 2D array.")
            
            # Create an ImageView widget for displaying the image
            


            self.img.setImage(self.data)
            self.img_widget.setAspectLocked(True)

            self.line_width, self.scan_num = self.data.shape
            # self.img.setImage(data)
            
            # Add the ImageView to a new tab
          

            self.proxy = pg.SignalProxy(self.img_widget.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)
        
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
    def mouse_moved(self, event):

    
      
        self.axis_label_offset_calculated = False
        scene_pos = self.img_widget.getPlotItem().getViewBox().mapToView(event[0])
     
        x, y = scene_pos.x(), scene_pos.y()
        self.location = (x, y)

        if not self.axis_label_offset_calculated:
            top_axis_coords = self.img_widget.getPlotItem().getAxis('top').geometry().getCoords()
            right_axis_coords = self.img_widget.getPlotItem().getAxis('right').geometry().getCoords()
            view_range = self.img_widget.getPlotItem().getViewBox().viewRange()
            self.x_range, self.y_range = (view_range[0][1] - view_range[0][0], view_range[1][1] - view_range[1][0])
            self.x_offset = self.x_range *  top_axis_coords[0] / (top_axis_coords[2] - top_axis_coords[0])
            self.y_offset = self.y_range *  right_axis_coords[1] / (right_axis_coords[3] - right_axis_coords[1])

        x_label = int(x - self.x_offset)
        y_label = int(y - self.y_offset)

        x_label = max(0, min(x_label, self.data.shape[0] - 1))
        y_label = max(0, min(y_label, self.data.shape[1] - 1))

        x_pos = self.position_parameters.x_coordinates[y_label, x_label]
        y_pos = self.position_parameters.y_coordinates[y_label, x_label]

        # print("\n\n\n")
        # print(self.position_parameters.x_coordinates.shape)

        # # Update the textbox with the coordinates
        current_val = self.data[x_label, y_label]
       
        # self.xy_label.setText(f"X, Y position = {x_pos:.1f} µm, {y_pos:.1f} µm, data = {current_val:.2e}")

        self.info.setText(f"X, Y position = {x_pos:.1f} µm, {y_pos:.1f} µm, data = {current_val:.2e}")
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewerApp()
    viewer.show()
    sys.exit(app.exec())
