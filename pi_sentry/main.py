"""Pi Sentry - Motion-triggered camera capture."""

import signal
import sys
import time

from camera import Camera
from config import CAPTURE_COOLDOWN, MOCK_HARDWARE
from led import StatusLED
from motion import MotionSensor


def main():
    """Main entry point - motion detection loop."""
    print("Pi Sentry starting...")
    if MOCK_HARDWARE:
        print("[MOCK MODE] Hardware simulation enabled")

    led = StatusLED()
    camera = Camera()
    sensor = MotionSensor()

    # Graceful shutdown handler
    def shutdown(signum, frame):
        print("\nShutting down...")
        sensor.stop()
        sensor.cleanup()
        camera.stop()
        led.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        # Initialize hardware
        sensor.calibrate()
        sensor.start()
        camera.start()
        led.blink(count=2)  # Ready signal

        print("Monitoring for motion... (Ctrl+C to exit)")

        while True:
            if sensor.wait_for_motion(timeout=1.0):
                print("Motion detected!")

                # Capture and signal
                filepath = camera.capture()
                led.blink()

                print(f"Saved: {filepath}")

                # Cooldown to prevent overheating
                time.sleep(CAPTURE_COOLDOWN)
            # No motion - loop continues

    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        sensor.stop()
        sensor.cleanup()
        camera.stop()
        led.cleanup()


if __name__ == "__main__":
    main()
