#!/usr/bin/bash

set -xe

pip3 install -y Adafruit_Python_DHT

git clone https://github.com/jschnab/weather-station.git
cp weather-station/install/weatherstation_temperature.service /etc/systemd/system/weatherstation_temperature.service

systemctl enable weatherstation_temperature.service
systemctl start weatherstation_temperature.service
