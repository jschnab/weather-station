#!/usr/bin/env python3

from weather_station.utils.cli import parse_cli


def main():
    args = parse_cli()

    if args.listen:
        from weather_station.server import server

        server.listen()

    if args.temperature:
        from weather_station.sensing import temperature_humidity

        temperature_humidity.record()


if __name__ == "__main__":
    main()
