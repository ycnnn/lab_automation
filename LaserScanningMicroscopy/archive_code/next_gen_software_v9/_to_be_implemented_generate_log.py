import logging
import sys
import os
# import path

# Create a custom handler
class DualHandler(logging.Handler):
    def __init__(self, file_handler, console_handler):
        super().__init__()
        self.file_handler = file_handler
        self.console_handler = console_handler

    def emit(self, record):
        self.file_handler.emit(record)
        self.console_handler.emit(record)

# Set up the logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

directory_path = os.path.dirname(os.path.realpath(__file__)) + '/' + 'log.log'

# Create handlers for both the file and console
file_handler = logging.FileHandler(directory_path)
console_handler = logging.StreamHandler(sys.stdout)

# Set the level and format for handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setLevel(logging.DEBUG)
console_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the custom DualHandler to the logger
dual_handler = DualHandler(file_handler, console_handler)
logger.addHandler(dual_handler)

# Now use the logger instead of print
logger.debug('Debug message')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message')
logger.critical('Critical message')
