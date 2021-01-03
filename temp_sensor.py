import csv

from datetime import datetime
from time import sleep

import Adafruit_DHT as dht

COLUMNS = ["time", "temperature", "humidity"]


def main():
    while True:
        humi, temp = dht.read_retry(dht.DHT22, 23)
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        row = [
             timestamp,
             "{0:.2f}".format(temp),
             "{0:.2f}".format(humi),
        ]
        print(*row)
        with open("temperatures.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerow(row)
        sleep(60)


if __name__ == "__main__":
    main()
