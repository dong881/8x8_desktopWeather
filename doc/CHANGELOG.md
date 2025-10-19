# Changelog

All notable changes to the 8x8 Desktop Weather Display project.

## [2.0.0] - 2024-10-19

### 🎉 Major Release - Modular Architecture

This is a major upgrade that transforms the project from a simple data display to a comprehensive weather visualization system with enhanced API integration and intelligent features.

### Added

#### Modular Architecture
- Created `src/` directory structure with organized modules
- `src/api/` - API clients and data processing
- `src/display/` - Display control and visualization
- `src/utils/` - Utility modules (logging, scheduling)

#### API Integration
- **CWA API Client** (`src/api/cwa_client.py`)
  - Weather forecast (F-D0047-061)
  - Real-time observation data (O-A0001-001)
  - Earthquake reports (E-A0015-001)
  - Weather alerts (W-C0033-001)
  - UV index data (O-A0005-001)
  - Data caching with configurable TTL
  - Automatic fallback to cache on API failure
  - Request rate limiting

- **EPA Client** (`src/api/cwa_client.py`)
  - Air quality data integration (foundation)

- **Data Processor** (`src/api/data_processor.py`)
  - Temperature to LED level conversion
  - Precipitation probability processing
  - Weather icon name mapping
  - Array shifting for time alignment
  - Earthquake data processing
  - Observation data processing

#### Display System
- **8x8 Icon Library** (`src/display/icons.py`)
  - Weather icons: sunny, cloudy, rainy, thunderstorm, snowy, typhoon
  - Alert icons: earthquake, warning, alert
  - Temperature icons: hot/cold thermometer
  - Wind icon
  - Number digits (0-9) with 5x7 font
  - 20+ total icons

- **Animation Engine** (`src/display/animations.py`)
  - Rain animation with falling droplets
  - Sun shine animation with blinking rays
  - Earthquake shake effect
  - Fade in/out transitions
  - Slide transitions (left, right, up, down)
  - Horizontal text scrolling
  - Blinking effects

- **Display Manager** (`src/display/display_manager.py`)
  - Multiple display modes:
    - Carousel mode (rotating pages)
    - Icon mode (static/animated icons)
    - Mixed mode (icon + text)
    - Scrolling mode (long text)
    - Alert mode (interrupting alerts)
  - Priority-based content system (1=urgent, 2=important, 3=normal)
  - Page-based content organization
  - Smooth transitions between content
  - Alert interruption system
  - Startup logo animation

#### Background Services
- **Content Scheduler** (`src/utils/scheduler.py`)
  - Background thread-based update system
  - Weather forecast updates (30 min interval)
  - Earthquake monitoring (5 min interval)
  - Observation data updates (10 min interval)
  - Configurable update intervals
  - Callback-based event system
  - Force update capabilities

- **Logger** (`src/utils/logger.py`)
  - Structured logging system
  - Console output with timestamps
  - Configurable log levels

#### Main Application
- **Enhanced Main Program** (`main.py`)
  - Unified entry point using modular architecture
  - Automatic data fetching on startup
  - Background scheduler integration
  - Multiple display pages with rotation
  - Earthquake alert handling
  - Temperature bar display with blinking
  - Weather icon display
  - Temperature digit display
  - Graceful shutdown handling

#### Documentation
- **FEATURES.md** - Comprehensive feature documentation (Chinese/English)
  - Feature overview
  - Usage instructions
  - API endpoint documentation
  - Technical details
  - Performance metrics
  - Troubleshooting guide
  - Future enhancement roadmap

- **API_GUIDE.md** - Complete API integration guide (Chinese)
  - All CWA API endpoints explained
  - Usage strategies and priorities
  - Update frequency recommendations
  - API rate limiting information
  - Extension tutorial
  - EPA air quality integration guide
  - Testing tools and debugging

- **config.example.py** - Configuration template
  - Required API settings
  - Optional display settings
  - Advanced configuration options
  - Location and station settings
  - Alert configuration
  - Cache and logging settings

#### Configuration & Infrastructure
- **.gitignore** - Comprehensive exclusions
  - Python cache files
  - Virtual environments
  - Data cache directory
  - IDE files
  - OS-specific files

- **tests/test_components.py** - Component testing
  - DataProcessor tests
  - WeatherIcons tests
  - CWAClient mock tests
  - DisplayManager mock tests

### Changed

#### Core Changes
- Updated `install.sh` to use `main.py` instead of `Weather.py` for service
- Updated `requirements.txt` with new dependencies:
  - Pillow >= 8.0.0 (for image processing)
  - urllib3 >= 1.26.0 (for security warnings)

- Enhanced `README.md` with:
  - New features overview
  - Architecture documentation
  - Enhanced version usage instructions
  - Links to new documentation files

#### Backward Compatibility
- Original `Weather.py` remains unchanged and functional
- Users can choose between:
  - Enhanced version: `python3 main.py`
  - Original version: `python3 Weather.py`

### Technical Improvements

#### Code Quality
- Modular design following single responsibility principle
- Comprehensive docstrings for all classes and methods
- Type hints for better code clarity
- Error handling with try-except blocks
- Logging throughout the application

#### Performance
- Efficient caching system reduces API calls
- Background threads for non-blocking updates
- Configurable update intervals
- Resource-efficient animations (<10% CPU)

#### Reliability
- Fallback to cache on API failures
- Request timeout handling
- Connection error recovery
- Graceful degradation
- Service restart on failure (via systemd)

#### Extensibility
- Easy to add new API endpoints
- Pluggable display modes
- Configurable update intervals
- Custom animation support
- Priority-based alert system

### Security
- urllib3 warning suppression for self-signed certificates
- No hardcoded credentials
- Configuration file separation
- Secure token storage in config.py

### For Developers

#### New Module Structure
```
src/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── cwa_client.py      (270 lines)
│   └── data_processor.py  (270 lines)
├── display/
│   ├── __init__.py
│   ├── icons.py           (280 lines)
│   ├── animations.py      (180 lines)
│   └── display_manager.py (270 lines)
└── utils/
    ├── __init__.py
    ├── logger.py          (35 lines)
    └── scheduler.py       (150 lines)
```

#### API Usage Example
```python
from src.api.cwa_client import CWAClient
from src.display.display_manager import DisplayManager

# Initialize
client = CWAClient(authorization_token)
display = DisplayManager(device)

# Fetch and display weather
weather_data = client.get_weather_forecast()
display.show_icon('sunny', duration=5.0, animate=True)
```

### Migration Guide

#### For Existing Users

1. **No immediate action required** - Original `Weather.py` continues to work

2. **To use enhanced version**:
   ```bash
   # Ensure you have the latest code
   git pull
   
   # Install/update dependencies
   pip3 install -r requirements.txt
   
   # Run enhanced version
   python3 main.py
   ```

3. **To update systemd service**:
   ```bash
   # Edit service file
   sudo nano /etc/systemd/system/weather.service
   
   # Change ExecStart line to use main.py
   ExecStart=/path/to/venv/bin/python3 /path/to/main.py
   
   # Reload and restart
   sudo systemctl daemon-reload
   sudo systemctl restart weather.service
   ```

### Known Issues

- Hardware-specific: Requires actual MAX7219 LED matrix to run
- Testing: Some tests require hardware mocking for full coverage
- EPA API: Air quality integration requires separate API key (not included)

### Future Plans

See [FEATURES.md](FEATURES.md) for detailed future enhancement roadmap including:
- Air quality integration
- Multi-matrix support
- RGB LED support
- Web configuration interface
- Mobile app control

---

## [1.0.0] - 2023

### Initial Release
- Basic weather forecast display
- Temperature bar visualization
- Rainfall probability indicators
- Single API endpoint (F-D0047-061)
- Manual configuration
- Simple installation script

---

**Note**: Version 2.0.0 maintains full backward compatibility with 1.0.0. Users can continue using the original `Weather.py` or migrate to the enhanced `main.py` at their convenience.
