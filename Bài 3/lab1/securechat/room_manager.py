import threading


class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.lock = threading.RLock()

    def create_room(self, room_name):
        with self.lock:
            self.rooms.setdefault(room_name, set())

    def join_room(self, room_name, client):
        with self.lock:
            self.rooms.setdefault(room_name, set()).add(client)

    def leave_room(self, room_name, client):
        with self.lock:
            members = self.rooms.get(room_name)
            if members is not None:
                members.discard(client)
                if not members:
                    self.rooms.pop(room_name)

    def members(self, room_name):
        with self.lock:
            return tuple(self.rooms.get(room_name, ()))
