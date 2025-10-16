# Installation Guide for DietPi

This guide will help you install and configure the 8x8 Desktop Weather Display on DietPi - a lightweight Debian-based OS optimized for single-board computers.

## System Requirements

- Raspberry Pi or other SBC supported by DietPi
- DietPi OS (version 7.0 or newer recommended)
- 8x8 LED Matrix with MAX7219 driver
- Internet connection

## Installation Steps

### 1. Update System

First, ensure your system is up to date:

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

Or use DietPi's built-in update tool:

```bash
dietpi-update
```

### 2. Install System Dependencies

DietPi is minimal by default, so we need to install required packages.

**Option 1: Using DietPi-Software (Recommended)**

DietPi provides a convenient software installation tool:

```bash
dietpi-software
```

Install these software items:
- Select option `152` - Python 3
- Select option `130` - Python pip

Then install additional system packages:

```bash
sudo apt-get install -y python3-dev python3-spidev \
    libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev \
    libopenjp2-7 libtiff5 build-essential git
```

**Option 2: Manual Installation**

Install all packages directly:

```bash
sudo apt-get install -y python3 python3-pip python3-dev python3-spidev \
    libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev \
    libopenjp2-7 libtiff5 build-essential git
```

Alternatively, use the requirements file:

```bash
# Read packages from requirements_system.txt and install
cat requirements_system.txt | grep -v '^#' | grep -v '^$' | xargs sudo apt-get install -y
```

### 3. Enable SPI Interface

The MAX7219 LED matrix requires SPI to be enabled.

**Method 1: Using dietpi-config (Recommended for DietPi)**

```bash
dietpi-config
```

Navigate to:
- `Advanced Options` → `SPI` → `Enable` → `OK`

**Method 2: Using raspi-config (on Raspberry Pi)**

```bash
sudo raspi-config
```

Navigate to:
- `3 Interface Options` → `I4 SPI` → `Yes` → `OK` → `Finish`

**Method 3: Manual Configuration**

Edit the boot configuration file. The location may vary depending on your hardware:

For Raspberry Pi:
```bash
sudo nano /boot/config.txt
```

For other SBCs, check DietPi documentation for the correct config file location.

Add or uncomment the following line:

```
dtparam=spi=on
```

Save and exit (Ctrl+X, then Y, then Enter).

### 4. Reboot

Reboot your device to apply changes:

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
cd /mnt/dietpi_userdata
git clone https://github.com/dong881/8x8_desktopWeather.git
cd 8x8_desktopWeather
```

Note: DietPi recommends storing user data in `/mnt/dietpi_userdata` for better organization.

### 7. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

If you encounter permission issues, use:

```bash
pip3 install --user -r requirements.txt
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

DietPi has a dedicated timezone configuration tool:

```bash
dietpi-config
```

Navigate to:
- `Language/Regional Options` → `Timezone` → Select your region and city

Or use the standard Linux command:

```bash
sudo timedatectl set-timezone Asia/Taipei
```

Verify the timezone:

```bash
timedatectl status
```

### 10. Test the Application

Run a test to ensure everything is working:

```bash
python3 SmartWeather.py
```

Press Ctrl+C to stop the test.

### 11. Run as Background Service (Recommended for DietPi)

DietPi uses systemd for service management. Create a service file:

```bash
sudo nano /etc/systemd/system/smartweather.service
```

Add the following content (adjust paths if needed):

```ini
[Unit]
Description=Smart Weather Display
After=network.target

[Service]
Type=simple
User=dietpi
WorkingDirectory=/mnt/dietpi_userdata/8x8_desktopWeather
ExecStart=/usr/bin/python3 /mnt/dietpi_userdata/8x8_desktopWeather/SmartWeather.py
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

View logs:

```bash
sudo journalctl -u smartweather.service -f
```

### 12. Optional: Configure DietPi-Autostart

DietPi offers an autostart configuration tool:

```bash
dietpi-autostart
```

Select `Custom Script` and point it to your Python script if you prefer this method over systemd.

## Hardware Connections

Connect the MAX7219 LED matrix to your device as follows:

| MAX7219 Pin | Raspberry Pi Pin | Generic SPI |
|-------------|------------------|-------------|
| VCC         | 5V (Pin 2 or 4)  | 5V          |
| GND         | GND (Pin 6)      | GND         |
| DIN         | MOSI (Pin 19)    | MOSI        |
| CS          | CE0 (Pin 24)     | CS/CE0      |
| CLK         | SCLK (Pin 23)    | SCLK        |

Reference: https://luma-led-matrix.readthedocs.io/en/latest/install.html#gpio-pin-outs

## DietPi-Specific Optimizations

### Reduce Memory Usage

DietPi is optimized for minimal resource usage. To further optimize:

1. Disable unnecessary services:
```bash
dietpi-services
```

2. Use DietPi-RAMlog to reduce SD card writes:
```bash
dietpi-ramlog
```

### Network Configuration

Use DietPi's network tool for WiFi setup:

```bash
dietpi-config
```

Navigate to: `Network Options` → `WiFi`

## Troubleshooting

### SPI not found
- Ensure SPI is enabled using `dietpi-config`
- Reboot after making changes
- Check with `ls /dev/spi*`

### Permission denied when accessing SPI
```bash
sudo usermod -a -G spi,gpio dietpi
```
Then log out and log back in.

### Python module not found
- Ensure pip packages are installed: `pip3 list | grep luma`
- Try installing with --user flag: `pip3 install --user -r requirements.txt`

### LED matrix not displaying
- Check wiring connections
- Verify SPI is enabled
- Test with the test script: `python3 TEST_8x8LED\(MAX7219\).py`
- Check DietPi logs: `dietpi-logclear`

### Weather data not updating
- Check internet connection: `dietpi-config` → `Network Options`
- Verify your CWB API authorization token is correct
- Check API quota limits
- View service logs: `sudo journalctl -u smartweather.service -n 50`

### Low memory issues
- DietPi is already optimized, but you can free up more memory:
  ```bash
  dietpi-services
  ```
  Disable unused services

## Uninstallation

To remove the application:

```bash
# Stop and disable the service
sudo systemctl stop smartweather.service
sudo systemctl disable smartweather.service
sudo rm /etc/systemd/system/smartweather.service
sudo systemctl daemon-reload

# Remove the application directory
cd /mnt/dietpi_userdata
rm -rf 8x8_desktopWeather

# Optional: Remove Python packages
pip3 uninstall luma.led-matrix requests -y

# Optional: Remove system packages (use with caution)
# sudo apt-get remove --purge python3-spidev libjpeg-dev zlib1g-dev
```

## Additional Resources

- DietPi Documentation: https://dietpi.com/docs/
- DietPi Forum: https://dietpi.com/forum/
- Luma LED Matrix Documentation: https://luma-led-matrix.readthedocs.io/
- CWB API Documentation: https://opendata.cwb.gov.tw/
