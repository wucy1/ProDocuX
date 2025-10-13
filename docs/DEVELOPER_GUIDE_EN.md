# ProDocuX Developer Guide

## Overview

ProDocuX is an AI-powered intelligent document conversion platform that transforms various document formats (PDF, Word, etc.) into structured Chinese documents. This guide provides comprehensive information for developers who want to contribute to or integrate with ProDocuX.

## Architecture

### Core Components

```
ProDocuX/
├── core/              # Core processing modules
│   ├── extractor.py   # Document extraction logic
│   ├── transformer.py # Data transformation logic
│   └── ...
├── web/               # Web interface
│   ├── app.py         # Flask application
│   ├── templates/     # HTML templates
│   └── static/        # CSS, JS, images
├── utils/             # Utility functions
│   ├── multi_ai_client.py  # AI client management
│   └── ...
├── profiles/          # Extraction rule configurations
├── prompts/           # AI prompt templates
└── templates/         # Output document templates
```

### Key Classes

#### DocumentExtractor
- **Purpose**: Extracts structured data from documents using AI
- **Key Methods**:
  - `extract_data()`: Main extraction method
  - `_parse_ai_response()`: Parses AI responses (JSON, direct files)
  - `_is_file_output_response()`: Detects direct file outputs

#### DocumentTransformer
- **Purpose**: Transforms extracted data into output documents
- **Key Methods**:
  - `transform_to_document()`: Main transformation method
  - `_extract_ingredients_from_field()`: Handles ingredient parsing
  - `_load_profile()`: Loads profile configurations

#### MultiAIClient
- **Purpose**: Manages multiple AI providers and models
- **Key Methods**:
  - `get_available_providers()`: Lists available AI providers
  - `process_prompt()`: Processes prompts with selected AI
  - `get_model_pricing()`: Returns model pricing information

## AI Integration

### Supported Providers

1. **OpenAI**
   - Models: GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
   - API: OpenAI API v1

2. **Claude (Anthropic)**
   - Models: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus
   - API: Anthropic API

3. **Gemini (Google)**
   - Models: Gemini 2.5 Pro/Flash, Gemini 2.0 Flash series
   - API: Google AI Studio API

4. **Grok (xAI)**
   - Models: Grok-2, Grok-beta
   - API: xAI API

5. **Microsoft Copilot**
   - Models: Based on Azure OpenAI Service
   - API: Azure OpenAI API

### Response Handling

ProDocuX handles multiple AI response formats:

1. **Structured JSON**: Standard structured data response
2. **JSON in Markdown**: JSON wrapped in markdown code blocks
3. **Direct File Output**: Base64-encoded files or download links
4. **Multi-level JSON**: Nested JSON structures

```python
# Example response parsing
def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
    # Try direct file output first
    if self._is_file_output_response(response_text):
        return self._extract_file_from_response(response_text)
    
    # Try JSON parsing
    json_data = self._extract_json_from_response(response_text)
    if json_data:
        return json_data
    
    # Fallback to text processing
    return {"raw_text": response_text}
```

## Profile System

Profiles define extraction rules and field mappings for different document types.

### Profile Structure

```yaml
# Example profile (YAML format)
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

### Profile Loading

```python
def _load_profile(self, profile_path: str):
    """Load profile configuration from YAML file"""
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile_data = yaml.safe_load(f)
    
    self.profile_fields = {}
    for field_key, field_config in profile_data.get('fields', {}).items():
        self.profile_fields[field_key] = field_config.get('name', field_key)
```

## API Development

### Flask Routes

#### Main Processing Route
```python
@app.route('/process', methods=['POST'])
def process_document():
    # File upload handling
    # AI processing
    # Document transformation
    # Response generation
```

#### Settings Management
```python
@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    # Get/set application settings
    # AI provider configuration
    # Model selection
```

### Error Handling

```python
try:
    # Processing logic
    result = process_document(file, template, settings)
    return jsonify({"success": True, "result": result})
except Exception as e:
    logger.error(f"Processing failed: {str(e)}")
    return jsonify({"success": False, "error": str(e)}), 500
```

## Frontend Development

### JavaScript Architecture

#### Main Application (main.js)
- File upload handling
- AI model selection
- Cost calculation
- Progress tracking

#### Settings Management
- Provider selection
- API key management
- Model configuration
- Settings persistence

### UI Components

#### File Upload
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

#### Cost Calculation
```javascript
function calculateCost(tokens, model) {
    const pricing = getModelPricing(model);
    const inputCost = (tokens.input / 1000) * pricing.input;
    const outputCost = (tokens.output / 1000) * pricing.output;
    return inputCost + outputCost;
}
```

## Testing

### Unit Tests

```python
import pytest
from core.extractor import DocumentExtractor

def test_extract_data():
    """Test document data extraction"""
    extractor = DocumentExtractor()
    result = extractor.extract_data("test content")
    assert result is not None
    assert "extracted_data" in result

def test_ai_response_parsing():
    """Test AI response parsing"""
    extractor = DocumentExtractor()
    
    # Test JSON response
    json_response = '{"data": {"field": "value"}}'
    result = extractor._parse_ai_response(json_response)
    assert result["data"]["field"] == "value"
    
    # Test file output response
    file_response = "Here is your document: [FILE:base64data]"
    result = extractor._parse_ai_response(file_response)
    assert "file_content" in result
```

### Integration Tests

```python
def test_end_to_end_processing():
    """Test complete document processing workflow"""
    # Upload test document
    # Process with AI
    # Verify output format
    # Check cost calculation
```

## Deployment

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"
export CLAUDE_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export GROK_API_KEY="your-key"

# Run application
python run.py
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

## Performance Optimization

### Caching Strategy

- **Response Caching**: Cache AI responses for similar documents
- **Template Caching**: Cache compiled templates
- **Profile Caching**: Cache loaded profiles

### Memory Management

- **Streaming Processing**: Process large documents in chunks
- **Garbage Collection**: Clean up temporary files
- **Resource Limits**: Set limits on concurrent processing

## Security Considerations

### API Key Management

- Store API keys in environment variables
- Never commit keys to version control
- Use secure key rotation

### Input Validation

- Validate file types and sizes
- Sanitize user inputs
- Implement rate limiting

### Data Privacy

- Process documents locally
- Don't store sensitive data
- Implement data retention policies

## Contributing

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Add unit tests for new features

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request
5. Address review feedback

### Issue Reporting

When reporting issues, include:
- Python version
- Operating system
- Error messages
- Steps to reproduce
- Expected vs actual behavior

## Resources

- **GitHub Repository**: https://github.com/wucy1/ProDocuX
- **API Documentation**: [API.md](../API.md)
- **User Guide**: [USAGE.md](../USAGE.md)
- **Contributing Guide**: [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**Version**: RC1  
**Last Updated**: January 6, 2025





