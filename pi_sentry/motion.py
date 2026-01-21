"""PIR motion sensor handling."""

import time
from typing import Callable

from config import MOCK_HARDWARE, PIR_PIN

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
        self._callback = None
        self._running = False

        if not MOCK_HARDWARE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def calibrate(self):
        """Wait for PIR sensor to calibrate on power-up."""
        print(f"Calibrating PIR sensor ({self._calibration_time}s)...")
        time.sleep(self._calibration_time)
        print("PIR sensor ready")

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
            print("[MOCK] Simulating motion detection...")
            time.sleep(2.0)
            return True

        start = time.time()
        while True:
            if self.motion_detected():
                return True
            if timeout is not None and (time.time() - start) >= timeout:
                return False
            time.sleep(0.1)  # Polling interval

    def on_motion(self, callback: Callable[[], None]):
        """
        Register a callback for motion detection events.

        Args:
            callback: Function to call when motion is detected.
        """
        self._callback = callback

        if not MOCK_HARDWARE:
            GPIO.add_event_detect(
                self._pin,
                GPIO.RISING,
                callback=lambda _: self._callback(),
                bouncetime=300  # Debounce in ms
            )

    def start(self):
        """Start monitoring for motion."""
        self._running = True
        print(f"Motion sensor active on GPIO {self._pin}")

    def stop(self):
        """Stop monitoring and cleanup GPIO."""
        self._running = False
        if not MOCK_HARDWARE:
            GPIO.remove_event_detect(self._pin)

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
