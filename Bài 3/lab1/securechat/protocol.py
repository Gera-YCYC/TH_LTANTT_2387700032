import json
import struct

MAX_FRAME_SIZE = 1_048_576


def encode_frame(payload):
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    if len(body) > MAX_FRAME_SIZE:
        raise ValueError("Frame exceeds the maximum size")
    return struct.pack("!I", len(body)) + body


def send_frame(sock, payload):
    sock.sendall(encode_frame(payload))


def receive_exactly(sock, size):
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            if chunks:
                raise ConnectionError("Connection ended in the middle of a frame")
            return None
        chunks.extend(chunk)
    return bytes(chunks)


def receive_frame(sock):
    header = receive_exactly(sock, 4)
    if header is None:
        return None
    size = struct.unpack("!I", header)[0]
    if not 0 < size <= MAX_FRAME_SIZE:
        raise ValueError("Invalid frame size")
    body = receive_exactly(sock, size)
    if body is None:
        raise ConnectionError("Connection ended before the frame body")
    return json.loads(body.decode("utf-8"))
