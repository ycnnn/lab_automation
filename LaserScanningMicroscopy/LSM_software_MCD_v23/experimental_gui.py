import sys
import os
import time
import inspect
import importlib
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QLabel,QPushButton, QProgressBar, QSpacerItem, QSizePolicy,QToolTip, QSpacerItem, QLineEdit, QScrollArea, QComboBox, QCheckBox,QLayout
from PySide6.QtGui import QFontDatabase, QColor,QMouseEvent, QFont,QFontMetrics
from PySide6.QtCore import Qt, QRectF, QTimer
import pyqtgraph as pg
import numpy as np
from decimal import Decimal
from functools import partial
import random


def read_instrument_setup(path='source.inst_driver'):
    instr_module = importlib.import_module(path)
    instr_classes = inspect.getmembers(instr_module, inspect.isclass)

    instr_names = []
    instr_params = {}
    instr_init_arguments = {}
    for instr_name, instr_obj in instr_classes:
        if issubclass(instr_obj, instr_module.Instrument) and instr_obj is not instr_module.Instrument:
            instr_names.append(instr_name)
            instr_params[instr_name] = instr_obj._params
            init_method = instr_obj.__init__
            signature = inspect.signature(init_method)
            default_args = {
                            param_name: param.default
                            for param_name, param in signature.parameters.items()
                            if param.default is not inspect.Parameter.empty and param.default is not None
                        }
            instr_init_arguments[instr_name] = default_args


    return instr_names, instr_params, instr_init_arguments
   
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



class Instrument_area(QLabel):
    def __init__(self, instr_type='Example instr', instr_params={}, init_arguments={}):
        super().__init__()
        self.instr_type = instr_type
        self.setStyleSheet("background-color: black;")
        self.char_height = QFontMetrics(self.font()).height()
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        
        self.type_label = QLabel(self.instr_type)
        self.layout.addWidget(self.type_label, 0, 0)

        self.name_label = QLabel('Instrument name')
        self.layout.addWidget(self.name_label, 0,1)

        self.name_field = QLineEdit(self.instr_type)
        self.layout.addWidget(self.name_field, 0,2)

        self.params = instr_params
        self.init_arguments = init_arguments
        self.param_list = []

        # print(self.init_arguments)

        self.param_dropdowns = []
        self.param_modes = {}
        self.total_rows = 1
        for param in self.params:
            self.add_param(param=param)
        ######################################
        # Additional setttings
        # self.address_label = QLabel('Address')
        # self.layout.addWidget(self.address_label, self.total_rows,0)

        # self.address_field = QLineEdit('USB::0')
        # self.layout.addWidget(self.address_field, self.total_rows,1)
        for init_arg in self.init_arguments:
            self.add_init_arguments(init_arg)
        ######################################

        self.set_size()
    def add_init_arguments(self, arg='address'):
        self.layout.addWidget(QLabel(arg), self.total_rows,0)
        init_arg_input_field = QLineEdit(str(self.init_arguments[arg]))
        self.layout.addWidget(init_arg_input_field, self.total_rows,1)
        self.total_rows += 1


    def add_param(self, param='Param1'):
        
        param_id = len(self.param_dropdowns)
        self.param_modes[param_id] = 0
        self.param_list.append(param)
        self.layout.addWidget(QLabel(param), self.total_rows,0)
        param_dropdown = QComboBox()
        param_dropdown.addItems(['Constant', 'Linear', 'Trace/retrace', 'Custom'])
        self.layout.addWidget(param_dropdown, self.total_rows,1)
        constant_input_field = QLineEdit(str(self.params[param]))
        self.layout.addWidget(constant_input_field)
        param_dropdown.currentIndexChanged.connect(partial(self.switch_param_input, param_id=param_id))
        self.param_dropdowns.append(param_dropdown)

        self.total_rows += 1
        
    def remove_param_input_menu(self, param_id):
        for index in [2,3,4,5]:
            item = self.layout.itemAtPosition(param_id+1, index)
            if item:
                item.widget().deleteLater()


    def switch_param_input(self, index, param_id):
        param = self.param_list[param_id]
        defult_val = str(self.params[param])
        self.remove_param_input_menu(param_id=param_id)
        self.param_modes[param_id] = index
        if index == 0:
            param_constant_field = QLineEdit(defult_val)
            self.layout.addWidget(param_constant_field, param_id + 1, 2)
        elif index == 1:
            param_start_field = QLineEdit(defult_val)
            param_end_field = QLineEdit(defult_val)
            self.layout.addWidget(QLabel('Start'), param_id + 1, 2)
            self.layout.addWidget(param_start_field, param_id + 1, 3)
            self.layout.addWidget(QLabel('End'), param_id + 1, 4)
            self.layout.addWidget(param_end_field, param_id + 1, 5)
        elif index == 2:
            param_trace_field = QLineEdit(defult_val)
            param_retrace_field = QLineEdit(defult_val)
            self.layout.addWidget(QLabel('Trace'), param_id + 1, 2)
            self.layout.addWidget(param_trace_field, param_id + 1, 3)
            self.layout.addWidget(QLabel('Retrace'), param_id + 1, 4)
            self.layout.addWidget(param_retrace_field, param_id + 1, 5)
        elif index == 3:
            param_constant_field = QLineEdit('List of shape (2, y_pixels)')
            self.layout.addWidget(param_constant_field, param_id + 1, 2,1,2)
        else:
            raise RuntimeError


        
    def set_size(self):
        self.setMinimumHeight((self.total_rows + 1) * 2 * self.char_height)
        self.setMaximumHeight((self.total_rows + 1) * 2 * self.char_height)
     
        
        

class ControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Setup a LSM Scan")
        self.setStyleSheet("QMainWindow { background-color: black; }")
        screen = QApplication.primaryScreen()
        screen_height = screen.geometry().height()
        # Set the widget's height to match the screen height
        self.setFixedHeight(0.90 * screen_height)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        # Main layout
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.params_layout = QGridLayout()

        self.params_layout.addWidget(QLabel('Step 1: Setting up scan parameters'), 0, 0, 1,4)

        self.params_layout.addWidget(QLabel('Scan ID'), 1, 0)
        self.scan_id_field = QLineEdit('Test_scan')
        self.params_layout.addWidget(self.scan_id_field, 1, 1)

        self.save_settings_button = QPushButton('Save settings')
        self.load_settings_button = QPushButton('Load settings')
        self.params_layout.addWidget(self.save_settings_button, 1, 2)
        self.params_layout.addWidget(self.load_settings_button, 1, 3)

        self.params_layout.addWidget(QLabel('XYZ Center (um)'), 2, 0)
        self.x_center_field = QLineEdit('50')
        self.y_center_field = QLineEdit('50')
        self.z_center_field = QLineEdit('25')
        self.params_layout.addWidget(self.x_center_field, 2, 1)
        self.params_layout.addWidget(self.y_center_field, 2, 2)
        self.params_layout.addWidget(self.z_center_field, 2, 3)

        self.params_layout.addWidget(QLabel('XY Size (um)'), 3, 0)
        self.x_size_field = QLineEdit('20')
        self.y_size_field = QLineEdit('20')
        self.params_layout.addWidget(self.x_size_field, 3, 1)
        self.params_layout.addWidget(self.y_size_field, 3, 2)

        self.params_layout.addWidget(QLabel('XY Pixels'), 4, 0)
        self.x_pixel_field = QLineEdit('100')
        self.y_pixel_field = QLineEdit('100')
        self.params_layout.addWidget(self.x_pixel_field, 4, 1)
        self.params_layout.addWidget(self.y_pixel_field, 4, 2)

        self.params_layout.addWidget(QLabel('Rotate angle (deg)'), 5, 0)
        self.rotate_angle_field = QLineEdit('0')
        self.params_layout.addWidget(self.rotate_angle_field, 5, 1)

        self.retrace_state = QCheckBox("Retrace time constant is different")
        self.retrace_state.stateChanged.connect(self.set_retrace_state)
        self.params_layout.addWidget(self.retrace_state, 6,0,1,4)
        self.params_layout.addWidget(QLabel('Trace'), 7, 1)
        self.retrace_label = QLabel('Retrace time same as trace time')
        self.params_layout.addWidget(self.retrace_label, 7, 2,1,2)

        self.params_layout.addWidget(QLabel('Time constants (s)'), 8, 0)
        self.trace_time_constant_field = QLineEdit('0.1')
        self.retrace_time_constant_field = QLineEdit('0.1')
        self.retrace_label.setVisible(False)
        self.retrace_time_constant_field.setVisible(False)
        self.params_layout.addWidget(self.trace_time_constant_field, 8, 1)
        self.params_layout.addWidget(self.retrace_time_constant_field, 8, 2)

        self.params_layout.addWidget(QLabel('Step 2: Setting up instruments'), 9, 0, 1,4)


        self.instr_dropdown = QComboBox()
        self.instr_names, self.instr_params, self.instr_init_arguments = read_instrument_setup()
        self.instr_dropdown.addItems(self.instr_names)
        self.params_layout.addWidget(self.instr_dropdown,10,0,1,2)
        self.add_instr_button = QPushButton('Add')
        self.remove_instr_button = QPushButton('Remove')
        self.remove_instr_button.setEnabled(False) 
        

        self.params_layout.addWidget(self.add_instr_button, 10,2)
        self.params_layout.addWidget(self.remove_instr_button, 10,3)

        self.instrument_display_area = QScrollArea()
        self.instrument_display_area.setWidgetResizable(True)
        self.instrument_display_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.instrument_display_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)        
        self.instrument_content = QWidget()
        self.instrument_layout = QVBoxLayout()
        self.instrument_layout.setAlignment(Qt.AlignTop) 
        self.instrument_display_area.setWidget(self.instrument_content)
        self.instrument_content.setLayout(self.instrument_layout)
        self.params_layout.addWidget(self.instrument_display_area, 11,0,1,4)
        self.add_instr_button.clicked.connect(self.add_instr)
        self.remove_instr_button.clicked.connect(self.remove_instr)
        self.selected_instr = None

        self.main_layout.addLayout(self.params_layout)


        self.params_layout.addWidget(QLabel('Step 3: Start the scan'), 12, 0, 1,3)
        self.start_scan_button = QPushButton('Start scan')
        self.params_layout.addWidget(self.start_scan_button, 12, 3)


    def set_retrace_state(self, state):
        if Qt.CheckState(state) == Qt.Unchecked:
            self.retrace_label.setText('Retrace time same as trace time')
            self.retrace_label.setVisible(False)
            self.retrace_time_constant_field.setVisible(False)
            trace_time_constant = self.trace_time_constant_field.text()
            self.retrace_time_constant_field.setText(trace_time_constant)
            self.retrace_time_constant_field.setReadOnly(True)
        elif Qt.CheckState(state) == Qt.Checked:
            self.retrace_label.setVisible(True)
            self.retrace_time_constant_field.setVisible(True)
            self.retrace_label.setText('Retrace')
            self.retrace_time_constant_field.setReadOnly(False)
        else:
            raise RuntimeError
    
    def add_instr(self):
        instr_type = self.instr_dropdown.currentText()
        instr_params = self.instr_params[instr_type]
        init_arguments = self.instr_init_arguments[instr_type]
        instr_area = Instrument_area(instr_type=instr_type,
                                     instr_params=instr_params,
                                     init_arguments=init_arguments)
        instr_area.mouseReleaseEvent = lambda event, instr=instr_area: self.select_instr(instr)
        self.instrument_layout.addWidget(instr_area)
        

    def remove_instr(self):
        if self.selected_instr:
            self.instrument_layout.removeWidget(self.selected_instr)
            self.selected_instr.deleteLater()
            self.selected_instr = None
            self.remove_instr_button.setEnabled(False)

    def select_instr(self, instr):
        # Reset previous selection
        if self.selected_instr:
            self.selected_instr.setStyleSheet("background-color: black;")

        # Highlight the new selection
        self.selected_instr = instr
        self.selected_instr.setStyleSheet("background-color: darkgreen;")

        # Enable remove button
        self.remove_instr_button.setEnabled(True)



        
  


if not QApplication.instance():
    app = QApplication([])
else:
    app = QApplication.instance()

font_family = load_font('font/SourceCodePro-Medium.ttf')
if font_family:
    global_font = QFont(font_family)
    global_font.setPixelSize(12)
    app.setFont(global_font)
control_panel = ControlPanel()
control_panel.show()
app.exec()