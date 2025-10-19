# Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     8x8 Weather Display                          │
│                    Enhanced System v2.0                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         Main Program                             │
│                         (main.py)                                │
│                                                                   │
│  • Initializes all components                                    │
│  • Manages display loop                                          │
│  • Handles graceful shutdown                                     │
└──────────┬──────────────────────────────────────────────────────┘
           │
           │ Uses
           │
┌──────────▼──────────────────────────────────────────────────────┐
│                    Modular Architecture                          │
└─────────────────────────────────────────────────────────────────┘

┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   API Layer    │  │ Display Layer  │  │  Utils Layer   │
│   (src/api)    │  │ (src/display)  │  │  (src/utils)   │
└────────────────┘  └────────────────┘  └────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                                │
│                        (src/api/)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CWAClient (cwa_client.py)                                      │
│  ├── get_weather_forecast()     [F-D0047-061]                   │
│  ├── get_observation_data()     [O-A0001-001]                   │
│  ├── get_earthquake_report()    [E-A0015-001]                   │
│  ├── get_weather_alerts()       [W-C0033-001]                   │
│  ├── get_uv_index()             [O-A0005-001]                   │
│  └── check_recent_earthquake()                                   │
│                                                                   │
│  EPAClient (cwa_client.py)                                      │
│  └── get_air_quality()          [EPA API]                       │
│                                                                   │
│  DataProcessor (data_processor.py)                              │
│  ├── process_weather_forecast()                                 │
│  ├── process_observation_data()                                 │
│  ├── process_earthquake_data()                                  │
│  ├── process_uv_index()                                         │
│  ├── get_weather_icon_name()                                    │
│  ├── calculate_time_index()                                     │
│  └── shift_array()                                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Display Layer                               │
│                     (src/display/)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  WeatherIcons (icons.py)                                        │
│  ├── Weather: SUNNY, CLOUDY, RAINY, THUNDERSTORM, SNOWY        │
│  ├── Alerts: EARTHQUAKE, WARNING, ALERT                         │
│  ├── Temperature: THERMOMETER_HOT, THERMOMETER_COLD            │
│  ├── Other: WINDY, TYPHOON                                      │
│  └── Digits: 0-9 (5x7 pixel font)                              │
│                                                                   │
│  AnimationFrames (icons.py)                                     │
│  ├── RAIN (3 frames)                                            │
│  ├── SUN (2 frames)                                             │
│  └── SHAKE (4 frames)                                           │
│                                                                   │
│  AnimationEngine (animations.py)                                │
│  ├── rain_animation()                                           │
│  ├── sun_animation()                                            │
│  ├── earthquake_shake()                                         │
│  ├── fade_transition()                                          │
│  ├── blink()                                                    │
│  ├── scroll_text_horizontal()                                   │
│  └── slide_in()                                                 │
│                                                                   │
│  DisplayManager (display_manager.py)                            │
│  ├── Display Modes:                                             │
│  │   ├── MODE_CAROUSEL (rotating pages)                        │
│  │   ├── MODE_SCROLLING (text scroll)                          │
│  │   ├── MODE_ICON (static/animated)                           │
│  │   ├── MODE_MIXED (icon + text)                              │
│  │   └── MODE_ALERT (interrupting)                             │
│  │                                                               │
│  ├── Content Management:                                        │
│  │   ├── add_page()                                             │
│  │   ├── rotate_pages()                                         │
│  │   └── trigger_alert()                                        │
│  │                                                               │
│  └── Display Methods:                                           │
│      ├── show_icon()                                            │
│      ├── show_text_scroll()                                     │
│      ├── show_mixed()                                           │
│      ├── show_temperature_bar()                                 │
│      └── transition_to()                                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       Utils Layer                                │
│                      (src/utils/)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ContentScheduler (scheduler.py)                                │
│  ├── Background Threads:                                        │
│  │   ├── weather_update_loop (30 min)                          │
│  │   ├── earthquake_check_loop (5 min)                         │
│  │   └── observation_update_loop (10 min)                      │
│  │                                                               │
│  ├── Callbacks:                                                 │
│  │   ├── on_weather_update                                      │
│  │   ├── on_earthquake_detected                                 │
│  │   └── on_observation_update                                  │
│  │                                                               │
│  └── Control:                                                   │
│      ├── start()                                                │
│      ├── stop()                                                 │
│      ├── force_weather_update()                                 │
│      └── force_earthquake_check()                               │
│                                                                   │
│  Logger (logger.py)                                             │
│  └── setup_logger()                                             │
│      ├── Console output                                         │
│      ├── Timestamp formatting                                   │
│      └── Configurable levels (DEBUG, INFO, WARNING, ERROR)     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Data Flow Diagram                            │
└─────────────────────────────────────────────────────────────────┘

CWA OpenData API ──┐
                   │
EPA API (optional) ├─► CWAClient ──► Cache (JSON) ──┐
                   │     ▲                          │
Hardware Sensors ──┘     │                          │
                         │ Retry on failure          │
                         └──────────────────────────┘
                                                     │
                                                     ▼
                                              DataProcessor
                                                     │
                                                     ▼
                                              DisplayManager
                                                     │
                                                     ▼
                                              AnimationEngine
                                                     │
                                                     ▼
                                            MAX7219 LED Matrix
                                            (8x8 Display)

┌─────────────────────────────────────────────────────────────────┐
│                    Priority System                               │
└─────────────────────────────────────────────────────────────────┘

Level 1 (Urgent)         Level 2 (Important)      Level 3 (Normal)
━━━━━━━━━━━━━━━          ━━━━━━━━━━━━━━━━━━       ━━━━━━━━━━━━━━━
• Earthquake (M≥4.0)     • Strong Wind Alert      • Weather Forecast
• Typhoon Warning        • Temperature Warning    • Current Weather
• Heavy Rain Alert       • UV Warning             • Temperature
━━━━━━━━━━━━━━━          ━━━━━━━━━━━━━━━━━━       • Humidity
Duration: 60-120s        Duration: 30s            Duration: 15-20s
Animation: Shake         Animation: Blink         Animation: Smooth
Interrupts: Yes          Interrupts: Partial      Interrupts: No

┌─────────────────────────────────────────────────────────────────┐
│                    Update Schedule                               │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────┬──────────────┬─────────────┐
│   Data Source    │ Update Freq  │  Cache Time  │   Priority  │
├──────────────────┼──────────────┼──────────────┼─────────────┤
│ Earthquake       │   5 minutes  │   5 minutes  │   Level 1   │
│ Weather Alerts   │  10 minutes  │  10 minutes  │   Level 1-2 │
│ Observation      │  10 minutes  │  10 minutes  │   Level 3   │
│ Weather Forecast │  30 minutes  │  30 minutes  │   Level 3   │
│ UV Index         │  60 minutes  │  60 minutes  │   Level 3   │
└──────────────────┴──────────────┴──────────────┴─────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Configuration Files                            │
└─────────────────────────────────────────────────────────────────┘

config.py                    Required configuration
├── WeatherAPI               CWA authorization token
├── DisplayConfig (opt)      Display settings
└── AdvancedConfig (opt)     Advanced settings

config.example.py            Template with all options
FEATURES.md                  Feature documentation
API_GUIDE.md                 API integration guide
CHANGELOG.md                 Version history
README.md                    Main documentation

┌─────────────────────────────────────────────────────────────────┐
│                     File Structure                               │
└─────────────────────────────────────────────────────────────────┘

8x8_desktopWeather/
├── config.py                    # User configuration
├── main.py                      # Enhanced main program
├── Weather.py                   # Original program (v1.0)
├── install.sh                   # Installation script
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git exclusions
│
├── src/                         # Modular source code
│   ├── __init__.py
│   ├── api/                     # API clients
│   │   ├── __init__.py
│   │   ├── cwa_client.py        # CWA/EPA API client
│   │   └── data_processor.py    # Data processing
│   ├── display/                 # Display control
│   │   ├── __init__.py
│   │   ├── icons.py             # Icon library
│   │   ├── animations.py        # Animation engine
│   │   └── display_manager.py   # Display manager
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── logger.py            # Logging
│       └── scheduler.py         # Background scheduler
│
├── data/                        # Data directory
│   └── cache/                   # API response cache
│       ├── weather_forecast.json
│       ├── observation.json
│       ├── earthquake.json
│       └── alerts.json
│
├── tests/                       # Test suite
│   └── test_components.py       # Component tests
│
└── docs/                        # Documentation
    ├── README.md                # Main documentation
    ├── FEATURES.md              # Feature guide
    ├── API_GUIDE.md             # API integration guide
    ├── CHANGELOG.md             # Version history
    └── config.example.py        # Configuration template

┌─────────────────────────────────────────────────────────────────┐
│                    Hardware Connection                           │
└─────────────────────────────────────────────────────────────────┘

Raspberry Pi                    MAX7219 LED Matrix
┌──────────┐                    ┌──────────┐
│          │                    │  8x8 LED │
│    GPIO  ├────────────────────┤   Matrix │
│          │  SPI Connection    │          │
│  MOSI ───┼────────────────────┤ DIN      │
│  CLK  ───┼────────────────────┤ CLK      │
│  CE0  ───┼────────────────────┤ CS       │
│  3.3V ───┼────────────────────┤ VCC      │
│  GND  ───┼────────────────────┤ GND      │
└──────────┘                    └──────────┘

Note: Enable SPI via raspi-config before use
```

## Component Interaction Flow

```
1. Startup
   main.py → Initialize Device → Initialize CWAClient → Initialize DisplayManager
                                                      → Initialize Scheduler

2. Normal Operation
   Scheduler (Background) ──► CWAClient.get_weather_forecast()
                          │
                          ├──► CWAClient.get_earthquake_report()
                          │
                          └──► CWAClient.get_observation_data()
                                        │
                                        ▼
                                   DataProcessor
                                        │
                                        ▼
                                   DisplayManager ──► Show on LED

3. Alert Detection
   Scheduler.earthquake_check ──► Recent earthquake detected
                                          │
                                          ▼
                                  Trigger Alert (Priority 1)
                                          │
                                          ▼
                                  Interrupt normal display
                                          │
                                          ▼
                                  AnimationEngine.earthquake_shake()
                                          │
                                          ▼
                                  DisplayManager.scroll_text()
                                          │
                                          ▼
                                  Resume normal operation

4. User Customization
   config.py ──► Update intervals, locations, thresholds
                            │
                            ▼
                    Restart service to apply
```

## Performance Characteristics

```
Resource Usage:
├── CPU: < 10% (idle with background updates)
├── Memory: < 50 MB
├── Network: < 1 MB per API request
└── Storage: < 5 MB (cache)

Response Times:
├── Display Update: < 50ms
├── API Request: 100-500ms
├── Cache Read: < 10ms
└── Animation Frame: 33ms (30 FPS)

Update Frequencies:
├── Display Refresh: 1 Hz (1 time/sec)
├── Earthquake Check: 5 min
├── Observation Update: 10 min
└── Weather Forecast: 30 min
```
