import csv
import os
import sys

from datetime import datetime
from time import sleep

import Adafruit_DHT as dht

sys.path.insert(os.path.abspath(".."))

from server.client import send_data
from utils.config import get_config


def write_csv(file_name, data, column_names):
    """
    Write data to a CSV file.

    :param dict data: data to write to the CSV
    :param sequence column_names: name of the columns, provides
        the order of columns when writing to the CSV file
    """
    with open(file_name, "a") as f:
        writer = csv.DictWriter(f)
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


def main():
    config = get_config()
    gpio_port = config["temperature"]["gpio_port"]
    timestamp_format = config["recording"]["timestamp_format"]
    device_id = config["temperature"]["device_id"]
    sensor_id = config["temperature"]["sensor_id"]
    csv_columns = config["recording"]["csv_columns"].split(",")
    host = config["communication"]["host"]
    port = config["communication"]["port"]

    while True:
        data = measure_temp_humid(gpio_port, timestamp_format)
        for d in data:
            d.update({"device_id": device_id, "sensor_id": sensor_id})
            send_data(data=d, host=host, port=port)
            parameter = d.pop("parameter")
            write_csv(
                file_name=f"{parameter}.csv",
                data=d,
                column_names=csv_columns,
            )
        sleep(60)


if __name__ == "__main__":
    main()
