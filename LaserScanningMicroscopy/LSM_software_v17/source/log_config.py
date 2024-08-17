import logging

def setup_logging(log_file_path):
    # Create a custom logger
    logger = logging.getLogger(__name__)
    
    # Set the overall log level
    logger.setLevel(logging.DEBUG)
    
    # Create handlers
    console_handler = logging.StreamHandler()  # Console output
    file_handler = logging.FileHandler(log_file_path + '/log.txt')  # File output# Set level for handlers
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    
    # Create formatters and add them to handlers
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger