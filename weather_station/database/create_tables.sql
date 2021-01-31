CREATE DATABASE IF NOT EXISTS weather_station;
USE weather_station;

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

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS temperature_day
AS SELECT t.timestamp ts,
    t.value val,
    l.name loc
FROM temperature t JOIN location l
ON t.location_id = l.id
WHERE t.timestamp >= NOW() - INTERVAL 1 day;

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS temperature_3days
AS SELECT t.timestamp ts,
    t.value val,
    l.name loc
FROM temperature t JOIN location l
ON t.location_id = l.id
WHERE t.timestamp >= NOW() - INTERVAL 3 day;

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS temperature_week
AS SELECT t.timestamp ts,
    t.value val,
    l.name loc
FROM temperature t JOIN location l
ON t.location_id = l.id
WHERE t.timestamp >= NOW() - INTERVAL 7 day;

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS temperature_day_rolling_master_bedroom
AS SELECT *,
    AVG(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_avg,
    STD(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_std
FROM temperature_day
WHERE loc = 'master bedroom';

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS temperature_day_rolling_living_room
AS SELECT *,
    AVG(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_avg,
    STD(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_std
FROM temperature_day
WHERE loc = 'living room';

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS temperature_3days_rolling_master_bedroom
AS SELECT *,
    AVG(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_avg,
    STD(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_std
FROM temperature_3days
WHERE loc = 'master bedroom';

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS temperature_3days_rolling_living_room
AS SELECT *,
    AVG(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_avg,
    STD(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_std
FROM temperature_3days
WHERE loc = 'living room';

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS temperature_week_rolling_master_bedroom
AS SELECT *,
    AVG(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_avg,
    STD(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_std
FROM temperature_week
WHERE loc = 'master bedroom';

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS temperature_week_rolling_living_room
AS SELECT *,
    AVG(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_avg,
    STD(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_std
FROM temperature_week
WHERE loc = 'living room';

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS humidity_day
AS SELECT h.timestamp ts,
    h.value val,
    l.name loc
FROM humidity h JOIN location l
ON h.location_id = l.id
WHERE h.timestamp >= NOW() - INTERVAL 1 day;

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS humidity_3days
AS SELECT h.timestamp ts,
    h.value val,
    l.name loc
FROM humidity h JOIN location l
ON h.location_id = l.id
WHERE h.timestamp >= NOW() - INTERVAL 3 day;

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS humidity_week 
AS SELECT h.timestamp ts,
    h.value val,
    l.name loc
FROM humidity h JOIN location l
ON h.location_id = l.id
WHERE h.timestamp >= NOW() - INTERVAL 7 day;

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS humidity_day_rolling_master_bedroom
AS SELECT *,
    AVG(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_avg,
    STD(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_std
FROM humidity_day
WHERE loc = 'master bedroom';

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS humidity_day_rolling_living_room
AS SELECT *,
    AVG(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_avg,
    STD(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_std
FROM humidity_day
WHERE loc = 'living room';

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS humidity_3days_rolling_master_bedroom
AS SELECT *,
    AVG(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_avg,
    STD(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_std
FROM humidity_3days
WHERE loc = 'master bedroom';

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS humidity_3days_rolling_living_room
AS SELECT *,
    AVG(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_avg,
    STD(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_std
FROM humidity_3days
WHERE loc = 'living room';

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS humidity_week_rolling_master_bedroom
AS SELECT *,
    AVG(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_avg,
    STD(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_std
FROM humidity_week
WHERE loc = 'master bedroom';

CREATE SQL SECURITY INVOKER VIEW IF NOT EXISTS humidity_week_rolling_living_room
AS SELECT *,
    AVG(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_avg,
    STD(val) OVER(
	ORDER BY ts
	ROWS BETWEEN 10 PRECEDING AND CURRENT ROW
    ) AS roll_std
FROM humidity_week
WHERE loc = 'living room';
