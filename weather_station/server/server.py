#!/usr/bin/env python3

import selectors
import socket
import traceback

from weather_station.server import libserver
from weather_station.utils.config import get_config
from weather_station.utils.log import get_logger

logger = get_logger()


def accept_wrapper(sock, selector):
    conn, addr = sock.accept()
    logger.info(f"Accepted connection from {addr}")
    conn.setblocking(False)
    message = libserver.Message(selector, conn, addr)
    selector.register(conn, selectors.EVENT_READ, data=message)


def start_server(host, port):
    sel = selectors.DefaultSelector()
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((host, port))
    lsock.listen()
    logger.info(f"Listening on {host}:{port}")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj, sel)
            else:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    logger.error(
                        f"Error for {message.addr}:\n"
                        f"{traceback.format_exc()}"
                    )
                    message.close()
    sel.close()


def listen():
    config = get_config["server"]
    port = int(config["port"])
    start_server(config["bind_address"], port)


if __name__ == "__main__":
    listen()
