import json
import selectors
import struct
import sys

from weather_station.database import db_utils
from weather_station.utils.config import get_config
from weather_station.utils.log import get_logger

logger = get_logger()

HDRLEN = 2  # length of the request header


class Message:
    def __init__(self, selector, sock, addr):
        self.encoding = get_config["server"]["encoding"]
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False

    def _set_selector_events_mask(self, mode):
        """
        Set selector to listen for events.
        Mode is 'r', 'w', or 'rw'.
        """
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            data = self.sock.recv(4096)
        except BlockingIOError:
            # resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            logger.info(f"sending {repr(self._send_buffer)} to {self.addr}")
            try:
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # close when buffer is drained (response has been sent)
                if sent and not self._send_buffer:
                    self.close()

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        return json.loads(json_bytes.decode(encoding))

    def _create_message(
        self,
        *,
        content_bytes,
        content_type,
        content_encoding,
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, self.encoding)
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _create_response_json_content(self):
        content = "200 Request was processed"
        content_encoding = self.encoding
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response

    def _create_response_binary_content(self):
        response = {
            "content_bytes": b"First 10 bytes of request: "
            + self.request[:10],
            "content_type": "binary/custom-server-binary-type",
            "content_encoding": "binary",
        }
        return response

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()
        self._write()

    def close(self):
        logger.info("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            logger.error(
                "Error: selector.unregister() exception for "
                f"{self.addr}: {repr(e)}"
            )

        try:
            self.sock.close()
        except OSError as e:
            logger.error(
                "Error: socket.close() exception for "
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # delete reference to socket object for garbage collection
            self.sock = None

    def process_protoheader(self):
        if len(self._recv_buffer) >= HDRLEN:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:HDRLEN]
            )[0]
            self._recv_buffer = self._recv_buffer[HDRLEN:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], self.encoding
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f"Missing required header '{reqhdr}'")

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return

        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]

        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            db_utils.load_data(self.request)
            logger.info(
                f"Received request {repr(self.request)} from {self.addr}")

        else:
            # binary or unknown content-type
            self.request = data
            logger.info(
                f"Received {self.jsonheader['content-type']} request from "
                f"{self.addr}"
            )

        # set selector to listen for write events, we're done writing
        self._set_selector_events_mask("w")

    def create_response(self):
        if self.jsonheader["content-type"] == "text/json":
            response = self._create_response_json_content()

        else:
            # binary or unknown content type
            response = self._create_response_binary_content()

        message = self._create_message(**response)
        self.response_created = True
        self._send_buffer += message
