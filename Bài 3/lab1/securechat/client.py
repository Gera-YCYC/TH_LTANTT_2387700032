import base64
import hashlib
import os
import socket
import ssl
import threading
from pathlib import Path

from cryptography.exceptions import InvalidTag

from .message_encryption import MessageEncryption
from .protocol import receive_frame, send_frame

BASE_DIR = Path(__file__).resolve().parent
CERT_DIR = BASE_DIR.parent / "certs"
SERVER_HOST = os.getenv("SECURECHAT_HOST", "localhost")
SERVER_PORT = int(os.getenv("SECURECHAT_PORT", "8443"))


def receive_messages(tls_socket, encryption, room_name, stop_event):
    try:
        while not stop_event.is_set():
            packet = receive_frame(tls_socket)
            if packet is None:
                break
            if packet.get("type") == "message":
                encrypted = base64.b64decode(packet["ciphertext"], validate=True)
                message = encryption.decrypt(encrypted, room_name.encode("utf-8"))
                print(f"\n[{packet['username']}] {message}")
    except (OSError, ValueError, KeyError, ConnectionError, InvalidTag) as error:
        if not stop_event.is_set():
            print(f"\n[!] Receive error: {error}")
    finally:
        stop_event.set()


def main():
    username = input("Username: ").strip()
    room_name = input("Room [general]: ").strip() or "general"
    secret = os.getenv("SECURECHAT_E2E_SECRET")
    if not secret:
        raise SystemExit("Set SECURECHAT_E2E_SECRET to the same strong, out-of-band shared secret on every client.")
    key = hashlib.sha256(secret.encode("utf-8")).digest()
    encryption = MessageEncryption(key)

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=CERT_DIR / "ca" / "ca.crt")
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(CERT_DIR / "client" / "client.crt", CERT_DIR / "client" / "client.key")
    context.check_hostname = True

    stop_event = threading.Event()
    with socket.create_connection((SERVER_HOST, SERVER_PORT), timeout=10) as raw_socket:
        with context.wrap_socket(raw_socket, server_hostname=SERVER_HOST) as tls_socket:
            send_frame(tls_socket, {"type": "join", "username": username, "room": room_name})
            response = receive_frame(tls_socket)
            if not response or response.get("type") != "joined":
                raise SystemExit(f"Server rejected the join request: {response}")
            print(f"Joined #{room_name}; type /exit to leave.")
            receiver = threading.Thread(
                target=receive_messages,
                args=(tls_socket, encryption, room_name, stop_event),
                daemon=True,
            )
            receiver.start()
            try:
                while not stop_event.is_set():
                    message = input()
                    if message.strip().lower() == "/exit":
                        break
                    encrypted = encryption.encrypt(message, room_name.encode("utf-8"))
                    send_frame(tls_socket, {
                        "type": "message",
                        "ciphertext": base64.b64encode(encrypted).decode("ascii"),
                    })
            except (EOFError, OSError):
                pass
            finally:
                stop_event.set()
                try:
                    tls_socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass


if __name__ == "__main__":
    main()
