import argparse


def parse_cli():
    """
    Parse command-line interface arguments.

    :returns: CLI arguments
    """
    parser = argparse.ArgumentParser(
        "Command-line interface for weather station"
    )
    parser.add_argument(
        "-l",
        "--listen",
        action="store_true",
        help="start the server, listen for requests to store recordings",
    )
    args = parser.parse_args()
    return args
