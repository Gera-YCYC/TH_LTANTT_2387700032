import ipaddress


def filter_targets(ip_list, whitelist=None, blacklist=None):
    allowed = {str(ipaddress.ip_address(value)) for value in (whitelist or [])}
    denied = {str(ipaddress.ip_address(value)) for value in (blacklist or [])}
    filtered = []
    for value in ip_list:
        address = str(ipaddress.ip_address(value))
        if address not in denied and (not allowed or address in allowed):
            filtered.append(address)
    return filtered
