import csv
import os
import sys

from pathlib import Path

from weather_station.database.db_utils import load_data
from weather_station.utils.log import get_logger

logger = get_logger()

HOME = str(Path.home())
CSV_PATH = os.path.join(HOME, "weather-station", "analysis")
CSV_COLUMNS = ("timestamp", "temperature", "humidity")


def load_csv(location, csv_path):
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            data = {
                "parameter": "temperature",
                "value": row["temperature"],
                "timestamp": row["timestamp"],
                "location": location,
                "device_id": 1,
                "sensor_id": 1,
            }
            load_data(data)


def main():
    location = sys.argv[1]
    if location == "living room":
        csv_path = os.path.join(CSV_PATH, "temp_livingroom.csv")
    elif location == "master bedroom":
        csv_path = os.path.join(CSV_PATH, "temp_master_bed.csv")
    else:
        logging.error(f"invalid location '{location}', exiting")
        return
    load_csv(location, csv_path)


if __name__ == "__main__":
    main()
