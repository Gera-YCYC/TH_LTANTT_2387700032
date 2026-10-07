import pytest
from cryptography.exceptions import InvalidTag

from securechat.message_encryption import MessageEncryption
from securechat.protocol import receive_frame, send_frame


class MemorySocket:
    def __init__(self):
        self.data = bytearray()

    def sendall(self, data):
        self.data.extend(data)

    def recv(self, size):
        chunk = bytes(self.data[:size])
        del self.data[:size]
        return chunk


def test_message_encryption_round_trip_and_authentication():
    cipher = MessageEncryption(b"k" * 32)
    encrypted = cipher.encrypt("xin chao", b"general")
    assert cipher.decrypt(encrypted, b"general") == "xin chao"
    with pytest.raises(InvalidTag):
        cipher.decrypt(encrypted, b"other-room")


def test_frame_round_trip():
    sock = MemorySocket()
    send_frame(sock, {"type": "join", "room": "general"})
    assert receive_frame(sock) == {"type": "join", "room": "general"}
    assert receive_frame(sock) is None
