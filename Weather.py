# commands:
# ps aux | grep SmartWeather.py

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
import time
import requests
from datetime import datetime, timedelta
import sys
import random
# Import the configuration from config.py
from config import WeatherAPI
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Carousel mode constants
MODE_ANIMATION = 0
MODE_TICKER = 1
MODE_BARGRAPH = 2
CAROUSEL_DURATION = 15  # seconds per mode (increased for better viewing)
TICKER_FULL_CYCLE = 80  # frames for complete ticker scroll

# Access the Authorization value from the configuration
Authorization = WeatherAPI['Authorization'].strip()  # Remove any whitespace
if not Authorization or Authorization == '':
    print("=" * 60)
    print("🌤️  Smart Weather Display Setup Required")
    print("=" * 60)
    print("Please configure your CWA authorization token:")
    print("1. Visit: https://opendata.cwa.gov.tw/user/authkey")
    print("2. Get your authorization token")
    print("3. Edit config.py and add your token:")
    print("   WeatherAPI = {'Authorization': 'YOUR_TOKEN_HERE'}")
    print("=" * 60)
    print("If you have already configured the token, please check config.py")
    exit()
else:
    print("=" * 60)
    print("😊  Cute Weather Display Starting...")
    print("=" * 60)
    print("Token found! Skipping token input step.")
    print("Starting with cute smiley animations! 🎉")
    print("=" * 60)

# 定義函式，從交通部氣象局網站獲取當天天氣預報
def get_weather_forecast(TODAY_Date):
    # 獲取當天日期
    delat = 0
    today = (TODAY_Date+ timedelta(days=delat)).strftime('%Y-%m-%d')
    tomorrow = (TODAY_Date+ timedelta(days=delat+1)).strftime('%Y-%m-%d')
    print(today + " ~ " + tomorrow)
    # 組裝 API URL
    type = "T,PoP6h" #溫度(3h)、降雨機率(6h)
    NowTime = ("0" if(TODAY_Date.hour<10) else "" )+ str(TODAY_Date.hour)
    print(NowTime)
    url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization='+Authorization+'&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName='+ type +'&timeFrom='+today+'T'+NowTime+'%3A00%3A00&timeTo='+tomorrow+'T'+NowTime+'%3A00%3A00'
    # 用 requests 套件發送 GET 請求獲取資料
    # print(url)
    response = requests.get(url,verify=False)

    # 解析 JSON 資料
    data = response.json()
    # print(data)
    PoPdata = data["records"]["Locations"][0]["Location"][0]["WeatherElement"][1]["Time"]
    T_data = data["records"]["Locations"][0]["Location"][0]["WeatherElement"][0]["Time"]
    # 從資料中提取出每個時間段的平均溫度
    print(PoPdata)
    print(T_data)

    TDataList = [list(d['ElementValue'][0].values())[0] for d in T_data]
    PopDataList = [list(d['ElementValue'][0].values())[0] for d in PoPdata]
    print(TDataList)
    print(PopDataList)
    return temperature_to_led_levels(TDataList),PoP_to_led_levels(PopDataList)



# 定義函式，將溫度轉換為 8 階層，用於顯示在 8x8 矩陣上
def temperature_to_led_levels(temperature):
    # 將溫度轉換為整數
    temperature = [int(t) for t in temperature]

    # 計算最大和最小值，用於將溫度轉換為 8 階層
    temperature_min = 12
    temperature_max = 33

    # 將溫度轉換為 8 階層
    levels = []
    for t in temperature:
        if t>temperature_max: t = temperature_max
        if t<temperature_min: t = temperature_min
        level = round(7 * (t - temperature_min) / (temperature_max - temperature_min))
        levels.append(level)
    return levels

# NowPoPvalue = -1
def PoP_to_led_levels(Pop):
    Pop = [int(t) for t in Pop]
    levels = []
    PoP_level = 60
    for p in Pop:
        levels.append(round(p>=PoP_level))
        levels.append(round(p>=PoP_level))
    # levels.insert(0,NowPoPvalue if NowPoPvalue!=-1 else levels[0])
    # levels.pop()
    return levels

# initialize SPI interface for the LED matrix
serial = spi(port=0, device=0)
device = max7219(serial, cascaded=1, block_orientation=0, rotate=0)


def START_LOGO():
    """Cute startup animation with smiley faces"""
    # Show different cute smiley faces in sequence
    smiley_animations = [
        # Happy smiley
        lambda draw: draw_happy_smiley(draw, 0),
        # Winking smiley
        lambda draw: draw_winking_smiley(draw, 0),
        # Big smile smiley
        lambda draw: draw_big_smile_smiley(draw, 0),
        # Excited smiley
        lambda draw: draw_excited_smiley(draw, 0)
    ]
    
    for i, smiley_func in enumerate(smiley_animations):
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            smiley_func(draw)
        time.sleep(0.8)
    
    # Fade out effect
    for intensity in list(range(15,0,-1)):
        device.contrast(intensity * 16)
        time.sleep(0.05)
    for intensity in range(16):
        device.contrast(intensity * 16)
        time.sleep(0.05)


def shift_array(data, index):
    start = 8 - index
    end = start + 8
    shifted_data = data[start:end] + data[:start] + data[end:]
    # shifted_data.append(shifted_data.pop(0))
    return shifted_data

def calculate_output(hour):
    if hour in [1, 2, 3]:
        return 0
    elif hour in [4, 5, 6]:
        return 1
    elif hour in [7, 8, 9]:
        return 2
    elif hour in [10, 11, 12]:
        return 3
    elif hour in [13, 14, 15]:
        return 4
    elif hour in [16, 17, 18]:
        return 5
    elif hour in [19, 20, 21]:
        return 6
    elif hour in [22, 23, 0]:
        return 7
    else:
        return 0

def calculate_output_forPoP(hour):
    if hour in [1, 2, 3, 4, 5, 6]:
        return 1
    elif hour in [7, 8, 9, 10, 11, 12]:
        return 3
    elif hour in [13, 14, 15, 16, 17, 18]:
        return 5
    elif hour in [19, 20, 21, 22, 23, 0]:
        return 7
    else:
        return 0

def get_brightness_for_time(hour):
    """Return brightness level based on time (night mode: 12 AM - 6 AM)"""
    if 0 <= hour < 6:  # Night mode: 12 AM to 6 AM
        return 8  # Darker brightness (range 0-255, using 8 for night)
    else:
        return 30  # Normal brightness

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
    """Show cute smiley animation while updating weather data"""
    update_animations = [
        # Thinking smiley
        lambda draw: draw_thinking_smiley(draw, 0),
        # Loading smiley
        lambda draw: draw_loading_smiley(draw, 0),
        # Success smiley
        lambda draw: draw_success_smiley(draw, 0)
    ]
    
    for i, anim_func in enumerate(update_animations):
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            anim_func(draw)
        time.sleep(0.5)

def draw_thinking_smiley(draw, frame):
    """Draw a thinking smiley face"""
    # Face outline
    draw.ellipse([(1, 1), (6, 6)], outline="white", fill="white")
    # Eyes looking up (thinking)
    draw.point((2, 1), fill="black")
    draw.point((5, 1), fill="black")
    # Thinking mouth (straight line)
    draw.point((2, 4), fill="black")
    draw.point((3, 4), fill="black")
    draw.point((4, 4), fill="black")
    draw.point((5, 4), fill="black")
    # Question mark above head
    draw.point((7, 0), fill="white")
    draw.point((7, 1), fill="white")
    draw.point((7, 2), fill="white")
    draw.point((6, 3), fill="white")

def draw_loading_smiley(draw, frame):
    """Draw a loading smiley face with spinning effect"""
    # Face outline
    draw.ellipse([(1, 1), (6, 6)], outline="white", fill="white")
    # Eyes
    draw.point((2, 2), fill="black")
    draw.point((5, 2), fill="black")
    # Loading mouth (dots)
    if frame % 2 == 0:
        draw.point((3, 4), fill="black")
        draw.point((4, 4), fill="black")
    else:
        draw.point((2, 4), fill="black")
        draw.point((5, 4), fill="black")
    # Spinning dots around face
    angle = frame % 8
    if angle < 4:
        draw.point((0, 2 + angle), fill="white")
    else:
        draw.point((7, 2 + (angle - 4)), fill="white")

def draw_success_smiley(draw, frame):
    """Draw a success smiley face with checkmark"""
    # Face outline
    draw.ellipse([(1, 1), (6, 6)], outline="white", fill="white")
    # Happy eyes
    draw.point((2, 2), fill="black")
    draw.point((5, 2), fill="black")
    # Big happy smile
    draw.point((1, 4), fill="black")
    draw.point((2, 5), fill="black")
    draw.point((3, 6), fill="black")
    draw.point((4, 6), fill="black")
    draw.point((5, 5), fill="black")
    draw.point((6, 4), fill="black")
    # Checkmark
    draw.point((7, 1), fill="white")
    draw.point((7, 2), fill="white")
    draw.point((6, 3), fill="white")
    draw.point((5, 4), fill="white")

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

def draw_weather_animation(temperature_avg, pop_avg, frame):
    """Draw weather animation based on temperature and precipitation with more detailed conditions"""
    current_hour = datetime.now().hour
    brightness = get_brightness_for_time(current_hour)
    device.contrast(brightness)
    
    with canvas(device) as draw:
        # More detailed weather condition detection
        if temperature_avg <= 5:
            # Extremely cold - show blizzard
            draw_blizzard_animation(draw, frame)
        elif temperature_avg <= 15:
            # Very cold - show snow with variations
            if pop_avg >= 70:
                draw_heavy_snow_animation(draw, frame)
            else:
                draw_snowy_animation(draw, frame)
        elif temperature_avg <= 20:
            # Cool weather - show overcast or light rain
            if pop_avg >= 80:
                draw_heavy_rain_animation(draw, frame)
            elif pop_avg >= 50:
                draw_rainy_animation(draw, frame)
            else:
                draw_overcast_animation(draw, frame)
        elif temperature_avg <= 25:
            # Mild weather - show partly cloudy or light rain
            if pop_avg >= 80:
                draw_thunderstorm_animation(draw, frame)
            elif pop_avg >= 60:
                draw_rainy_animation(draw, frame)
            elif pop_avg >= 30:
                draw_partly_cloudy_animation(draw, frame)
            else:
                draw_cloudy_animation(draw, frame)
        elif temperature_avg <= 30:
            # Warm weather - show sunny or light clouds
            if pop_avg >= 70:
                draw_rainy_animation(draw, frame)
            elif pop_avg >= 40:
                draw_partly_cloudy_animation(draw, frame)
            else:
                draw_sunny_animation(draw, frame)
        else:
            # Hot weather - show bright sun or heat wave
            if pop_avg >= 60:
                draw_rainy_animation(draw, frame)
            elif temperature_avg >= 35:
                draw_heat_wave_animation(draw, frame)
            else:
                draw_sunny_animation(draw, frame)

def draw_digit(draw, digit, x_offset, y_offset):
    """Draw a single digit (0-9) in 3x5 pixel font"""
    digits = {
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
    }
    
    if digit in digits:
        pattern = digits[digit]
        for y, row in enumerate(pattern):
            for x, pixel in enumerate(row):
                if pixel:
                    draw.point((x_offset + x, y_offset + y), fill="white")

def display_ticker(T_data, PoP_data, scroll_offset):
    """Display scrolling ticker with 24-hour forecast"""
    current_hour = datetime.now().hour
    brightness = get_brightness_for_time(current_hour)
    device.contrast(brightness)
    
    with canvas(device) as draw:
        # Create ticker message
        # Show next few hours forecast
        num_hours = min(3, len(T_data))
        x_pos = 8 - scroll_offset
        
        for i in range(num_hours):
            if i < len(T_data) and i < len(PoP_data):
                temp = str(int(float(T_data[i]))) if i < len(T_data) else "??"
                pop = str(int(float(PoP_data[i//2]))) if i//2 < len(PoP_data) else "?"
                
                # Draw temperature
                for char in temp:
                    if x_pos >= -3 and x_pos < 8:
                        draw_digit(draw, char, x_pos, 1)
                    x_pos += 4
                
                # Draw degree symbol
                if x_pos >= -3 and x_pos < 8:
                    draw_digit(draw, '°', x_pos, 1)
                x_pos += 3
                
                # Space
                x_pos += 2
                
                # Draw precipitation %
                for char in pop:
                    if x_pos >= -3 and x_pos < 8:
                        draw_digit(draw, char, x_pos, 1)
                    x_pos += 4
                
                if x_pos >= -3 and x_pos < 8:
                    draw_digit(draw, '%', x_pos, 1)
                x_pos += 4
                
                # Separator
                x_pos += 3

def display_heights(bool,heights,PoP_format,IndexCol):
    # set the brightness level of the LED matrix based on time
    current_hour = datetime.now().hour
    brightness = get_brightness_for_time(current_hour)
    device.contrast(brightness)
    
    # display the heights on the LED matrix
    with canvas(device) as draw:
        for i in range(8):
            if bool and i==IndexCol:
                continue 
            height = heights[i]
            for j in range(height):
                draw.point((i, 7-j-1), fill="white")
            if PoP_format[i] == 1:
                draw.point((i, 7), fill="white")
# START_LOGO()

sec = 60*40*99
T_format = []
PoP_format = []
T_data_raw = []
PoP_data_raw = []
carousel_mode = MODE_ANIMATION
carousel_timer = 0
animation_frame = 0
ticker_scroll = 0

# TODAY_Date = datetime.now()

while 1:
    try:
        if sec >= 60*40: # 每隔40分鐘更新一次資料
            TODAY_Date = datetime.now()
            # TODAY_Date = datetime.ate + timedelta(hours=0))
            thisHour = TODAY_Date.hour
            print(str(thisHour))
            START_LOGO()
            # Show cute smiley animation while updating data
            show_data_update_animation()
            ArrayData = get_weather_forecast(TODAY_Date)
            print(ArrayData)
            IndexCol = calculate_output(thisHour)
            PoPIndexCol = calculate_output_forPoP(thisHour)
            T_format   = shift_array(ArrayData[0],IndexCol)
            if sec == 60*40*99 or thisHour not in [7,8,9,13,14,15,19,20,21,1,2,3]:
                PoP_format = shift_array(ArrayData[1],PoPIndexCol)
            print(T_format)
            print(PoP_format)
            sys.stdout.flush()
            sec = 0
            
            # Store raw data for ticker display
            T_data_raw = []
            PoP_data_raw = []
        
        # Carousel mode switching with proper timing
        carousel_timer += 1
        
        # Special handling for ticker mode - wait for full cycle completion
        if carousel_mode == MODE_TICKER:
            if ticker_scroll >= TICKER_FULL_CYCLE and carousel_timer >= CAROUSEL_DURATION:
                carousel_timer = 0
                carousel_mode = (carousel_mode + 1) % 3
                ticker_scroll = 0  # Reset ticker scroll
                print(f"Ticker completed, switching to mode: {['ANIMATION', 'TICKER', 'BARGRAPH'][carousel_mode]}")
        else:
            # Normal timing for other modes
            if carousel_timer >= CAROUSEL_DURATION:
                carousel_timer = 0
                carousel_mode = (carousel_mode + 1) % 3
                ticker_scroll = 0  # Reset ticker scroll
                print(f"Switching to mode: {['ANIMATION', 'TICKER', 'BARGRAPH'][carousel_mode]}")
        
        # Display based on current carousel mode
        if carousel_mode == MODE_ANIMATION:
            # Show cute weather animation with smooth transitions
            animation_frame += 1
            if len(T_format) > 0 and len(PoP_format) > 0:
                # Calculate average temperature and precipitation
                temp_avg = sum(T_format) / len(T_format) * 4 + 12  # Convert back to temperature
                pop_values = [p for i, p in enumerate(PoP_format) if i % 2 == 0]
                pop_avg = sum(pop_values) / len(pop_values) * 60 if pop_values else 0
                draw_weather_animation(temp_avg, pop_avg, animation_frame)
            time.sleep(0.3)  # Slower, more pleasant animation speed
            
        elif carousel_mode == MODE_TICKER:
            # Show digital ticker with 24-hour forecast
            # Get raw temperature and precipitation data from API
            TODAY_Date = datetime.now()
            try:
                url_temp = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization={Authorization}&limit=10&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=T'
                url_pop = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization={Authorization}&limit=10&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=PoP6h'
                
                if not T_data_raw:
                    response_t = requests.get(url_temp, verify=False, timeout=5)
                    data_t = response_t.json()
                    T_data_raw = [list(d['ElementValue'][0].values())[0] for d in data_t["records"]["Locations"][0]["Location"][0]["WeatherElement"][0]["Time"][:8]]
                
                if not PoP_data_raw:
                    response_p = requests.get(url_pop, verify=False, timeout=5)
                    data_p = response_p.json()
                    PoP_data_raw = [list(d['ElementValue'][0].values())[0] for d in data_p["records"]["Locations"][0]["Location"][0]["WeatherElement"][0]["Time"][:4]]
                
                display_ticker(T_data_raw, PoP_data_raw, ticker_scroll)
                ticker_scroll += 1
                if ticker_scroll > TICKER_FULL_CYCLE:  # Reset scroll after full cycle
                    ticker_scroll = TICKER_FULL_CYCLE  # Keep at max to signal completion
                    
            except Exception as e:
                print(f"Ticker error: {e}")
                # Fallback to animation if ticker fails
                carousel_mode = MODE_ANIMATION
                
            time.sleep(0.2)  # Smoother scrolling for better readability
            
        elif carousel_mode == MODE_BARGRAPH:
            # Show original bar graph
            display_heights(sec%2, T_format, PoP_format, IndexCol)
            time.sleep(1)
        
        sec += 1
        # TODAY_Date =  (TODAY_Date + timedelta(hours=1))
        
    except Exception as e:
        print("An error occurred:", str(e))
        time.sleep(1)

    


