"""API client for uploading captures to sentry server."""

import base64
import logging
from datetime import datetime
from pathlib import Path

import requests

from .config import API_ENDPOINT, API_KEY, API_TIMEOUT

logger = logging.getLogger(__name__)


class CaptureUploader:
    """Uploads captured images to the sentry API."""

    def __init__(
        self,
        endpoint: str = API_ENDPOINT,
        api_key: str = API_KEY,
        timeout: float = API_TIMEOUT,
    ):
        """
        Initialize the uploader.

        Args:
            endpoint: API endpoint URL.
            api_key: Authentication token.
            timeout: Request timeout in seconds.
        """
        self._endpoint = endpoint
        self._api_key = api_key
        self._timeout = timeout

    def upload(self, filepath: Path) -> bool:
        """
        Upload an image to the API.

        Args:
            filepath: Path to the JPEG image file.

        Returns:
            True if upload succeeded, False otherwise.
            Never raises exceptions - all errors are logged and return False.
        """
        try:
            # Read and encode image
            image_data = filepath.read_bytes()
            image_b64 = base64.b64encode(image_data).decode("utf-8")

            # Build payload
            payload = {
                "date": datetime.utcnow().isoformat() + "Z",
                "image": image_b64,
            }

            # Send request
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }

            response = requests.post(
                self._endpoint,
                json=payload,
                headers=headers,
                timeout=self._timeout,
            )

            if response.ok:
                logger.info("Uploaded: %s", filepath.name)
                return True
            else:
                logger.warning(
                    "Upload failed (%d): %s",
                    response.status_code,
                    response.text[:100],
                )
                return False

        except requests.Timeout:
            logger.warning("Upload timeout for %s", filepath.name)
            return False
        except requests.RequestException as e:
            logger.warning("Upload error for %s: %s", filepath.name, e)
            return False
        except Exception as e:
            logger.exception("Unexpected upload error: %s", e)
            return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m pi_sentry.api <image_path>")
        sys.exit(1)

    uploader = CaptureUploader()
    success = uploader.upload(Path(sys.argv[1]))
    print(f"Upload {'succeeded' if success else 'failed'}")
