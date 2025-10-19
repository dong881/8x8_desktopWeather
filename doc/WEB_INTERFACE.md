# Web Configuration Interface

The 8x8 Weather Display includes a modern web-based configuration interface that allows you to monitor and control your weather display remotely.

## Overview

The web interface runs on port 6666 and provides real-time monitoring and configuration capabilities through a clean, minimalist UI that works on both desktop and mobile devices.

## Features

### Real-Time Monitoring
- **Current Weather**: Temperature, humidity, and weather conditions updated every 5 seconds
- **System Status**: Display whether the system is running and when it was last updated
- **Visual Indicators**: Pulsing indicators show when the system is actively refreshing data

### Display Configuration
- **Display Mode**: Switch between 5 different display modes:
  - Carousel: Automatically rotate through all enabled pages
  - Icon Only: Show only weather icons
  - Scrolling Text: Display scrolling weather information
  - Mixed: Combine icon and text displays
  - Alert: Priority-based alert system
  
- **Page Duration**: Adjust how long each page is displayed (5-60 seconds)
- **Brightness Control**: Set display brightness from 0-255
- **Carousel Items**: Select which content to include in the carousel rotation:
  - Temperature bars
  - Weather icon
  - Temperature display

### Update Intervals
Configure how frequently data is fetched:
- **Weather Updates**: 5-120 minutes (default: 30 minutes)
- **Earthquake Checks**: 1-60 minutes (default: 5 minutes)
- **Observation Updates**: 5-60 minutes (default: 10 minutes)

### Manual Controls
- **Force Update Buttons**: Trigger immediate data updates for weather or earthquake information
- **Save Settings**: Apply configuration changes immediately

## Accessing the Web Interface

### Local Access
If you're on the same network as your Raspberry Pi:
```
http://[raspberry-pi-ip]:6666
```

For example:
```
http://192.168.1.100:6666
```

### Finding Your Raspberry Pi IP Address
On your Raspberry Pi, run:
```bash
hostname -I
```

## API Endpoints

The web interface also provides REST API endpoints for programmatic access:

### GET /api/status
Get current system status including weather data, display settings, and update intervals.

**Response:**
```json
{
  "current_status": {
    "temperature": 25.5,
    "humidity": 65,
    "weather": "Partly Cloudy",
    "running": true
  },
  "display_settings": {
    "mode": "carousel",
    "page_duration": 15.0,
    "brightness": 255,
    "carousel_items": ["temperature_bars", "weather_icon", "temperature_display"]
  },
  "update_intervals": {
    "weather": 1800,
    "earthquake": 300,
    "observation": 600
  },
  "timestamp": "2025-10-19T17:00:00"
}
```

### POST /api/settings
Update display settings or update intervals.

**Request Body:**
```json
{
  "display_settings": {
    "mode": "carousel",
    "page_duration": 20.0,
    "brightness": 200,
    "carousel_items": ["temperature_bars", "weather_icon"]
  },
  "update_intervals": {
    "weather": 1800,
    "earthquake": 300
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Settings updated"
}
```

### POST /api/force_update
Force immediate data update.

**Request Body:**
```json
{
  "type": "weather"  // or "earthquake"
}
```

**Response:**
```json
{
  "success": true,
  "message": "weather update triggered"
}
```

### POST /api/display_mode
Change display mode.

**Request Body:**
```json
{
  "mode": "carousel"  // or "icon", "scrolling", "mixed", "alert"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Display mode changed to carousel"
}
```

## Integration with Main Application

The web server runs in a background thread and integrates seamlessly with the main weather display application. Changes made through the web interface are applied immediately to the running system.

### Starting the Web Server

The web server starts automatically when you run `main.py`:

```bash
python3 main.py
```

### Running Standalone

You can also run the web interface in standalone mode for testing:

```bash
python3 web_config.py
```

Note: In standalone mode, some features will not work as they require the full application to be running.

## Security Considerations

The web interface is designed for use on a local network. For remote access:

1. **VPN**: Use a VPN connection to securely access your home network
2. **SSH Tunnel**: Create an SSH tunnel to access the web interface:
   ```bash
   ssh -L 6666:localhost:6666 pi@your-pi-ip
   ```
   Then access at `http://localhost:6666`

3. **Reverse Proxy**: Set up a reverse proxy (nginx, Apache) with authentication

**Do not expose port 6666 directly to the internet without proper security measures.**

## Troubleshooting

### Cannot Access Web Interface

1. Check if the server is running:
   ```bash
   netstat -tuln | grep 6666
   ```

2. Check firewall settings:
   ```bash
   sudo ufw status
   sudo ufw allow 6666
   ```

3. Verify the IP address:
   ```bash
   hostname -I
   ```

### Settings Not Applying

1. Check the main application logs for errors
2. Ensure the main application is running
3. Try forcing a data update through the web interface

### Page Not Loading

1. Clear browser cache
2. Try a different browser
3. Check browser console for JavaScript errors

## Development

The web interface is built with:
- **Backend**: Flask (Python)
- **Frontend**: Pure HTML/CSS/JavaScript (no frameworks)
- **Design**: Modern, minimalist, responsive

### File Structure
```
web_config.py          # Flask application and API endpoints
templates/index.html   # Web interface HTML/CSS/JavaScript
```

### Customization

You can customize the web interface by editing:
- `templates/index.html`: Modify the UI, add new features
- `web_config.py`: Add new API endpoints, change behavior

## Support

For issues or feature requests related to the web interface, please open an issue on GitHub.
