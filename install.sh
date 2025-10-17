#!/bin/bash
# filepath: \8x8_desktopWeather\install.sh

# Automated installation script for 8x8 Desktop Weather Display
# Supports Raspberry Pi OS (PiOS) and DietPi
# Run with: bash install.sh

set -e  # Exit on error

# Detect OS
if grep -q "DietPi" /etc/os-release; then
    OS="DietPi"
    USER_DATA_DIR="/mnt/dietpi_userdata"
    USER="dietpi"
else
    OS="PiOS"
    USER_DATA_DIR="$HOME"
    USER="$USER"
fi

PROJECT_DIR="$(pwd)"
VENV_DIR="../pienv"

echo "Detected OS: $OS"
echo "Project directory: $PROJECT_DIR"
echo "Virtual environment: $VENV_DIR"

# Step 1: Update system
echo "Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

# Step 2: Install system dependencies
echo "Installing system dependencies..."
# Fix invalid package name libtiff5 -> libtiff-dev
sed -i 's/libtiff5/libtiff-dev/g' requirements_system.txt
cat requirements_system.txt | grep -v '^#' | grep -v '^$' | xargs sudo apt-get install -y

# Step 3: Enable SPI (automated via config file)
echo "Enabling SPI..."
if [ -f /boot/config.txt ]; then
    sudo sed -i 's/^#dtparam=spi=on/dtparam=spi=on/' /boot/config.txt
    if ! grep -q "dtparam=spi=on" /boot/config.txt; then
        echo "dtparam=spi=on" | sudo tee -a /boot/config.txt > /dev/null
    fi
else
    echo "Warning: /boot/config.txt not found. Please enable SPI manually."
fi

# Step 4: Reboot notification (script will stop here; user must reboot and rerun)
if [ ! -e /dev/spidev0.0 ]; then
    # verify SPI
    echo "Please reboot your system and rerun this script to continue."
    read -p "Press Enter to continue..."
    exit 1
fi
echo "SPI enabled."

# Step 5: Create virtual environment in parent directory (skip if exists)
echo "Checking virtual environment at $VENV_DIR..."
if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ]; then
    echo "Virtual environment already exists at $VENV_DIR. Skipping creation."
else
    if ! command -v python3 >/dev/null 2>&1; then
        echo "Error: python3 not found. Please install Python 3."
        exit 1
    fi
    echo "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created at $VENV_DIR."
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Step 6: Install Python dependencies in venv
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Step 7: Configure Weather API
echo "Configuring Weather API..."
read -p "Enter your CWA (https://opendata.cwa.gov.tw/user/authkey) authorization token: " TOKEN
cat > config.py << EOF
# config.py
WeatherAPI = {
    'Authorization': '$TOKEN'
}
EOF

# Step 8: Set timezone (assume Asia/Taipei; can be adjusted)
echo "Setting timezone to Asia/Taipei..."
sudo timedatectl set-timezone Asia/Taipei

# Step 9: Create systemd service
SERVICE_FILE="/etc/systemd/system/smartweather.service"
VENV_DIR_ABS="$(cd "$VENV_DIR" && pwd)"
PROJECT_DIR_ABS="$(cd "$PROJECT_DIR" && pwd)"
echo "Creating systemd service..."
sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Smart Weather Display
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR_ABS
ExecStart=$VENV_DIR_ABS/bin/python3 $PROJECT_DIR_ABS/SmartWeather.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 10: Enable and start service
echo "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable smartweather.service
sudo systemctl start smartweather.service

echo "Installation complete! Service is running."
echo "Check status with: sudo systemctl status smartweather.service"