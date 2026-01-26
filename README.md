# Pi-Sentry
A motion-activated surveillance system.

## Installation

### Prerequisites
- Raspberry Pi with Pi OS (Trixie/Bookworm)
- Git installed: `sudo apt install git`

### Setup
```bash
# Clone the repository
cd ~
git clone <repo-url>
cd pi-sentry

# Install dependencies, create venv, and configure environment
sudo bash scripts/setup.sh

# Install and enable the systemd service
sudo bash scripts/install-service.sh

# Start the service
sudo systemctl start pi-sentry
```

### Updates
```bash
cd ~/pi-sentry
git pull
sudo systemctl restart pi-sentry
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/common.sh` | Shared variables (paths, user) sourced by other scripts |
| `scripts/setup.sh` | Installs system packages, creates venv, installs pip requirements, creates captures directory |
| `scripts/install-service.sh` | Creates and enables the systemd service |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PI_SENTRY_ENABLED` | `1` | Set to `0` to disable the service without using systemctl |
| `MOCK_HARDWARE` | `0` | Set to `1` to skip GPIO/camera initialization (for development) |
| `DEBUG` | `0` | Set to `1` to enable debug logging |

## Hardware
* Raspberry Pi Zero W
* PIR Motion Sensor
* LED

## Schematic
![Schematic](/docs/pi-sentry-schematic.png)

## Assembly

For the PIR, duponts were crimped on both ends of the leads to make it easier to mount/unmount in the enclosure.

The LED was soldered to the leads with the resistor (330 ohm) directly on the anode post and buried in heat shrink.
Duponts were used on the Pi side to make it easier to mount/unmount. 

On the Pi, pin headers were used rather than solder directly to the pads.

Leads are 22AWG.