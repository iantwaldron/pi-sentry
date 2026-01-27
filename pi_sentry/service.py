"""Systemd service entrypoint for Pi Sentry."""

import logging
import os
import sys

from .config import LOG_FORMAT, LOG_DATE_FORMAT, LOG_LEVEL
from .led import StatusLED
from .main import main

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger(__name__)

PI_SENTRY_ENABLED = os.environ.get("PI_SENTRY_ENABLED", "1") == "1"


def start():
    """Service entrypoint - startup sequence then main loop."""
    if not PI_SENTRY_ENABLED:
        logger.info("Pi Sentry disabled via PI_SENTRY_ENABLED=0")
        sys.exit(0)

    logger.info("Pi Sentry starting")

    # Startup blink pattern - 5 quick blinks
    with StatusLED() as led:
        led.blink(duration=0.1, count=5, gap=0.1)

    main()


if __name__ == "__main__":
    start()
