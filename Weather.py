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
import subprocess
import os
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

# Git pull checking function
def check_git_updates():
    """Check if there are remote updates and restart service if needed"""
    try:
        # Change to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        # Check if we're in a git repository
        if not os.path.exists('.git'):
            return False
            
        # Fetch latest changes from remote
        result = subprocess.run(['git', 'fetch'], capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"Git fetch failed: {result.stderr}")
            return False
            
        # Check if there are updates
        result = subprocess.run(['git', 'rev-list', 'HEAD..origin/HEAD', '--count'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            commit_count = int(result.stdout.strip())
            if commit_count > 0:
                print(f"Found {commit_count} new commits. Restarting service...")
                
                # Stop the weather service
                subprocess.run(['sudo', 'systemctl', 'stop', 'weather.service'], 
                             capture_output=True, timeout=10)
                
                # Pull the latest changes
                result = subprocess.run(['git', 'pull'], capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print("Git pull successful. Running install script...")
                    
                    # Run the install script
                    install_result = subprocess.run(['./install.sh'], 
                                                  capture_output=True, text=True, timeout=120)
                    if install_result.returncode == 0:
                        print("Install script completed successfully.")
                        return True
                    else:
                        print(f"Install script failed: {install_result.stderr}")
                        return False
                else:
                    print(f"Git pull failed: {result.stderr}")
                    return False
        return False
    except Exception as e:
        print(f"Error checking git updates: {e}")
        return False

# Access the Authorization value from the configuration
Authorization = WeatherAPI['Authorization'].strip()  # Remove any whitespace
if not Authorization or Authorization == '' or Authorization == 'CWA-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX':
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
    print("=" * 60)
    print("🔗 Example API URLs (replace YOUR_TOKEN_HERE with actual token):")
    TODAY_Date = datetime.now()
    today = TODAY_Date.strftime('%Y-%m-%d')
    tomorrow = (TODAY_Date + timedelta(days=1)).strftime('%Y-%m-%d')
    NowTime = ("0" if(TODAY_Date.hour<10) else "" )+ str(TODAY_Date.hour)
    
    temp_url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization=YOUR_TOKEN_HERE&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=T&timeFrom={today}T{NowTime}%3A00%3A00&timeTo={tomorrow}T{NowTime}%3A00%3A00'
    pop_url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization=YOUR_TOKEN_HERE&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=PoP6h&timeFrom={today}T{NowTime}%3A00%3A00&timeTo={tomorrow}T{NowTime}%3A00%3A00'
    print("Temperature API:", temp_url)
    print("Precipitation API:", pop_url)
    print("=" * 60)
    exit()
else:
    print("=" * 60)
    print("😊  Cute Weather Display Starting...")
    print("=" * 60)
    print("Token found! Skipping token input step.")
    print("Starting with cute smiley animations! 🎉")
    print("=" * 60)
    
    # Print API URLs for debugging
    TODAY_Date = datetime.now()
    today = TODAY_Date.strftime('%Y-%m-%d')
    tomorrow = (TODAY_Date + timedelta(days=1)).strftime('%Y-%m-%d')
    NowTime = ("0" if(TODAY_Date.hour<10) else "" )+ str(TODAY_Date.hour)
    
    print("🔗 API URLs with token:")
    print("Temperature API:")
    temp_url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization={Authorization}&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=T&timeFrom={today}T{NowTime}%3A00%3A00&timeTo={tomorrow}T{NowTime}%3A00%3A00'
    print(temp_url)
    print("Precipitation API:")
    pop_url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization={Authorization}&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=PoP6h&timeFrom={today}T{NowTime}%3A00%3A00&timeTo={tomorrow}T{NowTime}%3A00%3A00'
    print(pop_url)
    print("=" * 60)

def filter_3hour_intervals(temp_list, pop_list, temp_data, pop_data, current_time):
    """
    過濾出3小時間隔的資料
    從當前時間開始，每3小時取一個資料點
    """
    filtered_temp = []
    filtered_pop = []
    
    if not temp_data or not pop_data:
        return temp_list[:8], pop_list[:8]
    
    # 獲取當前時間
    current_hour = current_time.hour
    current_date = current_time.strftime('%Y-%m-%d')
    
    # 計算3小時間隔的時間點
    three_hour_intervals = []
    for i in range(8):  # 取8個時間點
        hour = (current_hour + i * 3) % 24
        day_offset = (current_hour + i * 3) // 24
        target_date = (current_time + timedelta(days=day_offset)).strftime('%Y-%m-%d')
        target_time = f"{target_date}T{hour:02d}:00:00"
        three_hour_intervals.append(target_time)
    
    print(f"3-hour intervals to filter: {three_hour_intervals}")
    
    # 從溫度資料中過濾
    temp_dict = {}
    if temp_data:
        for item in temp_data:
            start_time = item.get('StartTime', '')
            end_time = item.get('EndTime', '')
            element_value = item['ElementValue'][0]
            if 'Temperature' in element_value:
                temp_value = element_value['Temperature']
                # 使用開始時間作為鍵
                temp_dict[start_time] = temp_value
                print(f"Temperature data point: {start_time} -> {temp_value}")
    
    # 從降雨機率資料中過濾
    pop_dict = {}
    if pop_data:
        for item in pop_data:
            start_time = item.get('StartTime', '')
            end_time = item.get('EndTime', '')
            element_value = item['ElementValue'][0]
            pop_value = None
            
            # 尋找降雨機率值
            for key in ['PoP12h', 'PoP6h', 'PoP', 'Precipitation']:
                if key in element_value:
                    pop_value = element_value[key]
                    break
            
            if pop_value is not None:
                pop_dict[start_time] = pop_value
                print(f"Precipitation data point: {start_time} -> {pop_value}")
    
    # 為每個3小時間隔尋找最接近的資料
    for target_time in three_hour_intervals:
        # 尋找最接近的溫度資料
        temp_value = None
        for time_key, value in temp_dict.items():
            # 處理API返回的時間格式 (包含時區信息)
            clean_time_key = time_key.split('+')[0] if '+' in time_key else time_key
            if target_time in clean_time_key or clean_time_key in target_time:
                temp_value = value
                break
        
        if temp_value is None:
            # 如果找不到精確匹配，使用預設值
            temp_value = '22'
        
        filtered_temp.append(temp_value)
        
        # 尋找最接近的降雨機率資料
        pop_value = None
        for time_key, value in pop_dict.items():
            # 處理API返回的時間格式 (包含時區信息)
            clean_time_key = time_key.split('+')[0] if '+' in time_key else time_key
            if target_time in clean_time_key or clean_time_key in target_time:
                pop_value = value
                break
        
        if pop_value is None:
            # 如果找不到精確匹配，使用預設值
            pop_value = '20'
        
        filtered_pop.append(pop_value)
    
    print(f"Filtered temperature values: {filtered_temp}")
    print(f"Filtered precipitation values: {filtered_pop}")
    
    return filtered_temp, filtered_pop

# 定義函式，從交通部氣象局網站獲取當天天氣預報
def get_weather_forecast(TODAY_Date):
    # 獲取當天日期
    delat = 0
    today = (TODAY_Date+ timedelta(days=delat)).strftime('%Y-%m-%d')
    tomorrow = (TODAY_Date+ timedelta(days=delat+1)).strftime('%Y-%m-%d')
    print(today + " ~ " + tomorrow)
    
    NowTime = ("0" if(TODAY_Date.hour<10) else "" )+ str(TODAY_Date.hour)
    print(f"Current time: {NowTime}")
    
    # 計算3小時間隔的時間點
    current_hour = TODAY_Date.hour
    # 找到下一個3小時間隔的時間點 (0, 3, 6, 9, 12, 15, 18, 21)
    next_3hour = ((current_hour // 3) + 1) * 3
    if next_3hour >= 24:
        next_3hour = 0
        tomorrow = (TODAY_Date + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 設定時間範圍為未來24小時，每3小時一個間隔
    time_from = f"{today}T{NowTime}:00:00"
    time_to = f"{tomorrow}T{NowTime}:00:00"
    
    print(f"Time range: {time_from} to {time_to}")
    
    # 使用F-D0047-061 API - 臺灣各縣市鄉鎮未來1週逐12小時天氣預報
    # 獲取多個天氣元素：溫度、體感溫度、降雨機率、天氣現象、相對濕度、風速、風向
    elements = ['T', 'AT', 'PoP12h', 'Wx', 'RH', 'WS', 'WD']
    element_names = ','.join(elements)
    
    # 構建API URL
    url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization={Authorization}&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName={element_names}&timeFrom={time_from}&timeTo={time_to}'
    
    print(f"API URL: {url}")
    
    # 備用API URLs for individual elements if needed
    url_temp = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization={Authorization}&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=T&timeFrom={time_from}&timeTo={time_to}'
    url_pop = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061?Authorization={Authorization}&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=PoP12h&timeFrom={time_from}&timeTo={time_to}'
    
    try:
        # 首先嘗試獲取包含所有元素的綜合資料
        response = requests.get(url, verify=False, timeout=10)
        data = response.json()
        print("Full API response:", data)
        
        T_data = None
        PoPdata = None
        
        # 檢查API回應是否有效
        if (data.get("success") == "true" and 
            "records" in data and 
            "Locations" in data["records"] and 
            len(data["records"]["Locations"]) > 0 and
            "Location" in data["records"]["Locations"][0] and
            len(data["records"]["Locations"][0]["Location"]) > 0):
            
            location_data = data["records"]["Locations"][0]["Location"][0]
            weather_elements = location_data["WeatherElement"]
            
            # 從綜合資料中提取溫度和降雨機率資料
            for element in weather_elements:
                element_name = element.get("elementName", "Unknown")
                print(f"Processing element: {element_name}")
                
                if element_name == "T":  # 溫度
                    T_data = element["Time"]
                    print("Temperature data:", T_data)
                elif element_name == "PoP12h":  # 12小時降雨機率
                    PoPdata = element["Time"]
                    print("Precipitation data:", PoPdata)
                elif "ProbabilityOfPrecipitation" in str(element.get("Time", [])):  # 降雨機率
                    PoPdata = element["Time"]
                    print("Precipitation data (ProbabilityOfPrecipitation):", PoPdata)
        
        # 如果綜合API失敗，嘗試個別API
        if T_data is None:
            print("Trying individual temperature API...")
            response_temp = requests.get(url_temp, verify=False, timeout=10)
            data_temp = response_temp.json()
            
            if (data_temp.get("success") == "true" and 
                "records" in data_temp and 
                "Locations" in data_temp["records"] and 
                len(data_temp["records"]["Locations"]) > 0 and
                "Location" in data_temp["records"]["Locations"][0] and
                len(data_temp["records"]["Locations"][0]["Location"]) > 0):
                
                T_data = data_temp["records"]["Locations"][0]["Location"][0]["WeatherElement"][0]["Time"]
                print("Individual temperature data:", T_data)
            else:
                print("Temperature API returned empty data, using fallback")
                T_data = [{'ElementValue': [{'Temperature': '22'}]} for _ in range(8)]
        
        if PoPdata is None:
            print("Trying individual precipitation API...")
            response_pop = requests.get(url_pop, verify=False, timeout=10)
            data_pop = response_pop.json()
            
            if (data_pop.get("success") == "true" and 
                "records" in data_pop and 
                "Locations" in data_pop["records"] and 
                len(data_pop["records"]["Locations"]) > 0 and
                "Location" in data_pop["records"]["Locations"][0] and
                len(data_pop["records"]["Locations"][0]["Location"]) > 0):
                
                PoPdata = data_pop["records"]["Locations"][0]["Location"][0]["WeatherElement"][0]["Time"]
                print("Individual precipitation data:", PoPdata)
            else:
                print("Precipitation API returned empty data, using fallback")
                PoPdata = None
        
        # 從資料中提取出每個時間段的數值
        TDataList = []
        if T_data:
            for d in T_data:
                element_value = d['ElementValue'][0]
                if 'Temperature' in element_value:
                    TDataList.append(element_value['Temperature'])
                else:
                    # 如果沒有找到溫度資料，使用預設值
                    TDataList.append('22')
        else:
            TDataList = ['22'] * 8
            
        print("Temperature values:", TDataList)
        
        # 處理降雨機率資料
        PopDataList = []
        if PoPdata:
            print("Raw PoP data structure:", [d['ElementValue'] for d in PoPdata])
            print("Available field names in PoP data:", [list(d['ElementValue'][0].keys()) for d in PoPdata])
            
            # 提取降雨機率資料
            for d in PoPdata:
                element_value = d['ElementValue'][0]
                print(f"Processing element value: {element_value}")
                
                # 尋找降雨機率相關欄位名稱
                if 'ProbabilityOfPrecipitation' in element_value:
                    PopDataList.append(element_value['ProbabilityOfPrecipitation'])
                    print(f"Found ProbabilityOfPrecipitation data: {element_value['ProbabilityOfPrecipitation']}")
                elif 'PoP12h' in element_value:
                    PopDataList.append(element_value['PoP12h'])
                    print(f"Found PoP12h data: {element_value['PoP12h']}")
                elif 'PoP6h' in element_value:
                    PopDataList.append(element_value['PoP6h'])
                    print(f"Found PoP6h data: {element_value['PoP6h']}")
                elif 'PoP' in element_value:
                    PopDataList.append(element_value['PoP'])
                    print(f"Found PoP data: {element_value['PoP']}")
                elif 'Precipitation' in element_value:
                    PopDataList.append(element_value['Precipitation'])
                    print(f"Found Precipitation data: {element_value['Precipitation']}")
                else:
                    # 如果沒有找到降雨機率欄位，使用預設值
                    print(f"Warning: No precipitation data found in {element_value}, using default value 0")
                    PopDataList.append('0')
        else:
            print("No precipitation data available, using fallback values")
            # 使用預設降雨機率資料
            PopDataList = ['20', '30', '25', '35', '40', '30', '25', '20']
        
        print("Precipitation values:", PopDataList)
        
        # 過濾出3小時間隔的資料
        filtered_temp, filtered_pop = filter_3hour_intervals(TDataList, PopDataList, T_data, PoPdata, TODAY_Date)
        
        return temperature_to_led_levels(filtered_temp), PoP_to_led_levels(filtered_pop)
        
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        # 返回預設值
        return [4, 4, 4, 4, 4, 4, 4, 4], [0, 0, 0, 0, 0, 0, 0, 0]



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
    """Convert precipitation probability to LED levels with better scaling"""
    try:
        Pop = [int(t) for t in Pop]
        levels = []
        # Use different thresholds for better visualization
        for p in Pop:
            if p >= 80:  # High probability
                levels.append(1)
                levels.append(1)
            elif p >= 60:  # Medium-high probability
                levels.append(1)
                levels.append(0)
            elif p >= 40:  # Medium probability
                levels.append(0)
                levels.append(1)
            elif p >= 20:  # Low probability
                levels.append(0)
                levels.append(0)
            else:  # Very low probability
                levels.append(0)
                levels.append(0)
        return levels
    except Exception as e:
        print(f"Error in PoP_to_led_levels: {e}")
        return [0, 0, 0, 0, 0, 0, 0, 0]

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
    """Draw weather animation based on temperature and precipitation with more detailed conditions"""
    current_hour = datetime.now().hour
    brightness = get_brightness_for_time(current_hour)
    device.contrast(brightness)
    
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
                    
                    # Check if temperature data is valid
                    if (data_t.get("success") == "true" and 
                        "records" in data_t and 
                        "Locations" in data_t["records"] and 
                        len(data_t["records"]["Locations"]) > 0 and
                        "Location" in data_t["records"]["Locations"][0] and
                        len(data_t["records"]["Locations"][0]["Location"]) > 0):
                        T_data_raw = [list(d['ElementValue'][0].values())[0] for d in data_t["records"]["Locations"][0]["Location"][0]["WeatherElement"][0]["Time"][:8]]
                    else:
                        print("Temperature API returned empty data for ticker, using fallback")
                        T_data_raw = ['22', '23', '24', '25', '24', '23', '22', '21']
                
                if not PoP_data_raw:
                    response_p = requests.get(url_pop, verify=False, timeout=5)
                    data_p = response_p.json()
                    
                    # Check if precipitation data is valid
                    if (data_p.get("success") == "true" and 
                        "records" in data_p and 
                        "Locations" in data_p["records"] and 
                        len(data_p["records"]["Locations"]) > 0 and
                        "Location" in data_p["records"]["Locations"][0] and
                        len(data_p["records"]["Locations"][0]["Location"]) > 0):
                        PoP_data_raw = [list(d['ElementValue'][0].values())[0] for d in data_p["records"]["Locations"][0]["Location"][0]["WeatherElement"][0]["Time"][:4]]
                    else:
                        print("Precipitation API returned empty data for ticker, using fallback")
                        PoP_data_raw = ['20', '30', '25', '35']
                
                display_ticker(T_data_raw, PoP_data_raw, ticker_scroll)
                ticker_scroll += 1
                if ticker_scroll > TICKER_FULL_CYCLE:  # Reset scroll after full cycle
                    ticker_scroll = TICKER_FULL_CYCLE  # Keep at max to signal completion
                    
            except Exception as e:
                print(f"Ticker error: {e}")
                # Use fallback data instead of switching modes
                if not T_data_raw:
                    T_data_raw = ['22', '23', '24', '25', '24', '23', '22', '21']
                if not PoP_data_raw:
                    PoP_data_raw = ['20', '30', '25', '35']
                display_ticker(T_data_raw, PoP_data_raw, ticker_scroll)
                ticker_scroll += 1
                if ticker_scroll > TICKER_FULL_CYCLE:
                    ticker_scroll = TICKER_FULL_CYCLE
                
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

    


