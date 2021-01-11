from configparser import ConfigParser

from weather_station.settings import CONFIG_FILE


def get_config(config_file=CONFIG_FILE):
    """
    Read the configuration file.

    :param str config_file: path to the configuration file
    :returns (dict): configuration
    """
    config = ConfigParser(interpolation=None)
    config.read(config_file)
    return config
