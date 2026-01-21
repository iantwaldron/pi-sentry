"""Configuration settings for Pi Sentry."""

import os
from pathlib import Path

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
