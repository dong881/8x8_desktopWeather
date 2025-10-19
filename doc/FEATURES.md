# Enhanced 8x8 Weather Display - Feature Overview

## 新功能概述 (New Features Overview)

這個增強版本將原本數據導向的顯示轉變為智能視覺化天氣助手。

### 核心改進 (Core Improvements)

#### 1. 模組化架構 (Modular Architecture)
```
src/
├── api/              # API 客戶端和資料處理
│   ├── cwa_client.py      # CWA API 整合
│   └── data_processor.py  # 資料處理器
├── display/          # 顯示控制和視覺化
│   ├── icons.py           # 8x8 圖示庫
│   ├── animations.py      # 動畫引擎
│   └── display_manager.py # 顯示管理器
└── utils/            # 工具模組
    ├── logger.py          # 日誌系統
    └── scheduler.py       # 任務排程器
```

#### 2. 多重 API 整合 (Multiple API Integration)
- **天氣預報** (F-D0047-061): 今明 36 小時溫度和降雨
- **即時觀測** (O-A0001-001): 氣象站即時資料
- **地震報告** (E-A0015-001): 最新地震資訊，自動警報
- **天氣警報** (W-C0033-001): 颱風、豪雨等警報
- **紫外線指數** (O-A0005-001): UV 指數資訊

#### 3. 8x8 圖示庫 (Icon Library)
完整的像素圖示系統：
- 天氣圖示：晴天、多雲、雨天、雷雨、下雪、颱風
- 警報圖示：地震、警告、高溫、低溫
- 溫度計圖示：冷/熱狀態顯示
- 數字字型：0-9 大字體顯示

#### 4. 動畫系統 (Animation System)
- **雨滴動畫**: 模擬下雨效果
- **陽光閃爍**: 太陽光線閃爍
- **地震震動**: 地震時震動效果
- **淡入淡出**: 平滑場景切換
- **滑動轉場**: 內容滑入/滑出
- **跑馬燈**: 長文字滾動顯示

#### 5. 顯示模式 (Display Modes)
- **輪播模式** (Carousel): 多頁面定時切換
- **圖示模式** (Icon): 顯示天氣圖示
- **混合模式** (Mixed): 圖示 + 文字組合
- **警報模式** (Alert): 緊急訊息中斷顯示
- **傳統模式** (Bar): 原始溫度條圖

#### 6. 自動亮度調整 (Automatic Brightness Control)
- **夜間模式**: 自動根據時間調整 LED 亮度
  - 深夜 (0-5, 22-23): 極低亮度 (10-30)
  - 黎明/黃昏 (6-9, 18-21): 中等亮度 (50-150)
  - 白天 (10-17): 最高亮度 (200-255)
- **手動控制**: 可透過 Web 介面手動設定亮度
- **省電節能**: 夜間自動降低亮度，延長 LED 壽命

#### 7. 智能警報系統 (Intelligent Alert System)
優先級分層：
- **Level 1 緊急**: 地震（60秒，震動動畫）
- **Level 2 重要**: 颱風、豪雨（30秒，閃爍警示）
- **Level 3 日常**: 天氣、溫度、空氣品質（正常輪播）

#### 8. 資料快取與容錯 (Caching & Error Handling)
- 本地 JSON 快取系統
- API 失敗時使用快取資料
- 自動重試機制
- 完整錯誤日誌

## 使用方式 (Usage)

### 啟動增強版本 (Run Enhanced Version)
```bash
# 使用新的模組化主程式
python3 main.py

# 或使用原始版本（保留向下相容）
python3 Weather.py
```

### 配置選項 (Configuration)

`config.py` 範例：
```python
# 基本配置
WeatherAPI = {
    'Authorization': 'YOUR_CWA_TOKEN'
}

# 進階配置（可選）
DisplayConfig = {
    'brightness': 30,           # LED 亮度 (0-255)
    'auto_brightness': True,    # 自動調整亮度（夜間自動降低）
    'update_interval': 1800,    # 天氣更新間隔（秒）
    'earthquake_check': 300,    # 地震檢查間隔（秒）
    'page_duration': 15,        # 頁面顯示時間（秒）
    'location': '大安區'         # 地區名稱
}
```

## API 端點說明 (API Endpoints)

### 1. 天氣預報 (Weather Forecast)
- **端點**: `F-D0047-061`
- **更新頻率**: 30 分鐘
- **快取時間**: 30 分鐘
- **資料內容**: 36 小時溫度、降雨機率

### 2. 即時觀測 (Real-time Observation)
- **端點**: `O-A0001-001`
- **更新頻率**: 10 分鐘
- **快取時間**: 10 分鐘
- **資料內容**: 溫度、濕度、天氣狀況

### 3. 地震報告 (Earthquake Report)
- **端點**: `E-A0015-001`
- **更新頻率**: 5 分鐘
- **快取時間**: 5 分鐘
- **資料內容**: 規模、震央、深度、震度

### 4. 天氣警報 (Weather Alerts)
- **端點**: `W-C0033-001`
- **更新頻率**: 10 分鐘
- **快取時間**: 10 分鐘
- **資料內容**: 颱風、豪雨等警報

### 5. 紫外線指數 (UV Index)
- **端點**: `O-A0005-001`
- **更新頻率**: 1 小時
- **快取時間**: 1 小時
- **資料內容**: UV 指數值

## 技術細節 (Technical Details)

### 圖示設計 (Icon Design)
每個圖示為 8x8 像素，使用 byte array 表示：
```python
SUNNY = [
    0b00010000,  # 第 1 行
    0b01010100,  # 第 2 行
    0b00111000,  # 第 3 行
    0b01111100,  # 第 4 行
    0b01111100,  # 第 5 行
    0b00111000,  # 第 6 行
    0b01010100,  # 第 7 行
    0b00010000,  # 第 8 行
]
```

### 動畫實現 (Animation Implementation)
```python
# 雨滴動畫範例
animator = AnimationEngine(device)
animator.rain_animation(duration=3.0, fps=10)

# 地震震動範例
animator.earthquake_shake(duration=5.0, shake_speed=0.1)
```

### 自訂顯示頁面 (Custom Display Pages)
```python
def my_custom_page(device):
    with canvas(device) as draw:
        # 繪製自訂內容
        draw.point((4, 4), fill="white")

page = DisplayPage("custom", my_custom_page, duration=10.0, priority=3)
display_manager.add_page(page)
```

## 系統需求 (System Requirements)

### 硬體 (Hardware)
- Raspberry Pi (任何版本)
- MAX7219 驅動的 8x8 LED 矩陣
- SPI 介面連接

### 軟體 (Software)
- Python 3.7+
- luma.led-matrix >= 1.7.0
- requests >= 2.25.0
- Pillow >= 8.0.0
- urllib3 >= 1.26.0

## 效能優化 (Performance)

### 資源使用 (Resource Usage)
- CPU 使用率: < 10%
- 記憶體: < 50 MB
- 網路: 每 API 請求 < 1 MB
- 快取空間: < 5 MB

### 最佳實踐 (Best Practices)
1. 使用虛擬環境 (venv)
2. 定期清理快取（> 1 天）
3. 監控 API 請求次數（< 20 次/分鐘）
4. 檢查日誌檔案大小

## 故障排除 (Troubleshooting)

### 常見問題 (Common Issues)

#### 1. 無法連接 API
```bash
# 檢查網路連線
ping opendata.cwa.gov.tw

# 檢查 Authorization Token
cat config.py
```

#### 2. LED 顯示異常
```bash
# 檢查 SPI 介面
ls /dev/spi*

# 重新啟用 SPI
sudo raspi-config
```

#### 3. 模組導入錯誤
```bash
# 確認在專案根目錄
cd /path/to/8x8_desktopWeather

# 確認模組結構
ls -R src/
```

## 未來擴充方向 (Future Enhancements)

### 短期計劃 (Short-term)
- [ ] 環保署空氣品質 API 整合
- [ ] 更多天氣圖示（霧、霾等）
- [ ] 自訂動畫速度設定
- [ ] Web 介面配置

### 中期計劃 (Mid-term)
- [ ] 多個 LED 矩陣串聯支援
- [ ] RGB LED 矩陣支援
- [ ] 聲音警報系統
- [ ] 移動應用程式控制

### 長期計劃 (Long-term)
- [ ] 機器學習天氣預測
- [ ] 社群天氣分享平台
- [ ] 多語言支援
- [ ] 雲端同步配置

## 貢獻指南 (Contributing)

歡迎提交 Pull Request！請遵循：
1. 符合 PEP 8 程式碼風格
2. 添加適當的註解和文檔
3. 通過現有測試
4. 更新 README 說明

## 授權 (License)

Copyright (c) 2023-2024 MingHung
MIT License

## 致謝 (Acknowledgments)

- [luma.led_matrix](https://github.com/rm-hull/luma.led_matrix) - LED 矩陣驅動
- [中央氣象署開放資料平臺](https://opendata.cwa.gov.tw) - 天氣資料來源
- 所有貢獻者和使用者的支持
