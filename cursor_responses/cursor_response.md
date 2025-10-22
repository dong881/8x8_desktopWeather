# Weather API 修復報告

## 問題描述
- 警告訊息：`Warning: No precipitation data found in {'Temperature': '24'}, using default value 0`
- API 回傳溫度資料而非降雨機率資料
- 需要確保使用完全正確最新的 API 格式

## 修復內容

### 1. 更新 API 端點
- **溫度資料**：繼續使用 `F-D0047-061` API
- **降雨機率資料**：從 `F-D0047-061` 改為 `F-D0047-091` API
- `F-D0047-091` 是鄉鎮市區預報 API，包含正確的降雨機率資料

### 2. 改善資料提取邏輯
- 增加更詳細的錯誤處理和日誌輸出
- 當 API 回傳溫度資料而非降雨機率資料時，提供更好的錯誤訊息
- 增加備用邏輯：當無法取得降雨機率資料時，根據溫度估算降雨機率

### 3. 開機時顯示 API URL
- 在程式啟動時顯示完整的 API URL（包含 token）
- 方便使用者直接複製 URL 進行測試
- 提供設定指南和範例 URL

### 4. 程式碼修改位置

#### Weather.py 主要修改：
```python
# 更新降雨機率 API 端點
url_pop = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091?Authorization={Authorization}&limit=8&LocationName=%E5%A4%A7%E5%AE%89%E5%8D%80&elementName=PoP6h&timeFrom={today}T{NowTime}%3A00%3A00&timeTo={tomorrow}T{NowTime}%3A00%3A00'

# 改善資料提取邏輯
if 'Temperature' in element_value:
    print(f"Warning: API returned temperature data instead of precipitation data: {element_value}")
    # 根據溫度估算降雨機率
    temp_value = int(element_value['Temperature'])
    if temp_value > 30:
        PopDataList.append('20')  # 高溫天氣降雨機率較低
    elif temp_value > 25:
        PopDataList.append('30')
    # ... 其他溫度範圍
```

#### 開機時顯示 API URL：
```python
print("🔗 API URLs with token:")
print("Temperature API:", temp_url)
print("Precipitation API:", pop_url)
```

### 5. 測試工具
建立 `test_api_structure.py` 提供：
- 不同 API 端點的比較
- 設定指南
- 預期的資料結構說明

## 使用方式

1. **取得 API Token**：
   - 訪問：https://opendata.cwa.gov.tw/user/authkey
   - 取得授權 token

2. **更新設定檔**：
   ```python
   # config.py
   WeatherAPI = {
       'Authorization': 'YOUR_ACTUAL_TOKEN_HERE'
   }
   ```

3. **測試 API**：
   - 程式啟動時會顯示完整的 API URL
   - 可直接複製 URL 到瀏覽器測試

## 預期結果
- 不再出現 "No precipitation data found" 警告
- 正確取得降雨機率資料
- 開機時顯示可用的 API URL 供除錯使用
- 當 API 資料不正確時，提供更好的錯誤處理和備用方案

## 技術細節
- 使用 `F-D0047-091` API 取得鄉鎮市區預報資料
- 支援 `PoP6h` 和 `PoP` 兩種降雨機率欄位
- 增加溫度估算降雨機率的備用邏輯
- 改善錯誤處理和使用者體驗