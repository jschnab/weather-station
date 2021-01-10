#!/usr/bin/env python3

import selectors
import socket
import traceback

import libserver

HOST = "localhost"
PORT = 65432


def accept_wrapper(sock, selector):
    conn, addr = sock.accept()
    print("Accepted connection from", addr)
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
    print("Listening on", (host, port))
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
                    print(
                        f"Error for {message.addr}:\n"
                        f"{traceback.format_exc()}"
                    )
                    message.close()
    sel.close()


def main():
    start_server(HOST, PORT)


if __name__ == "__main__":
    main()
