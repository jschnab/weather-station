import logging

from weather_station.utils.config import get_config


def get_logger():
    """
    Configure logging.
    :returns: logger object
    """
    level = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    config = get_config()["logging"]
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=level[config["level"]],
        filename=config["log_file"],
        filemode="a",
    )
    return logging.getLogger()
