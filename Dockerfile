FROM debian:bookworm-slim

WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .

RUN \
    # Install system dependencies \
    apt-get update && apt-get install -y --no-install-recommends \
    python3-venv && \
    rm -rf /var/lib/apt/lists/* && \
    # Create and activate venv \
    python3 -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install --no-cache-dir -r requirements.txt

ENV PATH="/py/bin:$PATH"

# Copy package
COPY pi_sentry/ pi_sentry/

# Enable mock hardware mode for containerized testing
ENV MOCK_HARDWARE=1
