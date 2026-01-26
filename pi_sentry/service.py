"""Systemd service entrypoint for Pi Sentry."""

import logging

from config import LOG_FORMAT, LOG_DATE_FORMAT, LOG_LEVEL
from led import StatusLED
from main import main

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger(__name__)


def start():
    """Service entrypoint - startup sequence then main loop."""
    logger.info("Py Sentry starting")

    # Startup blink pattern - 5 quick blinks
    with StatusLED() as led:
        led.blink(duration=0.1, count=5, gap=0.1)

    main()


if __name__ == "__main__":
    start()
