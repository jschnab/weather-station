#!/usr/bin/bash

set -xe

pip3 install -y Adafruit_Python_DHT

git clone https://github.com/jschnab/weather-station.git
cp weather-station/install/temperature_service /etc/systemd/system/temperature.service

systemctl enable temperature.service
systemctl start temperature.service
