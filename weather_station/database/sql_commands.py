CREATE_TEMPERATURE_TEMPORARY = """
CREATE TEMPORARY TABLE temp_stage (
    value FLOAT,
    timestamp TIMESTAMP,
    location VARCHAR(100),
    device_id INTEGER,
    sensor_id INTEGER
);"""

INSERT_TEMPERATURE_TEMP = """
INSERT INTO temp_stage values (%s, %s, %s, %s, %s);"""

INSERT_TEMPERATURE_FACT = """
INSERT INTO temperature
SELECT s.value, s.timestamp, l.id, s.device_id, s.sensor_id
FROM temp_stage s
JOIN location l on s.location = l.name;"""

CREATE_HUMIDITY_TEMPORARY = """
CREATE TEMPORARY TABLE humid_stage (
    value FLOAT,
    timestamp TIMESTAMP,
    location VARCHAR(100),
    device_id INTEGER,
    sensor_id INTEGER
);"""

INSERT_HUMIDITY_TEMP = """
INSERT INTO humid_stage values (%s, %s, %s, %s, %s);"""

INSERT_HUMIDITY_FACT = """
INSERT INTO humidity
SELECT s.value, s.timestamp, l.id, s.device_id, s.sensor_id
FROM humid_stage s
JOIN location l on s.location = l.name;"""
