from weather_station.server import server
from weather_station.utils.cli import parse_cli


def main():
    args = parse_cli()

    if args.listen:
        server.listen()


if __name__ == "__main__":
    main()
