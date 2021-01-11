#!/usr/bin/bash

set -ex

HERE=$(cd "$(dirname "$0")" && pwd)

# fill these variables before running this script
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWD=
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

[server]
host = $SERVER_HOST
port = $SERVER_PORT
bind_address = 0.0.0.0
encoding = utf-8

[logging]
log_file = /var/log/weatherstation/log
level = info
EOF
chown -R pi: /etc/weatherstation

# install necessary libraries
apt update
apt install -y git apache2 php libapache2-mod-php mariadb-server php-mysql
pip3 install mysql-connector-python

# configure and start the dashboard web server
echo "export DB_USER=$DB_USER" >> /etc/apache2/envvars
echo "export DB_PASSWD=$DB_PASSWD" >> /etc/apache2/envvars
cp "$HERE"/apache-virtual-server.conf /etc/apache2/sites-available/000-default.conf
chown www-data: /etc/apache2/sites-available/000-default.conf
mkdir -p /var/www/html/weather_station
cp -R "$HERE"/../weather-station/web/* /var/www/html/weather_station/
chown -R  www-data: /var/www/html/weather_station/
curl "https://jpgraph.net/download/download.php?p=49" > jpgraph.tar.gz
tar -xzf jpgraph.tar.gz -C /usr/share/
rm jpgraph.tar.gz
systemctl restart apache2.service

# configure mysql
mysql < "$HERE"/../weather_station/database/create_tables.sql
mysql --execute "CREATE USER IF NOT EXISTS '$DB_USER' IDENTIFIED BY '$DB_PASSWD'"
mysql --execute "GRANT ALL PRIVILEGES on weather_station.* TO '$DB_USER'"
sed -i -E 's/^#(general_log.*)/\1/g' /etc/mysql/mariadb.conf.d/50-server.cnf
systemctl restart mariadb.service

# start the weatherstation data server
cp "$HERE"/weatherstation_server.service /etc/systemd/system/weatherstation_server.service
mkdir -p /var/log/weatherstation
chown -R pi: /var/log/weatherstation
systemctl enable weatherstation_server.service
systemctl start weatherstation_server.service
