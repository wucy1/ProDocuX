# ProDocuX Project Structure

## 📁 Directory Overview

```
ProDocuX/
├── 📄 README.md              # Main project documentation
├── 📄 LICENSE                # License terms
├── 📄 requirements.txt       # Python dependencies
├── 📄 env_example.txt        # Environment variables example
├── 📄 run.py                 # Main program entry point
├── 📄 simple_setup.py        # Simplified setup script
├── 📄 workflow_preferences.json # Workflow preferences
├── 📁 core/                  # Core processing modules
│   ├── __init__.py
│   ├── extractor.py          # Document extractor
│   ├── transformer.py        # Document transformer
│   ├── profile_manager.py    # Configuration manager
│   ├── learner.py            # Learning module
│   └── prompt_parser.py      # Prompt parser
├── 📁 utils/                 # Utility functions
│   ├── __init__.py
│   ├── ai_client.py          # AI client
│   ├── multi_ai_client.py    # Multi-AI model client
│   ├── file_handler.py       # File processor
│   ├── settings_manager.py   # Settings manager
│   ├── desktop_manager.py    # Desktop manager
│   ├── cost_calculator.py    # Cost calculator
│   ├── logger.py             # Logging utility
│   ├── pricing_manager.py    # Pricing manager
│   ├── safety_precheck.py    # Safety pre-check
│   └── workflow_preferences.py # Workflow preferences
├── 📁 web/                   # Web interface
│   ├── app.py                # Flask application
│   ├── static/               # Static resources
│   │   ├── css/style.css     # Stylesheet
│   │   ├── js/main.js        # JavaScript
│   │   └── images/logo.png   # Logo image
│   └── templates/            # HTML templates
│       ├── index.html        # Main page
│       ├── settings.html     # Settings page
│       └── setup.html        # Setup page
├── 📁 profiles/              # Extraction rule configurations
│   ├── base/                 # Base profiles
│   │   ├── default.yml       # Default profile
│   │   ├── msds.yml          # MSDS profile
│   │   └── pif.yml           # PIF profile
│   ├── default.yml           # Default profile
│   └── pif.yml               # PIF profile
├── 📁 templates/             # Output templates
├── 📁 locale/                # Internationalization
│   ├── en.json               # English translations
│   └── zh_TW.json            # Traditional Chinese translations
├── 📁 config/                # Configuration files
│   └── ai_pricing.json       # AI model pricing
├── 📁 deploy/                # Deployment scripts
│   └── build.py              # Build script
└── 📁 docs/                  # Documentation
    ├── README.md             # Documentation center
    ├── USER_GUIDE_EN.md      # English user guide
    ├── USER_GUIDE_ZH.md      # Chinese user guide
    ├── DEVELOPER_GUIDE_EN.md # English developer guide
    ├── DEVELOPER_GUIDE_ZH.md # Chinese developer guide
    ├── WORKFLOW_GUIDE.md     # Workflow management guide
    ├── LEARNING_GUIDE.md     # Learning feature guide
    ├── LEARNING_SYSTEM_GUIDE.md # Learning system guide
    ├── STRUCTURE_EN.md       # English structure guide
    ├── STRUCTURE_ZH.md       # Chinese structure guide
    ├── API_EN.md             # English API documentation
    └── API_ZH.md             # Chinese API documentation
```

## 🔧 Core Modules

### core/ - Core Processing Modules
- **extractor.py**: Extracts structured data from documents
- **transformer.py**: Transforms extracted data into target formats
- **profile_manager.py**: Manages extraction rules for different document types
- **learner.py**: Learns and optimizes rules from user corrections
- **prompt_parser.py**: Parses and processes AI prompts

### utils/ - Utility Functions
- **ai_client.py**: Basic AI client implementation
- **multi_ai_client.py**: Unified management of multiple AI models
- **file_handler.py**: File read/write and format conversion
- **settings_manager.py**: System settings management
- **desktop_manager.py**: Desktop environment management
- **cost_calculator.py**: API cost calculation
- **logger.py**: Logging utility
- **pricing_manager.py**: AI model pricing management
- **safety_precheck.py**: Content safety pre-checking
- **workflow_preferences.py**: Workflow preferences management

### web/ - Web Interface
- **app.py**: Flask web application main program
- **static/**: Frontend static resources (CSS, JS, images)
- **templates/**: HTML template files

## 📋 Configuration Files

### profiles/ - Extraction Rules
- Defines extraction rules for different document types
- Supports YAML format configuration
- Customizable and extensible
- Hierarchical profile system (base → brand → work-specific)

### templates/ - Output Templates
- Word document templates
- Supports variable replacement
- Customizable styles
- Template management system

### locale/ - Internationalization
- English and Traditional Chinese support
- JSON-based translation files
- Dynamic language switching

### config/ - Configuration Files
- AI model pricing configuration
- System-wide settings
- Environment-specific configurations

## 🚀 Entry Points

### run.py - Main Program
- Program startup entry point
- Handles command line arguments
- Starts web service
- Environment setup

### simple_setup.py - Simplified Setup
- First-time startup configuration
- Guides users through initial setup
- Creates necessary directories
- API key configuration

## 🧪 Testing & Deployment

### deploy/ - Deployment Scripts
- Build scripts
- Installation programs
- Release tools
- Package creation

## 📝 Documentation Files

- **README.md**: Main project description
- **docs/**: Comprehensive documentation center
- **USER_GUIDE_***: Detailed user guides (EN/ZH)
- **DEVELOPER_GUIDE_***: Developer guides (EN/ZH)
- **API_***: API documentation (EN/ZH)
- **STRUCTURE_***: Project structure guides (EN/ZH)

## 🔒 Security Files

- **.gitignore**: Git ignore file list
- **env_example.txt**: Environment variables example
- **LICENSE**: MIT License terms

## 🌟 Key Features

### Multi-AI Model Support
- OpenAI GPT series
- Claude series
- Gemini series
- Grok series
- Microsoft Copilot

### Document Processing
- PDF, DOCX, DOC format support
- Structured data extraction
- Chinese language optimization
- Batch processing
- Direct file output (PDF/Word)

### Workflow Management
- Named work creation
- Intelligent profile recommendations
- Work history tracking
- Continuous learning optimization

### Learning System
- JSON data learning
- Word document learning
- Pattern recognition
- Rule generation
- Continuous improvement

---

**Note**: This structure is designed for GitHub release, with development temporary files and sensitive information removed.





