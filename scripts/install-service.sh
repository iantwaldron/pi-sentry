#!/bin/bash
# install-service.sh
# Creates a systemd unit file that starts pi-sentry on powerup

set -e  # Exit on error

echo "=== Pi Sentry Service Setup ==="

# Check if running as root (needed for systemctl)
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo bash $0"
    exit 1
fi

APP_NAME="pi-sentry"
APP_DESCRIPTION="Pi Sentry - Raspberry Pi surveillance and motion detection application"
APP_USER="pi"
APP_DIR="/home/$APP_USER/$APP_NAME"
APP_ENV="$APP_DIR/py/bin"

echo "Creating service file..."
cat > /tmp/${APP_NAME}.service <<EOF
[Unit]
Description=$APP_DESCRIPTION
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PYTHONUNBUFFERED=1
ExecStart=$APP_ENV/python3 -m pi_sentry.service
Restart=always
RestartSec=5s
# hardening
ProtectSystem=strict
PrivateTmp=true
NoNewPrivileges=true
RestrictNamespaces=true
ReadWritePaths=/home/pi/captures # WARNING! Make sure this aligns with config.py

[Install]
WantedBy=multi-user.target

EOF

echo "Installing and enabling service..."
mv /tmp/${APP_NAME}.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ${APP_NAME}.service

echo ""
echo "=== Setup complete ==="