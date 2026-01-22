"""Pi Sentry - Motion-triggered camera capture."""

import signal
import time

from camera import Camera
from config import CAPTURE_COOLDOWN, MOCK_HARDWARE
from led import StatusLED
from motion import MotionSensor


_shutdown_requested = False


def main():
    """Main entry point - motion detection loop."""
    global _shutdown_requested

    print("Pi Sentry starting...")
    if MOCK_HARDWARE:
        print("[MOCK MODE] Hardware simulation enabled")

    led = StatusLED()
    camera = Camera()
    sensor = MotionSensor()

    # Graceful shutdown handler - just sets flag, cleanup happens in finally
    # noinspection PyUnusedLocal
    def shutdown(signum, frame):
        global _shutdown_requested
        print("\nShutting down...")
        _shutdown_requested = True

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        # Initialize hardware
        sensor.calibrate()
        sensor.start()
        camera.start()
        led.blink(count=2)  # Ready signal

        print("Monitoring for motion... (Ctrl+C to exit)")

        while not _shutdown_requested:
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
