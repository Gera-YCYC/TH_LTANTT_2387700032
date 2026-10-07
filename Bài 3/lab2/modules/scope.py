import ipaddress

ALLOWED_NETWORKS = tuple(ipaddress.ip_network(value) for value in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8",
    "fc00::/7", "::1/128",
))


def validate_authorized_target(target, authorized_target, whitelist=None, blacklist=None):
    try:
        address = ipaddress.ip_address(target)
    except ValueError as error:
        raise ValueError("Target must be a literal IP address; hostnames are not accepted") from error
    if not any(address.version == network.version and address in network for network in ALLOWED_NETWORKS):
        raise ValueError("Only private or loopback IP targets are allowed")
    if authorized_target != str(address):
        raise ValueError("Pass --authorized-target with the exact target IP to confirm authorization")
    if whitelist and str(address) not in {str(ipaddress.ip_address(item)) for item in whitelist}:
        raise ValueError("Target is not in the whitelist")
    if str(address) in {str(ipaddress.ip_address(item)) for item in (blacklist or [])}:
        raise ValueError("Target is in the blacklist")
    return str(address)


def parse_ports(value):
    try:
        ports = [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as error:
        raise ValueError("Ports must be comma-separated integers") from error
    if not ports or any(port < 1 or port > 65535 for port in ports):
        raise ValueError("Provide one or more TCP ports in the range 1-65535")
    if len(set(ports)) > 32:
        raise ValueError("At most 32 distinct ports may be scanned per request")
    return list(dict.fromkeys(ports))
