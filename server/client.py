#!/usr/bin/env python3

import selectors
import socket
import traceback

import libclient

HOST = "localhost"
PORT = 65432


def start_connection(selector, host, port, request):
    addr = (host, port)
    print(f"Starting connection to {addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(selector, sock, addr, request)
    selector.register(sock, events, data=message)


def send_data(data, host=HOST, port=PORT):
    request = {
        "type": "text/json",
        "encoding": "utf8",
        "content": data
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
                print(
                    f"Error for {message.addr}:\n"
                    f"{traceback.format_exc()}"
                )
                message.close()
    sel.close()


def main():
    data = {
        "parameter": "temperature",
        "value": 17.401,
        "timestamp": "2020-01-06 23:12:28",
        "location": "master bedroom",
        "device_id": 1,
        "sensor_id": 1,
    }
    send_data(data)


if __name__ == "__main__":
    main()
