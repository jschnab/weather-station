import csv

from datetime import datetime
from time import sleep

import Adafruit_DHT as dht

from weather_station.server.client import send_data
from weather_station.utils.config import get_config
from weather_station.utils.log import get_logger

logger = get_logger()


def write_csv(file_name, data, column_names):
    """
    Write data to a CSV file.

    :param dict data: data to write to the CSV
    :param sequence column_names: name of the columns, provides
        the order of columns when writing to the CSV file
    """
    with open(file_name, "a") as f:
        writer = csv.DictWriter(f, fieldnames=column_names)
        writer.writerow(data)


def measure_temp_humid(sensor_gpio_port, timestamp_format):
    humid, temp = dht.read_retry(dht.DHT22, sensor_gpio_port)
    timestamp = datetime.now().strftime(timestamp_format)
    data = [
        {
            "parameter": "temperature",
            "value": temp,
            "timestamp": timestamp,
        },
        {
            "parameter": "humidity",
            "value": humid,
            "timestamp": timestamp,
        },
    ]
    return data


def record():
    config = get_config()
    location_name = config["location"]["name"]
    device_id = config["device"]["device_id"]
    sensor_id = config["temperature"]["sensor_id"]
    gpio_port = config["temperature"]["gpio_port"]
    interval_seconds = config["temperature"]["interval_seconds"]
    csv_columns = config["recording"]["csv_columns"].split(",")
    timestamp_format = config["recording"]["timestamp_format"]
    host = config["server"]["host"]
    port = config["server"]["port"]

    while True:
        data = measure_temp_humid(gpio_port, timestamp_format)
        for d in data:
            d.update(
                {
                    "device_id": device_id,
                    "sensor_id": sensor_id,
                    "location": location_name,
                }
            )
            send_data(data=d, host=host, port=port)
            parameter = d.pop("parameter")
            write_csv(
                file_name=f"{parameter}.csv",
                data=d,
                column_names=csv_columns,
            )
        sleep(interval_seconds)


if __name__ == "__main__":
    record()
