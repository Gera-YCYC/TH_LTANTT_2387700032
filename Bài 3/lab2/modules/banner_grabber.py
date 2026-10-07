import socket

from .audit_log import log_action
from .scope import validate_authorized_target


def grab_banner(target, port, timeout=1.0, *, authorized_target=None):
    """Read a small service greeting, sending only a bounded HTTP GET when useful."""
    target = validate_authorized_target(target, authorized_target)
    if not 1 <= int(port) <= 65535:
        raise ValueError("Port must be in the range 1-65535")
    try:
        with socket.create_connection((target, int(port)), timeout=timeout) as connection:
            connection.settimeout(timeout)
            if port in (80, 8000, 8080):
                connection.sendall(
                    f"GET / HTTP/1.0\r\nHost: {target}\r\nConnection: close\r\n\r\n".encode("ascii")
                )
            data = connection.recv(512)
        banner = data.decode("utf-8", errors="replace").strip()
        log_action(f"Banner read target={target} port={port} bytes={len(data)}")
        return banner or "No banner returned"
    except (OSError, TimeoutError) as error:
        log_action(f"Banner read failed target={target} port={port}: {error}")
        return f"No banner available ({type(error).__name__})"
