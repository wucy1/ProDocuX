# ProDocuX 專案結構

## 📁 目錄說明

```
ProDocuX/
├── 📄 README.md              # 專案主要說明文檔
├── 📄 USAGE.md               # 使用指南
├── 📄 API.md                 # API文檔
├── 📄 CONTRIBUTING.md        # 貢獻指南
├── 📄 LICENSE                # 授權條款
├── 📄 STRUCTURE.md           # 專案結構說明
├── 📄 requirements.txt       # Python依賴套件
├── 📄 env_example.txt        # 環境變數範例
├── 📄 run.py                 # 主程式入口
├── 📄 simple_setup.py        # 簡化設定腳本
├── 📄 desktop_launcher.py    # 桌面啟動器
├── 📁 core/                  # 核心處理模組
│   ├── __init__.py
│   ├── extractor.py          # 文檔提取器
│   ├── transformer.py        # 文檔轉換器
│   ├── profile_manager.py    # 配置管理器
│   └── learner.py            # 學習模組
├── 📁 utils/                 # 工具函數
│   ├── __init__.py
│   ├── ai_client.py          # AI客戶端
│   ├── multi_ai_client.py    # 多AI模型客戶端
│   ├── file_handler.py       # 檔案處理器
│   ├── settings_manager.py   # 設定管理器
│   ├── desktop_manager.py    # 桌面管理器
│   ├── cost_calculator.py    # 成本計算器
│   └── logger.py             # 日誌工具
├── 📁 web/                   # Web介面
│   ├── app.py                # Flask應用
│   ├── static/               # 靜態資源
│   │   ├── css/style.css     # 樣式表
│   │   └── js/main.js        # JavaScript
│   └── templates/            # HTML模板
│       ├── index.html        # 主頁面
│       └── settings.html     # 設定頁面
├── 📁 profiles/              # 提取規則配置
│   └── pif.yml               # PIF文檔配置
├── 📁 prompts/               # AI提示詞
│   └── extract.md            # 提取提示詞
├── 📁 templates/             # 輸出模板
├── 📁 tests/                 # 測試檔案
└── 📁 deploy/                # 部署腳本
    └── build.py              # 打包腳本
```

## 🔧 核心模組

### core/ - 核心處理模組
- **extractor.py**: 負責從文檔中提取結構化資料
- **transformer.py**: 負責將提取的資料轉換為目標格式
- **profile_manager.py**: 管理不同文檔類型的提取規則
- **learner.py**: 從使用者修正中學習和優化規則

### utils/ - 工具函數
- **ai_client.py**: 基礎AI客戶端實現
- **multi_ai_client.py**: 多AI模型統一管理
- **file_handler.py**: 檔案讀寫和格式轉換
- **settings_manager.py**: 系統設定管理
- **desktop_manager.py**: 桌面環境管理
- **cost_calculator.py**: API成本計算
- **logger.py**: 日誌記錄工具

### web/ - Web介面
- **app.py**: Flask Web應用主程式
- **static/**: 前端靜態資源（CSS、JS）
- **templates/**: HTML模板檔案

## 📋 配置檔案

### profiles/ - 提取規則
- 定義不同文檔類型的提取規則
- 支援YAML格式配置
- 可自定義和擴展

### prompts/ - AI提示詞
- 存儲AI模型的提示詞模板
- 支援Markdown格式
- 可根據需求調整

### templates/ - 輸出模板
- Word文檔模板
- 支援變數替換
- 可自定義樣式

## 🚀 入口點

### run.py - 主程式
- 程式啟動入口
- 處理命令行參數
- 啟動Web服務

### simple_setup.py - 簡化設定
- 首次啟動設定
- 引導使用者完成配置
- 創建必要目錄

### desktop_launcher.py - 桌面啟動器
- 桌面環境啟動
- 無控制台視窗
- 適合一般使用者

## 🧪 測試與部署

### tests/ - 測試檔案
- 單元測試
- 整合測試
- 性能測試

### deploy/ - 部署腳本
- 打包腳本
- 安裝程式
- 發布工具

## 📝 文檔檔案

- **README.md**: 專案主要說明
- **USAGE.md**: 詳細使用指南
- **API.md**: API文檔
- **CONTRIBUTING.md**: 貢獻指南
- **STRUCTURE.md**: 專案結構說明

## 🔒 安全檔案

- **.gitignore**: Git忽略檔案清單
- **env_example.txt**: 環境變數範例
- **LICENSE**: 授權條款

---

**注意**: 此結構專為GitHub發布設計，移除了開發過程中的臨時檔案和敏感資訊。
























