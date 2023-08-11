import logging
import os


def setup_logger():  # apply condition directory existing
    log_directory = 'core'  # Change this to your desired directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # os.path.join(log_directory, 'app.log')

    logger = logging.getLogger('my_app')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)s- %(message)s')

    file_handler = logging.FileHandler('core/app.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


app_logger = setup_logger()
