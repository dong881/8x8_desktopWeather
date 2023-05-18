Smart Weather Display
=====================

This Python script retrieves weather forecast data from the Central Weather Bureau (CWB) API and displays it on an 8x8 LED matrix using a MAX7219 driver.

Prerequisites
-------------

-   Python 3.x
-   Raspberry Pi (or any other compatible hardware) with SPI interface
-   `luma.led_matrix` library (install using `pip install luma.led_matrix`)
-   Internet connection

Configuration
-------------

Before running the script, make sure to set up the configuration by following these steps:

1.  Create a new file named `config.py` in the same folder as the script.
    
2.  In `config.py`, define the WeatherAPI configuration with your CWB authorization token. It should look like this:
    
    python Copy code
    
    `# config.py
    
    WeatherAPI = {
        'Authorization': 'YOUR_CWB_AUTHORIZATION_TOKEN'
    }` 
    
    Replace `'YOUR_CWB_AUTHORIZATION_TOKEN'` with your actual CWB authorization token.
    

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

Acknowledgments
---------------

-   This project is based on the [luma.led_matrix](https://github.com/rm-hull/luma.led_matrix) library.
    
-   Weather data is retrieved from the Central Weather Bureau (CWB) API.
