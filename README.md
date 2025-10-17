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

Prerequisites
-------------

-   Python 3.x
-   Raspberry Pi (or any other compatible hardware) with SPI interface
-   `luma.led_matrix` library (install using `pip install luma.led_matrix`)
```bash
pip install luma.led_matrix
pip install requests
pip install RPi.GPIO
pip install spidev

```
-   Internet connection

## Installation Guides

For detailed installation instructions for your specific operating system, please refer to:

- **[Installation Guide for Raspberry Pi OS (PiOS)](INSTALL_PiOS.md)** - Complete step-by-step guide for Raspberry Pi OS
- **[Installation Guide for DietPi](INSTALL_DietPi.md)** - Optimized instructions for DietPi OS

Quick install using requirements files:

```bash
# Install system dependencies (PiOS/DietPi)
cat requirements_system.txt | grep -v '^#' | grep -v '^$' | xargs sudo apt-get install -y

# Install Python dependencies
pip3 install -r requirements.txt
```

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
   Replace `'YOUR_CWB_AUTHORIZATION_TOKEN'` with [your actual CWB authorization token](https://opendata.cwb.gov.tw/user/authkey).

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
    python SmartWeather.py
    ``` 
    - for long-term use
    ```cmd=
    nohup python SmartWeather.py
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
