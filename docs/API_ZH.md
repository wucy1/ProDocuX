# ProDocuX API 文檔

## 概述

ProDocuX提供RESTful API，讓開發者可以程式化地使用文檔處理功能。

## 基礎URL

```
http://localhost:5000/api
```

## 認證

目前API不需要認證，但需要設定有效的AI API金鑰。

## 端點

### 1. 健康檢查

**GET** `/health`

檢查服務狀態。

**回應：**
```json
{
  "status": "healthy",
  "version": "RC1",
  "timestamp": "2025-01-06T00:00:00Z"
}
```

### 2. 上傳檔案

**POST** `/upload`

上傳文檔檔案進行處理。

**請求：**
- Content-Type: `multipart/form-data`
- 參數：
  - `file`: 文檔檔案
  - `template`: 模板名稱（可選）
  - `provider`: AI提供者（可選）

**回應：**
```json
{
  "success": true,
  "task_id": "task_123456",
  "message": "檔案上傳成功，開始處理"
}
```

### 3. 處理狀態

**GET** `/status/{task_id}`

查詢處理任務狀態。

**回應：**
```json
{
  "success": true,
  "status": "processing",
  "progress": 50,
  "message": "正在處理中..."
}
```

**狀態值：**
- `pending`: 等待處理
- `processing`: 處理中
- `completed`: 處理完成
- `failed`: 處理失敗

### 4. 下載結果

**GET** `/download/{task_id}`

下載處理結果。

**回應：**
- 成功：返回檔案流
- 失敗：返回JSON錯誤訊息

### 5. 獲取設定

**GET** `/settings`

獲取當前設定。

**回應：**
```json
{
  "success": true,
  "settings": {
    "ai_provider": "openai",
    "ai_model": "gpt-4",
    "max_file_size": 50,
    "auto_cleanup": true
  }
}
```

### 6. 更新設定

**POST** `/settings`

更新系統設定。

**請求：**
```json
{
  "ai_provider": "claude",
  "ai_model": "claude-3-sonnet-20240229",
  "max_file_size": 100
}
```

**回應：**
```json
{
  "success": true,
  "message": "設定已更新"
}
```

### 7. 開啟資料夾

**GET** `/open-folder/{folder_type}`

開啟指定類型的資料夾。

**參數：**
- `folder_type`: 資料夾類型（input/output/template）

**回應：**
```json
{
  "success": true,
  "message": "已開啟 input 資料夾",
  "path": "/path/to/folder"
}
```

## 錯誤處理

所有API端點都可能返回以下錯誤：

### 400 Bad Request
```json
{
  "error": "無效的請求參數",
  "details": "具體錯誤描述"
}
```

### 404 Not Found
```json
{
  "error": "資源不存在",
  "details": "請求的資源未找到"
}
```

### 500 Internal Server Error
```json
{
  "error": "內部伺服器錯誤",
  "details": "處理過程中發生錯誤"
}
```

## 使用範例

### Python範例

```python
import requests

# 上傳檔案
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/api/upload', files=files)
    result = response.json()
    task_id = result['task_id']

# 查詢狀態
while True:
    response = requests.get(f'http://localhost:5000/api/status/{task_id}')
    status = response.json()
    
    if status['status'] == 'completed':
        break
    elif status['status'] == 'failed':
        print(f"處理失敗: {status['message']}")
        break
    
    print(f"處理進度: {status['progress']}%")
    time.sleep(2)

# 下載結果
response = requests.get(f'http://localhost:5000/api/download/{task_id}')
with open('result.docx', 'wb') as f:
    f.write(response.content)
```

### JavaScript範例

```javascript
// 上傳檔案
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/api/upload', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    const taskId = data.task_id;
    pollStatus(taskId);
});

// 查詢狀態
function pollStatus(taskId) {
    fetch(`/api/status/${taskId}`)
    .then(response => response.json())
    .then(data => {
        if (data.status === 'completed') {
            downloadResult(taskId);
        } else if (data.status === 'failed') {
            console.error('處理失敗:', data.message);
        } else {
            setTimeout(() => pollStatus(taskId), 2000);
        }
    });
}

// 下載結果
function downloadResult(taskId) {
    window.open(`/api/download/${taskId}`);
}
```

### cURL範例

```bash
# 上傳檔案
curl -X POST -F "file=@document.pdf" http://localhost:5000/api/upload

# 查詢狀態
curl http://localhost:5000/api/status/task_123456

# 下載結果
curl -O http://localhost:5000/api/download/task_123456
```

## 限制

- 單個檔案大小限制：50MB（可配置）
- 並發處理任務數：5個
- 處理超時時間：10分鐘
- 支援的檔案格式：PDF, DOCX, DOC, TXT

## 版本資訊

- API版本：RC1
- 支援的Python版本：3.8+
- 支援的瀏覽器：Chrome, Firefox, Safari, Edge
- 最新更新：2025年1月6日

---

**注意**: 這是內部API文檔，主要供開發者參考。一般使用者建議使用Web介面。








