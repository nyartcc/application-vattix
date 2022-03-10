import configparser


def read_config():
    config = configparser.ConfigParser()
    config.read('configuration.ini')
    return config
