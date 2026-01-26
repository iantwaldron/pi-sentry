#!/bin/bash
# setup.sh
# Installs dependencies, creates virtual environment, and installs requirements

set -e  # Exit on error

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/common.sh"

echo "=== Pi Sentry Environment Setup ==="

# Check if running as root (needed for apt)
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo bash $0"
    exit 1
fi

# Install system packages
echo "Installing system packages..."
apt update
apt install -y \
    python3-pip \
    python3-venv \
    python3-picamera2 \
    python3-rpi-lgpio

# Create venv with access to system site-packages (required for picamera2)
echo "Creating virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    sudo -u "$APP_USER" python3 -m venv --system-site-packages "$VENV_DIR"
else
    echo "Virtual environment already exists, skipping creation."
fi

# Install Python requirements
echo "Installing Python requirements..."
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

# Create captures directory
echo "Creating captures directory..."
sudo -u "$APP_USER" mkdir -p "$CAPTURES_DIR"

echo ""
echo "=== Setup complete ==="
