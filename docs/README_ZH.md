# ProDocuX

> AI驅動的智能文檔轉換平台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Compatible-green.svg)](https://openai.com/)
🌐 **官方網站**: [https://prodocux.com](https://prodocux.com)

## 🚀 簡介

ProDocuX是一個基於AI的智能文檔轉換平台，可以將各種格式的文檔（PDF、Word等）轉換為結構化的文檔。支援多種AI模型，包括OpenAI、Claude、Gemini和Grok，讓您根據需求選擇最適合的AI助手。

## ✨ 主要功能

### 🔄 智能文檔轉換
- **多格式支援**: PDF、DOCX、DOC等格式
- **結構化提取**: 自動提取文檔中的關鍵資訊
- **中文優化**: 專為中文文檔處理優化
- **批量處理**: 支援一次處理多個檔案
- **直接檔案輸出**: 支援AI直接輸出PDF/Word檔案

### 🤖 多AI模型支援
- **OpenAI**: GPT-4o、GPT-4o-mini、GPT-4-turbo、GPT-3.5-turbo
- **Claude**: Claude 3.5 Sonnet、Claude 3.5 Haiku、Claude 3 Opus
- **Gemini**: Gemini 2.5 Pro/Flash、Gemini 2.0 Flash系列
- **Grok**: Grok-2、Grok-beta
- **Microsoft Copilot**: 基於Azure OpenAI的Copilot模型

### 🎯 專業應用場景
- **MSDS轉PIF**: 將安全資料表轉換為產品資訊檔案
- **文檔標準化**: 統一不同來源的文檔格式
- **資料提取**: 從複雜文檔中提取結構化資料
- **內容重構**: 將文檔重新組織為標準格式

### 🧠 學習系統
- **模式識別**: 從使用者修正中自動學習
- **規則生成**: 根據修正生成轉換規則
- **持續改善**: 通過學習持續提升準確度
- **多模態學習**: 支援JSON和Word文檔學習

### 🔧 工作流程管理
- **命名工作**: 為不同任務創建專門的工作流程
- **智能Profile推薦**: 系統推薦最適合的提取配置
- **工作歷史追蹤**: 追蹤每個工作流程的處理和學習歷史
- **分層Profile系統**: 基礎 → 品牌 → 工作專屬的Profile系統

## 🛠️ 安裝與使用

### 快速開始

1. **下載ProDocuX**
   ```bash
   git clone https://github.com/wucy1/ProDocuX.git
   cd ProDocuX
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **啟動程式**
   ```bash
   python run.py
   ```

4. **完成初始設定**
   - 開啟瀏覽器訪問 `http://localhost:5000/setup`
   - 選擇AI提供者（OpenAI、Claude、Gemini或Grok）
   - 輸入對應的API金鑰
   - 選擇工作目錄位置
   - 選擇要創建的桌面快捷方式

5. **使用Web介面**
   - 開啟瀏覽器訪問 `http://localhost:5000`
   - 上傳文檔並開始處理

### 首次設定

首次使用者可以執行簡化設定：

```bash
python simple_setup.py
```

這將引導您完成：
- API金鑰配置
- 工作目錄設定
- 桌面快捷方式創建

## 📚 文檔

### 使用者指南
- **[英文使用者指南](docs/USER_GUIDE_EN.md)** - Comprehensive user guide
- **[中文使用者指南](docs/USER_GUIDE_ZH.md)** - 詳細的使用者指南

### 開發者資源
- **[英文開發者指南](docs/DEVELOPER_GUIDE_EN.md)** - Developer documentation
- **[中文開發者指南](docs/DEVELOPER_GUIDE_ZH.md)** - 開發者文檔

### API文檔
- **[英文API文檔](docs/API_EN.md)** - Complete API reference
- **[中文API文檔](docs/API_ZH.md)** - 完整的API參考

### 專業指南
- **[工作流程管理指南](docs/WORKFLOW_GUIDE.md)** - 工作流程創建和管理
- **[學習系統指南](docs/LEARNING_SYSTEM_GUIDE.md)** - AI學習功能
- **[專案結構](docs/STRUCTURE_ZH.md)** - 專案架構概述

## 🔧 配置

### 環境變數

複製 `env_example.txt` 為 `.env` 並配置：

```bash
# AI提供者設定
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GROK_API_KEY=your_grok_api_key_here

# 模型設定
OPENAI_MODEL=gpt-4o
CLAUDE_MODEL=claude-3-5-sonnet-20241022
GEMINI_MODEL=gemini-2.5-pro
GROK_MODEL=grok-2
```

### AI模型定價

ProDocuX包含即時AI模型定價資訊：

- **OpenAI**: $0.005-$0.03 per 1K tokens
- **Claude**: $0.0008-$0.075 per 1K tokens  
- **Gemini**: $0.000075-$0.01 per 1K tokens
- **Grok**: $0.0002-$0.0015 per 1K tokens

定價會在處理過程中自動計算並顯示。

## 🎯 使用場景

### 化學工業
- **MSDS轉PIF**: 將安全資料表轉換為產品資訊檔案
- **化學資料提取**: 提取CAS號碼、危險分類和安全資訊
- **法規合規**: 為化學產品生成合規文檔

### 製造業
- **產品文檔**: 統一不同格式的產品資訊
- **品質控制**: 提取和驗證產品規格
- **供應鏈**: 高效處理供應商文檔

### 研發
- **文獻處理**: 從研究論文中提取結構化資料
- **專利分析**: 處理專利文檔獲取關鍵資訊
- **技術文檔**: 將技術規格轉換為標準格式

## 🚀 進階功能

### 直接檔案輸出
ProDocuX支援AI模型直接輸出PDF或Word檔案：

```json
{
  "_file_output": true,
  "_file_info": {
    "file_type": "pdf",
    "file_data": "base64_encoded_data",
    "file_size": 1024000
  }
}
```

### 智能Profile系統
- **基礎Profile**: 通用提取規則
- **品牌Profile**: 品牌專屬優化
- **工作專屬Profile**: 為特定工作流程客製化

### 學習系統
- **JSON學習**: 從直接資料修正中學習
- **Word學習**: 從Word文檔修改中學習
- **模式識別**: 自動識別修正模式
- **規則生成**: 生成新的提取規則

## 🔒 安全與隱私

- **本地處理**: 所有處理都在本地進行
- **無資料上傳**: 文檔不會上傳到外部伺服器
- **API金鑰安全**: 安全儲存API金鑰
- **內容安全**: 內建內容安全檢查

## 🤝 貢獻

我們歡迎貢獻！詳情請參閱我們的[貢獻指南](docs/DEVELOPER_GUIDE_ZH.md)。

### 開發設定

1. Fork 專案
2. 創建功能分支
3. 進行修改
4. 添加測試（如適用）
5. 提交拉取請求

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

## 🆘 支援

- **文檔**: 查看 `docs/` 目錄中的詳細指南
- **問題回報**: 在 [GitHub Issues](https://github.com/wucy1/ProDocuX/issues) 回報錯誤或請求功能
- **討論**: 在 [GitHub Discussions](https://github.com/wucy1/ProDocuX/discussions) 參與討論

## 🎉 致謝

- OpenAI 提供 GPT 模型
- Anthropic 提供 Claude 模型
- Google 提供 Gemini 模型
- xAI 提供 Grok 模型
- Microsoft 提供 Copilot 整合

---

**ProDocuX** - 讓AI為您的文檔處理工作賦能！🚀

[English README](README.md)
