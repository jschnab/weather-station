#!/usr/bin/env python3

import selectors
import socket
import traceback
from typing import Any

from weather_station.server import libclient
from weather_station.utils.config import get_config
from weather_station.utils.log import get_logger

logger = get_logger()


def start_connection(
    selector: selectors.DefaultSelector,
    host: str,
    port: int,
    request: dict[str, Any],
) -> None:
    addr = (host, port)
    logger.info(f"Starting connection to {addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(selector, sock, addr, request)
    selector.register(sock, events, data=message)


def send_data(data: dict[str, Any], host: str, port: int) -> None:
    request = {
        "type": "text/json",
        "encoding": get_config()["client"]["encoding"],
        "content": data,
    }
    sel = selectors.DefaultSelector()
    start_connection(sel, host, port, request)

    # loop as long as a socket is being monitored
    while sel.get_map():
        events = sel.select(timeout=1)
        for key, mask in events:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
                logger.error(
                    f"Error for {message.addr}:\n{traceback.format_exc()}"
                )
                message.close()
    sel.close()


def main() -> None:
    data = {
        "parameter": "temperature",
        "value": 17.401,
        "timestamp": "2020-01-06 23:12:28",
        "location": "master bedroom",
        "device_id": 1,
        "sensor_id": 1,
    }
    config = get_config()["server"]
    send_data(data, config["host"], int(config["port"]))


if __name__ == "__main__":
    main()
