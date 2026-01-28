"""Status LED control."""

import logging
import time
import threading

from .config import MOCK_HARDWARE, LED_PIN

logger = logging.getLogger(__name__)

if not MOCK_HARDWARE:
    # noinspection PyUnresolvedReferences
    # noinspection PyPackageRequirements
    import RPi.GPIO as GPIO


class StatusLED:
    """Wrapper for status indicator LED via GPIO."""

    def __init__(self, pin: int = LED_PIN):
        """
        Initialize the status LED.

        Args:
            pin: GPIO pin number (BCM mode).
        """
        self._pin = pin
        self._lock = threading.Lock()

        if not MOCK_HARDWARE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._pin, GPIO.OUT)
            GPIO.output(self._pin, GPIO.LOW)

    def on(self):
        """Turn LED on."""
        with self._lock:
            if MOCK_HARDWARE:
                logger.debug("LED on")
            else:
                GPIO.output(self._pin, GPIO.HIGH)

    def off(self):
        """Turn LED off."""
        with self._lock:
            if MOCK_HARDWARE:
                logger.debug("LED off")
            else:
                GPIO.output(self._pin, GPIO.LOW)

    def blink(self, duration: float = 0.1, count: int = 1, gap: float = 0.1):
        """
        Blink the LED.

        Args:
            duration: How long LED stays on per blink (seconds).
            count: Number of blinks.
            gap: Time between blinks (seconds).
        """
        for i in range(count):
            self.on()
            time.sleep(duration)
            self.off()
            if i < count - 1:
                time.sleep(gap)

    def cleanup(self):
        """Release GPIO resources."""
        self.off()
        if not MOCK_HARDWARE:
            GPIO.cleanup(self._pin)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


if __name__ == "__main__":
    # Quick test - blink 3 times
    with StatusLED() as led:
        print("Blinking LED 3 times...")
        led.blink(duration=0.2, count=3)
        print("Done")
