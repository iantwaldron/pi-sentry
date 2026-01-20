"""Camera capture logic using picamera2."""

import time
from pathlib import Path

from config import MOCK_HARDWARE, CAMERA_RESOLUTION, CAPTURES_DIR

if not MOCK_HARDWARE:
    # noinspection PyUnresolvedReferences
    from picamera2 import Picamera2


class Camera:
    """Wrapper for Pi Camera Module 2 using picamera2."""

    def __init__(self):
        self._camera = None
        if not MOCK_HARDWARE:
            self._camera = Picamera2()
            config = self._camera.create_still_configuration(
                main={"size": CAMERA_RESOLUTION}
            )
            self._camera.configure(config)

    def start(self):
        """Start the camera (required before capturing)."""
        if self._camera:
            self._camera.start()
            time.sleep(0.5)  # Allow camera to warm up

    def stop(self):
        """Stop the camera."""
        if self._camera:
            self._camera.stop()

    def capture(self, filename: str | None = None) -> Path:
        """
        Capture a single image.

        Args:
            filename: Optional filename. If not provided, uses timestamp.

        Returns:
            Path to the saved image.
        """
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"

        filepath = CAPTURES_DIR / filename

        if MOCK_HARDWARE:
            # Create a placeholder file for testing
            filepath.touch()
            print(f"[MOCK] Would capture image to {filepath}")
        else:
            self._camera.capture_file(str(filepath))
            print(f"Captured image to {filepath}")

        return filepath

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def capture_single_image(filename: str | None = None) -> Path:
    """
    Convenience function to capture a single image.

    Args:
        filename: Optional filename. If not provided, uses timestamp.

    Returns:
        Path to the saved image.
    """
    with Camera() as camera:
        return camera.capture(filename)


if __name__ == "__main__":
    # Quick test
    path = capture_single_image()
    print(f"Saved to: {path}")
