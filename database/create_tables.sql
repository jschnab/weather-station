USE WEATHER_STATION;

CREATE TABLE IF NOT EXISTS location (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS device (
    id SERIAL PRIMARY KEY,
    model VARCHAR(100),
    manufacturer_id INTEGER,
    os VARCHAR(40),
    date_bought DATE
);

CREATE TABLE IF NOT EXISTS sensor (
    id SERIAL PRIMARY KEY,
    model VARCHAR(100),
    manufacturer_id INTEGER,
    date_bought DATE
);

CREATE TABLE IF NOT EXISTS manufacturer (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS temperature (
    value FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    location_id BIGINT UNSIGNED,
    device_id BIGINT UNSIGNED,
    sensor_id BIGINT UNSIGNED,
    PRIMARY KEY (timestamp, location_id, device_id),
    FOREIGN KEY (location_id) REFERENCES location(id),
    FOREIGN KEY (device_id) REFERENCES device(id),
    FOREIGN KEY (sensor_id) REFERENCES sensor(id)
);

CREATE TABLE IF NOT EXISTS humidity (
    value FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    location_id BIGINT UNSIGNED,
    device_id BIGINT UNSIGNED,
    sensor_id BIGINT UNSIGNED,
    PRIMARY KEY (timestamp, location_id, device_id),
    FOREIGN KEY (location_id) REFERENCES location(id),
    FOREIGN KEY (device_id) REFERENCES device(id),
    FOREIGN KEY (sensor_id) REFERENCES sensor(id)
);
