# Sentry API

## Quick Start

**Prerequisites:** Node.js

**Setup:**

1. `npm install`
2. Copy `.env.example` to `.env` and fill in your values

**Run:**

- `npm run dev` — starts the dev server with hot reload on port 3050

---

# Sentry API Endpoints

## Health Check

**GET** `/health`

Returns the server status. No authentication required.

**Response:**

```json
{ "status": "ok" }
```

---

## Submit Capture

**POST** `/capture`

Stores a captured image.

**Authentication:** Bearer token (`API_KEY`)

**Request Body:**

```json
{
  "date": "2024-01-15T10:30:00Z",
  "image": "<base64-encoded image>"
}
```

**Response (201):**

```json
{
  "success": true,
  "message": "Capture saved",
  "filename": "img_01152024103000.png",
  "date": "2024-01-15T10:30:00Z"
}
```

---

## List Captures (Admin)

**GET** `/admin/captures`

Returns all stored captures with base64 data URLs.

**Authentication:** Bearer token (`ADMIN_API_KEY`)

**Response:**

```json
{
  "captures": [
    {
      "filename": "img_01152024103000.png",
      "size": 12345,
      "createdAt": "2024-01-15T10:30:00.000Z",
      "url": "data:image/png;base64,..."
    }
  ],
  "count": 1
}
```

---

## Configuration

| Setting        | Default      | Description             |
| -------------- | ------------ | ----------------------- |
| Port           | 3050         | Server port             |
| Rate Limit     | 60/min       | Requests per minute     |
| Body Limit     | 10MB         | Max request body size   |
| `CAPTURES_DIR` | `./captures` | Image storage directory |
