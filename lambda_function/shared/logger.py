import logging
import os


def setup_logger(name):
    """
    Set up a logger for the module
    :param name: The name of the module
    :return: The logger
    """
    # Set up logging
    logger = logging.getLogger(name)
    logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
