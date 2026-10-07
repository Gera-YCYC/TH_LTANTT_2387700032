import asyncio

from flask import Flask, render_template, request

from modules.banner_grabber import grab_banner
from modules.port_scanner import async_scan_ports
from modules.scope import parse_ports, validate_authorized_target
from modules.service_detector import detect_services
from modules.vuln_checker import check_exposures

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html", error=None, report=None)


@app.post("/scan")
def scan():
    target = request.form.get("target", "").strip()
    try:
        if request.form.get("authorized") != "yes":
            raise ValueError("Confirm that you own or have permission to test this target.")
        validate_authorized_target(target, target)
        ports = parse_ports(request.form.get("ports", "22,80,443"))
        results = asyncio.run(async_scan_ports(
            target, ports, rate_limit=3, authorized_target=target
        ))
        report = {
            "scan": results,
            "services": detect_services(results),
            "banners": {
                item["port"]: grab_banner(target, item["port"], authorized_target=target)
                for item in results if item["state"] == "open"
            },
            "exposures": check_exposures(results),
        }
        return render_template("index.html", error=None, report=report)
    except ValueError as error:
        return render_template("index.html", error=str(error), report=None), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
