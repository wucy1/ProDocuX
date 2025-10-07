# ProDocuX User Guide

## 🚀 Quick Start

### 1. First Launch

1. **Download and Install**
   ```bash
   git clone https://github.com/wucy1/ProDocuX.git
   cd ProDocuX
   pip install -r requirements.txt
   ```

2. **Start the Application**
   ```bash
   python run.py
   ```

3. **Complete Initial Setup**
   - Open browser and visit `http://localhost:5000/setup`
   - Select AI provider (OpenAI, Claude, Gemini, or Grok)
   - Enter corresponding API key
   - Choose working directory location
   - Select desktop shortcuts to create

### 2. Using Web Interface

1. **Open Browser**
   - Visit `http://localhost:5000`
   - Or click the URL displayed after program startup

2. **Upload Files**
   - Click "Choose Files" button
   - Select PDF or Word files to process
   - Supports batch upload

3. **Select Template**
   - Choose output template from dropdown menu
   - Or use default template

4. **Start Processing**
   - Click "Start Processing" button
   - Wait for AI processing to complete
   - Download processing results

### 3. Using Desktop Shortcuts

1. **Access Files**
   - Double-click "ProDocuX Input Files" shortcut
   - Place files to process in the folder

2. **View Results**
   - Double-click "ProDocuX Output Results" shortcut
   - Get processed files from the folder

3. **Manage Templates**
   - Double-click "ProDocuX Templates" shortcut
   - Customize or modify output templates

## 🔧 Advanced Settings

### 1. Switching AI Models

1. **Open Settings Page**
   - Click "Settings" button in web interface
   - Or directly visit `http://localhost:5000/settings`

2. **Select AI Provider**
   - Choose different AI provider from dropdown
   - Enter corresponding API key

3. **Select Model**
   - Choose specific model based on selected provider
   - Save settings

### 2. Custom Templates

1. **Open Template Folder**
   - Use desktop shortcut or web interface
   - Find `templates/` folder

2. **Modify Template**
   - Edit Word template files
   - Keep variable names unchanged
   - Can modify styles and formats

3. **Test Template**
   - Use test files to validate template
   - Ensure output format is correct

### 3. Batch Processing

1. **Prepare Files**
   - Place all files to process in `input/` folder
   - Ensure file formats are correct

2. **Start Batch Processing**
   - Select "Batch Processing" mode in web interface
   - Or use command line tools

3. **Monitor Progress**
   - View processing progress and status
   - Check results after processing completes

## 📋 Frequently Asked Questions

### Q: How to get API keys?

**A: Based on selected AI provider:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Claude**: https://console.anthropic.com/
- **Gemini**: https://makersuite.google.com/app/apikey
- **Grok**: https://console.x.ai/

### Q: What file formats are supported?

**A: Currently supports:**
- PDF files (.pdf)
- Word documents (.docx, .doc)
- Plain text files (.txt)

### Q: How fast is processing?

**A: Processing speed depends on:**
- File size and complexity
- Selected AI model
- Network connection speed
- Generally, 1-2 page documents take 10-30 seconds

### Q: How to improve processing accuracy?

**A: Recommendations:**
- Use high-quality AI models (like GPT-4, Claude 3)
- Ensure input documents are clear and readable
- Use appropriate prompt templates
- Select corresponding processing rules based on document type

### Q: Is data secure?

**A: Completely secure:**
- All documents processed locally
- API keys stored securely
- Not uploaded to external servers
- Can choose to delete cache after processing

## 🛠️ Troubleshooting

### Problem 1: Cannot start application

**Solutions:**
1. Check Python version (requires 3.8+)
2. Confirm all dependencies installed: `pip install -r requirements.txt`
3. Check firewall settings
4. View error logs

### Problem 2: Invalid API key

**Solutions:**
1. Confirm API key format is correct
2. Check if API key has expired
3. Confirm account has sufficient credits
4. Reconfigure API key

### Problem 3: Processing failed

**Solutions:**
1. Check if file format is supported
2. Confirm file is not corrupted
3. Try using different AI model
4. Check network connection

### Problem 4: Incorrect output format

**Solutions:**
1. Check if template file is correct
2. Confirm variable names match
3. Try using default template
4. Adjust prompt settings

## 💰 Cost Management

### Real-time Cost Calculation

ProDocuX provides real-time cost estimation for all supported AI models:

- **Input Tokens**: Calculated based on document content
- **Output Tokens**: Calculated based on AI response length
- **Model Pricing**: Updated with latest official pricing
- **Batch Processing**: Supports batch mode discounts

### Cost Optimization Tips

1. **Choose Appropriate Model**
   - Use GPT-4o-mini for simple tasks
   - Use GPT-4o for complex documents
   - Consider Gemini Flash for cost-effective processing

2. **Optimize Prompts**
   - Use concise, clear prompts
   - Avoid unnecessary instructions
   - Test with smaller documents first

3. **Batch Processing**
   - Process multiple documents together
   - Use batch mode when available
   - Monitor token usage

## 🎯 Use Cases

### 1. Enterprise Document Standardization

- Convert MSDS from different suppliers to unified format
- Automatically extract product information and ingredient data
- Generate PIF documents compliant with regulations

### 2. Research Data Organization

- Extract key data from research reports
- Convert PDF documents to structured data
- Automatically generate summaries and classifications

### 3. Content Creation Assistance

- Restructure long documents into concise formats
- Extract key information and reorganize
- Generate documents in different languages

## 🔒 Privacy and Security

### Data Protection

- **Local Processing**: All documents processed locally
- **API Security**: API keys securely stored in local environment variables
- **Data Protection**: Data during processing is not permanently saved
- **Open Source**: Completely open source, code auditable

### Security Features

- No data uploaded to external servers
- API keys encrypted and stored locally
- Automatic cleanup of temporary files
- No tracking or analytics

## 📞 Getting Help

If you encounter other issues:

1. **Check Documentation**: Read complete README and documentation
2. **Search Issues**: Search for similar issues in GitHub Issues
3. **Report Issues**: Create new Issue describing the problem
4. **Join Discussions**: Ask questions in GitHub Discussions

## 📚 Additional Resources

- **GitHub Repository**: https://github.com/wucy1/ProDocuX
- **API Documentation**: [API.md](../API.md)
- **Developer Guide**: [DEVELOPER_GUIDE_EN.md](DEVELOPER_GUIDE_EN.md)
- **Contributing Guide**: [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**Version**: RC1  
**Last Updated**: January 6, 2025

**Happy Processing!** 🎉
