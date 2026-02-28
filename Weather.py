# 8x8 Desktop Weather Display
# Displays weather forecast on an 8x8 LED matrix (MAX7219)

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
import time
import sys
import signal
import logging
import requests
from datetime import datetime, timedelta
from urllib.parse import quote
from config import WeatherAPI
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================
# DISPLAY TIMING CONFIGURATION - 可自行調整以下設定
# ============================================================
BARGRAPH_DURATION = 15      # seconds for bar graph display (秒)
TICKER_DURATION = 20        # seconds for ticker scrolling (秒)
ICON_DURATION = 10          # seconds for icon display (秒)
BARGRAPH_SCAN_SPEED = 0.09  # seconds per scan step in column indicator animation
BLINK_LONG_SECS = 1.5       # seconds for normal bargraph display phase (after scan)
TICKER_SCROLL_SPEED = 0.10  # seconds between ticker scroll steps (slightly faster)
ICON_ANIMATION_SPEED = 0.5  # seconds between icon animation frames
UPDATE_INTERVAL_MINS = 40   # minutes between weather data updates
DEMO_MODE = False            # set True to enable debug/demo display mode
# ============================================================

# ============================================================
# LOCATION & API CONFIGURATION - 可自行調整地點設定
# ============================================================
LOCATION_NAME = '大安區'                    # 地點名稱 (Location name)
API_DATASET_TEMP = 'F-D0047-061'            # 溫度 API dataset ID
API_DATASET_POP = 'F-D0047-091'             # 降雨機率 API dataset ID
API_DATASET_POP_ALT = 'F-D0047-091'         # 備用降雨機率 API dataset ID
API_TIMEOUT = 10                             # API request timeout (seconds)
API_BASE_URL = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore'
# ============================================================

# ============================================================
# TEMPERATURE DISPLAY RANGE - 溫度顯示範圍設定
# ============================================================
TEMP_DISPLAY_MIN = 12       # minimum temperature for LED level mapping (°C)
TEMP_DISPLAY_MAX = 33       # maximum temperature for LED level mapping (°C)
# ============================================================

# ============================================================
# BRIGHTNESS CONFIGURATION - 亮度設定
# ============================================================
NIGHT_MODE_START = 0        # night mode start hour (24h format)
NIGHT_MODE_END = 6          # night mode end hour (24h format)
BRIGHTNESS_NIGHT = 8        # brightness during night mode (0-255)
BRIGHTNESS_DAY = 30         # brightness during daytime (0-255)
MAX_CONTRAST = 255          # maximum contrast value for LED
# ============================================================

# ============================================================
# DEFAULT FALLBACK DATA - 預設資料 (when API fails)
# ============================================================
DEFAULT_TEMPERATURE = 22    # default temperature (°C)
DEFAULT_POP = 20            # default precipitation probability (%)
DEFAULT_T_RAW = [DEFAULT_TEMPERATURE] * 8
DEFAULT_POP_RAW = [DEFAULT_POP] * 4
DEFAULT_T_LEVELS = [4] * 8
DEFAULT_POP_LEVELS = [0] * 8
DEFAULT_POP_LIST = ['20', '30', '25', '35', '40', '30', '25', '20']
# ============================================================

# Display mode constants
MODE_BARGRAPH = 0
MODE_TICKER = 1
MODE_ICON = 2
MODE_DEMO = 3               # demo/debug mode (only active when DEMO_MODE = True)

# Mode duration mapping (seconds)
MODE_DURATIONS = {
    MODE_BARGRAPH: BARGRAPH_DURATION,
    MODE_TICKER: TICKER_DURATION,
    MODE_ICON: ICON_DURATION,
    MODE_DEMO: TICKER_DURATION,
}

# Mode name strings for logging
MODE_NAMES = ['BARGRAPH', 'TICKER', 'ICON', 'DEMO']

# Number of carousel modes
NUM_MODES = 4 if DEMO_MODE else 3

# Precipitation field name lookup priority
POP_FIELD_NAMES = ['PoP6h', 'PoP', 'ProbabilityOfPrecipitation', 'Precipitation']

# 3x5 pixel font for digit display
DIGIT_FONT = {
    '0': [[1,1,1],[1,0,1],[1,0,1],[1,0,1],[1,1,1]],
    '1': [[0,1,0],[1,1,0],[0,1,0],[0,1,0],[1,1,1]],
    '2': [[1,1,1],[0,0,1],[1,1,1],[1,0,0],[1,1,1]],
    '3': [[1,1,1],[0,0,1],[1,1,1],[0,0,1],[1,1,1]],
    '4': [[1,0,1],[1,0,1],[1,1,1],[0,0,1],[0,0,1]],
    '5': [[1,1,1],[1,0,0],[1,1,1],[0,0,1],[1,1,1]],
    '6': [[1,1,1],[1,0,0],[1,1,1],[1,0,1],[1,1,1]],
    '7': [[1,1,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1]],
    '8': [[1,1,1],[1,0,1],[1,1,1],[1,0,1],[1,1,1]],
    '9': [[1,1,1],[1,0,1],[1,1,1],[0,0,1],[1,1,1]],
    ' ': [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],
    '°': [[1,1,0],[1,1,0],[0,0,0],[0,0,0],[0,0,0]],
    '%': [[1,0,1],[0,0,1],[0,1,0],[1,0,0],[1,0,1]],
    '-': [[0,0,0],[0,0,0],[1,1,1],[0,0,0],[0,0,0]],
    ':': [[0,0,0],[0,1,0],[0,0,0],[0,1,0],[0,0,0]],
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _format_hour(dt):
    """Format hour from datetime as zero-padded string (e.g., '08')."""
    return dt.strftime('%H')


def _build_api_url(dataset_id, auth_token, element_name, date_from, hour_from, date_to, hour_to):
    """Build a CWA weather API URL with the given parameters."""
    location_encoded = quote(LOCATION_NAME)
    return (
        f'{API_BASE_URL}/{dataset_id}'
        f'?Authorization={auth_token}'
        f'&limit=8'
        f'&LocationName={location_encoded}'
        f'&elementName={element_name}'
        f'&timeFrom={date_from}T{hour_from}%3A00%3A00'
        f'&timeTo={date_to}T{hour_to}%3A00%3A00'
    )


def _validate_api_response(data):
    """Validate CWA API response structure. Returns True if valid."""
    return (
        data.get("success") == "true"
        and "records" in data
        and "Locations" in data["records"]
        and len(data["records"]["Locations"]) > 0
        and "Location" in data["records"]["Locations"][0]
        and len(data["records"]["Locations"][0]["Location"]) > 0
    )


def _extract_weather_data(data):
    """Extract weather element time data from validated API response."""
    return data["records"]["Locations"][0]["Location"][0]["WeatherElement"][0]["Time"]


def _extract_pop_value(element_value):
    """Extract precipitation probability value from an element value dict.
    
    Returns the precipitation value as string, or None if not found.
    """
    for field_name in POP_FIELD_NAMES:
        if field_name in element_value:
            return element_value[field_name]
    return None


def _validate_config():
    """Validate and return the authorization token, or exit with instructions."""
    auth = WeatherAPI['Authorization'].strip()
    if not auth or auth == 'CWA-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX':
        logger.error("=" * 60)
        logger.error("🌤️  Smart Weather Display Setup Required")
        logger.error("=" * 60)
        logger.error("Please configure your CWA authorization token:")
        logger.error("1. Visit: https://opendata.cwa.gov.tw/user/authkey")
        logger.error("2. Get your authorization token")
        logger.error("3. Edit config.py and add your token:")
        logger.error("   WeatherAPI = {'Authorization': 'YOUR_TOKEN_HERE'}")
        logger.error("=" * 60)

        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
        hour_str = _format_hour(now)
        temp_url = _build_api_url(API_DATASET_TEMP, 'YOUR_TOKEN_HERE', 'T', today, hour_str, tomorrow, hour_str)
        pop_url = _build_api_url(API_DATASET_POP, 'YOUR_TOKEN_HERE', 'PoP6h', today, hour_str, tomorrow, hour_str)
        logger.info("🔗 Example API URLs:")
        logger.info("Temperature API: %s", temp_url)
        logger.info("Precipitation API: %s", pop_url)
        logger.error("=" * 60)
        sys.exit(1)
    return auth


# ============================================================
# CORE FUNCTIONS
# ============================================================

def get_weather_forecast(today_date):
    """Fetch weather forecast from CWA API.
    
    Args:
        today_date: datetime object for the forecast date.
    
    Returns:
        Tuple of (temperature_levels, pop_levels, raw_temperatures, raw_pop_values).
    """
    today = today_date.strftime('%Y-%m-%d')
    tomorrow = (today_date + timedelta(days=1)).strftime('%Y-%m-%d')
    hour_str = _format_hour(today_date)
    logger.info("%s ~ %s (hour: %s)", today, tomorrow, hour_str)
    
    # Build API URLs using helper
    url_temp = _build_api_url(API_DATASET_TEMP, Authorization, 'T', today, hour_str, tomorrow, hour_str)
    url_pop = _build_api_url(API_DATASET_POP, Authorization, 'PoP6h', today, hour_str, tomorrow, hour_str)
    url_pop_alt = _build_api_url(API_DATASET_POP_ALT, Authorization, 'PoP', today, hour_str, tomorrow, hour_str)
    
    try:
        # Fetch temperature data
        response_temp = requests.get(url_temp, verify=False, timeout=API_TIMEOUT)
        response_temp.raise_for_status()
        data_temp = response_temp.json()
        
        if _validate_api_response(data_temp):
            T_data = _extract_weather_data(data_temp)
            logger.info("Temperature data: %s", T_data)
        else:
            logger.warning("Temperature API returned empty data, using fallback")
            T_data = [{'ElementValue': [{'Temperature': str(DEFAULT_TEMPERATURE)}]} for _ in range(8)]
        
        # Fetch precipitation data
        response_pop = requests.get(url_pop, verify=False, timeout=API_TIMEOUT)
        response_pop.raise_for_status()
        data_pop = response_pop.json()
        logger.debug("Full PoP API response: %s", data_pop)
        
        # Validate and extract precipitation data
        pop_data = None
        if _validate_api_response(data_pop):
            try:
                pop_data = _extract_weather_data(data_pop)
                logger.info("Precipitation data: %s", pop_data)
                
                # Verify data actually contains precipitation fields
                has_pop = any(
                    _extract_pop_value(d['ElementValue'][0]) is not None
                    for d in pop_data
                )
                
                if not has_pop:
                    logger.warning("PoP6h API returned no precipitation data, trying alternative...")
                    pop_data = None
                    
            except (KeyError, IndexError) as e:
                logger.error("Error accessing precipitation data: %s", e)
                pop_data = None
        else:
            logger.warning("PoP API returned empty data, trying alternative...")
            pop_data = None
        
        # Try alternative API if primary failed
        if pop_data is None:
            try:
                response_pop_alt = requests.get(url_pop_alt, verify=False, timeout=API_TIMEOUT)
                response_pop_alt.raise_for_status()
                data_pop_alt = response_pop_alt.json()
                logger.debug("Alternative PoP API response: %s", data_pop_alt)
                
                if _validate_api_response(data_pop_alt):
                    pop_data = _extract_weather_data(data_pop_alt)
                    logger.info("Alternative precipitation data: %s", pop_data)
                else:
                    logger.warning("Alternative API also returned empty data")
            except (requests.RequestException, ValueError) as e:
                logger.error("Alternative PoP API error: %s", e)
        
        # Extract temperature values
        temp_values = []
        for d in T_data:
            ev = d['ElementValue'][0]
            if 'Temperature' in ev:
                temp_values.append(ev['Temperature'])
            else:
                temp_values.append(str(DEFAULT_TEMPERATURE))
        logger.info("Temperature values: %s", temp_values)
        
        # Extract precipitation values
        pop_values = []
        if pop_data:
            logger.debug("Raw PoP data structure: %s", [d['ElementValue'] for d in pop_data])
            
            for d in pop_data:
                element_value = d['ElementValue'][0]
                pop_val = _extract_pop_value(element_value)
                
                if pop_val is not None:
                    pop_values.append(pop_val)
                    logger.debug("Found precipitation data: %s", pop_val)
                elif 'Temperature' in element_value:
                    # API returned temperature data instead of precipitation
                    logger.warning("API returned temperature instead of PoP: %s", element_value)
                    temp_value = int(element_value['Temperature'])
                    if temp_value > 30:
                        pop_values.append('20')
                    elif temp_value > 25:
                        pop_values.append('30')
                    elif temp_value > 20:
                        pop_values.append('40')
                    else:
                        pop_values.append('60')
                else:
                    logger.warning("No precipitation data in %s, using default 0", element_value)
                    pop_values.append('0')
        else:
            logger.warning("No precipitation data available, using fallback values")
            pop_values = list(DEFAULT_POP_LIST)
        
        logger.info("Precipitation values: %s", pop_values)
        
        return (
            temperature_to_led_levels(temp_values),
            PoP_to_led_levels(pop_values),
            [int(t) for t in temp_values],
            [int(p) for p in pop_values],
        )
        
    except requests.RequestException as e:
        logger.error("Network error fetching weather data: %s", e)
        return DEFAULT_T_LEVELS[:], DEFAULT_POP_LEVELS[:], DEFAULT_T_RAW[:], DEFAULT_POP_RAW[:]
    except (ValueError, KeyError, IndexError) as e:
        logger.error("Data parsing error: %s", e)
        return DEFAULT_T_LEVELS[:], DEFAULT_POP_LEVELS[:], DEFAULT_T_RAW[:], DEFAULT_POP_RAW[:]
    except Exception as e:
        logger.error("Unexpected error fetching weather data: %s", e)
        return DEFAULT_T_LEVELS[:], DEFAULT_POP_LEVELS[:], DEFAULT_T_RAW[:], DEFAULT_POP_RAW[:]



def temperature_to_led_levels(temperature):
    """Convert temperature values to 8 LED levels (0-7) for the 8x8 matrix.
    
    Args:
        temperature: List of temperature values (strings or ints).
    
    Returns:
        List of LED level values (0-7).
    """
    temperature = [int(t) for t in temperature]
    levels = []
    temp_range = TEMP_DISPLAY_MAX - TEMP_DISPLAY_MIN
    if temp_range == 0:
        return [4] * len(temperature)
    for t in temperature:
        t = max(TEMP_DISPLAY_MIN, min(TEMP_DISPLAY_MAX, t))
        level = round(7 * (t - TEMP_DISPLAY_MIN) / temp_range)
        levels.append(level)
    return levels


def PoP_to_led_levels(pop_values):
    """Convert precipitation probability to LED indicator levels.
    
    Each PoP value produces 2 LED columns:
    - >=80%: both lit (high probability)
    - >=60%: first lit (medium-high)
    - >=40%: second lit (medium)
    - <40%:  both off (low probability)
    
    Args:
        pop_values: List of precipitation probability values (strings or ints).
    
    Returns:
        List of LED indicator values (0 or 1).
    """
    try:
        pop_ints = [int(p) for p in pop_values]
        levels = []
        for p in pop_ints:
            if p >= 80:
                levels.extend([1, 1])
            elif p >= 60:
                levels.extend([1, 0])
            elif p >= 40:
                levels.extend([0, 1])
            else:
                levels.extend([0, 0])
        return levels
    except (ValueError, TypeError) as e:
        logger.error("Error in PoP_to_led_levels: %s", e)
        return DEFAULT_POP_LEVELS[:]

# initialize SPI interface for the LED matrix
serial = spi(port=0, device=0)
device = max7219(serial, cascaded=1, block_orientation=0, rotate=0)


def START_LOGO():
    """Cute startup animation with smiley faces."""
    smiley_animations = [
        lambda draw: draw_happy_smiley(draw, 0),
        lambda draw: draw_winking_smiley(draw, 0),
        lambda draw: draw_big_smile_smiley(draw, 0),
        lambda draw: draw_excited_smiley(draw, 0),
    ]
    
    for smiley_func in smiley_animations:
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            smiley_func(draw)
        time.sleep(0.8)
    
    # Fade out/in effect
    for intensity in range(15, 0, -1):
        device.contrast(min(intensity * 16, MAX_CONTRAST))
        time.sleep(0.05)
    for intensity in range(16):
        device.contrast(min(intensity * 16, MAX_CONTRAST))
        time.sleep(0.05)


def shift_array(data, index):
    """Shift array by index positions for display alignment.
    
    Args:
        data: List of values to shift.
        index: Number of positions to shift.
    
    Returns:
        Shifted list, or empty list if input is empty.
    """
    if not data:
        return []
    start = 8 - index
    end = start + 8
    return data[start:end] + data[:start] + data[end:]


def calculate_output(hour):
    """Map hour (0-23) to temperature column index (0-7).
    
    Each column represents a 3-hour forecast period:
    Col 0: 01-03h, Col 1: 04-06h, Col 2: 07-09h, Col 3: 10-12h,
    Col 4: 13-15h, Col 5: 16-18h, Col 6: 19-21h, Col 7: 22-00h.
    """
    if hour == 0:
        return 7
    return ((hour - 1) // 3) % 8


def calculate_output_forPoP(hour):
    """Map hour (0-23) to precipitation column index (1,3,5,7).
    
    Each column pair represents a 6-hour forecast period:
    Col 1: 01-06h, Col 3: 07-12h, Col 5: 13-18h, Col 7: 19-00h.
    """
    if hour == 0:
        return 7
    return ((hour - 1) // 6) * 2 + 1


def get_brightness_for_time(hour):
    """Return brightness level based on time of day.
    
    Args:
        hour: Hour in 24h format (0-23).
    
    Returns:
        Brightness value (0-255).
    """
    if NIGHT_MODE_START <= hour < NIGHT_MODE_END:
        return BRIGHTNESS_NIGHT
    return BRIGHTNESS_DAY

def draw_happy_smiley(draw, frame):
    """Draw a super cute happy smiley face"""
    # Bigger, rounder face outline with more personality
    draw.ellipse([(0, 0), (7, 7)], outline="white", fill="white")
    # Bigger, more expressive eyes with sparkle
    draw.point((2, 1), fill="black")
    draw.point((5, 1), fill="black")
    draw.point((2, 2), fill="black")
    draw.point((5, 2), fill="black")
    # Eye sparkles for extra cuteness
    draw.point((1, 0), fill="white")
    draw.point((6, 0), fill="white")
    # Bigger, more cheerful smile
    draw.point((1, 4), fill="black")
    draw.point((2, 5), fill="black")
    draw.point((3, 6), fill="black")
    draw.point((4, 6), fill="black")
    draw.point((5, 5), fill="black")
    draw.point((6, 4), fill="black")
    # Cheek dimples for extra cuteness
    draw.point((0, 3), fill="white")
    draw.point((7, 3), fill="white")

def draw_winking_smiley(draw, frame):
    """Draw a super cute winking smiley face"""
    # Bigger, rounder face outline
    draw.ellipse([(0, 0), (7, 7)], outline="white", fill="white")
    # Left eye (big and open with sparkle)
    draw.point((2, 1), fill="black")
    draw.point((2, 2), fill="black")
    draw.point((1, 0), fill="white")  # sparkle
    # Right eye (cute winking - closed with eyelash)
    draw.point((5, 1), fill="white")
    draw.point((5, 2), fill="black")  # eyelash
    draw.point((4, 2), fill="black")  # eyelash
    draw.point((6, 2), fill="black")  # eyelash
    # Playful mouth
    draw.point((1, 4), fill="black")
    draw.point((2, 5), fill="black")
    draw.point((3, 6), fill="black")
    draw.point((4, 6), fill="black")
    draw.point((5, 5), fill="black")
    draw.point((6, 4), fill="black")
    # Cheek dimples
    draw.point((0, 3), fill="white")
    draw.point((7, 3), fill="white")

def draw_big_smile_smiley(draw, frame):
    """Draw a super cute big smile smiley face"""
    # Bigger, rounder face outline
    draw.ellipse([(0, 0), (7, 7)], outline="white", fill="white")
    # Bigger, more excited eyes
    draw.point((2, 1), fill="black")
    draw.point((5, 1), fill="black")
    draw.point((2, 2), fill="black")
    draw.point((5, 2), fill="black")
    # Eye sparkles for excitement
    draw.point((1, 0), fill="white")
    draw.point((6, 0), fill="white")
    draw.point((0, 1), fill="white")
    draw.point((7, 1), fill="white")
    # HUGE happy smile with teeth
    draw.point((0, 4), fill="black")
    draw.point((1, 5), fill="black")
    draw.point((2, 6), fill="black")
    draw.point((3, 7), fill="black")
    draw.point((4, 7), fill="black")
    draw.point((5, 6), fill="black")
    draw.point((6, 5), fill="black")
    draw.point((7, 4), fill="black")
    # Teeth showing
    draw.point((3, 6), fill="white")
    draw.point((4, 6), fill="white")
    # Cheek dimples
    draw.point((0, 3), fill="white")
    draw.point((7, 3), fill="white")

def draw_excited_smiley(draw, frame):
    """Draw a super excited smiley face with animated sparkles"""
    # Bigger, rounder face outline
    draw.ellipse([(0, 0), (7, 7)], outline="white", fill="white")
    # HUGE excited eyes with sparkle animation
    draw.point((2, 1), fill="black")
    draw.point((5, 1), fill="black")
    draw.point((2, 2), fill="black")
    draw.point((5, 2), fill="black")
    draw.point((2, 3), fill="black")
    draw.point((5, 3), fill="black")
    # Animated eye sparkles
    sparkle_frame = frame % 4
    if sparkle_frame == 0:
        draw.point((1, 0), fill="white")
        draw.point((6, 0), fill="white")
        draw.point((0, 1), fill="white")
        draw.point((7, 1), fill="white")
    elif sparkle_frame == 1:
        draw.point((0, 0), fill="white")
        draw.point((7, 0), fill="white")
        draw.point((1, 1), fill="white")
        draw.point((6, 1), fill="white")
    elif sparkle_frame == 2:
        draw.point((0, 2), fill="white")
        draw.point((7, 2), fill="white")
        draw.point((1, 3), fill="white")
        draw.point((6, 3), fill="white")
    else:
        draw.point((1, 2), fill="white")
        draw.point((6, 2), fill="white")
        draw.point((0, 3), fill="white")
        draw.point((7, 3), fill="white")
    # Excited open mouth with tongue
    draw.point((2, 4), fill="black")
    draw.point((5, 4), fill="black")
    draw.point((3, 5), fill="black")
    draw.point((4, 5), fill="black")
    draw.point((3, 6), fill="black")  # tongue
    draw.point((4, 6), fill="black")  # tongue
    # Animated sparkles around the face
    sparkle_positions = [(0, 0), (7, 0), (0, 7), (7, 7), (0, 3), (7, 3), (3, 0), (4, 0)]
    for i, (x, y) in enumerate(sparkle_positions):
        if (frame + i) % 3 == 0:
            draw.point((x, y), fill="white")

def show_data_update_animation():
    """Simple minimal update indicator - horizontal scan line."""
    for x in range(8):
        with canvas(device) as draw:
            draw.point((x, 3), fill="white")
            draw.point((x, 4), fill="white")
        time.sleep(0.08)
    # Clear display
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, fill="black")

def draw_sunny_animation(draw, frame):
    """Draw super cute sunny weather animation - big smiling sun with animated rays and sparkles"""
    # Bigger smiling sun center with face
    draw.ellipse([(1, 1), (6, 6)], outline="white", fill="white")
    # Bigger, more expressive eyes with sparkles
    draw.point((2, 2), fill="black")
    draw.point((5, 2), fill="black")
    draw.point((2, 3), fill="black")
    draw.point((5, 3), fill="black")
    # Eye sparkles for extra cuteness
    sparkle_frame = frame % 4
    if sparkle_frame == 0:
        draw.point((1, 1), fill="white")
        draw.point((6, 1), fill="white")
    elif sparkle_frame == 1:
        draw.point((0, 2), fill="white")
        draw.point((7, 2), fill="white")
    elif sparkle_frame == 2:
        draw.point((1, 3), fill="white")
        draw.point((6, 3), fill="white")
    else:
        draw.point((0, 3), fill="white")
        draw.point((7, 3), fill="white")
    
    # Bigger, more cheerful smile
    draw.point((1, 4), fill="black")
    draw.point((2, 5), fill="black")
    draw.point((3, 6), fill="black")
    draw.point((4, 6), fill="black")
    draw.point((5, 5), fill="black")
    draw.point((6, 4), fill="black")
    # Cheek dimples for extra cuteness
    draw.point((0, 3), fill="white")
    draw.point((7, 3), fill="white")
    
    # More prominent animated rays with pulsing effect
    ray_frame = frame % 6
    if ray_frame == 0 or ray_frame == 1:
        # Very long rays
        draw.point((0, 0), fill="white")
        draw.point((7, 0), fill="white")
        draw.point((0, 7), fill="white")
        draw.point((7, 7), fill="white")
        draw.point((3, 0), fill="white")
        draw.point((4, 0), fill="white")
        draw.point((3, 7), fill="white")
        draw.point((4, 7), fill="white")
        draw.point((0, 3), fill="white")
        draw.point((0, 4), fill="white")
        draw.point((7, 3), fill="white")
        draw.point((7, 4), fill="white")
        # Extra sparkle rays
        draw.point((1, 0), fill="white")
        draw.point((6, 0), fill="white")
        draw.point((1, 7), fill="white")
        draw.point((6, 7), fill="white")
    elif ray_frame == 2 or ray_frame == 3:
        # Medium rays
        draw.point((1, 0), fill="white")
        draw.point((6, 0), fill="white")
        draw.point((1, 7), fill="white")
        draw.point((6, 7), fill="white")
        draw.point((2, 0), fill="white")
        draw.point((5, 0), fill="white")
        draw.point((2, 7), fill="white")
        draw.point((5, 7), fill="white")
        draw.point((0, 2), fill="white")
        draw.point((0, 5), fill="white")
        draw.point((7, 2), fill="white")
        draw.point((7, 5), fill="white")
    else:
        # Short rays
        draw.point((2, 1), fill="white")
        draw.point((5, 1), fill="white")
        draw.point((2, 6), fill="white")
        draw.point((5, 6), fill="white")
        draw.point((1, 2), fill="white")
        draw.point((6, 2), fill="white")
        draw.point((1, 5), fill="white")
        draw.point((6, 5), fill="white")
    
    # Floating sparkles around the sun
    sparkle_positions = [(0, 1), (7, 1), (0, 6), (7, 6), (1, 0), (6, 0), (1, 7), (6, 7)]
    for i, (x, y) in enumerate(sparkle_positions):
        if (frame + i) % 3 == 0:
            draw.point((x, y), fill="white")

def draw_clear_sky_animation(draw, frame):
    """Draw clear sky animation - simple sun with gentle rays"""
    # Simple sun
    draw.ellipse([(2, 2), (5, 5)], outline="white", fill="white")
    # Happy face
    draw.point((2, 2), fill="black")  # eye
    draw.point((5, 2), fill="black")  # eye
    draw.point((2, 3), fill="black")  # eye
    draw.point((5, 3), fill="black")  # eye
    # Smile
    draw.point((2, 4), fill="black")
    draw.point((3, 4), fill="black")
    draw.point((4, 4), fill="black")
    draw.point((5, 4), fill="black")
    
    # Gentle rays
    ray_frame = frame % 4
    if ray_frame < 2:
        draw.point((0, 0), fill="white")
        draw.point((7, 0), fill="white")
        draw.point((0, 7), fill="white")
        draw.point((7, 7), fill="white")
        draw.point((3, 0), fill="white")
        draw.point((4, 0), fill="white")
        draw.point((3, 7), fill="white")
        draw.point((4, 7), fill="white")
        draw.point((0, 3), fill="white")
        draw.point((0, 4), fill="white")
        draw.point((7, 3), fill="white")
        draw.point((7, 4), fill="white")

def draw_cloudy_animation(draw, frame):
    """Draw super cute cloudy weather animation - big fluffy moving clouds with expressive faces"""
    offset = frame % 3
    # Bigger Cloud 1 with face
    draw.point((0+offset, 2), fill="white")
    draw.point((1+offset, 1), fill="white")
    draw.point((2+offset, 0), fill="white")
    draw.point((3+offset, 0), fill="white")
    draw.point((4+offset, 1), fill="white")
    draw.point((5+offset, 2), fill="white")
    draw.point((1+offset, 2), fill="white")
    draw.point((2+offset, 1), fill="white")
    draw.point((3+offset, 1), fill="white")
    draw.point((4+offset, 2), fill="white")
    
    # Cloud 1 face with more personality
    if offset == 0:
        draw.point((2, 0), fill="black")  # eye
        draw.point((3, 0), fill="black")  # eye
        draw.point((2, 1), fill="black")  # eye
        draw.point((3, 1), fill="black")  # eye
        # Happy smile
        draw.point((1, 2), fill="black")  # mouth
        draw.point((4, 2), fill="black")  # mouth
        # Cheek blush
        draw.point((0, 1), fill="white")
        draw.point((5, 1), fill="white")
    elif offset == 1:
        draw.point((3, 0), fill="black")  # eye
        draw.point((4, 0), fill="black")  # eye
        draw.point((3, 1), fill="black")  # eye
        draw.point((4, 1), fill="black")  # eye
        # Happy smile
        draw.point((2, 2), fill="black")  # mouth
        draw.point((5, 2), fill="black")  # mouth
        # Cheek blush
        draw.point((1, 1), fill="white")
        draw.point((6, 1), fill="white")
    else:
        draw.point((4, 0), fill="black")  # eye
        draw.point((5, 0), fill="black")  # eye
        draw.point((4, 1), fill="black")  # eye
        draw.point((5, 1), fill="black")  # eye
        # Happy smile
        draw.point((3, 2), fill="black")  # mouth
        draw.point((6, 2), fill="black")  # mouth
        # Cheek blush
        draw.point((2, 1), fill="white")
        draw.point((7, 1), fill="white")
    
    # Bigger Cloud 2 with face
    draw.point((1, 5), fill="white")
    draw.point((2, 4), fill="white")
    draw.point((3, 3), fill="white")
    draw.point((4, 3), fill="white")
    draw.point((5, 4), fill="white")
    draw.point((6, 5), fill="white")
    draw.point((2, 5), fill="white")
    draw.point((3, 4), fill="white")
    draw.point((4, 4), fill="white")
    draw.point((5, 5), fill="white")
    
    # Cloud 2 face with more expression
    draw.point((3, 3), fill="black")  # eye
    draw.point((4, 3), fill="black")  # eye
    draw.point((3, 4), fill="black")  # eye
    draw.point((4, 4), fill="black")  # eye
    # Gentle smile
    draw.point((2, 4), fill="black")  # mouth
    draw.point((5, 4), fill="black")  # mouth
    draw.point((3, 5), fill="black")  # mouth
    draw.point((4, 5), fill="black")  # mouth
    # Cheek blush
    draw.point((1, 4), fill="white")
    draw.point((6, 4), fill="white")
    
    # Floating cloud particles for extra cuteness
    particle_frame = frame % 4
    if particle_frame == 0:
        draw.point((0, 0), fill="white")
        draw.point((7, 0), fill="white")
        draw.point((0, 6), fill="white")
        draw.point((7, 6), fill="white")
    elif particle_frame == 1:
        draw.point((1, 0), fill="white")
        draw.point((6, 0), fill="white")
        draw.point((1, 6), fill="white")
        draw.point((6, 6), fill="white")
    elif particle_frame == 2:
        draw.point((2, 0), fill="white")
        draw.point((5, 0), fill="white")
        draw.point((2, 6), fill="white")
        draw.point((5, 6), fill="white")
    else:
        draw.point((3, 0), fill="white")
        draw.point((4, 0), fill="white")
        draw.point((3, 6), fill="white")
        draw.point((4, 6), fill="white")

def draw_light_rain_animation(draw, frame):
    """Draw cute light rain animation - gentle rain with happy cloud"""
    # Happy rain cloud
    draw.point((0, 0), fill="white")
    draw.point((1, 0), fill="white")
    draw.point((2, 0), fill="white")
    draw.point((3, 0), fill="white")
    draw.point((4, 0), fill="white")
    draw.point((5, 0), fill="white")
    draw.point((6, 0), fill="white")
    draw.point((7, 0), fill="white")
    draw.point((1, 1), fill="white")
    draw.point((2, 1), fill="white")
    draw.point((3, 1), fill="white")
    draw.point((4, 1), fill="white")
    draw.point((5, 1), fill="white")
    draw.point((6, 1), fill="white")
    draw.point((2, 2), fill="white")
    draw.point((3, 2), fill="white")
    draw.point((4, 2), fill="white")
    draw.point((5, 2), fill="white")
    
    # Happy cloud face
    draw.point((2, 0), fill="black")  # eye
    draw.point((5, 0), fill="black")  # eye
    draw.point((2, 1), fill="black")  # eye
    draw.point((5, 1), fill="black")  # eye
    # Happy smile
    draw.point((2, 2), fill="black")
    draw.point((3, 2), fill="black")
    draw.point((4, 2), fill="black")
    draw.point((5, 2), fill="black")
    
    # Gentle rain drops
    rain_frame = frame % 4
    for x in [1, 3, 5]:
        y = 3 + rain_frame
        if y < 8:
            draw.point((x, y), fill="white")
            if y < 7:
                draw.point((x, y+1), fill="white")
    
    # Light splash effects
    if rain_frame % 2 == 0:
        draw.point((1, 7), fill="white")
        draw.point((3, 7), fill="white")
        draw.point((5, 7), fill="white")

def draw_rainy_animation(draw, frame):
    """Draw super vivid rainy weather animation - instantly recognizable as rain forecast with cute details"""
    # Bigger, more prominent rain cloud with sad face
    # Cloud top layer
    draw.point((0, 0), fill="white")
    draw.point((1, 0), fill="white")
    draw.point((2, 0), fill="white")
    draw.point((3, 0), fill="white")
    draw.point((4, 0), fill="white")
    draw.point((5, 0), fill="white")
    draw.point((6, 0), fill="white")
    draw.point((7, 0), fill="white")
    # Cloud middle layer
    draw.point((0, 1), fill="white")
    draw.point((1, 1), fill="white")
    draw.point((2, 1), fill="white")
    draw.point((3, 1), fill="white")
    draw.point((4, 1), fill="white")
    draw.point((5, 1), fill="white")
    draw.point((6, 1), fill="white")
    draw.point((7, 1), fill="white")
    # Cloud bottom layer
    draw.point((1, 2), fill="white")
    draw.point((2, 2), fill="white")
    draw.point((3, 2), fill="white")
    draw.point((4, 2), fill="white")
    draw.point((5, 2), fill="white")
    draw.point((6, 2), fill="white")
    
    # Sad cloud face - more expressive with tears
    draw.point((2, 0), fill="black")  # left eye
    draw.point((5, 0), fill="black")  # right eye
    draw.point((2, 1), fill="black")  # left eye
    draw.point((5, 1), fill="black")  # right eye
    # Sad frowning mouth
    draw.point((1, 2), fill="black")  # sad mouth left
    draw.point((6, 2), fill="black")  # sad mouth right
    draw.point((2, 2), fill="black")  # sad mouth center
    draw.point((3, 2), fill="black")  # sad mouth center
    draw.point((4, 2), fill="black")  # sad mouth center
    draw.point((5, 2), fill="black")  # sad mouth center
    
    # Animated tears from cloud
    tear_frame = frame % 3
    if tear_frame == 0:
        draw.point((2, 2), fill="white")  # tear
        draw.point((5, 2), fill="white")  # tear
    elif tear_frame == 1:
        draw.point((2, 3), fill="white")  # tear
        draw.point((5, 3), fill="white")  # tear
    else:
        draw.point((2, 4), fill="white")  # tear
        draw.point((5, 4), fill="white")  # tear
    
    # MUCH more prominent and realistic falling rain with multiple layers
    # Fast rain drops (heavy rain)
    rain_speed1 = (frame % 2)  # Very fast
    rain_speed2 = (frame % 3)  # Medium fast
    rain_speed3 = (frame % 4)  # Medium
    rain_speed4 = (frame % 5)  # Slow
    
    # Heavy rain drops - multiple columns with different speeds
    for x in [0, 2, 4, 6]:
        y = 3 + rain_speed1
        if y < 8:
            draw.point((x, y), fill="white")
            if y < 7:  # Make rain drops longer
                draw.point((x, y+1), fill="white")
    
    for x in [1, 3, 5, 7]:
        y = 4 + rain_speed2
        if y < 8:
            draw.point((x, y), fill="white")
            if y < 7:
                draw.point((x, y+1), fill="white")
    
    # Additional rain drops for density
    for x in [0, 1, 6, 7]:
        y = 5 + rain_speed3
        if y < 8:
            draw.point((x, y), fill="white")
    
    for x in [2, 3, 4, 5]:
        y = 6 + rain_speed4
        if y < 8:
            draw.point((x, y), fill="white")
    
    # Rain splash effects at bottom with more detail
    splash_frame = frame % 3
    if splash_frame == 0:
        draw.point((1, 7), fill="white")
        draw.point((3, 7), fill="white")
        draw.point((5, 7), fill="white")
        draw.point((7, 7), fill="white")
        # Splash particles
        draw.point((0, 6), fill="white")
        draw.point((2, 6), fill="white")
        draw.point((4, 6), fill="white")
        draw.point((6, 6), fill="white")
    elif splash_frame == 1:
        draw.point((0, 7), fill="white")
        draw.point((2, 7), fill="white")
        draw.point((4, 7), fill="white")
        draw.point((6, 7), fill="white")
        # Splash particles
        draw.point((1, 6), fill="white")
        draw.point((3, 6), fill="white")
        draw.point((5, 6), fill="white")
        draw.point((7, 6), fill="white")
    else:
        draw.point((1, 7), fill="white")
        draw.point((2, 7), fill="white")
        draw.point((5, 7), fill="white")
        draw.point((6, 7), fill="white")
        # Splash particles
        draw.point((0, 6), fill="white")
        draw.point((3, 6), fill="white")
        draw.point((4, 6), fill="white")
        draw.point((7, 6), fill="white")

def draw_thunderstorm_animation(draw, frame):
    """Draw super vivid thunderstorm animation - instantly recognizable as severe weather with dramatic effects"""
    # Massive angry storm cloud
    # Top layer
    draw.point((0, 0), fill="white")
    draw.point((1, 0), fill="white")
    draw.point((2, 0), fill="white")
    draw.point((3, 0), fill="white")
    draw.point((4, 0), fill="white")
    draw.point((5, 0), fill="white")
    draw.point((6, 0), fill="white")
    draw.point((7, 0), fill="white")
    # Middle layer
    draw.point((0, 1), fill="white")
    draw.point((1, 1), fill="white")
    draw.point((2, 1), fill="white")
    draw.point((3, 1), fill="white")
    draw.point((4, 1), fill="white")
    draw.point((5, 1), fill="white")
    draw.point((6, 1), fill="white")
    draw.point((7, 1), fill="white")
    # Bottom layer
    draw.point((1, 2), fill="white")
    draw.point((2, 2), fill="white")
    draw.point((3, 2), fill="white")
    draw.point((4, 2), fill="white")
    draw.point((5, 2), fill="white")
    draw.point((6, 2), fill="white")
    
    # Very angry cloud face with animated eyebrows
    draw.point((2, 0), fill="black")  # angry left eye
    draw.point((5, 0), fill="black")  # angry right eye
    draw.point((2, 1), fill="black")  # angry left eye
    draw.point((5, 1), fill="black")  # angry right eye
    # Angry eyebrows that move
    angry_frame = frame % 4
    if angry_frame < 2:
        draw.point((1, 0), fill="black")  # angry eyebrow left
        draw.point((6, 0), fill="black")  # angry eyebrow right
    else:
        draw.point((0, 0), fill="black")  # angry eyebrow left
        draw.point((7, 0), fill="black")  # angry eyebrow right
    # Angry frowning mouth
    draw.point((1, 2), fill="black")  # angry mouth left
    draw.point((6, 2), fill="black")  # angry mouth right
    draw.point((2, 2), fill="black")  # angry mouth center
    draw.point((3, 2), fill="black")  # angry mouth center
    draw.point((4, 2), fill="black")  # angry mouth center
    draw.point((5, 2), fill="black")  # angry mouth center
    
    # DRAMATIC lightning with multiple bolts and flashing effect
    lightning_frame = frame % 8
    if lightning_frame == 0 or lightning_frame == 1:
        # Main lightning bolt - very bright and jagged
        draw.point((3, 2), fill="white")
        draw.point((2, 3), fill="white")
        draw.point((3, 4), fill="white")
        draw.point((4, 5), fill="white")
        draw.point((3, 6), fill="white")
        draw.point((2, 7), fill="white")
        # Secondary lightning
        draw.point((5, 2), fill="white")
        draw.point((4, 3), fill="white")
        draw.point((5, 4), fill="white")
        draw.point((6, 5), fill="white")
        draw.point((5, 6), fill="white")
        draw.point((4, 7), fill="white")
        # Extra bright flash
        draw.point((3, 3), fill="white")
        draw.point((4, 3), fill="white")
        draw.point((3, 4), fill="white")
        draw.point((4, 4), fill="white")
    elif lightning_frame == 2 or lightning_frame == 3:
        # Different lightning pattern
        draw.point((4, 2), fill="white")
        draw.point((3, 3), fill="white")
        draw.point((4, 4), fill="white")
        draw.point((5, 5), fill="white")
        draw.point((4, 6), fill="white")
        draw.point((3, 7), fill="white")
        # Forked lightning
        draw.point((1, 2), fill="white")
        draw.point((2, 3), fill="white")
        draw.point((1, 4), fill="white")
        draw.point((2, 5), fill="white")
        draw.point((1, 6), fill="white")
        draw.point((0, 7), fill="white")
    elif lightning_frame == 4 or lightning_frame == 5:
        # Multiple lightning bolts across the screen
        draw.point((2, 2), fill="white")
        draw.point((3, 3), fill="white")
        draw.point((2, 4), fill="white")
        draw.point((3, 5), fill="white")
        draw.point((2, 6), fill="white")
        draw.point((1, 7), fill="white")
        # Second bolt
        draw.point((5, 2), fill="white")
        draw.point((6, 3), fill="white")
        draw.point((5, 4), fill="white")
        draw.point((6, 5), fill="white")
        draw.point((5, 6), fill="white")
        draw.point((4, 7), fill="white")
        # Third bolt
        draw.point((4, 2), fill="white")
        draw.point((4, 3), fill="white")
        draw.point((4, 4), fill="white")
        draw.point((4, 5), fill="white")
        draw.point((4, 6), fill="white")
        draw.point((4, 7), fill="white")
    else:
        # Intense flash - all lightning at once
        for x in [1, 2, 3, 4, 5, 6]:
            for y in [2, 3, 4, 5, 6, 7]:
                if (x + y) % 2 == 0:
                    draw.point((x, y), fill="white")
    
    # Heavy rain during thunderstorm with wind effect
    rain_speed = (frame % 2)
    wind_offset = (frame % 3) - 1  # Wind effect
    for x in [0, 2, 4, 6]:
        y = 3 + rain_speed
        if y < 8:
            draw.point((x + wind_offset, y), fill="white")
            if y < 7:
                draw.point((x + wind_offset, y+1), fill="white")
    
    for x in [1, 3, 5, 7]:
        y = 4 + rain_speed
        if y < 8:
            draw.point((x + wind_offset, y), fill="white")
            if y < 7:
                draw.point((x + wind_offset, y+1), fill="white")
    
    # Dramatic splash effects
    splash_frame = frame % 2
    if splash_frame == 0:
        for x in [0, 1, 2, 3, 4, 5, 6, 7]:
            draw.point((x, 7), fill="white")
        # Extra splash particles
        for x in [0, 2, 4, 6]:
            draw.point((x, 6), fill="white")
    else:
        for x in [0, 2, 4, 6]:
            draw.point((x, 7), fill="white")
        for x in [1, 3, 5, 7]:
            draw.point((x, 6), fill="white")

def draw_snowy_animation(draw, frame):
    """Draw cute snowy weather animation - big snowman with falling snow"""
    # Bigger snowman body
    draw.ellipse([(1, 4), (6, 6)], outline="white", fill="white")  # body
    draw.ellipse([(2, 2), (5, 4)], outline="white", fill="white")  # head
    
    # Snowman face with more personality
    draw.point((2, 2), fill="black")  # eye
    draw.point((5, 2), fill="black")  # eye
    draw.point((2, 3), fill="black")  # eye
    draw.point((5, 3), fill="black")  # eye
    # Carrot nose
    draw.point((3, 3), fill="white")  # nose base
    draw.point((3, 4), fill="black")  # nose tip
    # Happy smile
    draw.point((1, 4), fill="black")  # mouth
    draw.point((6, 4), fill="black")  # mouth
    draw.point((2, 5), fill="black")  # mouth
    draw.point((5, 5), fill="black")  # mouth
    # Cheek blush
    draw.point((0, 3), fill="white")
    draw.point((7, 3), fill="white")
    
    # More prominent falling snowflakes with different patterns
    snow_y = (frame % 6)
    for x in [0, 2, 4, 6]:
        y = 0 + snow_y
        if y < 8:
            draw.point((x, y), fill="white")
    for x in [1, 3, 5, 7]:
        y = 1 + snow_y
        if y < 8:
            draw.point((x, y), fill="white")
    for x in [0, 1, 6, 7]:
        y = 2 + snow_y
        if y < 8:
            draw.point((x, y), fill="white")

def draw_blizzard_animation(draw, frame):
    """Draw extreme blizzard animation - snowman with heavy snow and wind"""
    # Snowman with winter hat
    draw.ellipse([(1, 4), (6, 6)], outline="white", fill="white")  # body
    draw.ellipse([(2, 2), (5, 4)], outline="white", fill="white")  # head
    # Winter hat
    draw.point((1, 1), fill="white")
    draw.point((2, 1), fill="white")
    draw.point((3, 1), fill="white")
    draw.point((4, 1), fill="white")
    draw.point((5, 1), fill="white")
    draw.point((6, 1), fill="white")
    draw.point((2, 0), fill="white")
    draw.point((3, 0), fill="white")
    draw.point((4, 0), fill="white")
    draw.point((5, 0), fill="white")
    
    # Cold face with shivering
    draw.point((2, 2), fill="black")  # eye
    draw.point((5, 2), fill="black")  # eye
    draw.point((2, 3), fill="black")  # eye
    draw.point((5, 3), fill="black")  # eye
    # Cold nose
    draw.point((3, 3), fill="black")  # nose
    # Shivering mouth
    if frame % 2 == 0:
        draw.point((2, 4), fill="black")  # mouth
        draw.point((5, 4), fill="black")  # mouth
    else:
        draw.point((1, 4), fill="black")  # mouth
        draw.point((6, 4), fill="black")  # mouth
    
    # Heavy snowstorm with wind effect
    snow_y = (frame % 3)  # Faster snow
    for x in [0, 1, 2, 3, 4, 5, 6, 7]:
        y = 0 + snow_y
        if y < 8:
            draw.point((x, y), fill="white")
            if y < 7:
                draw.point((x, y+1), fill="white")
    
    # Wind lines
    wind_frame = frame % 4
    if wind_frame == 0:
        draw.point((0, 1), fill="white")
        draw.point((1, 2), fill="white")
        draw.point((2, 3), fill="white")
    elif wind_frame == 1:
        draw.point((1, 1), fill="white")
        draw.point((2, 2), fill="white")
        draw.point((3, 3), fill="white")
    elif wind_frame == 2:
        draw.point((2, 1), fill="white")
        draw.point((3, 2), fill="white")
        draw.point((4, 3), fill="white")
    else:
        draw.point((3, 1), fill="white")
        draw.point((4, 2), fill="white")
        draw.point((5, 3), fill="white")

def draw_heavy_snow_animation(draw, frame):
    """Draw heavy snow animation - snowman with lots of snow"""
    # Snowman
    draw.ellipse([(1, 4), (6, 6)], outline="white", fill="white")  # body
    draw.ellipse([(2, 2), (5, 4)], outline="white", fill="white")  # head
    
    # Happy snowman face
    draw.point((2, 2), fill="black")  # eye
    draw.point((5, 2), fill="black")  # eye
    draw.point((2, 3), fill="black")  # eye
    draw.point((5, 3), fill="black")  # eye
    draw.point((3, 3), fill="black")  # nose
    # Big smile
    draw.point((1, 4), fill="black")  # mouth
    draw.point((6, 4), fill="black")  # mouth
    draw.point((2, 5), fill="black")  # mouth
    draw.point((5, 5), fill="black")  # mouth
    draw.point((3, 5), fill="black")  # mouth
    draw.point((4, 5), fill="black")  # mouth
    
    # Heavy snow with multiple layers
    snow_y = (frame % 4)
    for x in [0, 1, 2, 3, 4, 5, 6, 7]:
        y = 0 + snow_y
        if y < 8:
            draw.point((x, y), fill="white")
    for x in [0, 2, 4, 6]:
        y = 1 + snow_y
        if y < 8:
            draw.point((x, y), fill="white")
    for x in [1, 3, 5, 7]:
        y = 2 + snow_y
        if y < 8:
            draw.point((x, y), fill="white")

def draw_overcast_animation(draw, frame):
    """Draw overcast sky animation - thick clouds with no sun"""
    # Thick overcast clouds covering the sky
    for y in range(3):
        for x in range(8):
            if (x + y + frame) % 3 != 0:  # Create moving cloud pattern
                draw.point((x, y), fill="white")
    
    # Cloud faces - some happy, some neutral
    cloud_frame = frame % 6
    if cloud_frame < 3:
        # Happy cloud
        draw.point((2, 0), fill="black")  # eye
        draw.point((5, 0), fill="black")  # eye
        draw.point((3, 1), fill="black")  # smile
        draw.point((4, 1), fill="black")  # smile
    else:
        # Neutral cloud
        draw.point((2, 0), fill="black")  # eye
        draw.point((5, 0), fill="black")  # eye
        draw.point((3, 1), fill="black")  # straight mouth
        draw.point((4, 1), fill="black")  # straight mouth
    
    # Light drizzle
    drizzle_y = (frame % 5)
    for x in [1, 3, 5, 7]:
        y = 4 + drizzle_y
        if y < 8:
            draw.point((x, y), fill="white")

def draw_partly_cloudy_animation(draw, frame):
    """Draw partly cloudy animation - sun peeking through clouds"""
    # Sun with face
    draw.ellipse([(1, 1), (6, 6)], outline="white", fill="white")
    # Sun face
    draw.point((2, 2), fill="black")  # eye
    draw.point((5, 2), fill="black")  # eye
    draw.point((2, 3), fill="black")  # eye
    draw.point((5, 3), fill="black")  # eye
    draw.point((1, 4), fill="black")  # smile
    draw.point((2, 5), fill="black")  # smile
    draw.point((3, 6), fill="black")  # smile
    draw.point((4, 6), fill="black")  # smile
    draw.point((5, 5), fill="black")  # smile
    draw.point((6, 4), fill="black")  # smile
    
    # Sun rays
    ray_frame = frame % 4
    if ray_frame == 0 or ray_frame == 1:
        draw.point((0, 0), fill="white")
        draw.point((7, 0), fill="white")
        draw.point((0, 7), fill="white")
        draw.point((7, 7), fill="white")
        draw.point((3, 0), fill="white")
        draw.point((4, 0), fill="white")
        draw.point((3, 7), fill="white")
        draw.point((4, 7), fill="white")
        draw.point((0, 3), fill="white")
        draw.point((0, 4), fill="white")
        draw.point((7, 3), fill="white")
        draw.point((7, 4), fill="white")
    
    # Moving clouds partially covering sun
    cloud_offset = frame % 4
    if cloud_offset == 0:
        # Cloud 1
        draw.point((5, 0), fill="white")
        draw.point((6, 0), fill="white")
        draw.point((7, 0), fill="white")
        draw.point((6, 1), fill="white")
        draw.point((7, 1), fill="white")
    elif cloud_offset == 1:
        # Cloud 2
        draw.point((0, 0), fill="white")
        draw.point((1, 0), fill="white")
        draw.point((0, 1), fill="white")
        draw.point((1, 1), fill="white")
        draw.point((2, 1), fill="white")
    elif cloud_offset == 2:
        # Cloud 3
        draw.point((3, 0), fill="white")
        draw.point((4, 0), fill="white")
        draw.point((5, 0), fill="white")
        draw.point((4, 1), fill="white")
        draw.point((5, 1), fill="white")

def draw_heavy_rain_animation(draw, frame):
    """Draw heavy rain animation - very intense rain with splash effects"""
    # Heavy rain cloud
    for y in range(3):
        for x in range(8):
            draw.point((x, y), fill="white")
    
    # Sad cloud face
    draw.point((2, 0), fill="black")  # eye
    draw.point((5, 0), fill="black")  # eye
    draw.point((2, 1), fill="black")  # eye
    draw.point((5, 1), fill="black")  # eye
    # Very sad mouth
    draw.point((1, 2), fill="black")  # sad mouth
    draw.point((6, 2), fill="black")  # sad mouth
    draw.point((2, 2), fill="black")  # sad mouth
    draw.point((3, 2), fill="black")  # sad mouth
    draw.point((4, 2), fill="black")  # sad mouth
    draw.point((5, 2), fill="black")  # sad mouth
    
    # Very heavy rain - multiple layers
    rain_speed1 = (frame % 2)  # Very fast
    rain_speed2 = (frame % 3)  # Fast
    rain_speed3 = (frame % 4)  # Medium
    
    # Heavy rain drops
    for x in [0, 1, 2, 3, 4, 5, 6, 7]:
        y = 3 + rain_speed1
        if y < 8:
            draw.point((x, y), fill="white")
            if y < 7:
                draw.point((x, y+1), fill="white")
    
    for x in [0, 2, 4, 6]:
        y = 4 + rain_speed2
        if y < 8:
            draw.point((x, y), fill="white")
            if y < 7:
                draw.point((x, y+1), fill="white")
    
    for x in [1, 3, 5, 7]:
        y = 5 + rain_speed3
        if y < 8:
            draw.point((x, y), fill="white")
    
    # Heavy splash effects
    splash_frame = frame % 2
    if splash_frame == 0:
        for x in [0, 1, 2, 3, 4, 5, 6, 7]:
            draw.point((x, 7), fill="white")
    else:
        for x in [0, 2, 4, 6]:
            draw.point((x, 7), fill="white")
        for x in [1, 3, 5, 7]:
            draw.point((x, 6), fill="white")

def draw_heat_wave_animation(draw, frame):
    """Draw heat wave animation - very hot sun with heat distortion"""
    # Very bright sun with sunglasses
    draw.ellipse([(1, 1), (6, 6)], outline="white", fill="white")
    # Sunglasses
    draw.point((2, 2), fill="black")  # left lens
    draw.point((3, 2), fill="black")  # left lens
    draw.point((4, 2), fill="black")  # right lens
    draw.point((5, 2), fill="black")  # right lens
    draw.point((3, 3), fill="black")  # bridge
    # Big smile
    draw.point((1, 4), fill="black")  # smile
    draw.point((2, 5), fill="black")  # smile
    draw.point((3, 6), fill="black")  # smile
    draw.point((4, 6), fill="black")  # smile
    draw.point((5, 5), fill="black")  # smile
    draw.point((6, 4), fill="black")  # smile
    
    # Heat wave distortion effect
    heat_frame = frame % 6
    if heat_frame == 0 or heat_frame == 1:
        # Very long rays
        draw.point((0, 0), fill="white")
        draw.point((7, 0), fill="white")
        draw.point((0, 7), fill="white")
        draw.point((7, 7), fill="white")
        draw.point((3, 0), fill="white")
        draw.point((4, 0), fill="white")
        draw.point((3, 7), fill="white")
        draw.point((4, 7), fill="white")
        draw.point((0, 3), fill="white")
        draw.point((0, 4), fill="white")
        draw.point((7, 3), fill="white")
        draw.point((7, 4), fill="white")
        # Extra heat rays
        draw.point((1, 0), fill="white")
        draw.point((6, 0), fill="white")
        draw.point((1, 7), fill="white")
        draw.point((6, 7), fill="white")
        draw.point((0, 2), fill="white")
        draw.point((0, 5), fill="white")
        draw.point((7, 2), fill="white")
        draw.point((7, 5), fill="white")
    elif heat_frame == 2 or heat_frame == 3:
        # Medium rays
        draw.point((1, 0), fill="white")
        draw.point((6, 0), fill="white")
        draw.point((1, 7), fill="white")
        draw.point((6, 7), fill="white")
        draw.point((2, 0), fill="white")
        draw.point((5, 0), fill="white")
        draw.point((2, 7), fill="white")
        draw.point((5, 7), fill="white")
        draw.point((0, 2), fill="white")
        draw.point((0, 5), fill="white")
        draw.point((7, 2), fill="white")
        draw.point((7, 5), fill="white")
    else:
        # Short rays
        draw.point((2, 1), fill="white")
        draw.point((5, 1), fill="white")
        draw.point((2, 6), fill="white")
        draw.point((5, 6), fill="white")
        draw.point((1, 2), fill="white")
        draw.point((6, 2), fill="white")
        draw.point((1, 5), fill="white")
        draw.point((6, 5), fill="white")
    
    # Heat shimmer effect
    shimmer_frame = frame % 4
    if shimmer_frame == 0:
        draw.point((0, 1), fill="white")
        draw.point((7, 1), fill="white")
        draw.point((0, 6), fill="white")
        draw.point((7, 6), fill="white")
    elif shimmer_frame == 1:
        draw.point((1, 1), fill="white")
        draw.point((6, 1), fill="white")
        draw.point((1, 6), fill="white")
        draw.point((6, 6), fill="white")
    elif shimmer_frame == 2:
        draw.point((2, 1), fill="white")
        draw.point((5, 1), fill="white")
        draw.point((2, 6), fill="white")
        draw.point((5, 6), fill="white")
    else:
        draw.point((3, 1), fill="white")
        draw.point((4, 1), fill="white")
        draw.point((3, 6), fill="white")
        draw.point((4, 6), fill="white")

def draw_rainbow_animation(draw, frame):
    """Draw cute rainbow weather animation - rainbow with sun and clouds"""
    # Happy sun with face
    draw.ellipse([(1, 1), (6, 6)], outline="white", fill="white")
    # Sun face
    draw.point((2, 2), fill="black")  # eye
    draw.point((5, 2), fill="black")  # eye
    draw.point((2, 3), fill="black")  # eye
    draw.point((5, 3), fill="black")  # eye
    draw.point((1, 4), fill="black")  # smile
    draw.point((2, 5), fill="black")  # smile
    draw.point((3, 6), fill="black")  # smile
    draw.point((4, 6), fill="black")  # smile
    draw.point((5, 5), fill="black")  # smile
    draw.point((6, 4), fill="black")  # smile
    
    # Sun rays
    ray_frame = frame % 4
    if ray_frame == 0 or ray_frame == 1:
        draw.point((0, 0), fill="white")
        draw.point((7, 0), fill="white")
        draw.point((0, 7), fill="white")
        draw.point((7, 7), fill="white")
        draw.point((3, 0), fill="white")
        draw.point((4, 0), fill="white")
        draw.point((3, 7), fill="white")
        draw.point((4, 7), fill="white")
        draw.point((0, 3), fill="white")
        draw.point((0, 4), fill="white")
        draw.point((7, 3), fill="white")
        draw.point((7, 4), fill="white")
    
    # Animated rainbow arc
    rainbow_frame = frame % 8
    if rainbow_frame < 4:
        # Rainbow appears
        for i in range(rainbow_frame + 1):
            x = 0 + i
            y = 2 + i
            if x < 8 and y < 8:
                draw.point((x, y), fill="white")
            x = 7 - i
            if x >= 0 and y < 8:
                draw.point((x, y), fill="white")
    else:
        # Full rainbow
        for i in range(4):
            x = 0 + i
            y = 2 + i
            if x < 8 and y < 8:
                draw.point((x, y), fill="white")
            x = 7 - i
            if x >= 0 and y < 8:
                draw.point((x, y), fill="white")
    
    # Floating clouds
    cloud_offset = frame % 3
    if cloud_offset == 0:
        draw.point((0, 0), fill="white")
        draw.point((1, 0), fill="white")
        draw.point((2, 0), fill="white")
        draw.point((1, 1), fill="white")
    elif cloud_offset == 1:
        draw.point((5, 0), fill="white")
        draw.point((6, 0), fill="white")
        draw.point((7, 0), fill="white")
        draw.point((6, 1), fill="white")
    else:
        draw.point((2, 0), fill="white")
        draw.point((3, 0), fill="white")
        draw.point((4, 0), fill="white")
        draw.point((5, 0), fill="white")
        draw.point((3, 1), fill="white")
        draw.point((4, 1), fill="white")

def draw_foggy_animation(draw, frame):
    """Draw mysterious foggy weather animation - thick fog with hidden elements"""
    # Thick fog layers
    fog_frame = frame % 6
    for layer in range(3):
        for x in range(8):
            for y in range(2 + layer, 6 - layer):
                if (x + y + fog_frame + layer) % 3 == 0:
                    draw.point((x, y), fill="white")
    
    # Mysterious eyes peeking through fog
    eye_frame = frame % 8
    if eye_frame < 4:
        # Left eye appears
        draw.point((1, 2), fill="black")
        draw.point((2, 2), fill="black")
        draw.point((1, 3), fill="black")
        draw.point((2, 3), fill="black")
    if eye_frame >= 4:
        # Right eye appears
        draw.point((5, 2), fill="black")
        draw.point((6, 2), fill="black")
        draw.point((5, 3), fill="black")
        draw.point((6, 3), fill="black")
    
    # Floating fog particles
    particle_frame = frame % 4
    for i in range(particle_frame + 1):
        x = (i * 2) % 8
        y = 1 + (i % 2)
        draw.point((x, y), fill="white")
        x = (i * 2 + 1) % 8
        y = 6 + (i % 2)
        draw.point((x, y), fill="white")
    
    # Mysterious smile
    if frame % 8 >= 6:
        draw.point((2, 5), fill="black")
        draw.point((3, 5), fill="black")
        draw.point((4, 5), fill="black")
        draw.point((5, 5), fill="black")

def draw_windy_animation(draw, frame):
    """Draw windy weather animation - moving elements with wind effects"""
    # Windy cloud with worried face
    cloud_offset = frame % 4
    # Cloud body
    draw.point((0 + cloud_offset, 1), fill="white")
    draw.point((1 + cloud_offset, 0), fill="white")
    draw.point((2 + cloud_offset, 0), fill="white")
    draw.point((3 + cloud_offset, 0), fill="white")
    draw.point((4 + cloud_offset, 1), fill="white")
    draw.point((5 + cloud_offset, 2), fill="white")
    draw.point((1 + cloud_offset, 1), fill="white")
    draw.point((2 + cloud_offset, 1), fill="white")
    draw.point((3 + cloud_offset, 1), fill="white")
    draw.point((4 + cloud_offset, 2), fill="white")
    
    # Worried cloud face
    if cloud_offset < 2:
        draw.point((1, 0), fill="black")  # worried eye
        draw.point((3, 0), fill="black")  # worried eye
        draw.point((1, 1), fill="black")  # worried eye
        draw.point((3, 1), fill="black")  # worried eye
        # Worried mouth
        draw.point((2, 1), fill="black")  # worried mouth
        draw.point((3, 1), fill="black")  # worried mouth
    else:
        draw.point((2, 0), fill="black")  # worried eye
        draw.point((4, 0), fill="black")  # worried eye
        draw.point((2, 1), fill="black")  # worried eye
        draw.point((4, 1), fill="black")  # worried eye
        # Worried mouth
        draw.point((3, 1), fill="black")  # worried mouth
        draw.point((4, 1), fill="black")  # worried mouth
    
    # Wind lines
    wind_frame = frame % 6
    for i in range(3):
        x = (wind_frame + i * 2) % 8
        y = 3 + i
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
            if x < 7:
                draw.point((x + 1, y), fill="white")
    
    # Flying leaves
    leaf_frame = frame % 4
    for i in range(2):
        x = (leaf_frame + i * 3) % 8
        y = 4 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
            if x < 7:
                draw.point((x + 1, y), fill="white")
    
    # Wind swirls
    swirl_frame = frame % 8
    if swirl_frame < 4:
        draw.point((6, 5), fill="white")
        draw.point((7, 5), fill="white")
        draw.point((6, 6), fill="white")
    else:
        draw.point((0, 5), fill="white")
        draw.point((1, 5), fill="white")
        draw.point((0, 6), fill="white")

def draw_aurora_animation(draw, frame):
    """Draw aurora borealis animation - beautiful northern lights"""
    # Aurora waves
    aurora_frame = frame % 8
    for wave in range(3):
        wave_offset = (aurora_frame + wave * 2) % 8
        for x in range(8):
            y = 1 + wave + (x + wave_offset) % 2
            if y < 7:
                draw.point((x, y), fill="white")
                if y < 6:
                    draw.point((x, y + 1), fill="white")
    
    # Stars
    star_frame = frame % 6
    star_positions = [(1, 0), (6, 0), (0, 1), (7, 1), (2, 0), (5, 0)]
    for i, (x, y) in enumerate(star_positions):
        if (star_frame + i) % 3 == 0:
            draw.point((x, y), fill="white")
            if x < 7 and y < 7:
                draw.point((x + 1, y), fill="white")
                draw.point((x, y + 1), fill="white")
    
    # Aurora shimmer
    shimmer_frame = frame % 4
    if shimmer_frame == 0:
        for x in [0, 2, 4, 6]:
            draw.point((x, 2), fill="white")
            draw.point((x, 3), fill="white")
    elif shimmer_frame == 1:
        for x in [1, 3, 5, 7]:
            draw.point((x, 2), fill="white")
            draw.point((x, 3), fill="white")
    elif shimmer_frame == 2:
        for x in [0, 1, 6, 7]:
            draw.point((x, 3), fill="white")
            draw.point((x, 4), fill="white")
    else:
        for x in [2, 3, 4, 5]:
            draw.point((x, 3), fill="white")
            draw.point((x, 4), fill="white")

def draw_tornado_animation(draw, frame):
    """Draw tornado animation - spinning funnel cloud"""
    # Tornado funnel
    tornado_frame = frame % 8
    for i in range(4):
        width = 2 + i
        start_x = 3 - width // 2
        for x in range(width):
            y = 7 - i
            if start_x + x < 8 and y >= 0:
                draw.point((start_x + x, y), fill="white")
    
    # Spinning debris
    debris_frame = frame % 6
    for i in range(3):
        angle = (debris_frame + i * 2) % 8
        if angle < 4:
            x = 3 + angle
            y = 4 + i
        else:
            x = 3 - (angle - 4)
            y = 4 + i
        if 0 <= x < 8 and 0 <= y < 8:
            draw.point((x, y), fill="white")
    
    # Wind lines around tornado
    wind_frame = frame % 4
    for i in range(2):
        x = (wind_frame + i * 3) % 8
        y = 2 + i
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
            if x < 7:
                draw.point((x + 1, y), fill="white")

def draw_hail_animation(draw, frame):
    """Draw hail animation - bouncing ice particles"""
    # Angry cloud with hail
    draw.point((0, 0), fill="white")
    draw.point((1, 0), fill="white")
    draw.point((2, 0), fill="white")
    draw.point((3, 0), fill="white")
    draw.point((4, 0), fill="white")
    draw.point((5, 0), fill="white")
    draw.point((6, 0), fill="white")
    draw.point((7, 0), fill="white")
    draw.point((1, 1), fill="white")
    draw.point((2, 1), fill="white")
    draw.point((3, 1), fill="white")
    draw.point((4, 1), fill="white")
    draw.point((5, 1), fill="white")
    draw.point((6, 1), fill="white")
    
    # Angry cloud face
    draw.point((2, 0), fill="black")  # angry eye
    draw.point((5, 0), fill="black")  # angry eye
    draw.point((2, 1), fill="black")  # angry eye
    draw.point((5, 1), fill="black")  # angry eye
    # Angry mouth
    draw.point((1, 1), fill="black")  # angry mouth
    draw.point((6, 1), fill="black")  # angry mouth
    draw.point((2, 1), fill="black")  # angry mouth
    draw.point((3, 1), fill="black")  # angry mouth
    draw.point((4, 1), fill="black")  # angry mouth
    draw.point((5, 1), fill="black")  # angry mouth
    
    # Bouncing hail stones
    hail_frame = frame % 6
    for i in range(4):
        x = i * 2
        y = 2 + (hail_frame + i) % 4
        if y < 8:
            draw.point((x, y), fill="white")
            if x < 7 and y < 7:
                draw.point((x + 1, y), fill="white")
                draw.point((x, y + 1), fill="white")
                draw.point((x + 1, y + 1), fill="white")
    
    # Hail splashes
    splash_frame = frame % 3
    for i in range(3):
        x = i * 2 + 1
        y = 7
        if splash_frame == 0:
            draw.point((x, y), fill="white")
        elif splash_frame == 1:
            draw.point((x - 1, y), fill="white")
            draw.point((x + 1, y), fill="white")
        else:
            draw.point((x, y), fill="white")
            draw.point((x - 1, y), fill="white")
            draw.point((x + 1, y), fill="white")

def draw_sandstorm_animation(draw, frame):
    """Draw sandstorm animation - swirling sand particles"""
    # Sandstorm cloud
    sand_frame = frame % 4
    for y in range(3):
        for x in range(8):
            if (x + y + sand_frame) % 2 == 0:
                draw.point((x, y), fill="white")
    
    # Swirling sand particles
    swirl_frame = frame % 8
    for i in range(6):
        angle = (swirl_frame + i) % 8
        if angle < 4:
            x = 3 + angle
            y = 3 + i // 2
        else:
            x = 3 - (angle - 4)
            y = 3 + i // 2
        if 0 <= x < 8 and 0 <= y < 8:
            draw.point((x, y), fill="white")
    
    # Sand dunes
    dune_frame = frame % 6
    for i in range(3):
        x = (dune_frame + i * 2) % 8
        y = 6 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
            if x < 7:
                draw.point((x + 1, y), fill="white")

def draw_meteor_animation(draw, frame):
    """Draw meteor shower animation - shooting stars"""
    # Night sky background
    for y in range(2):
        for x in range(8):
            if (x + y + frame) % 4 == 0:
                draw.point((x, y), fill="white")
    
    # Shooting meteors
    meteor_frame = frame % 8
    for i in range(2):
        meteor_x = (meteor_frame + i * 3) % 8
        meteor_y = 1 + (meteor_frame + i) % 4
        if meteor_x < 8 and meteor_y < 8:
            # Meteor head
            draw.point((meteor_x, meteor_y), fill="white")
            # Meteor tail
            if meteor_x > 0 and meteor_y > 0:
                draw.point((meteor_x - 1, meteor_y - 1), fill="white")
            if meteor_x > 1 and meteor_y > 1:
                draw.point((meteor_x - 2, meteor_y - 2), fill="white")
    
    # Stars
    star_frame = frame % 6
    star_positions = [(1, 0), (6, 0), (0, 1), (7, 1), (3, 0), (4, 0)]
    for i, (x, y) in enumerate(star_positions):
        if (star_frame + i) % 3 == 0:
            draw.point((x, y), fill="white")
            if x < 7 and y < 7:
                draw.point((x + 1, y), fill="white")
                draw.point((x, y + 1), fill="white")

def draw_volcano_animation(draw, frame):
    """Draw volcanic eruption animation - lava and ash"""
    # Volcano mountain
    draw.point((2, 4), fill="white")
    draw.point((3, 4), fill="white")
    draw.point((4, 4), fill="white")
    draw.point((5, 4), fill="white")
    draw.point((3, 5), fill="white")
    draw.point((4, 5), fill="white")
    draw.point((3, 6), fill="white")
    draw.point((4, 6), fill="white")
    draw.point((3, 7), fill="white")
    draw.point((4, 7), fill="white")
    
    # Lava eruption
    lava_frame = frame % 6
    if lava_frame < 3:
        # Lava flowing down
        for i in range(lava_frame + 1):
            y = 3 - i
            draw.point((3, y), fill="white")
            draw.point((4, y), fill="white")
    else:
        # Lava explosion
        for i in range(3):
            y = 3 - i
            draw.point((3, y), fill="white")
            draw.point((4, y), fill="white")
        # Lava splashes
        draw.point((2, 2), fill="white")
        draw.point((5, 2), fill="white")
        draw.point((1, 3), fill="white")
        draw.point((6, 3), fill="white")
    
    # Ash cloud
    ash_frame = frame % 4
    for y in range(2):
        for x in range(8):
            if (x + y + ash_frame) % 3 == 0:
                draw.point((x, y), fill="white")
    
    # Fire sparks
    spark_frame = frame % 5
    for i in range(3):
        x = (spark_frame + i * 2) % 8
        y = 1 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")

def draw_tsunami_animation(draw, frame):
    """Draw tsunami wave animation - massive wave"""
    # Tsunami wave
    wave_frame = frame % 8
    if wave_frame < 4:
        # Wave building up
        for i in range(wave_frame + 1):
            y = 4 + i
            for x in range(8):
                draw.point((x, y), fill="white")
    else:
        # Full wave
        for y in range(4, 8):
            for x in range(8):
                draw.point((x, y), fill="white")
        # Wave crest
        for x in range(8):
            draw.point((x, 3), fill="white")
    
    # Water droplets
    droplet_frame = frame % 6
    for i in range(4):
        x = (droplet_frame + i * 2) % 8
        y = 2 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
    
    # Foam
    foam_frame = frame % 4
    for i in range(3):
        x = (foam_frame + i * 2) % 8
        y = 7
        if x < 8:
            draw.point((x, y), fill="white")
            if x < 7:
                draw.point((x + 1, y), fill="white")

def draw_earthquake_animation(draw, frame):
    """Draw earthquake animation - shaking ground"""
    # Shaking ground
    shake_frame = frame % 4
    ground_y = 6 + (shake_frame % 2)
    for x in range(8):
        draw.point((x, ground_y), fill="white")
        if ground_y < 7:
            draw.point((x, ground_y + 1), fill="white")
    
    # Cracks in ground
    crack_frame = frame % 6
    for i in range(3):
        x = (crack_frame + i * 2) % 8
        y = 5 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
            if x < 7:
                draw.point((x + 1, y), fill="white")
    
    # Shaking buildings
    building_frame = frame % 3
    for i in range(2):
        x = 1 + i * 4 + (building_frame % 2)
        for y in range(3, 6):
            if x < 8 and y < 8:
                draw.point((x, y), fill="white")
                if x < 7:
                    draw.point((x + 1, y), fill="white")
    
    # Dust particles
    dust_frame = frame % 5
    for i in range(4):
        x = (dust_frame + i * 2) % 8
        y = 2 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")

def draw_cyclone_animation(draw, frame):
    """Draw cyclone animation - spinning storm"""
    # Cyclone center
    draw.point((3, 3), fill="white")
    draw.point((4, 3), fill="white")
    draw.point((3, 4), fill="white")
    draw.point((4, 4), fill="white")
    
    # Spinning arms
    spin_frame = frame % 8
    for i in range(4):
        angle = (spin_frame + i * 2) % 8
        if angle < 4:
            x = 3 + angle
            y = 3 + i
        else:
            x = 3 - (angle - 4)
            y = 3 + i
        if 0 <= x < 8 and 0 <= y < 8:
            draw.point((x, y), fill="white")
            if x < 7 and y < 7:
                draw.point((x + 1, y), fill="white")
                draw.point((x, y + 1), fill="white")
    
    # Outer storm clouds
    cloud_frame = frame % 6
    for i in range(3):
        x = (cloud_frame + i * 2) % 8
        y = 1 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
            if x < 7:
                draw.point((x + 1, y), fill="white")
    
    # Wind lines
    wind_frame = frame % 4
    for i in range(2):
        x = (wind_frame + i * 3) % 8
        y = 6 + i
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
            if x < 7:
                draw.point((x + 1, y), fill="white")

def draw_ice_storm_animation(draw, frame):
    """Draw ice storm animation - freezing rain and ice"""
    # Ice storm cloud
    draw.point((0, 0), fill="white")
    draw.point((1, 0), fill="white")
    draw.point((2, 0), fill="white")
    draw.point((3, 0), fill="white")
    draw.point((4, 0), fill="white")
    draw.point((5, 0), fill="white")
    draw.point((6, 0), fill="white")
    draw.point((7, 0), fill="white")
    draw.point((1, 1), fill="white")
    draw.point((2, 1), fill="white")
    draw.point((3, 1), fill="white")
    draw.point((4, 1), fill="white")
    draw.point((5, 1), fill="white")
    draw.point((6, 1), fill="white")
    
    # Cold cloud face
    draw.point((2, 0), fill="black")  # cold eye
    draw.point((5, 0), fill="black")  # cold eye
    draw.point((2, 1), fill="black")  # cold eye
    draw.point((5, 1), fill="black")  # cold eye
    # Cold mouth
    draw.point((3, 1), fill="black")  # cold mouth
    draw.point((4, 1), fill="black")  # cold mouth
    
    # Freezing rain
    ice_frame = frame % 5
    for i in range(4):
        x = i * 2
        y = 2 + (ice_frame + i) % 4
        if y < 8:
            draw.point((x, y), fill="white")
            if x < 7 and y < 7:
                draw.point((x + 1, y), fill="white")
                draw.point((x, y + 1), fill="white")
                draw.point((x + 1, y + 1), fill="white")
    
    # Ice accumulation
    ice_acc_frame = frame % 6
    for i in range(3):
        x = (ice_acc_frame + i * 2) % 8
        y = 6 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
            if x < 7:
                draw.point((x + 1, y), fill="white")
    
    # Ice crystals
    crystal_frame = frame % 4
    for i in range(2):
        x = (crystal_frame + i * 3) % 8
        y = 4 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
            if x < 7 and y < 7:
                draw.point((x + 1, y), fill="white")
                draw.point((x, y + 1), fill="white")

def draw_heat_burst_animation(draw, frame):
    """Draw heat burst animation - extreme heat with distortion"""
    # Super hot sun with fire effects
    draw.ellipse([(1, 1), (6, 6)], outline="white", fill="white")
    # Fire eyes
    draw.point((2, 2), fill="black")  # eye
    draw.point((5, 2), fill="black")  # eye
    draw.point((2, 3), fill="black")  # eye
    draw.point((5, 3), fill="black")  # eye
    # Fire mouth
    draw.point((1, 4), fill="black")  # mouth
    draw.point((2, 5), fill="black")  # mouth
    draw.point((3, 6), fill="black")  # mouth
    draw.point((4, 6), fill="black")  # mouth
    draw.point((5, 5), fill="black")  # mouth
    draw.point((6, 4), fill="black")  # mouth
    
    # Extreme heat rays
    heat_frame = frame % 8
    if heat_frame < 4:
        # Maximum heat rays
        for x in range(8):
            draw.point((x, 0), fill="white")
            draw.point((x, 7), fill="white")
        for y in range(8):
            draw.point((0, y), fill="white")
            draw.point((7, y), fill="white")
    else:
        # Pulsing heat rays
        for x in [0, 2, 4, 6]:
            draw.point((x, 0), fill="white")
            draw.point((x, 7), fill="white")
        for y in [0, 2, 4, 6]:
            draw.point((0, y), fill="white")
            draw.point((7, y), fill="white")
    
    # Heat distortion waves
    distortion_frame = frame % 6
    for i in range(3):
        x = (distortion_frame + i * 2) % 8
        y = 1 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
            if x < 7:
                draw.point((x + 1, y), fill="white")
    
    # Fire sparks
    spark_frame = frame % 5
    for i in range(4):
        x = (spark_frame + i * 2) % 8
        y = 2 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")

def draw_cloudburst_animation(draw, frame):
    """Draw cloudburst animation - sudden heavy rain"""
    # Massive rain cloud
    for y in range(3):
        for x in range(8):
            draw.point((x, y), fill="white")
    
    # Shocked cloud face
    draw.point((2, 0), fill="black")  # shocked eye
    draw.point((5, 0), fill="black")  # shocked eye
    draw.point((2, 1), fill="black")  # shocked eye
    draw.point((5, 1), fill="black")  # shocked eye
    # Shocked mouth
    draw.point((3, 1), fill="black")  # shocked mouth
    draw.point((4, 1), fill="black")  # shocked mouth
    
    # Sudden heavy rain
    rain_frame = frame % 3
    for x in range(8):
        for y in range(3 + rain_frame, 8):
            draw.point((x, y), fill="white")
    
    # Rain splash effects
    splash_frame = frame % 2
    for x in range(8):
        if splash_frame == 0:
            draw.point((x, 7), fill="white")
        else:
            if x % 2 == 0:
                draw.point((x, 7), fill="white")
            else:
                draw.point((x, 6), fill="white")
    
    # Water droplets
    droplet_frame = frame % 4
    for i in range(3):
        x = (droplet_frame + i * 2) % 8
        y = 2 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")

def draw_dust_devil_animation(draw, frame):
    """Draw dust devil animation - spinning dust column"""
    # Dust devil column
    dust_frame = frame % 8
    for i in range(4):
        width = 1 + i // 2
        start_x = 3 - width // 2
        for x in range(width):
            y = 7 - i
            if start_x + x < 8 and y >= 0:
                draw.point((start_x + x, y), fill="white")
    
    # Spinning dust particles
    spin_frame = frame % 6
    for i in range(5):
        angle = (spin_frame + i) % 8
        if angle < 4:
            x = 3 + angle
            y = 3 + i // 2
        else:
            x = 3 - (angle - 4)
            y = 3 + i // 2
        if 0 <= x < 8 and 0 <= y < 8:
            draw.point((x, y), fill="white")
    
    # Dust clouds
    cloud_frame = frame % 5
    for i in range(3):
        x = (cloud_frame + i * 2) % 8
        y = 1 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
            if x < 7:
                draw.point((x + 1, y), fill="white")
    
    # Ground dust
    ground_frame = frame % 4
    for i in range(4):
        x = (ground_frame + i * 2) % 8
        y = 6 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")

def draw_lightning_storm_animation(draw, frame):
    """Draw enhanced lightning storm animation - more dramatic effects"""
    # Massive storm cloud
    for y in range(3):
        for x in range(8):
            draw.point((x, y), fill="white")
    
    # Very angry cloud face
    draw.point((2, 0), fill="black")  # angry eye
    draw.point((5, 0), fill="black")  # angry eye
    draw.point((2, 1), fill="black")  # angry eye
    draw.point((5, 1), fill="black")  # angry eye
    # Angry mouth
    draw.point((1, 1), fill="black")  # angry mouth
    draw.point((6, 1), fill="black")  # angry mouth
    draw.point((2, 1), fill="black")  # angry mouth
    draw.point((3, 1), fill="black")  # angry mouth
    draw.point((4, 1), fill="black")  # angry mouth
    draw.point((5, 1), fill="black")  # angry mouth
    
    # Multiple lightning bolts
    lightning_frame = frame % 10
    if lightning_frame < 3:
        # Main lightning bolt
        draw.point((3, 1), fill="white")
        draw.point((2, 2), fill="white")
        draw.point((3, 3), fill="white")
        draw.point((4, 4), fill="white")
        draw.point((3, 5), fill="white")
        draw.point((2, 6), fill="white")
        draw.point((3, 7), fill="white")
    elif lightning_frame < 6:
        # Forked lightning
        draw.point((4, 1), fill="white")
        draw.point((3, 2), fill="white")
        draw.point((4, 3), fill="white")
        draw.point((5, 4), fill="white")
        draw.point((4, 5), fill="white")
        draw.point((3, 6), fill="white")
        draw.point((4, 7), fill="white")
        # Fork
        draw.point((2, 3), fill="white")
        draw.point((1, 4), fill="white")
        draw.point((0, 5), fill="white")
    elif lightning_frame < 8:
        # Multiple bolts
        draw.point((2, 1), fill="white")
        draw.point((3, 2), fill="white")
        draw.point((2, 3), fill="white")
        draw.point((3, 4), fill="white")
        draw.point((2, 5), fill="white")
        draw.point((1, 6), fill="white")
        draw.point((2, 7), fill="white")
        # Second bolt
        draw.point((5, 1), fill="white")
        draw.point((6, 2), fill="white")
        draw.point((5, 3), fill="white")
        draw.point((6, 4), fill="white")
        draw.point((5, 5), fill="white")
        draw.point((4, 6), fill="white")
        draw.point((5, 7), fill="white")
    else:
        # Intense flash
        for x in range(8):
            for y in range(1, 8):
                if (x + y) % 2 == 0:
                    draw.point((x, y), fill="white")
    
    # Heavy rain
    rain_frame = frame % 2
    for x in range(8):
        y = 3 + rain_frame
        if y < 8:
            draw.point((x, y), fill="white")
            if y < 7:
                draw.point((x, y + 1), fill="white")
    
    # Dramatic splash effects
    splash_frame = frame % 3
    for x in range(8):
        if splash_frame == 0:
            draw.point((x, 7), fill="white")
        elif splash_frame == 1:
            if x % 2 == 0:
                draw.point((x, 7), fill="white")
        else:
            if x % 3 == 0:
                draw.point((x, 7), fill="white")

def draw_solar_flare_animation(draw, frame):
    """Draw solar flare animation - cosmic effects"""
    # Solar flare sun
    draw.ellipse([(1, 1), (6, 6)], outline="white", fill="white")
    # Cosmic eyes
    draw.point((2, 2), fill="black")  # eye
    draw.point((5, 2), fill="black")  # eye
    draw.point((2, 3), fill="black")  # eye
    draw.point((5, 3), fill="black")  # eye
    # Cosmic smile
    draw.point((1, 4), fill="black")  # smile
    draw.point((2, 5), fill="black")  # smile
    draw.point((3, 6), fill="black")  # smile
    draw.point((4, 6), fill="black")  # smile
    draw.point((5, 5), fill="black")  # smile
    draw.point((6, 4), fill="black")  # smile
    
    # Solar flare rays
    flare_frame = frame % 8
    if flare_frame < 4:
        # Intense flare
        for x in range(8):
            draw.point((x, 0), fill="white")
            draw.point((x, 7), fill="white")
        for y in range(8):
            draw.point((0, y), fill="white")
            draw.point((7, y), fill="white")
    else:
        # Pulsing flare
        for x in [0, 2, 4, 6]:
            draw.point((x, 0), fill="white")
            draw.point((x, 7), fill="white")
        for y in [0, 2, 4, 6]:
            draw.point((0, y), fill="white")
            draw.point((7, y), fill="white")
    
    # Cosmic particles
    particle_frame = frame % 6
    for i in range(4):
        x = (particle_frame + i * 2) % 8
        y = 1 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
            if x < 7 and y < 7:
                draw.point((x + 1, y), fill="white")
                draw.point((x, y + 1), fill="white")
    
    # Solar wind
    wind_frame = frame % 5
    for i in range(3):
        x = (wind_frame + i * 2) % 8
        y = 2 + (i % 2)
        if x < 8 and y < 8:
            draw.point((x, y), fill="white")
            if x < 7:
                draw.point((x + 1, y), fill="white")

def draw_weather_animation(temperature_avg, pop_avg, frame):
    """Draw weather animation based on temperature and precipitation with more detailed conditions."""
    _set_brightness()
    
    with canvas(device) as draw:
        # Special weather conditions (rare but dramatic)
        special_weather = frame % 100  # 1% chance for special weather
        
        # Extreme weather conditions
        if temperature_avg <= -10:
            # Extremely cold - show blizzard
            draw_blizzard_animation(draw, frame)
        elif temperature_avg <= -5:
            # Very cold - show ice storm
            draw_ice_storm_animation(draw, frame)
        elif temperature_avg <= 0:
            # Freezing - show heavy snow
            if pop_avg >= 80:
                draw_heavy_snow_animation(draw, frame)
            else:
                draw_snowy_animation(draw, frame)
        elif temperature_avg <= 5:
            # Very cold - show snow with variations
            if pop_avg >= 70:
                draw_heavy_snow_animation(draw, frame)
            elif pop_avg >= 50:
                draw_hail_animation(draw, frame)
            else:
                draw_snowy_animation(draw, frame)
        elif temperature_avg <= 10:
            # Cold weather - show foggy or overcast
            if pop_avg >= 80:
                draw_heavy_rain_animation(draw, frame)
            elif pop_avg >= 60:
                draw_rainy_animation(draw, frame)
            elif pop_avg >= 30:
                draw_foggy_animation(draw, frame)
            else:
                draw_overcast_animation(draw, frame)
        elif temperature_avg <= 15:
            # Cool weather - show overcast or light rain
            if pop_avg >= 80:
                draw_heavy_rain_animation(draw, frame)
            elif pop_avg >= 60:
                draw_rainy_animation(draw, frame)
            elif pop_avg >= 40:
                draw_foggy_animation(draw, frame)
            else:
                draw_overcast_animation(draw, frame)
        elif temperature_avg <= 20:
            # Mild cool weather
            if pop_avg >= 90:
                draw_cloudburst_animation(draw, frame)
            elif pop_avg >= 80:
                draw_thunderstorm_animation(draw, frame)
            elif pop_avg >= 60:
                draw_rainy_animation(draw, frame)
            elif pop_avg >= 40:
                draw_partly_cloudy_animation(draw, frame)
            else:
                draw_cloudy_animation(draw, frame)
        elif temperature_avg <= 25:
            # Mild weather - show partly cloudy or light rain
            if pop_avg >= 90:
                draw_cloudburst_animation(draw, frame)
            elif pop_avg >= 80:
                draw_lightning_storm_animation(draw, frame)
            elif pop_avg >= 60:
                draw_rainy_animation(draw, frame)
            elif pop_avg >= 40:
                draw_partly_cloudy_animation(draw, frame)
            elif pop_avg >= 20:
                draw_windy_animation(draw, frame)
            else:
                draw_cloudy_animation(draw, frame)
        elif temperature_avg <= 30:
            # Warm weather - show sunny or light clouds
            if pop_avg >= 90:
                draw_cloudburst_animation(draw, frame)
            elif pop_avg >= 70:
                draw_rainy_animation(draw, frame)
            elif pop_avg >= 50:
                draw_partly_cloudy_animation(draw, frame)
            elif pop_avg >= 30:
                draw_windy_animation(draw, frame)
            elif pop_avg >= 10:
                draw_light_rain_animation(draw, frame)
            else:
                draw_sunny_animation(draw, frame)
        elif temperature_avg <= 35:
            # Hot weather - show bright sun or heat effects
            if pop_avg >= 80:
                draw_rainy_animation(draw, frame)
            elif pop_avg >= 60:
                draw_partly_cloudy_animation(draw, frame)
            elif pop_avg >= 40:
                draw_windy_animation(draw, frame)
            elif temperature_avg >= 33:
                draw_heat_burst_animation(draw, frame)
            elif pop_avg >= 10:
                draw_light_rain_animation(draw, frame)
            else:
                draw_sunny_animation(draw, frame)
        else:
            # Very hot weather - show extreme heat
            if pop_avg >= 70:
                draw_rainy_animation(draw, frame)
            elif temperature_avg >= 40:
                draw_heat_burst_animation(draw, frame)
            else:
                draw_heat_wave_animation(draw, frame)
        
        # Special weather conditions (rare but dramatic)
        if special_weather == 0:
            # Rainbow (after rain)
            if pop_avg >= 50 and temperature_avg >= 15:
                draw_rainbow_animation(draw, frame)
        elif special_weather == 1:
            # Aurora borealis (very rare, cold weather)
            if temperature_avg <= 5:
                draw_aurora_animation(draw, frame)
        elif special_weather == 2:
            # Meteor shower (very rare)
            draw_meteor_animation(draw, frame)
        elif special_weather == 3:
            # Solar flare (very rare, hot weather)
            if temperature_avg >= 30:
                draw_solar_flare_animation(draw, frame)
        elif special_weather == 4:
            # Tornado (rare, stormy weather)
            if pop_avg >= 80 and 15 <= temperature_avg <= 30:
                draw_tornado_animation(draw, frame)
        elif special_weather == 5:
            # Cyclone (rare, stormy weather)
            if pop_avg >= 85 and 20 <= temperature_avg <= 35:
                draw_cyclone_animation(draw, frame)
        elif special_weather == 6:
            # Sandstorm (rare, hot dry weather)
            if temperature_avg >= 35 and pop_avg <= 20:
                draw_sandstorm_animation(draw, frame)
        elif special_weather == 7:
            # Dust devil (rare, hot dry weather)
            if temperature_avg >= 30 and pop_avg <= 30:
                draw_dust_devil_animation(draw, frame)
        elif special_weather == 8:
            # Volcano eruption (very rare)
            draw_volcano_animation(draw, frame)
        elif special_weather == 9:
            # Tsunami (very rare)
            draw_tsunami_animation(draw, frame)
        elif special_weather == 10:
            # Earthquake (very rare)
            draw_earthquake_animation(draw, frame)

def draw_sun_icon(draw, frame=0):
    """Animated sun icon: center block with alternating cardinal/diagonal ray dots"""
    # Center circle (4x4 at positions 2-5)
    for y in range(2, 6):
        for x in range(2, 6):
            draw.point((x, y), fill="white")
    # Alternate between cardinal directions and diagonal directions each frame
    if frame % 2 == 0:
        # Cardinal directions (N, E, S, W)
        draw.point((3, 0), fill="white")
        draw.point((4, 0), fill="white")
        draw.point((7, 3), fill="white")
        draw.point((7, 4), fill="white")
        draw.point((4, 7), fill="white")
        draw.point((3, 7), fill="white")
        draw.point((0, 4), fill="white")
        draw.point((0, 3), fill="white")
    else:
        # Diagonal directions (NE, SE, SW, NW)
        draw.point((7, 1), fill="white")
        draw.point((7, 6), fill="white")
        draw.point((0, 6), fill="white")
        draw.point((0, 1), fill="white")

def draw_cloud_icon(draw, frame=0):
    """Animated cloud icon: gently drifts left and right"""
    # Drift pattern: 0, +1, +1, 0, 0, -1, -1, 0 repeating
    drift_pattern = [0, 1, 1, 0, 0, -1, -1, 0]
    dx = drift_pattern[frame % 8]
    cloud_pixels = [
        (2,0),(3,0),(4,0),
        (1,1),(2,1),(3,1),(4,1),(5,1),(6,1),
        (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),
        (0,3),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),
        (1,4),(2,4),(3,4),(4,4),(5,4),(6,4),
    ]
    for (x, y) in cloud_pixels:
        nx = x + dx
        if 0 <= nx <= 7:
            draw.point((nx, y), fill="white")

def draw_umbrella_icon(draw, frame=0):
    """Animated umbrella icon: raindrops fall with staggered phase per column"""
    # Static umbrella canopy
    canopy = [
        (1,0),(2,0),(3,0),(4,0),(5,0),(6,0),
        (0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),
        (0,2),(7,2),
    ]
    for (x, y) in canopy:
        draw.point((x, y), fill="white")
    # Stem
    draw.point((3, 3), fill="white")
    draw.point((3, 4), fill="white")
    draw.point((3, 5), fill="white")
    # Handle curve
    draw.point((3, 6), fill="white")
    draw.point((2, 7), fill="white")
    # Animated raindrops: 4 columns, each column has a phase offset so they stagger
    rain_cols = [0, 2, 5, 7]
    for i, col in enumerate(rain_cols):
        # Each column's drop y cycles 3..7, with a phase offset per column
        drop_y = (frame + i * 2) % 5 + 3
        if 3 <= drop_y <= 7:
            draw.point((col, drop_y), fill="white")


def draw_digit(draw, digit, x_offset, y_offset):
    """Draw a single digit/character in 3x5 pixel font.
    
    Args:
        draw: PIL ImageDraw object.
        digit: Character to draw (0-9, space, °, %, -, :).
        x_offset: X position on the 8x8 matrix.
        y_offset: Y position on the 8x8 matrix.
    """
    if digit in DIGIT_FONT:
        pattern = DIGIT_FONT[digit]
        for y, row in enumerate(pattern):
            for x, pixel in enumerate(row):
                if pixel:
                    draw.point((x_offset + x, y_offset + y), fill="white")


def _set_brightness():
    """Set LED brightness based on current time of day."""
    current_hour = datetime.now().hour
    brightness = get_brightness_for_time(current_hour)
    device.contrast(brightness)


def display_ticker(temp_max, temp_min, pop_max, scroll_offset):
    """Display scrolling ticker showing temperature range and precipitation.
    
    Format: 'HH-LL PP%' (e.g., '28-18 30%')
    """
    _set_brightness()
    message = f"{temp_max}-{temp_min} {pop_max}%"
    
    with canvas(device) as draw:
        x_pos = 8 - scroll_offset
        for char in message:
            if -3 <= x_pos < 8:
                draw_digit(draw, char, x_pos, 1)
            x_pos += 4


def display_icon(temp_max, temp_min, pop_max, frame):
    """Display animated weather icon based on 24h forecast."""
    _set_brightness()
    
    with canvas(device) as draw:
        if pop_max >= 50:
            draw_umbrella_icon(draw, frame)
        elif pop_max >= 20:
            draw_cloud_icon(draw, frame)
        else:
            draw_sun_icon(draw, frame)


def display_demo(carousel_mode, temp_max, temp_min, pop_max, sec_elapsed, index_col, scroll_offset):
    """Demo/debug mode: scroll a status message showing key state variables.
    
    Format: 'M:3 T:28-18 P:30% C:3'
    """
    _set_brightness()
    message = f"M:{carousel_mode} T:{temp_max}-{temp_min} P:{pop_max}% C:{index_col}"
    with canvas(device) as draw:
        x_pos = 8 - scroll_offset
        for char in message:
            if -3 <= x_pos < 8:
                draw_digit(draw, char, x_pos, 1)
            x_pos += 4


def display_heights(scan_step, heights, pop_format, index_col):
    """Display bargraph with scan animation for current time period.
    
    Args:
        scan_step: 0-7 for scan animation, >=8 for normal display.
        heights: List of 8 temperature bar heights.
        pop_format: List of 8 precipitation indicator values.
        index_col: Current time period column index.
    """
    _set_brightness()
    
    with canvas(device) as draw:
        for i in range(8):
            if i == index_col and scan_step < 8:
                # Scan animation: light up rows from bottom (7) upward
                for row in range(7, max(7 - scan_step - 1, -1), -1):
                    draw.point((i, row), fill="white")
            else:
                # Normal bargraph column
                height = heights[i] if i < len(heights) else 0
                for j in range(height):
                    draw.point((i, 7 - j - 1), fill="white")
                if i < len(pop_format) and pop_format[i] == 1:
                    draw.point((i, 7), fill="white")


# ============================================================
# SIGNAL HANDLING & CLEANUP
# ============================================================

_running = True


def _signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global _running
    logger.info("Received signal %s, shutting down...", signum)
    _running = False


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


# ============================================================
# MAIN LOOP
# ============================================================

def main():
    """Main application entry point."""
    global _running
    
    # Validate configuration
    auth = _validate_config()
    # Store auth in module scope for get_weather_forecast
    global Authorization
    Authorization = auth
    
    logger.info("=" * 60)
    logger.info("😊  Cute Weather Display Starting...")
    logger.info("=" * 60)
    logger.info("Token found! Starting with cute smiley animations! 🎉")
    logger.info("Location: %s", LOCATION_NAME)
    logger.info("=" * 60)
    
    # Print API URLs for debugging
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
    hour_str = _format_hour(now)
    
    temp_url = _build_api_url(API_DATASET_TEMP, Authorization, 'T', today, hour_str, tomorrow, hour_str)
    pop_url = _build_api_url(API_DATASET_POP, Authorization, 'PoP6h', today, hour_str, tomorrow, hour_str)
    logger.info("🔗 API URLs:")
    logger.info("Temperature: %s", temp_url)
    logger.info("Precipitation: %s", pop_url)
    logger.info("=" * 60)
    
    # Show startup logo
    # START_LOGO()
    
    # ---- Main state ----
    sec = UPDATE_INTERVAL_MINS * 60 + 1  # force immediate update on first iteration
    t_format = []
    pop_format = []
    t_raw = DEFAULT_T_RAW[:]
    pop_raw = DEFAULT_POP_RAW[:]
    temp_max = 25
    temp_min = 18
    pop_max = DEFAULT_POP
    
    carousel_mode = MODE_BARGRAPH
    carousel_timer = 0.0
    animation_frame = 0
    ticker_scroll = 0
    ticker_completed_cycle = False
    
    # Scan state for bargraph
    scan_step = 0
    blink_timer = 0.0
    
    # Demo mode scroll state
    demo_scroll = 0
    demo_completed_cycle = False
    
    index_col = 0
    pop_index_col = 0
    
    while _running:
        try:
            # --- Weather data update ---
            if sec >= UPDATE_INTERVAL_MINS * 60:
                now = datetime.now()
                this_hour = now.hour
                logger.info("Updating weather data at %02d:00", this_hour)
                show_data_update_animation()
                result = get_weather_forecast(now)
                t_format, pop_format, t_raw, pop_raw = result
                index_col = calculate_output(this_hour)
                pop_index_col = calculate_output_forPoP(this_hour)
                t_format = shift_array(t_format, index_col)
                pop_format = shift_array(pop_format, pop_index_col)
                if t_raw:
                    temp_max = max(t_raw)
                    temp_min = min(t_raw)
                if pop_raw:
                    pop_max = max(pop_raw)
                logger.info("Temp max=%d min=%d, PoP max=%d%%", temp_max, temp_min, pop_max)
                if DEMO_MODE:
                    logger.debug("[DEMO] IndexCol=%d PoPIndexCol=%d T_format=%s PoP_format=%s",
                                 index_col, pop_index_col, t_format, pop_format)
                sec = 0

            # --- Mode switching ---
            can_switch = carousel_timer >= MODE_DURATIONS.get(carousel_mode, TICKER_DURATION)
            if carousel_mode == MODE_TICKER:
                can_switch = can_switch and ticker_completed_cycle
            if carousel_mode == MODE_DEMO:
                can_switch = can_switch and demo_completed_cycle
            if can_switch:
                carousel_timer = 0.0
                carousel_mode = (carousel_mode + 1) % NUM_MODES
                ticker_scroll = 0
                ticker_completed_cycle = False
                demo_scroll = 0
                demo_completed_cycle = False
                scan_step = 0
                blink_timer = 0.0
                animation_frame = 0
                logger.info("Switching to mode: %s", MODE_NAMES[carousel_mode])
                if DEMO_MODE:
                    logger.debug("[DEMO] State — temp_max=%d temp_min=%d pop_max=%d%% "
                                 "IndexCol=%d sec_elapsed=%d",
                                 temp_max, temp_min, pop_max, index_col, int(sec))

            # --- Display current mode ---
            if carousel_mode == MODE_BARGRAPH:
                sleep_t = BARGRAPH_SCAN_SPEED if scan_step < 8 else BLINK_LONG_SECS
                display_heights(scan_step, t_format, pop_format, index_col)
                time.sleep(sleep_t)
                blink_timer += sleep_t
                carousel_timer += sleep_t
                sec += sleep_t
                scan_step += 1
                if scan_step > 8:
                    scan_step = 0

            elif carousel_mode == MODE_TICKER:
                message = f"{temp_max}-{temp_min} {pop_max}%"
                ticker_total_width = len(message) * 4 + 8
                display_ticker(temp_max, temp_min, pop_max, ticker_scroll)
                ticker_scroll += 1
                if ticker_scroll >= ticker_total_width:
                    ticker_scroll = 0
                    ticker_completed_cycle = True
                time.sleep(TICKER_SCROLL_SPEED)
                carousel_timer += TICKER_SCROLL_SPEED
                sec += TICKER_SCROLL_SPEED

            elif carousel_mode == MODE_ICON:
                animation_frame += 1
                display_icon(temp_max, temp_min, pop_max, animation_frame)
                time.sleep(ICON_ANIMATION_SPEED)
                carousel_timer += ICON_ANIMATION_SPEED
                sec += ICON_ANIMATION_SPEED

            elif carousel_mode == MODE_DEMO:
                demo_message = f"M:{carousel_mode} T:{temp_max}-{temp_min} P:{pop_max}% C:{index_col}"
                demo_total_width = len(demo_message) * 4 + 8
                display_demo(carousel_mode, temp_max, temp_min, pop_max, sec, index_col, demo_scroll)
                demo_scroll += 1
                if demo_scroll >= demo_total_width:
                    demo_scroll = 0
                    demo_completed_cycle = True
                time.sleep(TICKER_SCROLL_SPEED)
                carousel_timer += TICKER_SCROLL_SPEED
                sec += TICKER_SCROLL_SPEED

        except Exception as e:
            logger.error("Main loop error: %s", e)
            time.sleep(1)
            sec += 1
    
    # Cleanup on exit
    logger.info("Shutting down display...")
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, fill="black")
    logger.info("Goodbye!")


if __name__ == '__main__':
    main()

