# Quick Start Guide - 8x8 Weather Display v2.0

## 🚀 5-Minute Setup

### Prerequisites
- Raspberry Pi (any model with GPIO)
- MAX7219 8x8 LED Matrix
- Internet connection
- CWA API Token (free from [opendata.cwa.gov.tw](https://opendata.cwa.gov.tw/user/authkey))

### Step 1: Hardware Connection

Connect your MAX7219 to Raspberry Pi:
```
MAX7219     Raspberry Pi
VCC    ───  3.3V (Pin 1)
GND    ───  GND (Pin 6)
DIN    ───  MOSI (GPIO 10, Pin 19)
CS     ───  CE0 (GPIO 8, Pin 24)
CLK    ───  SCLK (GPIO 11, Pin 23)
```

### Step 2: Clone Repository

```bash
cd ~
git clone https://github.com/dong881/8x8_desktopWeather.git
cd 8x8_desktopWeather
```

### Step 3: Automated Installation

```bash
# Run the install script
bash install.sh

# The script will:
# 1. Install system dependencies
# 2. Enable SPI interface
# 3. Create Python virtual environment
# 4. Install Python packages
# 5. Configure your API token
# 6. Create systemd service
```

**Note**: You'll be prompted for your CWA API token during installation.

### Step 4: Get Your API Token

1. Visit [CWA OpenData Platform](https://opendata.cwa.gov.tw/user/authkey)
2. Register/login
3. Copy your authorization key
4. Paste when prompted by install script

### Step 5: Test the Display

```bash
# Test enhanced version
python3 main.py

# Or test original version
python3 Weather.py
```

You should see:
1. Startup logo animation
2. Temperature bars with rainfall indicators
3. Current time column blinking
4. Automatic updates every 30 minutes

### Step 6: Enable Auto-Start (Optional)

```bash
# Check service status
sudo systemctl status weather.service

# Enable on boot
sudo systemctl enable weather.service

# Start now
sudo systemctl start weather.service

# View logs
sudo journalctl -u weather.service -f
```

---

## 📱 Manual Installation

If the automated script doesn't work:

### 1. Install Dependencies

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install system packages
sudo apt-get install -y python3 python3-pip python3-dev \
    python3-spidev libjpeg-dev zlib1g-dev libfreetype6-dev \
    liblcms2-dev libopenjp2-7 libtiff-dev build-essential git

# Install Python packages
pip3 install -r requirements.txt
```

### 2. Enable SPI

**On Raspberry Pi OS:**
```bash
sudo raspi-config
# Navigate to: 3 Interface Options → I4 SPI → Yes
sudo reboot
```

**On DietPi:**
```bash
dietpi-config
# Navigate to: Advanced Options → SPI → Enable
sudo reboot
```

**Verify SPI:**
```bash
ls /dev/spi*
# Should show: /dev/spidev0.0
```

### 3. Configure API

```bash
# Copy example config
cp config.example.py config.py

# Edit with your token
nano config.py
```

Replace `''` with your actual token:
```python
WeatherAPI = {
    'Authorization': 'YOUR_TOKEN_HERE'
}
```

### 4. Set Timezone

```bash
sudo timedatectl set-timezone Asia/Taipei
timedatectl status  # Verify
```

### 5. Run

```bash
# Test mode
python3 main.py

# Background mode
nohup python3 main.py &
```

---

## 🎨 Feature Tour

### What You'll See

**Every Second:**
- Temperature bars (0-7 levels, 12-33°C range)
- Rainfall indicators (dot at bottom if ≥60% chance)
- Current time column blinks
- 8 columns = next 24 hours in 3-hour intervals

**Every 30 Seconds:**
- Alternates between temperature bars and other views:
  - Weather icon (sunny/rainy/cloudy with animation)
  - Current temperature with thermometer
  - Additional weather info

**On Earthquake (M≥4.0):**
- Interrupts normal display immediately
- Shows earthquake shake animation (10 seconds)
- Scrolls earthquake details (magnitude, location)
- Returns to normal after 60 seconds

### Understanding the Display

#### Temperature Bars
```
Column Index: 0    1    2    3    4    5    6    7
Time Range:  0-3  3-6  6-9  9-12 12-15 15-18 18-21 21-24
             
Height = Temperature Level:
  7 = 33°C  ████████
  6 = 31°C  ███████
  5 = 28°C  ██████
  4 = 26°C  █████
  3 = 24°C  ████
  2 = 21°C  ███
  1 = 19°C  ██
  0 = 16°C  █

Bottom dot = Rain chance ≥60%
Blinking column = Current time
```

#### Weather Icons

| Icon | Meaning |
|------|---------|
| ☀️ Sunny | Clear sky with rays |
| ☁️ Cloudy | Wave-shaped cloud |
| 🌧️ Rainy | Cloud with raindrops |
| ⚡ Thunderstorm | Cloud with lightning |
| ❄️ Snowy | Cloud with snowflakes |
| 🌀 Typhoon | Spiral pattern |
| 🏔️ Earthquake | Concentric waves |
| ⚠️ Warning | Triangle with ! |

---

## ⚙️ Configuration

### Basic Settings (config.py)

```python
# Required
WeatherAPI = {
    'Authorization': 'YOUR_TOKEN'
}

# Optional
DisplayConfig = {
    'brightness': 30,              # LED brightness (0-255)
    'location_name': '大安區',      # Your location
    'page_duration': 15,           # Seconds per page
    'animation_enabled': True,     # Enable animations
}
```

### Advanced Settings

See [config.example.py](config.example.py) for all options:
- Update intervals
- Cache settings
- Alert thresholds
- Display priorities
- Logging configuration

---

## 🔧 Troubleshooting

### Problem: No display

**Solution 1: Check SPI**
```bash
ls /dev/spi*  # Should show /dev/spidev0.0
```

**Solution 2: Check connections**
```bash
# Run test script
python3 TEST_8x8LED\(MAX7219\).py
```

**Solution 3: Check permissions**
```bash
# Add user to spi group
sudo usermod -a -G spi $USER
# Logout and login again
```

### Problem: API error

**Solution 1: Verify token**
```bash
cat config.py  # Check Authorization value
```

**Solution 2: Test API manually**
```bash
curl "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization=YOUR_TOKEN&limit=1"
```

**Solution 3: Check internet**
```bash
ping opendata.cwa.gov.tw
```

### Problem: Service won't start

**Solution 1: Check logs**
```bash
sudo journalctl -u weather.service -n 50
```

**Solution 2: Check paths in service file**
```bash
sudo nano /etc/systemd/system/weather.service
# Verify WorkingDirectory and ExecStart paths
```

**Solution 3: Reload service**
```bash
sudo systemctl daemon-reload
sudo systemctl restart weather.service
```

### Problem: Module import error

**Solution: Install dependencies**
```bash
cd /path/to/8x8_desktopWeather
pip3 install -r requirements.txt
```

---

## 📚 Next Steps

### Learn More
- [FEATURES.md](FEATURES.md) - Complete feature documentation
- [API_GUIDE.md](API_GUIDE.md) - API integration details
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CHANGELOG.md](CHANGELOG.md) - Version history

### Customize
- Add more locations
- Adjust update intervals
- Enable/disable features
- Create custom icons
- Add new API endpoints

### Contribute
- Report issues on GitHub
- Submit pull requests
- Share your customizations
- Improve documentation

---

## 🆘 Support

### Getting Help

**GitHub Issues:**
https://github.com/dong881/8x8_desktopWeather/issues

**Check Logs:**
```bash
# Application logs
sudo journalctl -u weather.service -f

# System logs
dmesg | grep spi
```

**Common Issues:**
1. SPI not enabled → Run `raspi-config`
2. Wrong API token → Update `config.py`
3. No internet → Check network
4. Hardware issue → Test with `TEST_8x8LED(MAX7219).py`

### Useful Commands

```bash
# Service control
sudo systemctl status weather.service    # Check status
sudo systemctl start weather.service     # Start
sudo systemctl stop weather.service      # Stop
sudo systemctl restart weather.service   # Restart
sudo systemctl enable weather.service    # Enable on boot
sudo systemctl disable weather.service   # Disable on boot

# View logs
sudo journalctl -u weather.service -f    # Follow logs
sudo journalctl -u weather.service -n 100  # Last 100 lines

# Test components
python3 tests/test_components.py         # Run tests
python3 -m py_compile main.py            # Check syntax

# Update code
cd /path/to/8x8_desktopWeather
git pull                                 # Get latest code
pip3 install -r requirements.txt         # Update dependencies
sudo systemctl restart weather.service   # Restart service
```

---

## ✅ Checklist

Before asking for help, verify:

- [ ] SPI is enabled (`ls /dev/spi*`)
- [ ] LED matrix is connected correctly
- [ ] API token is in config.py
- [ ] Dependencies are installed (`pip3 list | grep luma`)
- [ ] Internet connection works (`ping opendata.cwa.gov.tw`)
- [ ] Test script works (`python3 TEST_8x8LED\(MAX7219\).py`)
- [ ] Timezone is correct (`timedatectl status`)
- [ ] Permissions are set (`groups` should include spi)

---

**Enjoy your enhanced weather display! 🌤️**
