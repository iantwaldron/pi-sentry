"""PIR motion sensor handling."""

import logging
import time

from .config import MOCK_HARDWARE, PIR_PIN

logger = logging.getLogger(__name__)

if not MOCK_HARDWARE:
    # noinspection PyUnresolvedReferences
    # noinspection PyPackageRequirements
    import RPi.GPIO as GPIO


class MotionSensor:
    """Wrapper for PIR motion sensor via GPIO."""

    def __init__(self, pin: int = PIR_PIN, calibration_time: float = 30.0):
        """
        Initialize the PIR motion sensor.

        Args:
            pin: GPIO pin number (BCM mode).
            calibration_time: Time to wait for PIR sensor calibration.
        """
        self._pin = pin
        self._calibration_time = calibration_time

        if not MOCK_HARDWARE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def calibrate(self):
        """Wait for PIR sensor to calibrate on power-up."""
        logger.info("Calibrating PIR sensor (%.0fs)...", self._calibration_time)
        time.sleep(self._calibration_time)
        logger.info("PIR sensor ready")

    def motion_detected(self) -> bool:
        """
        Check if motion is currently detected.

        Returns:
            True if motion is detected, False otherwise.
        """
        if MOCK_HARDWARE:
            return False
        return GPIO.input(self._pin) == GPIO.HIGH

    def wait_for_motion(self, timeout: float | None = None) -> bool:
        """
        Block until motion is detected or timeout.

        Args:
            timeout: Maximum time to wait in seconds. None for infinite.

        Returns:
            True if motion was detected, False if timeout.
        """
        if MOCK_HARDWARE:
            logger.debug("Simulating motion detection")
            time.sleep(2.0)
            return True

        start = time.time()
        while True:
            if self.motion_detected():
                return True
            if timeout is not None and (time.time() - start) >= timeout:
                return False
            time.sleep(0.1)  # Polling interval

    def start(self):
        """Start monitoring for motion."""
        logger.debug("Motion sensor active on GPIO %d", self._pin)

    def stop(self):
        """Stop monitoring."""
        pass

    def cleanup(self):
        """Release GPIO resources."""
        if not MOCK_HARDWARE:
            GPIO.cleanup(self._pin)

    def __enter__(self):
        self.calibrate()
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.cleanup()


if __name__ == "__main__":
    # Quick test - wait for motion
    with MotionSensor(calibration_time=5.0) as sensor:
        print("Waiting for motion...")
        if sensor.wait_for_motion(timeout=30):
            print("Motion detected!")
        else:
            print("Timeout - no motion detected")
