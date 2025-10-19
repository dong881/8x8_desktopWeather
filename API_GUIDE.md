# 中央氣象署 OpenData API 完整整合指南

## API 端點總覽

### 1. 天氣預報類 (Weather Forecast)

#### F-D0047-061: 鄉鎮天氣預報-臺北市
- **用途**: 取得臺北市各區域未來36小時天氣預報
- **更新頻率**: 每3小時
- **資料內容**: 溫度、降雨機率、天氣現象、舒適度
- **實現狀態**: ✅ 已實現

```python
# 使用範例
data = cwa_client.get_weather_forecast(location="大安區", element_name="T,PoP6h")
```

#### F-C0032-001: 一般天氣預報-今明36小時天氣預報
- **用途**: 全台各縣市今明36小時預報
- **更新頻率**: 每3小時
- **實現狀態**: 🔄 可擴充

#### F-B0053: 精緻化天氣預報
- **用途**: 高解析度網格預報
- **更新頻率**: 每小時
- **實現狀態**: 🔄 可擴充

### 2. 即時觀測類 (Real-time Observation)

#### O-A0001-001: 自動氣象站-氣象觀測資料
- **用途**: 即時溫度、氣壓、風速、降雨量、濕度
- **更新頻率**: 10分鐘
- **資料內容**: 完整氣象站觀測資料
- **實現狀態**: ✅ 已實現

```python
# 使用範例
data = cwa_client.get_observation_data(station_id="466920")  # 台北站
```

#### O-A0002-001: 自動雨量站-雨量觀測資料
- **用途**: 降雨量監測
- **更新頻率**: 10分鐘
- **實現狀態**: 🔄 可擴充

#### O-A0005-001: 紫外線觀測資料
- **用途**: UV指數監測
- **更新頻率**: 1小時
- **實現狀態**: ✅ 已實現

```python
# 使用範例
data = cwa_client.get_uv_index()
```

### 3. 災害警報類 (Disaster Alerts)

#### E-A0015-001: 顯著有感地震報告
- **用途**: 地震後5-10分鐘發布完整報告
- **更新頻率**: 事件觸發
- **資料內容**: 震央、規模、深度、各地震度
- **實現狀態**: ✅ 已實現

```python
# 使用範例
data = cwa_client.get_earthquake_report()
eq_data = cwa_client.check_recent_earthquake(time_threshold=600)  # 10分鐘內
```

#### E-A0016-001: 小區域有感地震報告
- **用途**: 小規模地震資訊
- **實現狀態**: 🔄 可擴充

#### W-C0033-001: 颱風警報
- **用途**: 颱風警報資訊
- **更新頻率**: 每6小時
- **實現狀態**: ✅ 已實現（基礎版）

```python
# 使用範例
data = cwa_client.get_weather_alerts()
```

#### W-C0034-001: 颱風消息
- **用途**: 颱風動態消息
- **實現狀態**: 🔄 可擴充

#### W-C0033-002: 大雨特報
- **用途**: 豪雨、大雨警報
- **實現狀態**: 🔄 可擴充

#### W-C0033-003: 強風特報
- **用途**: 強風警報
- **實現狀態**: 🔄 可擴充

#### W-C0034-005: 低溫特報
- **用途**: 低溫警報
- **實現狀態**: 🔄 可擴充

### 4. 其他資料 (Other Data)

#### F-A0021-001: 潮汐預報
- **用途**: 海洋潮汐資訊
- **實現狀態**: 📋 計劃中

## API 使用策略

### 資料優先級系統

**Level 1: 緊急警報** (立即中斷顯示)
- 地震報告 (M ≥ 4.0)
- 颱風警報
- 豪雨特報
- 顯示時間: 60-120秒
- 動畫效果: 閃爍、震動

**Level 2: 重要提醒** (插入輪播優先)
- 強風特報
- 低溫/高溫警告
- 顯示時間: 30秒
- 動畫效果: 警告圖示

**Level 3: 日常資訊** (正常輪播)
- 天氣預報
- 即時觀測
- UV指數
- 空氣品質
- 顯示時間: 15-20秒
- 動畫效果: 平滑過場

### 更新頻率建議

| API端點 | 建議間隔 | 快取時間 | 原因 |
|---------|---------|---------|------|
| 地震監測 | 5分鐘 | 5分鐘 | 緊急資訊需即時 |
| 即時觀測 | 10分鐘 | 10分鐘 | API更新頻率 |
| 天氣預報 | 30分鐘 | 30分鐘 | 資料穩定性 |
| 天氣警報 | 10分鐘 | 10分鐘 | 警報即時性 |
| UV指數 | 1小時 | 1小時 | 變化緩慢 |
| 空氣品質 | 30分鐘 | 30分鐘 | 環保署更新頻率 |

### API 請求限制

中央氣象署 API 限制：
- **每分鐘**: 20次請求
- **每小時**: 1000次請求
- **每天**: 10000次請求

本系統設計：
- 預設配置下每小時約 10-15 次請求
- 遠低於限制，安全可靠
- 使用快取減少不必要的請求

## 擴充 API 端點教學

### 步驟 1: 在 CWAClient 添加新方法

編輯 `src/api/cwa_client.py`:

```python
def get_tide_forecast(self) -> Optional[Dict]:
    """
    Get tide forecast data
    
    Returns:
        Tide forecast data or None
    """
    return self._make_request(
        'F-A0021-001',
        {},
        cache_file='tide_forecast.json',
        cache_duration=3600  # 1 hour
    )
```

### 步驟 2: 在 DataProcessor 添加處理方法

編輯 `src/api/data_processor.py`:

```python
@staticmethod
def process_tide_data(data: Dict) -> Optional[Dict]:
    """
    Process tide forecast data
    
    Args:
        data: API response data
        
    Returns:
        Processed tide data or None
    """
    try:
        # 解析 API 回應
        tide_info = data['records']['Location'][0]['TimePeriod']
        
        result = {
            'high_tide': tide_info['HighTide'],
            'low_tide': tide_info['LowTide'],
        }
        
        return result
    except Exception as e:
        print(f"Error processing tide data: {str(e)}")
        return None
```

### 步驟 3: 在 DisplayManager 添加顯示方法

編輯 `src/display/display_manager.py`:

```python
def show_tide_info(self, tide_data: Dict, duration: float = 10.0):
    """
    Display tide information
    
    Args:
        tide_data: Processed tide data
        duration: Display duration
    """
    # 實現潮汐資訊顯示
    pass
```

### 步驟 4: 在 Scheduler 添加更新任務

編輯 `src/utils/scheduler.py`:

```python
def _tide_update_loop(self):
    """Background loop for tide forecast updates"""
    while self.running:
        current_time = time.time()
        
        if current_time - self.last_tide_update >= self.tide_update_interval:
            try:
                data = self.cwa_client.get_tide_forecast()
                if data and self.on_tide_update:
                    self.on_tide_update(data)
                self.last_tide_update = current_time
            except Exception as e:
                print(f"Tide update error: {str(e)}")
        
        time.sleep(60)
```

## 環保署空氣品質 API

### API 資訊
- **基礎 URL**: https://data.moenv.gov.tw/api/v2
- **需要**: API Key (可從環保署開放平台申請)
- **資料內容**: AQI、PM2.5、PM10、O3等

### 整合範例

編輯 `src/api/cwa_client.py` 中的 EPAClient:

```python
def __init__(self, api_key: str):
    """Initialize EPA API client with API key"""
    self.api_key = api_key
    self.session = requests.Session()

def get_air_quality(self, location: str = "大安") -> Optional[Dict]:
    """Get air quality data with API authentication"""
    url = f"{self.BASE_URL}/aqx_p_432"
    params = {
        'api_key': self.api_key,
        'filters': f'sitename,like,{location}'
    }
    
    try:
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"EPA API error: {str(e)}")
        return None
```

## API 測試工具

### 測試腳本範例

建立 `tests/test_api.py`:

```python
#!/usr/bin/env python3
"""API Integration Test Script"""

from src.api.cwa_client import CWAClient
from config import WeatherAPI

def test_all_apis():
    """Test all API endpoints"""
    client = CWAClient(WeatherAPI['Authorization'])
    
    print("Testing Weather Forecast...")
    weather = client.get_weather_forecast()
    print(f"✓ Weather: {weather is not None}")
    
    print("Testing Observation Data...")
    obs = client.get_observation_data()
    print(f"✓ Observation: {obs is not None}")
    
    print("Testing Earthquake Report...")
    eq = client.get_earthquake_report()
    print(f"✓ Earthquake: {eq is not None}")
    
    print("Testing Weather Alerts...")
    alerts = client.get_weather_alerts()
    print(f"✓ Alerts: {alerts is not None}")
    
    print("Testing UV Index...")
    uv = client.get_uv_index()
    print(f"✓ UV Index: {uv is not None}")

if __name__ == "__main__":
    test_all_apis()
```

執行測試：
```bash
python3 tests/test_api.py
```

## 故障排除

### 常見 API 錯誤

#### 401 Unauthorized
- **原因**: Authorization token 無效或過期
- **解決**: 檢查 config.py 中的 token，重新申請

#### 429 Too Many Requests
- **原因**: 超過 API 請求限制
- **解決**: 增加更新間隔，檢查快取設定

#### 503 Service Unavailable
- **原因**: CWA 伺服器維護或過載
- **解決**: 使用快取資料，稍後重試

#### Connection Timeout
- **原因**: 網路連線問題
- **解決**: 檢查網路連線，使用快取資料

### Debug 模式

啟用詳細日誌：

```python
# 在 main.py 中
from src.utils.logger import setup_logger
logger = setup_logger("weather_display", level=logging.DEBUG)
```

查看 API 請求詳情：

```bash
# 設定環境變數
export DEBUG_API=1
python3 main.py
```

## 參考資源

- [中央氣象署開放資料平臺](https://opendata.cwa.gov.tw)
- [API 線上文件](https://opendata.cwa.gov.tw/dist/opendata-swagger.html)
- [資料集列表](https://opendata.cwa.gov.tw/devManual/datalist)
- [環保署開放資料](https://data.moenv.gov.tw)
