# Installation Guide for Raspberry Pi OS (PiOS)

This guide will help you install and configure the 8x8 Desktop Weather Display on Raspberry Pi OS (formerly Raspbian).

## System Requirements

- Raspberry Pi (any model with GPIO pins and SPI support)
- Raspberry Pi OS (Buster or newer)
- 8x8 LED Matrix with MAX7219 driver
- Internet connection

## Installation Steps

### 1. Update System

First, ensure your system is up to date:

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Install System Dependencies

Install all required system packages:

```bash
sudo apt-get install -y python3 python3-pip python3-dev python3-spidev \
    libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev \
    libopenjp2-7 libtiff5 build-essential git
```

Alternatively, you can install from the requirements file:

```bash
# Read packages from requirements_system.txt and install
cat requirements_system.txt | grep -v '^#' | grep -v '^$' | xargs sudo apt-get install -y
```

### 3. Enable SPI Interface

The MAX7219 LED matrix requires SPI to be enabled on your Raspberry Pi.

**Method 1: Using raspi-config (Recommended)**

```bash
sudo raspi-config
```

Navigate to:
- `3 Interface Options` → `I4 SPI` → `Yes` → `OK` → `Finish`

**Method 2: Manual Configuration**

Edit the boot configuration file:

```bash
sudo nano /boot/config.txt
```

Add or uncomment the following line:

```
dtparam=spi=on
```

Save and exit (Ctrl+X, then Y, then Enter).

### 4. Reboot

Reboot your Raspberry Pi to apply changes:

```bash
sudo reboot
```

### 5. Verify SPI is Enabled

After reboot, verify SPI is working:

```bash
ls /dev/spi*
```

You should see output like `/dev/spidev0.0` and `/dev/spidev0.1`.

### 6. Clone the Repository

```bash
cd ~
git clone https://github.com/dong881/8x8_desktopWeather.git
cd 8x8_desktopWeather
```

### 7. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 8. Configure Weather API

1. Get your CWB (Central Weather Bureau) API authorization token from:
   https://opendata.cwb.gov.tw/user/authkey

2. Edit the configuration file:

```bash
nano config.py
```

3. Add your authorization token:

```python
WeatherAPI = {
    'Authorization': 'YOUR_CWB_AUTHORIZATION_TOKEN'
}
```

Save and exit.

### 9. Set Correct Timezone

Verify your timezone:

```bash
timedatectl status
```

If needed, set the correct timezone (e.g., for Taiwan):

```bash
sudo timedatectl set-timezone Asia/Taipei
```

### 10. Test the Application

Run a test to ensure everything is working:

```bash
python3 SmartWeather.py
```

Press Ctrl+C to stop the test.

### 11. Run as Background Service (Optional)

For long-term use, you can run the script in the background:

```bash
nohup python3 SmartWeather.py &
```

Or create a systemd service for automatic startup:

```bash
sudo nano /etc/systemd/system/smartweather.service
```

Add the following content:

```ini
[Unit]
Description=Smart Weather Display
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/8x8_desktopWeather
ExecStart=/usr/bin/python3 /home/pi/8x8_desktopWeather/SmartWeather.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable smartweather.service
sudo systemctl start smartweather.service
```

Check service status:

```bash
sudo systemctl status smartweather.service
```

## Hardware Connections

Connect the MAX7219 LED matrix to your Raspberry Pi as follows:

| MAX7219 Pin | Raspberry Pi Pin |
|-------------|------------------|
| VCC         | 5V (Pin 2 or 4)  |
| GND         | GND (Pin 6)      |
| DIN         | MOSI (Pin 19)    |
| CS          | CE0 (Pin 24)     |
| CLK         | SCLK (Pin 23)    |

Reference: https://luma-led-matrix.readthedocs.io/en/latest/install.html#gpio-pin-outs

## Troubleshooting

### SPI not found
- Ensure SPI is enabled in `/boot/config.txt`
- Reboot after making changes
- Check with `ls /dev/spi*`

### Permission denied when accessing SPI
```bash
sudo usermod -a -G spi,gpio pi
```
Then log out and log back in.

### LED matrix not displaying
- Check wiring connections
- Verify SPI is enabled
- Test with the test script: `python3 TEST_8x8LED\(MAX7219\).py`

### Weather data not updating
- Check internet connection
- Verify your CWB API authorization token is correct
- Check API quota limits

## Uninstallation

To remove the application:

```bash
# Stop and disable the service (if configured)
sudo systemctl stop smartweather.service
sudo systemctl disable smartweather.service
sudo rm /etc/systemd/system/smartweather.service

# Remove the application directory
cd ~
rm -rf 8x8_desktopWeather

# Optional: Remove Python packages
pip3 uninstall luma.led-matrix requests -y
```
