#!/usr/bin/bash

set -xe

HERE=$(cd "$(dirname "$0")" && pwd)

# fill these variables before running this script
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWD=
DEVICE_ID=
LOCATION_NAME=
TEMPERATURE_GPIO_PORT=
TEMPERATURE_SENSOR_ID=
SERVER_HOST=
SERVER_PORT=

mkdir -p /etc/weatherstation
cat << EOF > /etc/weatherstation/weatherstation.conf
[database]
host = $DB_HOST
port = $DB_PORT
database = weather_station
username = $DB_USER
password = $DB_PASSWD

[device]
device_id = $DEVICE_ID

[location]
name = $LOCATION_NAME 

[temperature]
gpio_port = $TEMPERATURE_GPIO_PORT
sensor_id = $TEMPERATURE_SENSOR_ID
interval_seconds = 60

[recording]
timestamp_format = %Y-%m-%d %H:%M:%S
csv_columns = value,timestamp,location,device_id,sensor_id

[server]
host = $SERVER_HOST
port = $SERVER_PORT
bind_address = 0.0.0.0
encoding = utf-8

[client]
encoding = utf-8

[logging]
log_file = /var/log/weatherstation/log
level = info
EOF
chown -R pi: /etc/weatherstation

pip3 install Adafruit_Python_DHT

cp "$HERE"/weatherstation_temperature.service /etc/systemd/system/weatherstation_temperature.service

cd "$HERE"/..
pip3 install .

systemctl enable weatherstation_temperature.service
systemctl start weatherstation_temperature.service
