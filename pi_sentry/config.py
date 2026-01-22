"""Configuration settings for Pi Sentry."""

import logging
import os
from pathlib import Path

# Logging configuration
LOG_LEVEL = logging.DEBUG if os.environ.get("DEBUG", "0") == "1" else logging.INFO
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

# Hardware mock mode - set MOCK_HARDWARE=1 to skip GPIO/camera on dev machines
MOCK_HARDWARE = os.environ.get("MOCK_HARDWARE", "0") == "1"

# GPIO pins
PIR_PIN = 17  # GPIO 17 (physical pin 11)
LED_PIN = 22  # GPIO 22 (physical pin 15) - status LED

# Camera settings
CAMERA_RESOLUTION = (1280, 720)  # Keep reasonable for Pi Zero
CAPTURE_COOLDOWN = 5.0  # Seconds between captures to prevent Pi Zero overheating

# Paths
PROJECT_ROOT = Path(__file__).parent
CAPTURES_DIR = PROJECT_ROOT / "captures"

# Ensure captures directory exists
CAPTURES_DIR.mkdir(exist_ok=True)
