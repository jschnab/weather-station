#!/usr/bin/bash

set -xe

HERE=$(cd "$(dirname "$0")" && pwd)

# fill these variables before running this script
DEVICE_ID=
LOCATION_NAME=
TEMPERATURE_GPIO_PORT=
TEMPERATURE_SENSOR_ID=
SERVER_HOST=
SERVER_PORT=
APP_USERNAME=

VENV_PATH=/home/${APP_USERNAME}/.weatherstation_venv
SERVICE_NAME=weatherstation_temperature.service

mkdir -p /etc/weatherstation
cat << EOF > /etc/weatherstation/weatherstation.conf
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
chown -R ${APP_USERNAME}: /etc/weatherstation

mkdir -p /var/log/weatherstation
chown -R ${APP_USERNAME}: /var/log/weatherstation

su - ${APP_USERNAME} << EOF
python3 -m venv ${VENV_PATH}
source ${VENV_PATH}/bin/activate
pip install -U pip setuptools wheel
pip install RPi.GPIO==0.7.*
cd ${HERE}/..
pip install .
EOF

cat << EOF > /etc/systemd/system/${SERVICE_NAME}
[Unit]
Description=weather station temperature and humidity recording
After=network.target

[Service]
User=${APP_USERNAME}
Group=${APP_USERNAME}
ExecStart=${VENV_PATH}/bin/weather-station -t
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl enable ${SERVICE_NAME}
systemctl start ${SERVICE_NAME}
