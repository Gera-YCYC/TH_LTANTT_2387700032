import subprocess

from .audit_log import log_action


def map_local_neighbors():
    """Read the OS neighbor cache; this does not probe other hosts."""
    try:
        completed = subprocess.run(
            ["arp", "-a"], capture_output=True, text=True, timeout=3, check=True
        )
        output = completed.stdout.strip() or "Neighbor cache is empty."
        log_action("Read local ARP/neighbor cache")
        return output
    except (OSError, subprocess.SubprocessError) as error:
        log_action(f"Neighbor cache read failed: {error}")
        return f"Could not read local neighbor cache: {error}"
