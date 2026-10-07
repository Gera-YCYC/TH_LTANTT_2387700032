import asyncio
import socket

import pytest

from modules.filter_utils import filter_targets
from modules.banner_grabber import grab_banner
from modules.port_scanner import async_scan_ports
from modules.scope import parse_ports, validate_authorized_target


def test_target_requires_exact_authorization_and_private_range():
    assert validate_authorized_target("127.0.0.1", "127.0.0.1") == "127.0.0.1"
    with pytest.raises(ValueError):
        validate_authorized_target("127.0.0.1", "127.0.0.2")
    with pytest.raises(ValueError):
        validate_authorized_target("8.8.8.8", "8.8.8.8")
    with pytest.raises(ValueError):
        validate_authorized_target("localhost", "localhost")


def test_whitelist_blacklist_and_port_validation():
    assert filter_targets(
        ["192.168.1.2", "192.168.1.3"],
        whitelist=["192.168.1.2", "192.168.1.3"],
        blacklist=["192.168.1.3"],
    ) == ["192.168.1.2"]
    assert parse_ports("80,443,80") == [80, 443]
    with pytest.raises(ValueError):
        parse_ports("0")
    with pytest.raises(ValueError):
        parse_ports(",".join(str(port) for port in range(1, 34)))
    with pytest.raises(ValueError):
        grab_banner("127.0.0.1", 80)


def test_scanner_finds_an_explicitly_authorized_local_listener():
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    port = listener.getsockname()[1]
    try:
        results = asyncio.run(async_scan_ports(
            "127.0.0.1", [port], 1, authorized_target="127.0.0.1"
        ))
        assert results == [{"port": port, "state": "open", "protocol": "tcp"}]
    finally:
        listener.close()
