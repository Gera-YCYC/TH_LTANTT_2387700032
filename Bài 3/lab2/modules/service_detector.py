from .audit_log import log_action

COMMON_SERVICES = {
    21: "FTP (unencrypted control channel)",
    22: "SSH",
    23: "Telnet (unencrypted)",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS/TLS",
    3306: "MySQL",
    5432: "PostgreSQL",
    8080: "HTTP alternate",
}


def detect_services(scan_results):
    services = {
        item["port"]: COMMON_SERVICES.get(item["port"], "Unknown TCP service")
        for item in scan_results if item["state"] == "open"
    }
    log_action(f"Service labels generated for ports={list(services)}")
    return services
