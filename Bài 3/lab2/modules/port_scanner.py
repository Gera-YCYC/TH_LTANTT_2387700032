import asyncio

from .audit_log import log_action
from .scope import validate_authorized_target

MAX_CONCURRENCY = 5
CONNECT_TIMEOUT = 0.6


async def scan_port(target, port, semaphore):
    async with semaphore:
        writer = None
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(target, port), timeout=CONNECT_TIMEOUT
            )
            return {"port": port, "state": "open", "protocol": "tcp"}
        except (OSError, asyncio.TimeoutError):
            return {"port": port, "state": "closed_or_filtered", "protocol": "tcp"}
        finally:
            if writer is not None:
                writer.close()
                try:
                    await writer.wait_closed()
                except OSError:
                    pass


async def async_scan_ports(target, ports, rate_limit=5, *, authorized_target=None,
                          whitelist=None, blacklist=None):
    target = validate_authorized_target(
        target, authorized_target, whitelist=whitelist, blacklist=blacklist
    )
    port_list = list(dict.fromkeys(int(port) for port in ports))
    if not port_list or len(port_list) > 32 or any(port < 1 or port > 65535 for port in port_list):
        raise ValueError("Scan 1-32 TCP ports, each in the range 1-65535")
    if not 1 <= rate_limit <= MAX_CONCURRENCY:
        raise ValueError(f"Concurrency must be between 1 and {MAX_CONCURRENCY}")

    log_action(f"TCP scan start target={target} ports={port_list} concurrency={rate_limit}")
    semaphore = asyncio.Semaphore(rate_limit)
    results = await asyncio.gather(*(scan_port(target, port, semaphore) for port in port_list))
    log_action(f"TCP scan complete target={target} open={[r['port'] for r in results if r['state'] == 'open']}")
    return results
