#!/bin/bash
# install-service.sh
# Creates a systemd unit file that starts pi-sentry on powerup+

APP_NAME="pi-sentry"
APP_DESCRIPTION="Pi Sentry - Raspberry Pi surveillance and motion detection application"
APP_USER="pi"
APP_DIR="/home/$APP_USER/$APP_NAME"
APP_ENV="$APP_DIR/py/bin"

# Create the service file
cat > /tmp/${APP_NAME}.service <<EOF
[Unit]
Description=$APP_Description
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PYTHONUNBUFFERED=1
ExecStart=$APP_ENV/python3 -m pi_sentry/main
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

# Install and enable
sudo mv /tmp/${APP_NAME}.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ${APP_NAME}.service