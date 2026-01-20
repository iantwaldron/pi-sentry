"""Configuration settings for Pi Sentry."""

import os
from pathlib import Path

# Hardware mock mode - set MOCK_HARDWARE=1 to skip GPIO/camera on dev machines
MOCK_HARDWARE = os.environ.get("MOCK_HARDWARE", "0") == "1"

# GPIO pins
PIR_PIN = 17  # GPIO 17 (physical pin 11)

# Camera settings
CAMERA_RESOLUTION = (1280, 720)  # Keep reasonable for Pi Zero

# Paths
PROJECT_ROOT = Path(__file__).parent
CAPTURES_DIR = PROJECT_ROOT / "captures"

# Ensure captures directory exists
CAPTURES_DIR.mkdir(exist_ok=True)
