import ipaddress
from configparser import ConfigParser

from weather_station.settings import CONFIG_FILE


def validate_config(config: ConfigParser) -> None:
    ipaddress.ip_address(config["server"]["host"])
    ipaddress.ip_address(config["server"]["bind_address"])
    port = int(config["server"]["port"])
    if not 1024 <= port <= 65536:
        raise ValueError(
            f"Server port should be between 1001 and 65536, got: {port}"
        )


def get_config(config_file=CONFIG_FILE) -> ConfigParser:
    """
    Read the configuration file.

    :param str config_file: path to the configuration file
    :returns (dict): configuration
    """
    config = ConfigParser(interpolation=None)
    config.read(config_file)
    validate_config(config)
    return config
