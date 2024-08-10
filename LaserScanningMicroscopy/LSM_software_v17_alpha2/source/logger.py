import logging


class Logger:
    def __init__(self, address):
                
        # Create a logger
        self.logger = logging.getLogger('my_logger')
        self.logger.setLevel(logging.INFO)

        # Create handlers
        console_handler = logging.StreamHandler()  # For printing to screen
        file_handler = logging.FileHandler(address)  

        # Set logging level for handlers (optional, inherit from logger by default)
        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)

        # Create a formatter and set it for both handlers
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger
    
    def info(self, message):
        self.logger.info('\n    ' + message)
    
if __name__ == '__main__':
    logger = Logger(address='/Users/ycn/Desktop/LSM_software_v17_alpha/')
