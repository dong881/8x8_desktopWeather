# Configuration Example for Enhanced 8x8 Weather Display
# Copy this file to config.py and fill in your settings

# Required: CWA API Authorization Token
# Get your token from: https://opendata.cwa.gov.tw/user/authkey
WeatherAPI = {
    'Authorization': ''  # Fill in your CWA authorization token
}

# Optional: Display Configuration
DisplayConfig = {
    # LED brightness (0-255, default: 30)
    'brightness': 30,
    
    # Update intervals in seconds
    'weather_update_interval': 1800,     # 30 minutes
    'earthquake_check_interval': 300,    # 5 minutes
    'observation_update_interval': 600,  # 10 minutes
    
    # Display settings
    'page_duration': 15,        # Seconds per page in carousel mode
    'animation_enabled': True,  # Enable weather animations
    'scroll_speed': 0.05,       # Scrolling text speed
    
    # Location settings
    'location_name': '大安區',   # Location for weather forecast
    'station_id': '466920',     # Weather station ID (Taipei)
    
    # Alert settings
    'earthquake_alert_duration': 60,    # Seconds
    'typhoon_alert_duration': 30,       # Seconds
    'earthquake_magnitude_threshold': 4.0,  # Minimum magnitude to alert
}

# Optional: Advanced Settings
AdvancedConfig = {
    # Cache settings
    'cache_enabled': True,
    'cache_directory': 'data/cache',
    
    # Logging
    'log_level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'log_to_file': False,
    'log_file': 'weather_display.log',
    
    # API settings
    'api_timeout': 10,           # Seconds
    'api_retry_count': 3,
    'api_rate_limit': 20,        # Requests per minute
    
    # Display modes priority
    # 1 = highest priority (alerts)
    # 2 = important (warnings)
    # 3 = normal (regular info)
    'display_priorities': {
        'earthquake': 1,
        'typhoon': 1,
        'heavy_rain': 2,
        'temperature': 3,
        'weather_icon': 3,
    }
}
