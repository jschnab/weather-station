#!/usr/bin/bash

set -ex

# fill these two variables before running this script
# they define MariaDB database credentials
DB_USER=
DB_PASSWD=

# fill the HOME variable and the variables in the
# weatherstation.conf configuration file
HOME=
cd "$HOME"
cat << EOF > "$HOME"/.weatherstation.conf
[database]
host = localhost
port = 3306
database = weather_station
username = $DB_USER
password = $DB_PASSWD

[temperature]
gpio_port =
device_id =
sensor_id =

[recording]
timestamp_format = %Y-%m-%d %H:%M:%S
csv_columns = value,timestamp,location_id,device_id,sensor_id

[communication]
host =
port =
EOF

# install necessary libraries
apt update
apt install -y git apache2 php libapache2-mod-php mariadb-server php-mysql
pip3 install -y mysql-connector-python

# configure and start the dashboard web server
echo "export DB_USER=$DB_USER" >> /etc/apache2/envvars
echo "export DB_PASSWD=$DB_PASSWD" >> /etc/apache2/envvars
mv weather-station/install/apache-virtual-server.conf /etc/apache2/sites-available/000-default.conf
chown www-data: /etc/apache2/sites-available/000-default.conf
mkdir /var/www/html/weather-station
cp -R weather-station/web/* /var/www/html/weather-station/
chown -R  www-data: /var/www/html/weather-station/
curl "https://jpgraph.net/download/download.php?p=49" > jpgraph.tar.gz
tar -xzf jpgraph.tar.gz -C /usr/share/

# configure mysql
mysql < weather-station/database/create_tables.sql
mysql --execute "CREATE USER '$DB_USER' IDENTIFIED BY '$DB_PASSWD'"
mysql --execute "GRANT ALL PRIVILEGES on weather_station.* TO '$DB_USER'"

# start the weatherstation data server
cp weather-station/install/server_service/etc/systemd/system/weatherstation_server.service
systemctl enable weatherstation_server.service
systemctl start weatherstation.service
