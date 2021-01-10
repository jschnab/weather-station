import os

from configparser import ConfigParser
from pathlib import Path

HOME = str(Path.home())
CONFIG_FILE = os.path.join(HOME, ".weatherstation.conf")


def get_config(config_file=CONFIG_FILE):
    """
    Read the configuration file.

    :param str config_file: path to the configuration file
    :returns (dict): configuration
    """
    config = ConfigParser(interpolation=None)
    config.read(config_file)
    return config
