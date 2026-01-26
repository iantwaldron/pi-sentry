#!/bin/bash
# dependencies.sh
# Installs system packages for pi-sentry

set -e  # Exit on error

echo "=== Pi Sentry Dependency Setup ==="

# Check if running as root (needed for apt)
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo bash $0"
    exit 1
fi

# System packages
echo "Installing system packages..."
apt update
apt install -y \
    python3-pip \
    python3-venv \
    git \
    python3-picamera2 \
    python3-rpi-lgpio

echo ""
echo "=== Setup complete ==="

