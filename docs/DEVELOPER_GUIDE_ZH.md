# ProDocuX 開發者指南

## 概述

ProDocuX是一個基於AI的智能文檔轉換平台，可以將各種格式的文檔（PDF、Word等）轉換為結構化的中文文檔。本指南為想要貢獻或整合ProDocuX的開發者提供全面的技術資訊。

## 架構設計

### 核心組件

```
ProDocuX/
├── core/              # 核心處理模組
│   ├── extractor.py   # 文檔提取邏輯
│   ├── transformer.py # 資料轉換邏輯
│   └── ...
├── web/               # Web介面
│   ├── app.py         # Flask應用程式
│   ├── templates/     # HTML模板
│   └── static/        # CSS、JS、圖片
├── utils/             # 工具函數
│   ├── multi_ai_client.py  # AI客戶端管理
│   └── ...
├── profiles/          # 提取規則配置
├── prompts/           # AI提示詞模板
└── templates/         # 輸出文檔模板
```

### 關鍵類別

#### DocumentExtractor
- **用途**: 使用AI從文檔中提取結構化資料
- **主要方法**:
  - `extract_data()`: 主要提取方法
  - `_parse_ai_response()`: 解析AI回應（JSON、直接檔案）
  - `_is_file_output_response()`: 檢測直接檔案輸出

#### DocumentTransformer
- **用途**: 將提取的資料轉換為輸出文檔
- **主要方法**:
  - `transform_to_document()`: 主要轉換方法
  - `_extract_ingredients_from_field()`: 處理成分解析
  - `_load_profile()`: 載入配置檔案

#### MultiAIClient
- **用途**: 管理多個AI提供者和模型
- **主要方法**:
  - `get_available_providers()`: 列出可用的AI提供者
  - `process_prompt()`: 使用選定的AI處理提示詞
  - `get_model_pricing()`: 返回模型定價資訊

## AI整合

### 支援的提供者

1. **OpenAI**
   - 模型: GPT-4o、GPT-4o-mini、GPT-4-turbo、GPT-3.5-turbo
   - API: OpenAI API v1

2. **Claude (Anthropic)**
   - 模型: Claude 3.5 Sonnet、Claude 3.5 Haiku、Claude 3 Opus
   - API: Anthropic API

3. **Gemini (Google)**
   - 模型: Gemini 2.5 Pro/Flash、Gemini 2.0 Flash系列
   - API: Google AI Studio API

4. **Grok (xAI)**
   - 模型: Grok-2、Grok-beta
   - API: xAI API

5. **Microsoft Copilot**
   - 模型: 基於Azure OpenAI Service
   - API: Azure OpenAI API

### 回應處理

ProDocuX處理多種AI回應格式：

1. **結構化JSON**: 標準結構化資料回應
2. **Markdown中的JSON**: 包裝在markdown程式碼區塊中的JSON
3. **直接檔案輸出**: Base64編碼的檔案或下載連結
4. **多層JSON**: 巢狀JSON結構

```python
# 回應解析範例
def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
    # 首先嘗試直接檔案輸出
    if self._is_file_output_response(response_text):
        return self._extract_file_from_response(response_text)
    
    # 嘗試JSON解析
    json_data = self._extract_json_from_response(response_text)
    if json_data:
        return json_data
    
    # 回退到文字處理
    return {"raw_text": response_text}
```

## 配置檔案系統

配置檔案定義不同文檔類型的提取規則和欄位對應。

### 配置檔案結構

```yaml
# 配置檔案範例 (YAML格式)
document_type: "PIF"
fields:
  product_name:
    name: "產品名稱"
    type: "text"
    required: true
  ingredients:
    name: "全成分表"
    type: "table"
    required: true
    columns:
      - "成分名稱"
      - "CAS號"
      - "濃度"
```

### 配置檔案載入

```python
def _load_profile(self, profile_path: str):
    """從YAML檔案載入配置檔案"""
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile_data = yaml.safe_load(f)
    
    self.profile_fields = {}
    for field_key, field_config in profile_data.get('fields', {}).items():
        self.profile_fields[field_key] = field_config.get('name', field_key)
```

## API開發

### Flask路由

#### 主要處理路由
```python
@app.route('/process', methods=['POST'])
def process_document():
    # 檔案上傳處理
    # AI處理
    # 文檔轉換
    # 回應生成
```

#### 設定管理
```python
@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    # 獲取/設定應用程式設定
    # AI提供者配置
    # 模型選擇
```

### 錯誤處理

```python
try:
    # 處理邏輯
    result = process_document(file, template, settings)
    return jsonify({"success": True, "result": result})
except Exception as e:
    logger.error(f"處理失敗: {str(e)}")
    return jsonify({"success": False, "error": str(e)}), 500
```

## 前端開發

### JavaScript架構

#### 主要應用程式 (main.js)
- 檔案上傳處理
- AI模型選擇
- 成本計算
- 進度追蹤

#### 設定管理
- 提供者選擇
- API金鑰管理
- 模型配置
- 設定持久化

### UI組件

#### 檔案上傳
```javascript
function handleFileUpload(files) {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    fetch('/process', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => handleProcessingResult(data));
}
```

#### 成本計算
```javascript
function calculateCost(tokens, model) {
    const pricing = getModelPricing(model);
    const inputCost = (tokens.input / 1000) * pricing.input;
    const outputCost = (tokens.output / 1000) * pricing.output;
    return inputCost + outputCost;
}
```

## 測試

### 單元測試

```python
import pytest
from core.extractor import DocumentExtractor

def test_extract_data():
    """測試文檔資料提取"""
    extractor = DocumentExtractor()
    result = extractor.extract_data("測試內容")
    assert result is not None
    assert "extracted_data" in result

def test_ai_response_parsing():
    """測試AI回應解析"""
    extractor = DocumentExtractor()
    
    # 測試JSON回應
    json_response = '{"data": {"field": "value"}}'
    result = extractor._parse_ai_response(json_response)
    assert result["data"]["field"] == "value"
    
    # 測試檔案輸出回應
    file_response = "Here is your document: [FILE:base64data]"
    result = extractor._parse_ai_response(file_response)
    assert "file_content" in result
```

### 整合測試

```python
def test_end_to_end_processing():
    """測試完整的文檔處理工作流程"""
    # 上傳測試文檔
    # 使用AI處理
    # 驗證輸出格式
    # 檢查成本計算
```

## 部署

### 環境設定

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
export OPENAI_API_KEY="your-key"
export CLAUDE_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export GROK_API_KEY="your-key"

# 運行應用程式
python run.py
```

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

## 效能優化

### 快取策略

- **回應快取**: 快取類似文檔的AI回應
- **模板快取**: 快取編譯的模板
- **配置檔案快取**: 快取載入的配置檔案

### 記憶體管理

- **串流處理**: 分塊處理大型文檔
- **垃圾回收**: 清理臨時檔案
- **資源限制**: 設定並發處理限制

## 安全考量

### API金鑰管理

- 將API金鑰儲存在環境變數中
- 永遠不要將金鑰提交到版本控制
- 使用安全的金鑰輪換

### 輸入驗證

- 驗證檔案類型和大小
- 清理使用者輸入
- 實施速率限制

### 資料隱私

- 在本地處理文檔
- 不儲存敏感資料
- 實施資料保留政策

## 貢獻指南

### 代碼風格

- 遵循PEP 8規範
- 使用類型提示
- 編寫全面的文檔字串
- 為新功能添加單元測試

### Pull Request流程

1. Fork儲存庫
2. 創建功能分支
3. 實施變更並添加測試
4. 提交pull request
5. 處理審查回饋

### 問題回報

回報問題時，請包含：
- Python版本
- 作業系統
- 錯誤訊息
- 重現步驟
- 預期與實際行為

## 資源

- **GitHub儲存庫**: https://github.com/wucy1/ProDocuX
- **API文檔**: [API.md](../API.md)
- **使用者指南**: [USAGE.md](../USAGE.md)
- **貢獻指南**: [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**版本**: RC1  
**最後更新**: 2025年1月6日





