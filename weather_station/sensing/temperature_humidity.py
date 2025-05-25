import csv
import os
import time
from typing import Any

from datetime import datetime


from weather_station.sensing.gpio import DHT22
from weather_station.server.client import send_data
from weather_station.settings import APP_DIR
from weather_station.utils.config import get_config
from weather_station.utils.log import get_logger

logger = get_logger()


def write_csv(
    file_name: str, data: dict[str, Any], column_names: list[str]
) -> None:
    """
    Write data to a CSV file.

    :param dict data: data to write to the CSV
    :param sequence column_names: name of the columns, provides
        the order of columns when writing to the CSV file
    """
    with open(file_name, "a") as f:
        writer = csv.DictWriter(f, fieldnames=column_names)
        writer.writerow(data)


def record() -> None:
    config = get_config()
    sensor = DHT22(int(config["temperature"]["gpio_port"]))

    metadata = {
        "device_id": config["device"]["device_id"],
        "sensor_id": config["temperature"]["sensor_id"],
        "location": config["location"]["name"],
    }

    while True:
        LOGGER.debug("Preparing to read sensor data")
        result = sensor.read_retry()
        LOGGER.debug("Finished reading sensor data")
        timestamp = datetime.now().strftime(
            config["recording"]["timestamp_format"]
        )
        if result.ok:
            data = [
                {
                    "parameter": "temperature",
                    "value": result.temperature,
                    "timestamp": timestamp,
                    **metadata,
                },
                {
                    "parameter": "humidity",
                    "value": result.humidity,
                    "timestamp": timestamp,
                    **metadata,
                },
            ]
            for da in data:
                send_data(
                    data=da,
                    host=config["server"]["host"],
                    port=int(config["server"]["port"]),
                )
                parameter = da.pop("parameter")
                write_csv(
                    file_name=os.path.join(APP_DIR, f"{parameter}.csv"),
                    data=da,
                    column_names=config["recording"]["csv_columns"].split(","),
                )
        else:
            logger.error(f"Sensor reading error: {result.error.name}")

        time.sleep(int(config["temperature"]["interval_seconds"]))


if __name__ == "__main__":
    record()
