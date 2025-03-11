import sys
import os, json
import ast
import time, traceback
import inspect
import importlib
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QLabel,QPushButton, QProgressBar, QSpacerItem, QSizePolicy,QToolTip, QSpacerItem, QLineEdit, QScrollArea, QComboBox, QCheckBox,QLayout, QFileDialog, QDialog,QDialogButtonBox, QMessageBox
from PySide6.QtGui import QFontDatabase, QColor,QMouseEvent, QFont,QFontMetrics
from PySide6.QtCore import Qt, QRectF, QTimer
import pyqtgraph as pg
import numpy as np
from decimal import Decimal
from functools import partial
import random
import gc
import platform


def enforce_font_size(widget, font_size):
    """ Recursively apply font size to all child widgets. """
    font = widget.font()
    font.setPointSize(font_size)
    widget.setFont(font)

    for child in widget.findChildren(QWidget):
        enforce_font_size(child, font_size)  # Apply to all descendants




def read_instrument_setup(path='source.inst_driver'):
    instr_module = importlib.import_module(path)
    instr_classes = inspect.getmembers(instr_module, inspect.isclass)

    instr_names = []
    instr_params = {}
    instr_init_arguments = {}
    for instr_name, instr_obj in instr_classes:
        if issubclass(instr_obj, instr_module.Instrument) and instr_obj is not instr_module.Instrument:
            instr_names.append(instr_name)

            ##########################################
            ##########################################
            ##########################################
            init_method = instr_obj.__init__
            signature = inspect.signature(init_method)
            default_args = {
                            param_name: param.default
                            for param_name, param in signature.parameters.items()
                            if param_name not in ['self', 'scan_parameters', 'position_parameters',
                                                  'name','kwargs']
                        }
            for arg in default_args.keys():
                default_arg_val = default_args[arg]
                if isinstance(default_arg_val, type):
                    default_args[arg] = '0'
            instr_init_arguments[instr_name] = default_args
            ##########################################
            ##########################################
            ##########################################
            source = inspect.getsource(instr_obj)
            instr_params[instr_name] = {}
            # Parse the source code into an AST
            tree = ast.parse(source)
            
            # Traverse the AST to find the assignment to self.params
            class_body = [node for node in tree.body if isinstance(node, ast.ClassDef)][0]
            init_method = next(
                (node for node in class_body.body if isinstance(node, ast.FunctionDef) and node.name == "__init__"), 
                None
            )

            if not init_method:
                raise ValueError("No __init__ method found in the class.")

            for node in init_method.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        # print(target.attr)
                   
                        if isinstance(target, ast.Attribute) and target.attr == "params":
                            params_dict = ast.literal_eval(node.value)
                            instr_params[instr_name] = params_dict
                           


            
            ##########################################
            ##########################################
            ##########################################


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

class AppearanceDialog(QDialog):
    def __init__(self, system=None):
        super().__init__()
        self.system = system
        self.setWindowTitle("Setting window appearances")

        layout = QGridLayout()
        customize_font_size = system.scan_parameters['custom_font_size']
        customize_window_width = system.scan_parameters['custom_window_width']
        self.font_size_label = QLabel("Customize font size:")
        self.font_size_input = QLineEdit(str(customize_font_size))
        layout.addWidget(self.font_size_label, 0, 0)  # Row 0, Column 0
        layout.addWidget(self.font_size_input, 0, 1)  # Row 0, Column 1

        self.window_width_label = QLabel("Customize scanning window width:")
        self.window_width_input = QLineEdit(str(customize_window_width))
        layout.addWidget(self.window_width_label, 1, 0)  # Row 1, Column 0
        layout.addWidget(self.window_width_input, 1, 1)  # Row 1, Column 1


        self.save_destination_label = QLabel("Customize save destination:")
        self.save_destination_button = QPushButton("Choose")
        self.save_destination_button.clicked.connect(self.set_save_destination)
        self.save_destination_input = QLabel(system.save_destination)
        self.save_destination_input.setWordWrap(True)
        layout.addWidget(self.save_destination_label, 2, 0)  # Row 1, Column 0
        layout.addWidget(self.save_destination_button, 2, 1) 
        layout.addWidget(self.save_destination_input, 3, 0,1,2)  # Row 1, Column 1

        # OK and Cancel buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout.addWidget(self.buttonBox, 4, 0, 1, 2)  # Span across two columns

        self.setLayout(layout)

    def set_save_destination(self):
        # try:
            folder_path = QFileDialog.getExistingDirectory(self, "Select Directory to save",self.system.save_destination)
            self.save_destination_input.setText(folder_path)
        # except:
        #     pass
    def get_values(self):
        font_size_input, window_width_input, save_destination = self.font_size_input.text(), self.window_width_input.text(), self.save_destination_input.text()
        font_size_input = font_size_input.strip()  # Remove any spaces
        window_width_input = window_width_input.strip() 

        if font_size_input.lower() == "none":  # User explicitly types "None"
            font_size = None
        else:
            try:
                font_size = int(float(font_size_input))  # Convert to int otherwise
            except:
                pass

        if window_width_input.lower() == "none":  # User explicitly types "None"
            window_width= None
        else:
            try:
                window_width = int(float(window_width_input))  # Convert to int otherwise
            except:
                pass
        
        return font_size, window_width, save_destination


class Instrument_area(QLabel):
    def __init__(self, instr_type='Example instr', instr_params={}, init_arguments={}, scan_system=None):
        super().__init__()
        self.instr_type = instr_type
        self.setStyleSheet("background-color: black;")
        self.char_height = QFontMetrics(self.font()).height()
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.scan_system = scan_system

        self.init_args_values = {}
        self.init_args_input_fields = {}
        self.param_values = {}
        self.param_input_fields = {}
        self.is_selected = False

        
        self.type_label = QLabel("Type: " + self.instr_type)
        self.layout.addWidget(self.type_label, 0, 0)

        self.name_label = QLabel('Instrument name')
        self.layout.addWidget(self.name_label, 0,1)

        self.init_args_values['name'] = self.instr_type
        self.name_field = QLineEdit(self.init_args_values['name'])
        self.layout.addWidget(self.name_field, 0,2)
        self.init_args_input_fields['name'] = self.name_field
        self.name_field.editingFinished.connect(partial(self.set_init_args, 'name'))

        self.params = instr_params
        self.init_arguments = init_arguments
        self.param_list = []

        



        self.param_dropdowns = []
        self.param_modes = {}
        self.total_rows = 1
        for param in self.params:
            self.add_param(param=param)
        ######################################
        # Additional setttings
        for init_arg in self.init_arguments:
            self.add_init_arguments(init_arg)
        ######################################

        ######################################
        
        ######################################

        self.set_size()

    def add_init_arguments(self, arg='address', val=None):
        self.layout.addWidget(QLabel(arg), self.total_rows,0)
        val = str(self.init_arguments[arg]) if not val else ''
        init_arg_input_field = QLineEdit(str(self.init_arguments[arg]))
        self.layout.addWidget(init_arg_input_field, self.total_rows,1)
        self.total_rows += 1

        self.init_args_input_fields[arg] = init_arg_input_field
        self.init_args_values[arg] = self.init_arguments[arg]
        init_arg_input_field.editingFinished.connect(partial(self.set_init_args, arg))


    def add_param(self, param='Param1'):
        
        param_id = len(self.param_dropdowns)
        self.param_modes[param] = 'Constant'
        self.param_list.append(param)
        self.layout.addWidget(QLabel(param), self.total_rows,0)
        param_dropdown = QComboBox()
        param_dropdown.addItems(['Constant', 'Linear', 'Trace/retrace', 'Custom'])
        self.layout.addWidget(param_dropdown, self.total_rows,1)
        default_val = self.params[param]
        param_constant_field = QLineEdit(str(default_val))
        self.layout.addWidget(param_constant_field)
        param_dropdown.currentIndexChanged.connect(partial(self.switch_param_input, param_id=param_id))
        self.param_dropdowns.append(param_dropdown)

        param_constant_field.editingFinished.connect(partial(self.set_params_constant, param))
        self.param_input_fields[param] = [param_constant_field]
        self.param_values[param] = default_val
        
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
        
        if index == 0:
            self.param_modes[param] = 'Constant'
            param_constant_field = QLineEdit(defult_val)
            self.layout.addWidget(param_constant_field, param_id + 1, 2)
            self.param_input_fields[param] = [param_constant_field]
            self.set_params_constant(param)
            param_constant_field.editingFinished.connect(partial(self.set_params_constant, param))

        elif index == 1:
            self.param_modes[param] = 'Linear'
            param_start_field = QLineEdit(defult_val)
            param_end_field = QLineEdit(defult_val)
            self.layout.addWidget(QLabel('Start'), param_id + 1, 2)
            self.layout.addWidget(param_start_field, param_id + 1, 3)
            self.layout.addWidget(QLabel('End'), param_id + 1, 4)
            self.layout.addWidget(param_end_field, param_id + 1, 5)

            self.param_input_fields[param] = [param_start_field, param_end_field]
            self.set_params_linear(param)
            param_start_field.editingFinished.connect(partial(self.set_params_linear, param))
            param_end_field.editingFinished.connect(partial(self.set_params_linear, param))


        elif index == 2:
            self.param_modes[param] = 'Trace/retrace'
            param_trace_field = QLineEdit(defult_val)
            param_retrace_field = QLineEdit(defult_val)
            self.layout.addWidget(QLabel('Trace'), param_id + 1, 2)
            self.layout.addWidget(param_trace_field, param_id + 1, 3)
            self.layout.addWidget(QLabel('Retrace'), param_id + 1, 4)
            self.layout.addWidget(param_retrace_field, param_id + 1, 5)

            self.param_input_fields[param] = [param_trace_field, param_retrace_field]
            self.set_params_trace_retrace(param)
            param_trace_field.editingFinished.connect(partial(self.set_params_trace_retrace, param))
            param_retrace_field.editingFinished.connect(partial(self.set_params_trace_retrace, param))

        elif index == 3:
            self.param_modes[param] = 'Custom'
            param_custom_field = QLineEdit('[0,0,0]')
            self.layout.addWidget(param_custom_field, param_id + 1, 2,1,2)

            self.param_input_fields[param] = [param_custom_field]
            self.set_params_custom(param)
            param_custom_field.editingFinished.connect(partial(self.set_params_custom, param))
        else:
            raise RuntimeError

        
    def set_size(self):
        self.setFixedHeight((self.total_rows + 1) * 2 * self.char_height)
     
    def set_init_args(self, key):
        val = self.init_args_input_fields[key].text()
        self.init_args_values[key] = val
        print(key + ' set to ' + val)

    def set_params_constant(self, key):
        val = float(self.param_input_fields[key][0].text())
        # self.param_values[key] = np.ones(int(self.scan_system.scan_parameters['y_pixels'])) * val
        self.param_values[key] = val
        print(self.param_values[key])

    def set_params_linear(self, key):
        start_val = float(self.param_input_fields[key][0].text())
        end_val = float(self.param_input_fields[key][1].text())
        self.param_values[key] = [start_val, end_val]
        # self.param_values[key] = np.linspace(
        #     start=start_val, stop=end_val,
        #     num=int(self.scan_system.scan_parameters['y_pixels']))
    
        print(self.param_values[key])
    def set_params_trace_retrace(self, key):
        trace_val = float(self.param_input_fields[key][0].text())
        retrace_val = float(self.param_input_fields[key][1].text())
        self.param_values[key] = [trace_val, retrace_val]
        print(key + ' retrace_setting_pass ' + str(trace_val) + ' and ' + str(retrace_val))

    def set_params_custom(self, key):
        val = self.param_input_fields[key][0].text()
        self.param_values[key] = ast.literal_eval(val)
        print(self.param_values[key])
        
        

class ControlPanel(QMainWindow):
    def __init__(self, app, instrument_area_height_ratio=0.4):
        super().__init__()
        self.app = app
        ######################################
        # Define scan and position parameters to be used
        self.scan_parameters = {}
        self.scan_parameters_input_fields = {}
        self.scan_parameters['custom_font_size'] = None
        self.scan_parameters['custom_window_width'] = None
        self.scan_parameters['scan_id'] = 'LSM_scan'
        self.scan_parameters['x_center'] = 50
        self.scan_parameters['y_center'] = 50
        self.scan_parameters['z_center'] = 25
        self.scan_parameters['x_size'] = 0
        self.scan_parameters['y_size'] = 0
        self.scan_parameters['x_pixels'] = 50
        self.scan_parameters['y_pixels'] = 50
        self.scan_parameters['angle'] = 0
        self.scan_parameters['point_time_constant'] = 0.1
        self.scan_parameters['retrace_point_time_constant'] = self.scan_parameters['point_time_constant']
        self.scan_parameters['auto_close_after_finish'] = 10

        self.default_save_folder_path = os.path.dirname(os.path.abspath(__file__))
        self.save_destination = self.default_save_folder_path
        ######################################


        self.setWindowTitle("Setup a LSM Scan © Yue Zhang, vdZ Lab")
        self.setStyleSheet("QMainWindow { background-color: black; }")
        screen = QApplication.primaryScreen()
        screen_height = screen.geometry().height()
        self.screen_height = screen_height
        self.instrument_area_height_ratio = instrument_area_height_ratio
        # Set the widget's height to match the screen height
        # self.setFixedHeight(0.80 * screen_height)

        # scroll_area = QScrollArea(self)
        # scroll_area.setWidgetResizable(True)
        
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        # Main layout
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.params_layout = QGridLayout()

        self.params_layout.addWidget(QLabel('Step 1: Setting up scan parameters'), 0, 0, 1,3)

        self.params_layout.addWidget(QLabel('Scan ID'), 1, 0)
        self.scan_id_field = QLineEdit(self.scan_parameters['scan_id'])
        self.scan_parameters_input_fields['scan_id'] = self.scan_id_field
        
        self.params_layout.addWidget(self.scan_id_field, 1, 1)
        self.scan_id_field.editingFinished.connect(partial(
            self.set_scan_parameters, 'scan_id'))
        

        self.change_appearance_button = QPushButton('Change Appearance and save destination')
        self.change_appearance_button.clicked.connect(self.open_appearance_dialog)
        self.params_layout.addWidget(self.change_appearance_button, 0, 2,1,2)

        self.save_settings_button = QPushButton('Save settings')
        self.load_settings_button = QPushButton('Load settings')
        self.params_layout.addWidget(self.save_settings_button, 1, 2)
        self.params_layout.addWidget(self.load_settings_button, 1, 3)
        self.save_settings_button.clicked.connect(self.save_settings)
        self.load_settings_button.clicked.connect(self.load_settings)

        self.params_layout.addWidget(QLabel('XYZ Center (um)'), 2, 0)
        self.x_center_field = QLineEdit(str(self.scan_parameters['x_center']))
        self.y_center_field = QLineEdit(str(self.scan_parameters['y_center']))
        self.z_center_field = QLineEdit(str(self.scan_parameters['z_center']))
        self.params_layout.addWidget(self.x_center_field, 2, 1)
        self.params_layout.addWidget(self.y_center_field, 2, 2)
        self.params_layout.addWidget(self.z_center_field, 2, 3)
        self.scan_parameters_input_fields['x_center'] = self.x_center_field
        self.scan_parameters_input_fields['y_center'] = self.y_center_field
        self.scan_parameters_input_fields['z_center'] = self.z_center_field
        self.x_center_field.editingFinished.connect(partial(
            self.set_scan_parameters, 'x_center'))
        self.y_center_field.editingFinished.connect(partial(
            self.set_scan_parameters, 'y_center'))
        self.z_center_field.editingFinished.connect(partial(
            self.set_scan_parameters, 'z_center'))

        self.params_layout.addWidget(QLabel('XY Size (um)'), 3, 0)
        self.x_size_field = QLineEdit(str(self.scan_parameters['x_size'] ))
        self.y_size_field = QLineEdit(str(self.scan_parameters['y_size'] ))
        self.params_layout.addWidget(self.x_size_field, 3, 1)
        self.params_layout.addWidget(self.y_size_field, 3, 2)
        self.scan_parameters_input_fields['x_size'] = self.x_size_field
        self.scan_parameters_input_fields['y_size'] = self.y_size_field

        self.x_size_field.editingFinished.connect(partial(
            self.set_scan_parameters, 'x_size'))
        self.y_size_field.editingFinished.connect(partial(
            self.set_scan_parameters, 'y_size'))

        self.params_layout.addWidget(QLabel('XY Pixels'), 4, 0)
        self.x_pixel_field = QLineEdit(str(self.scan_parameters['x_pixels']))
        self.y_pixel_field = QLineEdit(str(self.scan_parameters['y_pixels']))
        self.params_layout.addWidget(self.x_pixel_field, 4, 1)
        self.params_layout.addWidget(self.y_pixel_field, 4, 2)
        self.scan_parameters_input_fields['x_pixels'] = self.x_pixel_field
        self.scan_parameters_input_fields['y_pixels'] = self.y_pixel_field
        self.x_pixel_field.editingFinished.connect(partial(
            self.set_scan_parameters, 'x_pixels'))
        self.y_pixel_field.editingFinished.connect(partial(
            self.set_scan_parameters, 'y_pixels'))

        self.params_layout.addWidget(QLabel('Rotate angle (deg)'), 5, 0)
        self.rotate_angle_field = QLineEdit(str(self.scan_parameters['angle']))
        self.params_layout.addWidget(self.rotate_angle_field, 5, 1)
        self.scan_parameters_input_fields['angle'] = self.rotate_angle_field
        self.rotate_angle_field.editingFinished.connect(partial(
            self.set_scan_parameters, 'angle'))

        self.retrace_state = QCheckBox("Retrace time constant is different")
        self.retrace_state.stateChanged.connect(self.set_retrace_state)
        self.params_layout.addWidget(self.retrace_state, 6,0,1,4)
        self.params_layout.addWidget(QLabel('Trace'), 7, 1)
        self.retrace_label = QLabel('Retrace time same as trace time')
        self.params_layout.addWidget(self.retrace_label, 7, 2,1,2)

        self.params_layout.addWidget(QLabel('Time constants (s)'), 8, 0)
        self.trace_time_constant_field = QLineEdit(str(self.scan_parameters['point_time_constant'] ))
        self.retrace_time_constant_field = QLineEdit(str(self.scan_parameters['retrace_point_time_constant'] ))
        self.scan_parameters_input_fields['point_time_constant'] = self.trace_time_constant_field
        self.scan_parameters_input_fields['retrace_point_time_constant'] = self.retrace_time_constant_field

        self.trace_time_constant_field.editingFinished.connect(partial(
            self.set_scan_parameters, 'point_time_constant'))
        self.trace_time_constant_field.editingFinished.connect(self.synchronize_retrace_if_retrace_time_equal_to_trace)
        self.retrace_time_constant_field.editingFinished.connect(partial(
            self.set_scan_parameters, 'retrace_point_time_constant'))
            
        self.retrace_label.setVisible(False)
        self.retrace_time_constant_field.setVisible(False)
        self.params_layout.addWidget(self.trace_time_constant_field, 8, 1)
        self.params_layout.addWidget(self.retrace_time_constant_field, 8, 2)

        self.params_layout.addWidget(QLabel('Auto close time after finish'), 9, 0, 1,2)
        self.auto_close_time_constant_field = QLineEdit(str(self.scan_parameters['auto_close_after_finish']))
        self.scan_parameters_input_fields['auto_close_after_finish'] = self.auto_close_time_constant_field
        self.auto_close_time_constant_field.editingFinished.connect(partial(self.set_scan_parameters, 'auto_close_after_finish'))
        self.params_layout.addWidget(self.auto_close_time_constant_field, 9, 2)
        self.params_layout.addWidget(QLabel('Step 2: Setting up instruments'), 10, 0, 1,4)


        self.instr_dropdown = QComboBox()
        self.instr_names, self.instr_params, self.instr_init_arguments = read_instrument_setup()
        self.instr_dropdown.addItems(self.instr_names)
        self.params_layout.addWidget(self.instr_dropdown,11,0,1,2)
        self.add_instr_button = QPushButton('Add')
        self.remove_instr_button = QPushButton('Remove')
        self.remove_instr_button.setEnabled(False) 
        

        self.params_layout.addWidget(self.add_instr_button, 11,2)
        self.params_layout.addWidget(self.remove_instr_button, 11,3)

        self.instrument_display_area = QScrollArea()
        self.instrument_display_area.setFixedHeight(instrument_area_height_ratio * screen_height)
        self.instrument_display_area.setWidgetResizable(True)
        self.instrument_display_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.instrument_display_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)        
        self.instrument_content = QWidget()
        self.instrument_layout = QVBoxLayout()
        self.instrument_layout.setAlignment(Qt.AlignTop) 
        self.instrument_display_area.setWidget(self.instrument_content)
        self.instrument_content.setLayout(self.instrument_layout)
        self.params_layout.addWidget(self.instrument_display_area, 12,0,1,4)
        self.add_instr_button.clicked.connect(self.add_instr)
        self.remove_instr_button.clicked.connect(self.remove_instr)
        self.selected_instr = None

        self.main_layout.addLayout(self.params_layout)


        self.params_layout.addWidget(QLabel('Step 3: Start the scan'), 13, 0, 1,3)
        self.start_scan_button = QPushButton('Start scan')
        self.start_scan_button.clicked.connect(self.start_scan)
        self.params_layout.addWidget(self.start_scan_button, 13, 3)


    def synchronize_retrace_if_retrace_time_equal_to_trace(self):
        if self.retrace_state.checkState() == Qt.Unchecked:
            self.retrace_time_constant_field.setText(self.trace_time_constant_field.text())
            self.retrace_time_constant_field.editingFinished.emit()
        else:
            print('Retrace time will not change.')

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
    
    def add_instr(self, instr_type=None):
        instr_type = self.instr_dropdown.currentText() if not instr_type else instr_type
        instr_params = self.instr_params[instr_type]
        init_arguments = self.instr_init_arguments[instr_type]
        instr_area = Instrument_area(instr_type=instr_type,
                                     instr_params=instr_params,
                                     init_arguments=init_arguments,
                                     scan_system=self)
        instr_area.mouseReleaseEvent = lambda event, instr=instr_area: self.select_instr(instr)
        self.instrument_layout.addWidget(instr_area)

        return instr_area
        

    def remove_instr(self):
        if self.selected_instr:
            self.instrument_layout.removeWidget(self.selected_instr)
            self.selected_instr.deleteLater()
            self.selected_instr = None
            self.remove_instr_button.setEnabled(False)

    def select_instr(self, instr):
        if self.selected_instr == instr:
            if instr.is_selected:
                self.selected_instr.setStyleSheet("background-color: black;")
                self.selected_instr.is_selected = False
                self.remove_instr_button.setEnabled(False)
                return
        # Reset previous selection
        if self.selected_instr:
            self.selected_instr.setStyleSheet("background-color: black;")
            self.selected_instr.is_selected = False

        # Highlight the new selection
        self.selected_instr = instr
        self.selected_instr.setStyleSheet("background-color: darkgreen;")
        self.selected_instr.is_selected = True

        # Enable remove button
        self.remove_instr_button.setEnabled(True)

    ###################################################
    def set_scan_parameters(self, key):
        val = self.scan_parameters_input_fields[key].text()
        self.scan_parameters[key] = val
        print(key + ' set to ' + val)


    def save_settings(self, forced_custom_save_path=None):
        self.overall_settings = {}
        
        self.instruments_save_list = []
        for instr_index in range(self.instrument_layout.count()):
            instrument = self.instrument_layout.itemAt(instr_index).widget()
            instrument_save_dict = {}
            instrument_save_dict['type'] = instrument.instr_type
            instrument_save_dict['init_args_values'] = instrument.init_args_values
            instrument_save_dict['param_list'] = instrument.param_list
            instrument_save_dict['param_modes'] = instrument.param_modes
            instrument_save_dict['param_values'] = instrument.param_values
            self.instruments_save_list.append(instrument_save_dict)
        # print(self.instruments_save_list)

        self.overall_settings['scan_paramaters'] = self.scan_parameters
        self.overall_settings['instruments_paramaters'] = self.instruments_save_list

        if forced_custom_save_path:
            folder_path = forced_custom_save_path
        else:
            folder_path = QFileDialog.getExistingDirectory(self, "Select Directory to save",self.default_save_folder_path)
  

        saved_setting_path = folder_path + '/' + self.scan_parameters['scan_id'] + '.json'
        try:
            with open(saved_setting_path, 'w') as json_file:
                json.dump(self.overall_settings, json_file, indent=4)
        except Exception as exception:
            error_details = 'The scan configuration has not been saved. \n\nExecution details:\n\n' + f"{type(exception).__name__}: {str(exception)}\n{traceback.format_exc()}"
            self.show_info_message(error_details)


    def load_settings(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        imported_settings_path, _ = QFileDialog.getOpenFileName(self, "Select a LSM setting file", current_dir, "JSON Files (*.json)")
        try:
            with open(imported_settings_path, 'r', encoding='utf-8') as file:
                saved_settings = json.load(file)

            saved_scan_parameters = saved_settings['scan_paramaters']
            saved_instruments_parameters = saved_settings['instruments_paramaters']
        except Exception as exception:
            error_details = 'No setting file has been loaded. \n\nExecution details:\n\n' + f"{type(exception).__name__}: {str(exception)}\n{traceback.format_exc()}"
            self.show_info_message(error_details)
            # self.show_info_message('No setting file has been loaded.')
            return
        
        for instr_index in range(self.instrument_layout.count()):
            instrument = self.instrument_layout.itemAt(instr_index).widget()
            instrument.deleteLater()
        self.remove_instr_button.setEnabled(False)

        
        

        ###################################################
        ###################################################
        self.retrace_state.setChecked(True)
        self.retrace_state.stateChanged.emit(self.retrace_state.checkState())
        self.set_retrace_state(self.retrace_state.checkState())
        for key in ['scan_id', 'x_center', 'y_center', 'z_center', 'x_size', 'y_size',
                     'x_pixels', 'y_pixels', 'angle', 'point_time_constant',
                     'retrace_point_time_constant', 'auto_close_after_finish']:
            self.scan_parameters_input_fields[key].setText(
                str(saved_scan_parameters[key]))
            self.scan_parameters_input_fields[key].editingFinished.emit()
        
        custom_font_size = saved_scan_parameters['custom_font_size']
        custom_window_width = saved_scan_parameters['custom_window_width']

        self.set_system_apprearance_and_save_destination(custom_font_size, 
                                                         custom_window_width,
                                                         self.save_destination
                                                         )

        ###################################################
        ###################################################
        for instrument_dict in saved_instruments_parameters:
            instr_type = instrument_dict['type']
            instr = self.add_instr(instr_type=instr_type)
            init_args_values = instrument_dict['init_args_values']
            param_list = instrument_dict['param_list']
            param_modes = instrument_dict['param_modes']
            param_values = instrument_dict['param_values']


            for init_arg, init_arg_val in init_args_values.items():
                instr.init_args_input_fields[init_arg].setText(str(init_arg_val))
                instr.init_args_input_fields[init_arg].editingFinished.emit()

            for param_index, param in enumerate(param_list):
                param_mode = str(param_modes[param])
                param_val = str(param_values[param])

  
                instr.param_dropdowns[param_index].setCurrentText(param_mode)
                instr.param_dropdowns[param_index].currentIndexChanged.emit(
                    instr.param_dropdowns[param_index].currentIndex())
                
                if param_mode == 'Constant':
                    constant_field = instr.param_input_fields[param][0]
                    constant_field.setText(param_val)
                    constant_field.editingFinished.emit()
                elif param_mode =='Linear':
                    start_field = instr.param_input_fields[param][0]
                    end_field = instr.param_input_fields[param][1]
                    start_val, end_val = ast.literal_eval(param_val)
                    start_field.setText(str(start_val))
                    end_field.setText(str(end_val))
                    start_field.editingFinished.emit()
                    end_field.editingFinished.emit()
                elif param_mode =='Trace/retrace':
                    trace_field = instr.param_input_fields[param][0]
                    retrace_field = instr.param_input_fields[param][1]
                    trace_val, retrace_val = ast.literal_eval(param_val)
                    trace_field.setText(str(trace_val))
                    retrace_field.setText(str(retrace_val))
                    trace_field.editingFinished.emit()
                    retrace_field.editingFinished.emit()
                elif param_mode =='Custom':
                    custom_field = instr.param_input_fields[param][0]
                    custom_field.setText(param_val)
                    custom_field.editingFinished.emit()
                else:
                    raise RuntimeError
                   
       
    def open_appearance_dialog(self):
        dialog = AppearanceDialog(system=self)
        if dialog.exec():  # If OK is pressed
            customize_font_size, customize_window_width, save_destination = dialog.get_values()   
            self.set_system_apprearance_and_save_destination(customize_font_size, customize_window_width, save_destination)
            
    def set_system_apprearance_and_save_destination(self, 
                                                    customize_font_size, 
                                                    customize_window_width,
                                                    save_destination):
        self.save_destination = save_destination
        self.scan_parameters['custom_font_size'] = customize_font_size
        self.scan_parameters['custom_window_width'] = customize_window_width
        if customize_font_size:
            # app = QApplication.instance()
            current_font = self.app.font()
            current_font.setPixelSize(customize_font_size)
            self.app.setFont(current_font)
            self.setFont(current_font)
            enforce_font_size(self, customize_font_size)
        
    def show_info_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle("Information")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    def parse_scan_aprameters_input(self, input_str):
        try:
            # Attempt to evaluate as a number or list
            parsed_value = ast.literal_eval(input_str)

            # Ensure it's either a number, list of numbers, or list of strings
            if isinstance(parsed_value, (int, float)):
                return parsed_value
            elif isinstance(parsed_value, list) and all(isinstance(i, (int, float, str)) for i in parsed_value):
                return parsed_value
        except (ValueError, SyntaxError):
            # If evaluation fails, return as a string (case 1)
            pass

        return input_str  # Return as string if none of the other conditions apply
    
    def start_scan(self):
        from source.params.position_params import Position_parameters
        from source.params.scan_params import Scan_parameters
        from source.params.display_params import Display_parameters
        from source.plot_process import LSM_plot
        import source.inst_driver as inst_driver

        try:

            customize_window_width = self.scan_parameters['custom_window_width']
            customize_font_size = self.scan_parameters['custom_font_size']
            # customize_save_destination = self.save_destination if len(self.save_destination) > 0  else None
            customize_save_destination = self.save_destination + '/'

            print(f'\n\nSave destination: {customize_save_destination}\n\n\n')

            display_parameters = Display_parameters(
                scan_id=self.scan_parameters['scan_id'], 
                window_width=customize_window_width,
                font_size=customize_font_size,   
                save_destination=customize_save_destination
                )

            position_parameters = Position_parameters(
                                                    x_size=float(self.scan_parameters['x_center']),
                                                    y_size=float(self.scan_parameters['y_center']),
                                                    x_pixels=int(self.scan_parameters['x_pixels']),
                                                    y_pixels=int(self.scan_parameters['y_pixels']),
                                                    z_center=float(self.scan_parameters['z_center']),
                                                    angle=float(self.scan_parameters['angle']))
        
            scan_parameters = Scan_parameters(
                point_time_constant=float(self.scan_parameters['point_time_constant']),retrace_point_time_constant=float(self.scan_parameters['retrace_point_time_constant']),
                return_to_zero=False)
            
            print('\n\n')
            print(float(self.scan_parameters['point_time_constant']))
            print(float(self.scan_parameters['retrace_point_time_constant']))
            print('\n\n')
            
            instruments = []

            for instr_index in range(self.instrument_layout.count()):
                instrument = self.instrument_layout.itemAt(instr_index).widget()
                instr_prop = {}
                init_args_values = {}
                for key, value in instrument.init_args_values.items():
                    init_args_values[key] = self.parse_scan_aprameters_input(value)
                    # print(f'Parsing {value} as {type(init_args_values[key])}')
                    # if isinstance(init_args_values[key], list):
                    #     print(f'List: first element {init_args_values[key][0]} is type {type(init_args_values[key])}')
                

                for param in instrument.param_list:
                    param_mode = instrument.param_modes[param]
                    param_val = instrument.param_values[param]

                    print('\n\n')
                    print(param)
                    print(param_mode)
                    print(type(param_val))
                    print(param_val)
                    print('\n\n')

                    if param_mode == 'Constant':
                        instr_prop[param] = float(param_val)
                    elif param_mode == 'Linear':
                        instr_prop[param] = [float(param_val[0]), float(param_val[1])]
                    elif param_mode == 'Trace/retrace':
                        instr_prop[param] = [[float(param_val[0])], [float(param_val[1])]]
                    elif param_mode == 'Custom':
                        instr_prop[param] = param_val
                    else:
                        raise RuntimeError

        
                instrument = getattr(inst_driver, instrument.instr_type)(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    **init_args_values,
                    **instr_prop
                )
                instruments.append(instrument)

            self.save_settings(forced_custom_save_path=customize_save_destination + '/results/' + self.scan_parameters['scan_id'] + '/')
            self.start_scan_button.setEnabled(False) 
            scan = LSM_plot(position_parameters=position_parameters,
                scan_parameters=scan_parameters,
                display_parameters=display_parameters,
                instruments=instruments,
                auto_close_time_in_s=int(self.scan_parameters['auto_close_after_finish']),
                simulate=False,
                show_zero=True,
                app=self.app,
                gui_start_scan_button=self.start_scan_button)
            # self.start_scan_button.setEnabled(True) 
        except Exception as exception:
            error_details = 'Error(s) occured. The scan has not been started or successfully finished. Error details:\n\n' + f"{type(exception).__name__}: {str(exception)}\n{traceback.format_exc()}"
            self.show_info_message(error_details)
            print(error_details)
            self.start_scan_button.setEnabled(True) 

if platform.system() == "Darwin":
    gc.disable()
if not QApplication.instance():
    app = QApplication([])
else:
    app = QApplication.instance()

font_family = load_font('font/SourceCodePro-Medium.ttf')
if font_family:
    global_font = QFont(font_family)
    app.setFont(global_font)

control_panel = ControlPanel(app=app)
control_panel.show()
app.exec()