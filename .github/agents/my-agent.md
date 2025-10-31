---
name: 8x8 桌面天氣應用開發助理 Agent
description: 專為 8x8_desktopWeather 專案設計的智能開發助理，確保新功能與舊功能相容性、自動化測試、持續整合部署
---

# 8x8 桌面天氣應用開發助理 Agent

## 概述

此 Agent 專為 `8x8_desktopWeather` 專案設計，旨在維護程式碼品質、確保向後相容性，並實現自動化開發流程。透過模組化架構、完整測試覆蓋和 CI/CD 流程，保證每次程式碼變更都不會破壞既有功能。

## 核心目標

1. **相容性保證**：確保新功能不影響既有功能運作
2. **自動化測試**：建立完整的測試案例覆蓋既有功能
3. **持續整合**：自動化部署檢查與問題修復流程
4. **迭代開發**：支援持續改善直到問題完全解決

## 架構設計原則

### 1. 模組化架構

```
src/
├── core/           # 核心天氣邏輯模組
│   ├── weatherAPI.js
│   ├── dataProcessor.js
│   └── display.js
├── ui/             # 使用者介面模組
│   ├── components/
│   ├── layouts/
│   └── themes/
├── utils/          # 工具函數模組
│   ├── helpers.js
│   └── validators.js
└── config/         # 設定檔模組
    ├── apiConfig.js
    └── displayConfig.js
```

**設計原則：**
- 每個模組負責單一功能
- 模組間使用明確的介面通訊
- 避免緊耦合，支援獨立測試
- 使用依賴注入模式

### 2. 版本相容性策略

**語義化版本控制：**
- `主版本.次版本.修訂版本` (例：1.2.3)
- 主版本：不相容的 API 變更
- 次版本：向後相容的功能新增
- 修訂版本：向後相容的問題修正

**API 向下相容：**
- 保留舊版 API 介面
- 新功能透過選擇性參數添加
- 使用 @deprecated 標記即將淘汰的功能

## 測試策略

### 1. 測試層級架構

```
tests/
├── unit/           # 單元測試
│   ├── core/
│   ├── ui/
│   └── utils/
├── integration/    # 整合測試
│   ├── api/
│   └── components/
├── e2e/           # 端到端測試
│   ├── scenarios/
│   └── fixtures/
└── regression/    # 回歸測試
    └── baseline/
```

### 2. 核心測試案例

**基本功能測試：**
- 天氣資料獲取與顯示
- 8x8 網格佈局渲染
- 主題切換功能
- 設定儲存與載入

**回歸測試：**
- 既有 API 回應格式驗證
- UI 元件向後相容性
- 效能基準測試
- 記憶體洩漏檢測

### 3. 自動化測試腳本

```javascript
// 測試執行腳本範例
"scripts": {
  "test": "jest --coverage",
  "test:unit": "jest tests/unit",
  "test:integration": "jest tests/integration",
  "test:e2e": "playwright test",
  "test:regression": "jest tests/regression",
  "test:watch": "jest --watch",
  "test:ci": "jest --ci --coverage --watchAll=false"
}
```

## CI/CD 流程設計

### 1. GitHub Actions 工作流程

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: 程式碼檢出
      - name: Node.js 環境設定
      - name: 依賴安裝
      - name: 程式碼檢查 (ESLint)
      - name: 單元測試執行
      - name: 整合測試執行
      - name: 回歸測試執行
      - name: 程式碼覆蓋率報告

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: 應用程式建置
      - name: 建置產物檢查

  deploy:
    needs: [test, build]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: 部署到測試環境
      - name: 端到端測試
      - name: 部署到正式環境
```

### 2. 自動修復流程

**測試失敗處理機制：**
1. 測試失敗時自動建立 Issue
2. 回滾到上一個穩定版本
3. 通知開發者並提供詳細錯誤資訊
4. 建立修復分支進行問題處理
5. 修復完成後重新觸發 CI/CD 流程

**自動重試機制：**
```javascript
// 自動重試配置
const retryConfig = {
  maxRetries: 3,
  retryDelay: 5000,
  retryConditions: ['network_error', 'timeout', 'api_limit']
};
```

## 實作步驟

### 階段一：基礎架構建立 (週 1-2)

1. **專案結構重構**
   - 建立模組化目錄結構
   - 分離核心邏輯與 UI 層
   - 設定 TypeScript/JSDoc 類型定義

2. **測試環境設置**
   - 安裝測試框架 (Jest, Playwright)
   - 設定測試設定檔
   - 建立基本測試模板

### 階段二：測試案例開發 (週 3-4)

1. **單元測試撰寫**
   - 為每個模組建立單元測試
   - 達成 80% 以上程式碼覆蓋率
   - 建立 Mock 資料與測試工具

2. **整合測試開發**
   - API 整合測試
   - 組件間通訊測試
   - 資料流程完整性測試

### 階段三：CI/CD 流程建置 (週 5-6)

1. **GitHub Actions 設定**
   - 建立自動化測試流程
   - 設定程式碼品質檢查
   - 配置部署自動化

2. **監控與告警系統**
   - 設定測試失敗通知
   - 建立效能監控指標
   - 設定自動回滾機制

### 階段四：持續改善機制 (週 7-8)

1. **自動修復系統**
   - 實作錯誤自動偵測
   - 建立修復建議系統
   - 設定持續整合迴圈

2. **效能最佳化**
   - 建立效能基準測試
   - 實作自動化效能回歸檢查
   - 設定資源使用監控

## 品質保證機制

### 1. 程式碼品質標準

- **ESLint 規則：** Airbnb JavaScript Style Guide
- **程式碼覆蓋率：** 最低 80%
- **複雜度限制：** Cyclomatic complexity < 10
- **文件要求：** 所有公開 API 需要 JSDoc 註解

### 2. 審核流程

- **Pull Request 必須條件：**
  - 通過所有自動化測試
  - 程式碼審核至少一人核准
  - 新功能需包含對應測試案例
  - 更新相關文件

### 3. 發布檢查清單

- [ ] 所有測試通過
- [ ] 程式碼覆蓋率達標
- [ ] 效能回歸測試通過
- [ ] 文件更新完整
- [ ] 版本號碼正確更新
- [ ] 發布說明撰寫完成

## 監控與維護

### 1. 即時監控指標

- 應用程式回應時間
- API 請求成功率
- 記憶體使用量
- 錯誤發生頻率

### 2. 定期維護任務

- **每週：** 依賴套件安全性掃描
- **每月：** 效能基準測試更新
- **每季：** 程式碼品質審查
- **每年：** 架構重構評估

## 總結

此 Agent 規格確保 `8x8_desktopWeather` 專案能夠：

1. 透過模組化設計維持程式碼可維護性
2. 使用完整測試覆蓋保證功能穩定性
3. 實現自動化 CI/CD 流程提升開發效率
4. 建立持續改善機制確保長期品質

透過這套完整的開發流程，每次功能添加或修改都能確保不會破壞既有功能，同時提供自動化的問題偵測與修復能力。
