import csv
import os
import sys

from datetime import datetime
from time import sleep

import Adafruit_DHT as dht

sys.path.insert(os.path.abspath(".."))

from server.client import send_data

CSV_COLUMNS = ("value", "timestamp", "location_id", "device_id", "sensor_id")
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
SENSOR_GPIO_PORT = 23
DEVICE_ID = 1
SENSOR_ID = 1
HOST = "localhost"
PORT = 65432


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
    while True:
        data = measure_temp_humid(SENSOR_GPIO_PORT, TIMESTAMP_FORMAT)
        for d in data:
            d.update({"device_id": DEVICE_ID, "sensor_id": SENSOR_ID})
            send_data(data=d, host=HOST, port=PORT)
            parameter = d.pop("parameter")
            write_csv(
                file_name=f"{parameter}.csv",
                data=d,
                column_names=CSV_COLUMNS,
            )
        sleep(60)


if __name__ == "__main__":
    main()
