from .audit_log import log_action

EXPOSURE_NOTES = {
    21: "FTP control traffic is commonly unencrypted; verify the service and use secure alternatives.",
    23: "Telnet is unencrypted; disable it or replace it with SSH where possible.",
}


def check_exposures(scan_results):
    notes = {
        item["port"]: EXPOSURE_NOTES[item["port"]]
        for item in scan_results
        if item["state"] == "open" and item["port"] in EXPOSURE_NOTES
    }
    log_action(f"Exposure notes generated for ports={list(notes)}")
    return notes
