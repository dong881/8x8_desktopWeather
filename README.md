Smart Weather Display
=====================

This Python script retrieves weather forecast data from the Central Weather Bureau (CWB) API and displays it on an 8x8 LED matrix using a MAX7219 driver.

![image](https://github.com/dong881/8x8_desktopWeather/assets/52557611/b090fc50-3632-4c0f-9d17-944792c73374)

For example (it is 7 o'clock):
- [**3rd column**] The closest forecast period column will blink
- [**3rd column**] Today from 6:00 to 9:00 the weather forecast temperature is 20-22 degrees
- [**3rd column**] The probability of precipitation is higher than 60%
- [**4th column**] Today from 9:00 to 12:00 the weather forecast temperature is 29-31 degrees
- [**4th column**] The probability of precipitation is less than 60%
- [**2nd column**] Tomorrow from 3:00 to 6:00 the weather forecast will be below 13 degrees

### Display Modes

The display cycles through three modes automatically:

1. **Bar Graph Mode** - Shows temperature as bar heights and precipitation probability as bottom-row indicators. The current time period column has a scan animation.
2. **Ticker Mode** - Scrolls text showing "MAX-MIN POP%" (e.g., "28-18 30%").
3. **Icon Mode** - Shows an animated weather icon (sun, cloud, or umbrella) based on precipitation forecast.

Prerequisites
-------------

-   Python 3.x
-   Raspberry Pi (or any other compatible hardware) with SPI interface
-   Internet connection

## Installation

### Quick Automated Setup (Recommended)

Run the automated script for PiOS or DietPi:

```bash
cd 8x8_desktopWeather
bash install.sh
```

This script handles system updates, dependencies, SPI setup, virtual environment, API config, and service creation.

### Manual Setup (If Script Fails)

1. **Update System**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

2. **Install Dependencies**:
   ```bash
   sudo apt-get install -y python3 python3-pip python3-dev python3-spidev libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff-dev build-essential git
   pip3 install -r requirements.txt
   ```

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
   python3 Weather.py
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

1.  Connect the 8x8 LED matrix to your Raspberry Pi or compatible hardware.
    
2.  Run the script by executing the following command:
    - used to test
    ```cmd=
    python Weather.py
    ``` 
    - for long-term use
    ```cmd=
    nohup python Weather.py
    ``` 
    
3.  The script will continuously retrieve the weather forecast data from the CWB API and display it on the LED matrix.
    

Customization
-------------

### Location Settings

Edit `Weather.py` to change the forecast location:
```python
LOCATION_NAME = '大安區'  # Change to your district/township name
```

### Display Timing

Adjust the display timing constants in `Weather.py`:
```python
BARGRAPH_DURATION = 15      # seconds for bar graph display
TICKER_DURATION = 20        # seconds for ticker scrolling
ICON_DURATION = 10          # seconds for icon display
UPDATE_INTERVAL_MINS = 40   # minutes between weather data updates
```

### Brightness Settings

Configure the LED brightness for day/night modes:
```python
NIGHT_MODE_START = 0        # night mode start hour (24h)
NIGHT_MODE_END = 6          # night mode end hour (24h)
BRIGHTNESS_NIGHT = 8        # brightness during night (0-255)
BRIGHTNESS_DAY = 30         # brightness during daytime (0-255)
```

### Temperature Display Range

Adjust the temperature mapping to LED levels:
```python
TEMP_DISPLAY_MIN = 12       # minimum temperature for LED mapping (°C)
TEMP_DISPLAY_MAX = 33       # maximum temperature for LED mapping (°C)
```

### API Token via Environment Variable

You can set the API token via environment variable instead of editing `config.py`:
```bash
export CWA_AUTH_TOKEN='your-token-here'
python3 Weather.py
```

### Demo Mode

Enable debug/demo mode to see state information:
```python
DEMO_MODE = True  # set True to enable debug display mode
```
    

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
