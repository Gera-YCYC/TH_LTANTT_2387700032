import os
import socket
import ssl
import threading
from pathlib import Path

from .connection_manager import ConnectionManager
from .protocol import encode_frame, receive_frame, send_frame
from .room_manager import RoomManager

BASE_DIR = Path(__file__).resolve().parent
HOST = os.getenv("SECURECHAT_HOST", "127.0.0.1")
PORT = int(os.getenv("SECURECHAT_PORT", "8443"))
CERT_DIR = BASE_DIR.parent / "certs"
connections = ConnectionManager()
rooms = RoomManager()


def handle_client(tls_socket, address):
    room_name = None
    try:
        hello = receive_frame(tls_socket)
        if not isinstance(hello, dict) or hello.get("type") != "join":
            return
        username = str(hello.get("username", "")).strip()[:32]
        room_name = str(hello.get("room", "general")).strip()[:32]
        if not username or not room_name:
            send_frame(tls_socket, {"type": "error", "message": "Username and room are required"})
            return

        connections.add_client(tls_socket, username, room_name)
        rooms.create_room(room_name)
        rooms.join_room(room_name, tls_socket)
        print(f"[+] {username} joined {room_name} from {address}")
        send_frame(tls_socket, {"type": "joined", "room": room_name})

        while True:
            packet = receive_frame(tls_socket)
            if packet is None:
                break
            if not isinstance(packet, dict) or packet.get("type") != "message":
                continue
            ciphertext = packet.get("ciphertext")
            if not isinstance(ciphertext, str) or len(ciphertext) > 100_000:
                continue
            relay = {"type": "message", "username": username, "ciphertext": ciphertext}
            for peer in rooms.members(room_name):
                if peer is not tls_socket:
                    connections.send(peer, encode_frame(relay))
    except (OSError, ValueError, ConnectionError, ssl.SSLError) as error:
        print(f"[!] Connection {address} ended: {error}")
    finally:
        if room_name:
            rooms.leave_room(room_name, tls_socket)
        connections.remove_client(tls_socket)
        try:
            tls_socket.close()
        except OSError:
            pass
        print(f"[-] Disconnected: {address}")


def main():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(CERT_DIR / "server" / "server.crt", CERT_DIR / "server" / "server.key")
    context.load_verify_locations(CERT_DIR / "ca" / "ca.crt")
    context.verify_mode = ssl.CERT_REQUIRED

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((HOST, PORT))
        listener.listen(32)
        print(f"SecureChat listening on {HOST}:{PORT} (mutual TLS)")
        while True:
            raw_socket, address = listener.accept()
            try:
                tls_socket = context.wrap_socket(raw_socket, server_side=True)
            except ssl.SSLError as error:
                print(f"[!] TLS handshake rejected from {address}: {error}")
                raw_socket.close()
                continue
            threading.Thread(target=handle_client, args=(tls_socket, address), daemon=True).start()


if __name__ == "__main__":
    main()
