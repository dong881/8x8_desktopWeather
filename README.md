Smart Weather Display
=====================

This Python script retrieves weather forecast data from the Central Weather Administration (CWA) API and displays it on an 8x8 LED matrix using a MAX7219 driver.

## 🎉 Enhanced Version Available!

This project now includes a **modular architecture** with advanced features and a **Web Configuration Interface**!

### ✨ New Features
- **Web Configuration Interface** (Port 5000): Modern, minimalist web UI to configure and monitor the display in real-time
- **Automatic Night Mode**: LED brightness automatically adjusts based on time of day (dimmer at night, brighter during day)
- **Multiple API Integration**: Weather forecast, real-time observation, earthquake alerts, UV index
- **8x8 Icon Library**: Visual weather icons (sunny, rainy, cloudy, etc.) - all properly centered and filling 8x8 pixels
- **Animation System**: Rain drops, sun shine, earthquake shake effects
- **Smart Display Modes**: Carousel rotation, scrolling text, icon display, mixed mode
- **Intelligent Alerts**: Priority-based alert system with earthquake detection
- **Data Caching**: Local caching with automatic fallback on API failure
- **Background Scheduler**: Automatic data updates with configurable intervals

### 🌐 Web Configuration Interface

Access the web interface at `http://[your-pi-ip]:5000` to:
- **Monitor** current temperature, humidity, and weather conditions in real-time
- **Configure** display modes, page durations, and carousel content
- **Adjust** brightness (manual or automatic night mode) and update intervals
- **Force** immediate weather or earthquake data updates
- **View** system status with auto-refreshing display

The interface features a modern, minimalist design that works on desktop and mobile devices.

### 📚 Documentation
- **[doc/FEATURES.md](doc/FEATURES.md)**: Complete feature overview and usage guide
- **[doc/API_GUIDE.md](doc/API_GUIDE.md)**: Comprehensive API integration documentation
- **[config.example.py](config.example.py)**: Configuration template

### 🚀 Quick Start
```bash
# Run enhanced version with web interface
python3 main.py

# Access web configuration interface
# Open browser: http://[your-pi-ip]:5000

# Or run original version (backward compatible)
python3 test/Weather.py
```

See [doc/FEATURES.md](doc/FEATURES.md) for detailed documentation on the new modular architecture.

---

## Original Features

![image](https://github.com/dong881/8x8_desktopWeather/assets/52557611/b090fc50-3632-4c0f-9d17-944792c73374)

For example (it is 7 o'clock):
- [**3rd column**] The closest forecast period column will blink
- [**3rd column**] Today from 6:00 to 9:00 the weather forecast temperature is 20-22 degrees
- [**3rd column**] The probability of precipitation is higher than 60%
- [**4th column**] Today from 9:00 to 12:00 the weather forecast temperature is 29-31 degrees
- [**4th column**] The probability of precipitation is less than 60%
- [**2nd column**] Tomorrow from 3:00 to 6:00 the weather forecast will be below 13 degrees

Prerequisites
-------------

-   Python 3.x
-   Raspberry Pi (or any other compatible hardware) with SPI interface
-   Internet connection

## Architecture

### Modular Structure
```
src/
├── api/              # API clients and data processing
│   ├── cwa_client.py      # CWA API integration
│   └── data_processor.py  # Data transformation
├── display/          # Display control and visualization
│   ├── icons.py           # 8x8 pixel icon library
│   ├── animations.py      # Animation engine
│   └── display_manager.py # Display mode manager
└── utils/            # Utility modules
    ├── logger.py          # Logging system
    └── scheduler.py       # Background task scheduler
```

### Key Components

**API Integration** (`src/api/`)
- Multi-endpoint CWA API client with caching
- Earthquake monitoring and alerts
- Real-time weather observation
- UV index and weather alerts

**Display System** (`src/display/`)
- 8x8 pixel icon library (20+ icons)
- Animation engine (rain, sun, earthquake effects)
- Multiple display modes (carousel, icon, mixed, alert)
- Smooth transitions and effects

**Background Services** (`src/utils/`)
- Automatic data updates (5-30 min intervals)
- Earthquake detection (5 min checks)
- Priority-based alert system
- Error handling and logging

## Installation

### Quick Automated Setup (Recommended)

Run the automated script for PiOS or DietPi:

```bash
cd 8x8_desktopWeather
bash install.sh
```

This script handles system updates, dependencies (including Flask for web interface), SPI setup, virtual environment, API config, and service creation.

### Manual Setup (If Script Fails)

1. **Update System**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

2. **Install Dependencies**:
   ```bash
   sudo apt-get install -y python3 python3-pip python3-dev python3-spidev libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5 build-essential git
   pip3 install -r requirements.txt
   ```
   
   Note: This will install all required packages including Flask for the web configuration interface.

3. **Enable SPI**:
   - **PiOS**: Run `sudo raspi-config`, go to `3 Interface Options` → `I4 SPI` → `Yes`.
   - **DietPi**: Run `dietpi-config`, go to `Advanced Options` → `SPI` → `Enable`.
   Then reboot: `sudo reboot`.
   Verify: `ls /dev/spi*` (should show `/dev/spidev0.0`).

4. **Configure API**:
   Get token from https://opendata.cwa.gov.tw/user/authkey.
   Edit `config.py`:
   ```python
   WeatherAPI = {'Authorization': 'YOUR_TOKEN'}
   ```

5. **Set Timezone**:
   ```bash
   sudo timedatectl set-timezone Asia/Taipei
   ```

6. **Run Manually**:
   ```bash
   python3 SmartWeather.py
   ```
   Or create a service (see script for details).

![image](https://github.com/dong881/8x8_desktopWeather/assets/52557611/6a0bf29a-e59f-48e8-adda-d70d049db4f9)

Reference: https://luma-led-matrix.readthedocs.io/en/latest/install.html#gpio-pin-outs

# Configuration

Before running the script, make sure to set up the configuration by following these steps:

1. In `config.py`, define the WeatherAPI configuration with your CWB authorization token. It should look like this:
    ```python
    # config.py
    
    WeatherAPI = {
        'Authorization': 'YOUR_CWB_AUTHORIZATION_TOKEN'
    }
    ```
   Replace `'YOUR_CWB_AUTHORIZATION_TOKEN'` with [your actual CWB authorization token](https://opendata.cwa.gov.tw/user/authkey).

![SPI Configuration](https://github.com/dong881/8x8_desktopWeather/assets/52557611/8c58272f-ec3d-41ad-81c8-a3b47bea6df2)


2. Open the terminal and enable SPI (Serial Peripheral Interface) on your Raspberry Pi by adding the following line to the `/boot/config.txt` file:
   ```bash
   sudo nano /boot/config.txt
   ```
   Add or uncomment the line:
   ```bash
   dtparam=spi=on
   ```
   Save and exit the editor.

3. Reboot your Raspberry Pi:
   ```bash
   sudo reboot
   ```

4. Verify that SPI is successfully enabled by checking for SPI devices:
   ```bash
   ls /dev/spi*
   ```

   You should see outputs like `/dev/spidev0.0` or `/dev/spidev0.1` if SPI is enabled.

Configuration is now complete, and SPI is ready for use.

Usage
-----

### Enhanced Version (Recommended)

The enhanced version provides multiple data sources, visual icons, smart alerts, and a web configuration interface:

1.  Connect the 8x8 LED matrix to your Raspberry Pi or compatible hardware.
    
2.  Run the enhanced version:
    ```bash
    # Test mode
    python3 main.py
    
    # Long-term background mode
    nohup python3 main.py &
    ```

3.  Access the web configuration interface:
    ```
    Open browser: http://[your-pi-ip]:5000
    ```

4.  The system will:
    - Display startup animation
    - Fetch weather data from CWA API
    - Show temperature bars with rainfall indicators (blinks current time)
    - Rotate through weather icons and temperature displays
    - Monitor for earthquakes and display alerts automatically
    - Update data in background (weather: 30min, earthquake: 5min)
    - Provide web interface for configuration and monitoring

### Original Version

For the classic temperature bar display only (without web interface):

1.  Connect the 8x8 LED matrix to your Raspberry Pi or compatible hardware.
    
2.  Run the script by executing the following command:
    - used to test
    ```cmd=
    python test/Weather.py
    ``` 
    - for long-term use
    ```cmd=
    nohup python test/Weather.py &
    ``` 
    
3.  The script will continuously retrieve the weather forecast data from the CWB API and display it on the LED matrix.
    

Customization
-------------

-   You can modify the location for which the weather forecast is retrieved by updating the `locationName` parameter in the API URL.
    
-   The script currently displays the temperature and precipitation probability data. You can customize the displayed data elements by modifying the `elementName` parameter in the API URL.
    
-   You can adjust the display intervals and timings by modifying the appropriate variables in the script.
    

Troubleshooting
---------------

-   If you encounter any issues, ensure that you have a stable internet connection and that your CWB authorization token is correct.
    
-   Make sure that the SPI interface is enabled on your Raspberry Pi. You can check and enable it using the `raspi-config` utility.
    
-   If the LED matrix is not displaying properly, check the wiring connections and make sure you have installed the necessary libraries.

-   Confirm the current time zone of your Raspberry Pi with `timedatectl status`, if the time zone is incorrect, you can use the following command to modify it:
    ```cmd=
    sudo timedatectl set-timezone <timezone>
    ```
    - Example of timezone: Asia/Taipei

License
---------------

Copyright (c) 2023 MingHung


Acknowledgments
---------------

-   This project is based on the [luma.led_matrix](https://github.com/rm-hull/luma.led_matrix) library.
    
-   Weather data is retrieved from the Central Weather Bureau (CWB) API.
