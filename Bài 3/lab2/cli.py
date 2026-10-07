import asyncio
import json

import click

from modules.banner_grabber import grab_banner
from modules.filter_utils import filter_targets
from modules.network_mapper import map_local_neighbors
from modules.port_scanner import async_scan_ports
from modules.scope import parse_ports, validate_authorized_target
from modules.service_detector import detect_services
from modules.vuln_checker import check_exposures


def parse_ip_list(value):
    return [item.strip() for item in value.split(",") if item.strip()]


@click.command()
@click.option("--target", required=True, help="One private/loopback IP literal.")
@click.option("--authorized-target", required=True, help="Repeat the exact IP to confirm authorization.")
@click.option("--ports", default="22,80,443", show_default=True, help="Comma-separated TCP ports; max 32.")
@click.option("--concurrency", default=3, type=click.IntRange(1, 5), show_default=True)
@click.option("--mode", type=click.Choice(["scan", "service", "banner", "map", "vuln", "all"]), default="all")
@click.option("--whitelist", default="", help="Optional comma-separated exact IP allowlist.")
@click.option("--blacklist", default="", help="Optional comma-separated exact IP denylist.")
def cli(target, authorized_target, ports, concurrency, mode, whitelist, blacklist):
    """Inventory a single explicitly authorized private/loopback host."""
    try:
        whitelist_items = parse_ip_list(whitelist)
        blacklist_items = parse_ip_list(blacklist)
        validate_authorized_target(target, authorized_target, whitelist_items, blacklist_items)
        selected = filter_targets([target], whitelist_items, blacklist_items)
        if not selected:
            raise ValueError("Target rejected by whitelist/blacklist")
        port_list = parse_ports(ports)
        results = asyncio.run(async_scan_ports(
            target, port_list, concurrency, authorized_target=authorized_target,
            whitelist=whitelist_items, blacklist=blacklist_items,
        ))
    except ValueError as error:
        raise click.ClickException(str(error)) from error

    report = {"target": target, "tcp": results}
    if mode in ("service", "all"):
        report["services"] = detect_services(results)
    if mode in ("banner", "all"):
        report["banners"] = {
            item["port"]: grab_banner(target, item["port"], authorized_target=authorized_target)
            for item in results if item["state"] == "open"
        }
    if mode in ("map", "all"):
        report["local_neighbor_cache"] = map_local_neighbors()
    if mode in ("vuln", "all"):
        report["exposure_notes"] = check_exposures(results)
    click.echo(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    cli()
