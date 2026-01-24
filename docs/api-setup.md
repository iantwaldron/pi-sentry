# API Upload Setup

Upload captured images to `sentry.nullpixels.com/capture` after each motion-triggered capture.

## Configuration

Set your API key in `pi_sentry/config.py`:

```python
API_KEY = "your-api-key-here"
```

### Available Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `API_ENDPOINT` | `https://sentry.nullpixels.com/capture` | API URL |
| `API_KEY` | `""` | Bearer token for authentication |
| `API_UPLOAD_ENABLED` | `True` | Set `False` to disable uploads |
| `API_TIMEOUT` | `30.0` | Request timeout in seconds |

## Installation

Install the required dependency:

```bash
pip install -r requirements.txt
```

## API Request Format

Each capture POSTs to the endpoint with:

```json
{
  "date": "2025-01-22T14:30:25.123456Z",
  "image": "base64-encoded-jpeg-data..."
}
```

Headers:
- `Authorization: Bearer <API_KEY>`
- `Content-Type: application/json`

## Testing

Test the upload directly with an image file:

```bash
python -m pi_sentry.api path/to/image.jpg
```

## Disabling Uploads

To disable uploads without removing your API key:

```python
API_UPLOAD_ENABLED = False
```
