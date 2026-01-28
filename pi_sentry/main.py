"""Pi Sentry - Motion-triggered camera capture."""

import logging
import signal
import time

from .api import CaptureUploader
from .camera import Camera
from .config import API_UPLOAD_ENABLED, CAPTURE_COOLDOWN, MOCK_HARDWARE
from .led import StatusLED
from .motion import MotionSensor

logger = logging.getLogger(__name__)

_shutdown_requested = False


def main():
    """Main entry point - motion detection loop."""
    global _shutdown_requested

    logger.info("Pi Sentry starting")
    if MOCK_HARDWARE:
        logger.warning("Mock hardware mode enabled")

    led = StatusLED()
    camera = Camera()
    sensor = MotionSensor()
    uploader = CaptureUploader() if API_UPLOAD_ENABLED else None

    # Graceful shutdown handler - just sets flag, cleanup happens in finally
    # noinspection PyUnusedLocal
    def shutdown(signum, frame):
        global _shutdown_requested
        logger.info("Shutdown requested")
        _shutdown_requested = True

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        # Initialize hardware
        sensor.calibrate()
        sensor.start()
        camera.start()
        led.blink(count=2)  # Ready signal

        logger.info("Monitoring for motion (Ctrl+C to exit)")

        while not _shutdown_requested:
            if sensor.wait_for_motion(timeout=1.0):
                logger.info("Motion detected")

                # Capture and signal
                filepath = camera.capture()
                led.blink()

                logger.info("Saved: %s", filepath)

                # Upload to API
                if uploader:
                    uploader.upload(filepath)

                # Cooldown to prevent overheating
                time.sleep(CAPTURE_COOLDOWN)
            # No motion - loop continues

    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise
    finally:
        sensor.stop()
        sensor.cleanup()
        camera.stop()
        led.cleanup()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    main()
