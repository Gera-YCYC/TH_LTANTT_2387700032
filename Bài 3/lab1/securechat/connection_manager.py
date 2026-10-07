import threading


class ConnectionManager:
    def __init__(self):
        self.clients = {}
        self._send_locks = {}
        self.lock = threading.RLock()

    def add_client(self, client, username, room):
        with self.lock:
            self.clients[client] = {"username": username, "room": room}
            self._send_locks[client] = threading.Lock()

    def remove_client(self, client):
        with self.lock:
            self.clients.pop(client, None)
            self._send_locks.pop(client, None)

    def get_client(self, client):
        with self.lock:
            return self.clients.get(client)

    def room_clients(self, room, exclude=None):
        with self.lock:
            return [client for client, info in self.clients.items()
                    if info["room"] == room and client is not exclude]

    def send(self, client, payload):
        with self.lock:
            send_lock = self._send_locks.get(client)
        if send_lock is None:
            return False
        try:
            with send_lock:
                client.sendall(payload)
            return True
        except OSError:
            return False
