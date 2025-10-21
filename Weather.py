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
CAROUSEL_DURATION = 10  # seconds per mode

Authorization = ''
# Access the Authorization value from the configuration
Authorization = WeatherAPI['Authorization']
if Authorization == '':
    print("You need to confirm whether the config.py in the same folder exists and whether you have entered the correct Authorization")
    exit()

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
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.ellipse([(0, 0), (7, 7)], outline="white", fill="black")
        draw.ellipse([(2, 2), (5, 5)], outline="white", fill="black")
    time.sleep(0.5)
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

def draw_sunny_animation(draw, frame):
    """Draw sunny weather animation - sun with rays"""
    # Sun center
    draw.ellipse([(2, 2), (5, 5)], outline="white", fill="white")
    # Animated rays
    if frame % 2 == 0:
        draw.point((1, 1), fill="white")
        draw.point((6, 1), fill="white")
        draw.point((1, 6), fill="white")
        draw.point((6, 6), fill="white")
    draw.point((3, 0), fill="white")
    draw.point((4, 0), fill="white")
    draw.point((3, 7), fill="white")
    draw.point((4, 7), fill="white")
    draw.point((0, 3), fill="white")
    draw.point((0, 4), fill="white")
    draw.point((7, 3), fill="white")
    draw.point((7, 4), fill="white")

def draw_cloudy_animation(draw, frame):
    """Draw cloudy weather animation - moving clouds"""
    offset = frame % 2
    # Cloud 1
    draw.point((1+offset, 2), fill="white")
    draw.point((2+offset, 1), fill="white")
    draw.point((3+offset, 1), fill="white")
    draw.point((4+offset, 2), fill="white")
    # Cloud 2
    draw.point((2, 5), fill="white")
    draw.point((3, 4), fill="white")
    draw.point((4, 4), fill="white")
    draw.point((5, 5), fill="white")

def draw_rainy_animation(draw, frame):
    """Draw rainy weather animation - cloud with falling rain"""
    # Cloud
    draw.point((2, 1), fill="white")
    draw.point((3, 0), fill="white")
    draw.point((4, 0), fill="white")
    draw.point((5, 1), fill="white")
    # Falling rain drops (animated)
    rain_y = (frame % 4)
    for x in [1, 3, 5]:
        y = 3 + rain_y
        if y < 8:
            draw.point((x, y), fill="white")
    for x in [2, 4, 6]:
        y = 4 + rain_y
        if y < 8:
            draw.point((x, y), fill="white")

def draw_thunderstorm_animation(draw, frame):
    """Draw thunderstorm animation - cloud with lightning"""
    # Cloud
    draw.point((2, 0), fill="white")
    draw.point((3, 0), fill="white")
    draw.point((4, 0), fill="white")
    draw.point((1, 1), fill="white")
    draw.point((5, 1), fill="white")
    # Lightning (flashing)
    if frame % 3 == 0:
        draw.point((3, 2), fill="white")
        draw.point((2, 3), fill="white")
        draw.point((3, 4), fill="white")
        draw.point((4, 5), fill="white")
        draw.point((3, 6), fill="white")

def draw_weather_animation(temperature_avg, pop_avg, frame):
    """Draw weather animation based on temperature and precipitation"""
    current_hour = datetime.now().hour
    brightness = get_brightness_for_time(current_hour)
    device.contrast(brightness)
    
    with canvas(device) as draw:
        if pop_avg >= 60:
            if pop_avg >= 80:
                draw_thunderstorm_animation(draw, frame)
            else:
                draw_rainy_animation(draw, frame)
        elif temperature_avg >= 28:
            draw_sunny_animation(draw, frame)
        else:
            draw_cloudy_animation(draw, frame)

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
        
        # Carousel mode switching
        carousel_timer += 1
        if carousel_timer >= CAROUSEL_DURATION:
            carousel_timer = 0
            carousel_mode = (carousel_mode + 1) % 3
            ticker_scroll = 0  # Reset ticker scroll
            print(f"Switching to mode: {['ANIMATION', 'TICKER', 'BARGRAPH'][carousel_mode]}")
        
        # Display based on current carousel mode
        if carousel_mode == MODE_ANIMATION:
            # Show cute weather animation
            animation_frame += 1
            if len(T_format) > 0 and len(PoP_format) > 0:
                # Calculate average temperature and precipitation
                temp_avg = sum(T_format) / len(T_format) * 4 + 12  # Convert back to temperature
                pop_values = [p for i, p in enumerate(PoP_format) if i % 2 == 0]
                pop_avg = sum(pop_values) / len(pop_values) * 60 if pop_values else 0
                draw_weather_animation(temp_avg, pop_avg, animation_frame)
            time.sleep(0.2)  # Faster updates for animation
            
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
                if ticker_scroll > 60:  # Reset scroll after full cycle
                    ticker_scroll = 0
                    
            except Exception as e:
                print(f"Ticker error: {e}")
                # Fallback to animation if ticker fails
                carousel_mode = MODE_ANIMATION
                
            time.sleep(0.15)  # Smooth scrolling
            
        elif carousel_mode == MODE_BARGRAPH:
            # Show original bar graph
            display_heights(sec%2, T_format, PoP_format, IndexCol)
            time.sleep(1)
        
        sec += 1
        # TODAY_Date =  (TODAY_Date + timedelta(hours=1))
        
    except Exception as e:
        print("An error occurred:", str(e))
        time.sleep(1)

    


