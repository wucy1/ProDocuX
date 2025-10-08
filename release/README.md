# ProDocuX

> AI-Driven Intelligent Document Conversion Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Compatible-green.svg)](https://openai.com/)
[![Claude](https://img.shields.io/badge/Claude-Compatible-orange.svg)](https://anthropic.com/)

🌐 **Official Website**: [https://prodocux.com](https://prodocux.com)

## 🚀 Introduction

ProDocuX is an AI-powered intelligent document conversion platform that transforms various document formats (PDF, Word, etc.) into structured documents. It supports multiple AI models including OpenAI, Claude, Gemini, and Grok, allowing you to choose the most suitable AI assistant for your needs.

## ✨ Key Features

### 🔄 Intelligent Document Conversion
- **Multi-format Support**: PDF, DOCX, DOC, and other formats
- **Structured Extraction**: Automatically extracts key information from documents
- **Chinese Optimization**: Optimized for Chinese document processing
- **Batch Processing**: Support for processing multiple files at once
- **Direct File Output**: Support for AI direct PDF/Word file output

### 🤖 Multi-AI Model Support
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
- **Claude**: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus
- **Gemini**: Gemini 2.5 Pro/Flash, Gemini 2.0 Flash series
- **Grok**: Grok-2, Grok-beta
- **Microsoft Copilot**: Copilot models based on Azure OpenAI

### 🎯 Professional Use Cases
- **MSDS to PIF**: Convert Safety Data Sheets to Product Information Files
- **Document Standardization**: Unify document formats from different sources
- **Data Extraction**: Extract structured data from complex documents
- **Content Restructuring**: Reorganize documents into standard formats

### 🧠 Learning System
- **Pattern Recognition**: Automatically learns from user corrections
- **Rule Generation**: Generates conversion rules based on corrections
- **Continuous Improvement**: Continuously improves accuracy through learning
- **Multi-modal Learning**: Supports both JSON and Word document learning

### 🔧 Workflow Management
- **Named Workflows**: Create dedicated workflows for different tasks
- **Intelligent Profile Recommendations**: System recommends optimal extraction configurations
- **Work History Tracking**: Track processing and learning history for each workflow
- **Hierarchical Profiles**: Base → Brand → Work-specific profile system

## 🛠️ Installation & Usage

### Quick Start

1. **Download ProDocuX**
   ```bash
   git clone https://github.com/wucy1/ProDocuX.git
   cd ProDocuX
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Application**
   ```bash
   python run.py
   ```

4. **Complete Initial Setup**
   - Open browser and visit `http://localhost:5000/setup`
   - Select AI provider (OpenAI, Claude, Gemini, or Grok)
   - Enter corresponding API key
   - Choose working directory location
   - Select desktop shortcuts to create

5. **Access Web Interface**
   - Open browser and visit `http://localhost:5000`
   - Upload documents and start processing

### First-Time Setup

For first-time users, run the simplified setup:

```bash
python simple_setup.py
```

This will guide you through:
- API key configuration
- Working directory setup
- Desktop shortcut creation

## 📚 Documentation

### User Guides
- **[English User Guide](docs/USER_GUIDE_EN.md)** - Comprehensive user guide
- **[Chinese User Guide](docs/USER_GUIDE_ZH.md)** - 中文使用者指南

### Developer Resources
- **[English Developer Guide](docs/DEVELOPER_GUIDE_EN.md)** - Developer documentation
- **[Chinese Developer Guide](docs/DEVELOPER_GUIDE_ZH.md)** - 中文開發者指南

### API Documentation
- **[English API Docs](docs/API_EN.md)** - Complete API reference
- **[Chinese API Docs](docs/API_ZH.md)** - 中文API文檔

### Specialized Guides
- **[Workflow Management Guide](docs/WORKFLOW_GUIDE.md)** - Workflow creation and management
- **[Learning System Guide](docs/LEARNING_SYSTEM_GUIDE.md)** - AI learning functionality
- **[Project Structure](docs/STRUCTURE_EN.md)** - Project architecture overview

## 🔧 Configuration

### Environment Variables

Copy `env_example.txt` to `.env` and configure:

```bash
# AI Provider Settings
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GROK_API_KEY=your_grok_api_key_here

# Model Settings
OPENAI_MODEL=gpt-4o
CLAUDE_MODEL=claude-3-5-sonnet-20241022
GEMINI_MODEL=gemini-2.5-pro
GROK_MODEL=grok-2
```

### AI Model Pricing

ProDocuX includes real-time AI model pricing information:

- **OpenAI**: $0.005-$0.03 per 1K tokens
- **Claude**: $0.0008-$0.075 per 1K tokens  
- **Gemini**: $0.000075-$0.01 per 1K tokens
- **Grok**: $0.0002-$0.0015 per 1K tokens

Pricing is automatically calculated and displayed during processing.

## 🎯 Use Cases

### Chemical Industry
- **MSDS to PIF Conversion**: Convert Safety Data Sheets to Product Information Files
- **Chemical Data Extraction**: Extract CAS numbers, hazard classifications, and safety information
- **Regulatory Compliance**: Generate compliant documentation for chemical products

### Manufacturing
- **Product Documentation**: Standardize product information across different formats
- **Quality Control**: Extract and validate product specifications
- **Supply Chain**: Process supplier documentation efficiently

### Research & Development
- **Literature Processing**: Extract structured data from research papers
- **Patent Analysis**: Process patent documents for key information
- **Technical Documentation**: Convert technical specifications to standard formats

## 🚀 Advanced Features

### Direct File Output
ProDocuX supports AI models that can directly output PDF or Word files:

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

### Intelligent Profile System
- **Base Profiles**: General extraction rules
- **Brand Profiles**: Brand-specific optimizations
- **Work-specific Profiles**: Customized for specific workflows

### Learning System
- **JSON Learning**: Learn from direct data corrections
- **Word Learning**: Learn from Word document modifications
- **Pattern Recognition**: Automatically identify correction patterns
- **Rule Generation**: Generate new extraction rules

## 🔒 Security & Privacy

- **Local Processing**: All processing happens locally
- **No Data Upload**: Documents are not uploaded to external servers
- **API Key Security**: Secure storage of API keys
- **Content Safety**: Built-in content safety checks

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/DEVELOPER_GUIDE_EN.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check our comprehensive guides in the `docs/` directory
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/wucy1/ProDocuX/issues)
- **Discussions**: Join the conversation on [GitHub Discussions](https://github.com/wucy1/ProDocuX/discussions)

## 🎉 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude models
- Google for Gemini models
- xAI for Grok models
- Microsoft for Copilot integration

---

**ProDocuX** - Empowering your document processing with AI! 🚀

[中文版 README](docs/README_ZH.md)