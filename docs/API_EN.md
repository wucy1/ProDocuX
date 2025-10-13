# ProDocuX API Documentation

## Overview

ProDocuX provides a RESTful API that allows developers to programmatically use document processing features.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, the API does not require authentication, but valid AI API keys must be configured.

## Endpoints

### 1. Health Check

**GET** `/health`

Check service status.

**Response:**
```json
{
  "status": "healthy",
  "version": "RC1",
  "timestamp": "2025-01-06T00:00:00Z"
}
```

### 2. File Upload

**POST** `/upload`

Upload document files for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Parameters:
  - `file`: Document file
  - `template`: Template name (optional)
  - `provider`: AI provider (optional)

**Response:**
```json
{
  "success": true,
  "file_id": "uuid-string",
  "filename": "document.pdf",
  "file_path": "/path/to/file"
}
```

### 3. Page Count

**POST** `/api/pages/count`

Get the number of pages in a document.

**Request:**
```json
{
  "file_id": "uuid-string"
}
```

**Response:**
```json
{
  "success": true,
  "total_pages": 10,
  "file_type": "pdf"
}
```

### 4. Page Preview

**POST** `/api/pages/preview`

Preview document pages for user selection.

**Request:**
```json
{
  "file_id": "uuid-string",
  "pages": [1, 2, 3]
}
```

**Response:**
```json
{
  "success": true,
  "total_pages": 10,
  "pages": [
    {
      "page_number": 1,
      "content": "Page content...",
      "tables": [],
      "images": []
    }
  ]
}
```

### 5. Document Processing

**POST** `/process`

Process documents with AI extraction.

**Request:**
```json
{
  "file_id": "uuid-string",
  "profile": "pif",
  "template": "template.docx",
  "output_format": "docx",
  "ai_provider": "openai",
  "ai_model": "gpt-4o",
  "user_prompt": "Extract product information",
  "selected_pages": [1, 2, 3]
}
```

**Response:**
```json
{
  "success": true,
  "file_id": "uuid-string",
  "data": {
    "product_name": "Product Name",
    "cas_number": "123-45-6",
    "hazard_class": "Flammable"
  },
  "download_url": "/download/filename_result.docx",
  "status": "success"
}
```

### 6. File Download

**GET** `/download/<filename>`

Download processed files.

**Response:**
- File download with appropriate headers

### 7. Profile Management

**GET** `/profiles`

List available profiles.

**Response:**
```json
{
  "success": true,
  "profiles": [
    {
      "name": "pif",
      "description": "Product Information File",
      "fields": ["product_name", "cas_number"]
    }
  ]
}
```

### 8. Template Management

**GET** `/templates`

List available templates.

**Response:**
```json
{
  "templates": [
    {
      "name": "template.docx",
      "description": "Standard template"
    }
  ]
}
```

### 9. Learning System

**POST** `/learn`

Learn from user corrections.

**Request:**
```json
{
  "original_data": {...},
  "corrected_data": {...},
  "source_file": "path/to/file",
  "profile": "pif"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Learning completed"
}
```

**POST** `/learn/word`

Learn from Word document corrections.

**Request:**
- Content-Type: `multipart/form-data`
- Parameters:
  - `file`: Corrected Word document
  - `original_data`: Original extracted data
  - `source_file`: Source file path
  - `profile`: Profile name

**Response:**
```json
{
  "success": true,
  "message": "Learning completed"
}
```

### 10. Cost Estimation

**POST** `/cost/estimate`

Estimate processing costs.

**Request:**
```json
{
  "file_id": "uuid-string",
  "profile": "pif"
}
```

**Response:**
```json
{
  "estimated_cost": 0.05,
  "currency": "USD",
  "breakdown": {
    "input_tokens": 1000,
    "output_tokens": 500,
    "input_cost": 0.02,
    "output_cost": 0.03
  }
}
```

### 11. Settings Management

**GET** `/api/settings`

Get current settings.

**Response:**
```json
{
  "success": true,
  "settings": {
    "ai_provider": "openai",
    "ai_model": "gpt-4o",
    "api_keys": {...},
    "work_directory": "/path/to/work"
  }
}
```

**POST** `/api/settings`

Update settings.

**Request:**
```json
{
  "ai_provider": "openai",
  "ai_model": "gpt-4o",
  "api_keys": {
    "openai": "sk-..."
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Settings updated"
}
```

### 12. Language Management

**GET** `/api/language`

Get current language.

**Response:**
```json
{
  "language": "en",
  "translations": {...}
}
```

**POST** `/api/language`

Set language.

**Request:**
```json
{
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Language updated"
}
```

### 13. Workflow Management

**POST** `/api/workflow/create`

Create a new workflow.

**Request:**
```json
{
  "name": "3M Product PIF",
  "description": "Convert 3M product documents to PIF",
  "type": "pif",
  "brand": "3M",
  "profile": "pif"
}
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "uuid-string",
  "message": "Workflow created"
}
```

**GET** `/api/workflow/list`

List all workflows.

**Response:**
```json
{
  "success": true,
  "workflows": [
    {
      "id": "uuid-string",
      "name": "3M Product PIF",
      "description": "Convert 3M product documents to PIF",
      "type": "pif",
      "brand": "3M",
      "processed_count": 5,
      "learning_count": 2,
      "created_at": "2025-01-06T00:00:00Z"
    }
  ]
}
```

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

Error responses include:
```json
{
  "error": "Error message",
  "details": "Additional error details"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## AI Model Support

### Supported Providers
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
- **Claude**: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus
- **Gemini**: Gemini 2.5 Pro/Flash, Gemini 2.0 Flash series
- **Grok**: Grok-2, Grok-beta
- **Microsoft Copilot**: Based on Azure OpenAI

### Model Pricing
Pricing information is available in the `/cost/estimate` endpoint and is updated regularly based on official provider pricing.

## Examples

### Complete Workflow Example

1. **Upload Document**
```bash
curl -X POST http://localhost:5000/upload \
  -F "file=@document.pdf"
```

2. **Process Document**
```bash
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "uuid-string",
    "profile": "pif",
    "ai_provider": "openai",
    "ai_model": "gpt-4o"
  }'
```

3. **Download Result**
```bash
curl -O http://localhost:5000/download/result.docx
```

## Version Information

- **Current Version**: RC1
- **API Version**: v1
- **Last Updated**: 2025-01-06

---

For more information, see the [User Guide](USER_GUIDE_EN.md) and [Developer Guide](DEVELOPER_GUIDE_EN.md).





