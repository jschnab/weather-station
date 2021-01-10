import os
import sys

from configparser import ConfigParser
from pathlib import Path

import mysql.connector

sys.path.append(os.path.abspath(".."))

from database import sql_commands

HOME = str(Path.home())
CONFIG_FILE = os.path.join(HOME, ".weatherstation.conf")


def get_connection(autocommit=False, config_file=CONFIG_FILE):
    """
    Get a connection to a MySQL database.

    :param bool autocommit: if SQL commands should be automatically committed
        (optional, default False)
    :param str config_file: path to the config file containing database
        connection information (optional, default ~/.weatherstation.conf)
    :returns: connection object
    """
    config = ConfigParser()
    config.read(CONFIG_FILE)
    host = config["database"]["host"]
    port = int(config["database"]["port"])
    database = config["database"]["database"]
    username = config["database"]["username"]
    password = config["database"]["password"]
    conn = mysql.connector.connect(
        host=host,
        port=port,
        username=username,
        password=password,
        database=database,
    )
    conn.autocommit = autocommit
    return conn


def execute_sql(
    statement,
    parameters=None,
    conn=None,
    close_conn=True,
    commit=True,
):
    """
    Execute a SQL statement with parameters.

    :param str statement: SQL statement
    :param tuple parameters: parameters of the SQL statement (optional,
        default None)
    :param conn: a connection object (optional, default None)
    :param bool close_conn: whether to close the connection when query
        execution is done (optional, default True)
    :param bool commit: whether to commit changes after query execution
        (optional, default True)
    """
    if not conn:
        conn = get_connection(autocommit=True)
    cur = conn.cursor()
    try:
        cur.execute(statement, parameters)
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        if close_conn:
            conn.close()


def query_sql(
    statement,
    parameters=None,
    conn=None,
    close_conn=True,
):
    """
    Query the database.

    :param str statement: SQL statement
    :param tuple parameters: parameters of the SQL statement (optional)
    :param conn: a connection object (optional, default None)
    :param bool close_conn: whether to close the connection when query
        execution is done (optional, default True)
    :returns (tuple): query results
    """
    if not conn:
        conn = get_connection(autocommit=True)
    cur = conn.cursor()
    try:
        cur.execute(statement, parameters)
        return cur.fetchall()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        if close_conn:
            conn.close()


def load_data(data):
    """
    Load a sensor recording event in the database, formatted as a dictionary
    with the following keys: parameter, value, timestamp, location, device_id,
    sensor_id. Valid values for the key 'parameter' include 'temperature' and
    'humidity'.

    :param dict data: sensor recording event
    """
    param = data["parameter"]
    value = data["value"]
    timestamp = data["timestamp"]
    location = data["location"]
    device = data["device_id"]
    sensor = data["sensor_id"]

    if param == "temperature":
        conn = get_connection()
        execute_sql(
            sql_commands.CREATE_TEMPERATURE_TEMPORARY,
            conn=conn,
            close_conn=False,
            commit=False,
        )
        execute_sql(
            sql_commands.INSERT_TEMPERATURE_TEMP,
            (value, timestamp, location, device, sensor),
            conn=conn,
            close_conn=False,
            commit=False,
        )
        execute_sql(
            sql_commands.INSERT_TEMPERATURE_FACT,
            conn=conn,
        )

    elif param == "humidity":
        conn = get_connection()
        execute_sql(
            sql_commands.CREATE_HUMIDITY_TEMPORARY,
            conn=conn,
            close_conn=False,
            commit=False,
        )
        execute_sql(
            sql_commands.INSERT_HUMIDITY_TEMP,
            (value, timestamp, location, device, sensor),
            conn=conn,
            close_conn=False,
            commit=False,
        )
        execute_sql(
            sql_commands.INSERT_HUMIDITY_FACT,
            conn=conn,
        )

    else:
        # unsupported parameter
        pass
