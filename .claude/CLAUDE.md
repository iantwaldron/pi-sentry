# Pi Sentry - Raspberry Pi License Plate Reader

## Project Overview

Motion-triggered license plate reader using a Raspberry Pi Zero W, Pi Camera Module 2, and PIR sensor.

## Hardware

- **Raspberry Pi Zero W** - Limited CPU/RAM, no hardware video encode, single-core ARM
- **Pi Camera Module 2** - 8MP Sony IMX219, use picamera2 library (not legacy picamera)
- **PIR Sensor** - Inland PIR motion sensor, 3.3V compatible, connected via GPIO

## Tech Stack

- **Python 3.11+** (match Pi OS Bookworm default)
- **picamera2** - Camera control (libcamera-based, replaces legacy picamera)
- See `requirements.txt` for Python dependencies

## Architecture

```
PIR Motion Detected → Capture Image → Preprocess → Detect Plate Region → OCR → Log Result
```

## Pi Zero Constraints

- **Memory**: Only 512MB RAM - avoid loading large models, process one frame at a time
- **CPU**: Single-core 1GHz - keep image resolution reasonable (1280x720 max recommended)
- **No GPU acceleration** - OpenCV operations are CPU-bound
- **Heat**: Sustained processing causes throttling - add cooldown between captures

## Project Structure

```
pi-sentry/
├── main.py           # Entry point, main loop
├── camera.py         # Camera capture logic using picamera2
├── motion.py         # PIR sensor handling
├── plate_detector.py # License plate detection/OCR
├── config.py         # GPIO pins, thresholds, paths
├── requirements.txt  # Python dependencies
└── captures/         # Saved images (gitignored)
```

## GPIO Pinout

- PIR OUT → GPIO 17 (pin 11) - configurable in config.py
- PIR VCC → 5V (pin 2)
- PIR GND → GND (pin 6)

## Development Notes

- Test camera with `libcamera-still -o test.jpg` before running Python code
- PIR needs 30-60 second calibration on power-up
- Use `--headless` OpenCV build to avoid X11 dependencies
- Log plates to CSV/SQLite for later review
- Consider systemd service for auto-start on boot

## Commands

```bash
# Install system dependencies (on Pi)
sudo apt update && sudo apt install -y python3-picamera2 python3-opencv tesseract-ocr

# Install Python packages
pip install -r requirements.txt

# Run
python main.py

# Test camera
libcamera-still -o test.jpg

# Check GPIO
pinout  # shows Pi pinout diagram
```

## Testing

- Development can happen on macOS/Linux with mocked hardware
- Use `MOCK_HARDWARE=1` environment variable to skip GPIO/camera initialization
- Test plate detection with sample images before deploying to Pi
