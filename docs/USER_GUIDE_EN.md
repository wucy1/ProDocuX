# ProDocuX User Guide

## 🚀 Quick Start

### 1. First Launch

#### Method 1: Using Executable (Recommended)

1. **Download RC Version**
   - Visit [GitHub Releases](https://github.com/wucy1/ProDocuX/releases)
   - Download `ProDocuX.exe` (approximately 100MB)
   - No Python environment installation required

2. **Start the Application**
   - Double-click `ProDocuX.exe` to launch
   - The application will automatically open browser and redirect to setup page

#### Method 2: Install from Source Code

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

### 📋 RC Version Special Notes

**RC1 Version Features:**
- ✅ File upload functionality working properly
- ✅ Workspace directory management optimized
- ✅ Multi-AI model support complete
- ✅ Chinese/English interface switching
- ⚠️ This is a release candidate version, feedback welcome

**Usage Recommendations:**
- First-time users recommended to use executable version
- If you encounter issues, please report at [GitHub Issues](https://github.com/wucy1/ProDocuX/issues)
- Recommend regular backup of important files in workspace directory

## 🎯 Core Concept: Workflow

**ProDocuX's core design philosophy is workflow-based**. Users must first create a work before they can start processing documents. Each work contains:

1. **Work Basic Information** - Name, description, type, brand
2. **Profile** - Document extraction configuration (AI-generated)
3. **Prompt** - Document processing instructions (AI-generated)
4. **Template** - Output format template (user-uploaded)

### 2. Create Your First Workflow

#### Step 1: Fill Basic Information
1. Click "New Work" button
2. Fill in work information:
   - **Work Name**: e.g., "3M Product PIF Conversion"
   - **Work Description**: Detailed description of the work's purpose and scope
   - **Document Type**: Select document type (PIF, MSDS, Contract, etc.)
   - **Brand/Company**: Enter brand name (optional)

#### Step 2: Upload Output Template
1. Click "Choose Template File"
2. Upload your output format template (Word, Excel, etc.)
3. System will analyze template structure

#### Step 3: Generate Profile (Document Extraction Configuration)
1. Click "Generate Profile Prompt"
2. Copy the generated prompt to your AI tool (ChatGPT, Claude, etc.)
3. Paste the AI-returned JSON configuration back into the system
4. Click "Validate Profile" to confirm correct format

#### Step 4: Generate Prompt (Document Processing Instructions)
1. Click "Generate Prompt Template"
2. Copy the generated prompt to your AI tool
3. Paste the AI-returned prompt back into the system
4. Click "Validate Prompt" to confirm correct content

#### Step 5: Complete Work Creation
1. Click "Create Work"
2. System will automatically select the newly created work
3. Start using this work to process documents

### 3. Using Workflow to Process Documents

#### Select Work
1. Choose the work to use from "Select Work" dropdown
2. System will display work information and configuration

#### Upload Documents
1. Click "Choose Files" button
2. Select PDF or Word files to process
3. Supports batch upload

#### Start Processing
1. Click "Start Processing" button
2. Wait for AI processing to complete
3. Download processing results

### 4. Workflow Management

#### View Work History
- Each work records processing count and learning count
- Can view work creation time and last usage time

#### Continuous Learning Optimization
- Each work learns and optimizes independently
- System automatically improves processing effectiveness based on user corrections

#### Work Switching
- Can switch between different works at any time
- Each work has independent configuration and history records

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
