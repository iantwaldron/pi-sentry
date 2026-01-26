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
APP_DIR = PROJECT_ROOT.parent  # The pi-sentry repo root
CAPTURES_DIR = APP_DIR.parent / "captures"  # /home/pi/captures - same level as app

# Ensure captures directory exists
CAPTURES_DIR.mkdir(exist_ok=True)

# API settings
API_ENDPOINT = "https://sentry.nullpixels.com/capture"
API_KEY = ""  # Set your API key here
API_UPLOAD_ENABLED = True  # Set False to disable uploads
API_TIMEOUT = 30.0  # Request timeout in seconds
