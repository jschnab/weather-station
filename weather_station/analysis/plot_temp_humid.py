#!/usr/bin/env python3

import sys

from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
CSV_PATH = "temperatures_est.csv"
FIGSIZE = (12, 8)
EVERY_5_MINUTES = tuple(range(0, 60, 5))
EVERY_15_MINUTES = tuple(range(0, 60, 15))
EVERY_2_HOURS = tuple(range(0, 24, 2))
EVERY_6_HOURS = tuple(range(0, 24, 6))
EVERY_12_HOURS = tuple(range(0, 24, 12))
HUMIDITY_COLUMN = "humidity"
HUMIDITY_LEGEND = "humidity"
HUMIDITY_LABEL = "Relative humidity (%)"
TEMPERATURE_COLUMN = "temperature"
TEMPERATURE_LEGEND = "temperature"
TEMPERATURE_LABEL = "Temperature (deg. Farenheit)"
TIMESTAMP_COLUMN = "timestamp"
WINDOW = 60  # time window (minutes) to calculate medians


def mad(x, median):
    """
    Calculate the mean absolute deviation of a sequence.
    """
    return np.median(np.fabs(x - median))


def filter_outliers(df):
    """
    Remove rows where temperature or humidity deviates too much from
    their median value on a time window
    """
    temp_med = df[TEMPERATURE_COLUMN].median()
    df["temp_med"] = df[TEMPERATURE_COLUMN].rolling(WINDOW).median()
    df["temp_mad"] = df[TEMPERATURE_COLUMN].rolling(WINDOW).apply(
        mad,
        raw=True,
        kwargs={"median": temp_med},
    )

    humid_med = df[HUMIDITY_COLUMN].median()
    df["humid_med"] = df[HUMIDITY_COLUMN].rolling(WINDOW).median()
    df["humid_mad"] = df[HUMIDITY_COLUMN].rolling(WINDOW).apply(
        mad,
        raw=True,
        kwargs={"median": humid_med},
    )

    filtered = df[
        (df["temperature"] > df["temp_med"] - 5 * df["temp_mad"]) &
        (df["temperature"] < df["temp_med"] + 5 * df["temp_mad"]) &
        (df["humidity"] > df["humid_med"] - 10 * df["humid_mad"]) &
        (df["humidity"] < df["humid_med"] + 10 * df["humid_mad"])
    ]

    return filtered


def convert_celsius_farenheit(x):
    return x * 9 / 5 + 32


def plot_temp_humid(csv_path, timeframe="day"):
    df = pd.read_csv(
        csv_path,
        parse_dates=[TIMESTAMP_COLUMN],
        index_col=TIMESTAMP_COLUMN,
    )
    # if the data was in a timezone different that the local one,
    # you would have to convert the timezone and pass the timezone
    # below in the DateFormatter() object
    # df.index = df.index.tz_convert("US/Eastern")
    # tz = df.index.tz
    df.reset_index(inplace=True)

    df = filter_outliers(df)

    df[TEMPERATURE_COLUMN] = df[TEMPERATURE_COLUMN].apply(
        convert_celsius_farenheit
    )

    today = datetime.today()
    if timeframe == "hour":
        data = df[df[TIMESTAMP_COLUMN] > today - timedelta(hours=1)]
    elif timeframe == "day":
        data = df[df[TIMESTAMP_COLUMN] > today - timedelta(days=1)]
    elif timeframe == "3days":
        data = df[df[TIMESTAMP_COLUMN] > today - timedelta(days=3)]
    elif timeframe == "week":
        data = df[df[TIMESTAMP_COLUMN] > today - timedelta(days=7)]

    fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=FIGSIZE, sharex=True)
    ax1.plot(
        TIMESTAMP_COLUMN,
        TEMPERATURE_COLUMN,
        label=TEMPERATURE_LEGEND,
        data=data,
        color="C0",
    )
    ax1.set_ylabel(TEMPERATURE_LABEL, fontsize=16)

    ax2.plot(
        TIMESTAMP_COLUMN,
        HUMIDITY_COLUMN,
        label=HUMIDITY_LEGEND,
        data=data,
        color="C1",
    )
    ax2.set_ylabel(HUMIDITY_LABEL, fontsize=16)

    if timeframe == "hour":
        ax1.xaxis.set_major_locator(mdates.MinuteLocator(
            byminute=EVERY_15_MINUTES)
        )
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax1.xaxis.set_minor_locator(mdates.MinuteLocator(
            byminute=EVERY_5_MINUTES)
        )

    elif timeframe == "day":
        ax1.xaxis.set_major_locator(mdates.HourLocator(byhour=EVERY_2_HOURS))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
        # ax1.xaxis.set_major_formatter(
        #     mdates.DateFormatter("%m/%d %H:%M", tz=tz))
        ax1.xaxis.set_minor_locator(mdates.HourLocator())

    elif timeframe == "3days":
        ax1.xaxis.set_major_locator(mdates.HourLocator(byhour=EVERY_6_HOURS))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
        ax1.xaxis.set_minor_locator(mdates.HourLocator())

    elif timeframe == "week":
        ax1.xaxis.set_major_locator(mdates.HourLocator(byhour=EVERY_12_HOURS))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
        ax1.xaxis.set_minor_locator(mdates.HourLocator())

    fig.autofmt_xdate()
    ax1.grid(linestyle=":")
    ax2.grid(linestyle=":")
    ax1.legend()
    ax2.legend()
    fig.tight_layout()
    plt.show()


def main():
    if len(sys.argv) < 2:
        print("Usage: plot_temp_humid.py <csv path> [timeframe]")
        sys.exit()
    csv_path = sys.argv[1]
    if len(sys.argv) >= 3:
        timeframe = sys.argv[2]
    else:
        timeframe = "day"
    plot_temp_humid(csv_path, timeframe)


if __name__ == "__main__":
    main()
