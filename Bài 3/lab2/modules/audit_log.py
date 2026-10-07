import logging
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parents[1] / "netrecon.log"
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def log_action(message):
    logging.info(message)
