#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProDocuX 主執行檔案
一鍵啟動ProDocuX應用
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """檢查並安裝依賴套件"""
    # 如果是打包後的可執行檔，跳過依賴檢查
    if getattr(sys, 'frozen', False):
        user_lang = get_user_language()
        print(get_message('packaged_version', user_lang))
        return True
    
    required_packages = [
        'flask',
        'openai',
        'pdfplumber',
        'python-docx',
        'docxtpl',
        'pyyaml',
        'pydantic',
        'python-dotenv',
        'docx2pdf'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("正在安裝依賴套件...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                *missing_packages, "--quiet"
            ])
            print("依賴套件安裝完成")
        except subprocess.CalledProcessError as e:
            print(f"依賴套件安裝失敗: {e}")
            return False
    
    return True

def check_api_key():
    """檢查API金鑰設定"""
    # 先檢查環境變數
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('IOPENAI_API_KEY')
    
    if not api_key:
        # 嘗試從工作空間載入.env檔案
        try:
            from utils.desktop_manager import DesktopManager
            desktop_manager = DesktopManager()
            env_file = desktop_manager.workspace_dir / ".env"
            
            if env_file.exists():
                from dotenv import load_dotenv
                load_dotenv(env_file)
                api_key = os.getenv('OPENAI_API_KEY') or os.getenv('IOPENAI_API_KEY')
        except Exception:
            pass
    
    if not api_key:
        user_lang = get_user_language()
        print(get_message('no_api_key', user_lang))
        print(get_message('api_key_help', user_lang))
        print(get_message('env_vars', user_lang))
        return False
    
    return True

def create_directories():
    """創建必要的目錄"""
    user_lang = get_user_language()
    try:
        from utils.desktop_manager import DesktopManager
        
        desktop_manager = DesktopManager()
        workspace_dirs = desktop_manager.setup_workspace()
        
        print(f"{get_message('workspace_ready', user_lang)}: {desktop_manager.workspace_dir}")
        
        if desktop_manager.is_desktop_environment:
            print(get_message('desktop_detected', user_lang))
        
        return True
        
    except Exception as e:
        print(f"目錄創建失敗: {e}")
        # 對於打包版本，不應該在 dist 目錄創建檔案
        if getattr(sys, 'frozen', False):
            print("打包版本無法創建目錄，請手動設定工作空間")
            return False
        
        # 回退到傳統方式（僅限開發環境）
        # 對於打包版本，不應該在 dist 目錄創建這些目錄
        if not getattr(sys, 'frozen', False):
            directories = [
                'uploads',
                'outputs', 
                'cache',
                'cache/learning',
                'profiles',
                'templates',
                'prompts'
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
        
        print("目錄結構已準備完成（傳統模式）")
        return True

def create_env_file():
    """創建環境變數範例檔案"""
    user_lang = get_user_language()
    # 對於打包版本，不應該在 dist 目錄創建 .env 檔案
    if getattr(sys, 'frozen', False):
        print(get_message('skip_env_creation', user_lang))
        return
    
    env_file = Path('.env')
    if not env_file.exists():
        # 嘗試複製env_example.txt
        env_example_file = Path('env_example.txt')
        if env_example_file.exists():
            import shutil
            shutil.copy2(env_example_file, env_file)
            print("已從 env_example.txt 創建 .env 檔案，請填入您的API金鑰")
        else:
            # 如果沒有範例檔案，創建基本.env檔案
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write("""# ProDocuX 環境變數設定
# 請填入您的OpenAI API金鑰

# OpenAI API設定
OPENAI_API_KEY=your_openai_api_key_here
IOPENAI_API_KEY=your_iopenai_api_key_here

# Claude API設定
CLAUDE_API_KEY=your_claude_api_key_here

# Gemini API設定
GEMINI_API_KEY=your_gemini_api_key_here

# Grok API設定
GROK_API_KEY=your_grok_api_key_here

# 模型設定
OPENAI_MODEL=gpt-4
IOPENAI_MODEL=gpt-4
CLAUDE_MODEL=claude-3-sonnet-20240229
GEMINI_MODEL=gemini-pro
GROK_MODEL=grok-beta

# 其他設定
MAX_CHUNK_SIZE=8000
CONFIDENCE_THRESHOLD=0.7
""")
            print("已創建 .env 範例檔案，請填入您的API金鑰")

def start_web_app():
    """啟動Web應用"""
    user_lang = get_user_language()
    try:
        from web.app import create_app
        
        app = create_app()
        
        print(get_message('starting_web_service', user_lang))
        print(get_message('browser_open', user_lang))
        print(get_message('stop_service', user_lang))
        
        # 延遲開啟瀏覽器
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"模組導入失敗: {e}")
        print("請確保所有依賴套件已正確安裝")
    except Exception as e:
        print(f"應用啟動失敗: {e}")

def is_chinese_language(lang_string):
    """檢查是否為中文語言"""
    if not lang_string:
        return False
    
    lang_lower = lang_string.lower()
    zh_indicators = [
        'zh', 'chinese', 'taiwan', 'traditional', 'simplified',
        'china', 'hong kong', 'macau', 'singapore', 'malaysia',
        'zh-cn', 'zh-tw', 'zh-hk', 'zh-sg', 'zh-mo',
        'zh_hans', 'zh_hant', 'zh_hans_cn', 'zh_hant_tw',
        'chinese_traditional', 'chinese_simplified',
        '繁體', '簡體', '中文', '中國', '台灣', '香港', '澳門'
    ]
    return any(zh_code in lang_lower for zh_code in zh_indicators)

def get_user_language():
    """檢測使用者語言"""
    import locale
    try:
        # 檢查環境變數
        lang = os.getenv('LANG') or os.getenv('LC_ALL') or os.getenv('LC_CTYPE')
        if is_chinese_language(lang):
            return 'zh_TW'
        
        # 檢查系統語言 (使用新的 API)
        try:
            # 嘗試使用新的 API
            system_lang = locale.getlocale()[0]
        except (AttributeError, ValueError):
            # 如果新 API 不可用，回退到舊 API
            try:
                system_lang = locale.getdefaultlocale()[0]
            except (AttributeError, ValueError):
                system_lang = None
        
        if is_chinese_language(system_lang):
            return 'zh_TW'
            
        return 'en'
    except:
        return 'en'

def get_message(key, lang):
    """獲取本地化訊息"""
    messages = {
        'zh_TW': {
            'title': 'ProDocuX - AI文檔智能轉換平台',
            'first_run_detected': '檢測到首次啟動，正在進行初始設定...',
            'setup_requirements': '為了確保ProDocuX正常運作，我們需要完成以下設定：',
            'step1': '   1. 工作空間目錄設定',
            'step2': '   2. AI提供者選擇',
            'step3': '   3. API金鑰配置',
            'step4': '   4. 桌面快捷方式選擇',
            'setup_methods': '建議使用以下方式進行設定：',
            'method1': '   方法1: 運行 \'python simple_setup.py\' 進行命令行設定',
            'method2': '   方法2: 啟動Web介面後在設定頁面中配置',
            'starting_web': '正在啟動Web設定介面...',
            'browser_url': '   請在瀏覽器中前往: http://localhost:5000/setup',
            'starting_app': '啟動ProDocuX Web應用...',
            'packaged_version': '檢測到打包版本，跳過依賴檢查',
            'workspace_ready': '工作目錄已準備完成',
            'desktop_detected': '桌面環境檢測完成，已創建專用工作目錄',
            'skip_env_creation': '打包版本跳過 .env 檔案創建，請在工作空間中設定',
            'no_api_key': '未設定OpenAI API金鑰',
            'api_key_help': '請在首次啟動時設定API金鑰，或手動設定環境變數',
            'env_vars': '環境變數: OPENAI_API_KEY 或 IOPENAI_API_KEY',
            'no_api_key_web': '未設定API金鑰，將啟動Web應用讓您在設定頁面中配置',
            'api_key_web_help': '您可以在Web介面的設定頁面中輸入API金鑰',
            'starting_web_service': '啟動ProDocuX Web服務...',
            'browser_open': '請在瀏覽器開啟: http://localhost:5000',
            'stop_service': '按 Ctrl+C 停止服務',
            'thanks': '感謝使用ProDocuX！',
            'error': '發生錯誤'
        },
        'en': {
            'title': 'ProDocuX - AI Document Intelligence Platform',
            'first_run_detected': 'First launch detected, initializing setup...',
            'setup_requirements': 'To ensure ProDocuX works properly, we need to complete the following setup:',
            'step1': '   1. Workspace directory setup',
            'step2': '   2. AI provider selection',
            'step3': '   3. API key configuration',
            'step4': '   4. Desktop shortcuts selection',
            'setup_methods': 'Recommended setup methods:',
            'method1': '   Method 1: Run \'python simple_setup.py\' for command line setup',
            'method2': '   Method 2: Configure in settings page after starting web interface',
            'starting_web': 'Starting web setup interface...',
            'browser_url': '   Please visit in browser: http://localhost:5000/setup',
            'starting_app': 'Starting ProDocuX Web application...',
            'packaged_version': 'Packaged version detected, skipping dependency check',
            'workspace_ready': 'Workspace directory ready',
            'desktop_detected': 'Desktop environment detected, created dedicated workspace',
            'skip_env_creation': 'Packaged version skips .env file creation, please configure in workspace',
            'no_api_key': 'OpenAI API key not set',
            'api_key_help': 'Please set API key during first launch, or manually set environment variables',
            'env_vars': 'Environment variables: OPENAI_API_KEY or IOPENAI_API_KEY',
            'no_api_key_web': 'No API key set, will start web application for configuration',
            'api_key_web_help': 'You can enter API key in the web interface settings page',
            'starting_web_service': 'Starting ProDocuX Web service...',
            'browser_open': 'Please open in browser: http://localhost:5000',
            'stop_service': 'Press Ctrl+C to stop service',
            'thanks': 'Thank you for using ProDocuX!',
            'error': 'An error occurred'
        }
    }
    return messages.get(lang, messages['en']).get(key, key)

def main():
    """主函數"""
    # 檢測使用者語言
    user_lang = get_user_language()
    msg = get_message
    
    print("=" * 60)
    print(msg('title', user_lang))
    print("=" * 60)
    
    # 檢查是否為首次啟動
    if is_first_run():
        print(msg('first_run_detected', user_lang))
        print(msg('setup_requirements', user_lang))
        print(msg('step1', user_lang))
        print(msg('step2', user_lang))
        print(msg('step3', user_lang))
        print(msg('step4', user_lang))
        print("")
        print(msg('setup_methods', user_lang))
        print(msg('method1', user_lang))
        print(msg('method2', user_lang))
        print("")
        print(msg('starting_web', user_lang))
        print(msg('browser_url', user_lang))
        print("")
    else:
        print(msg('starting_app', user_lang))
    
    # 檢查依賴
    if not check_dependencies():
        print("依賴檢查失敗，請手動安裝依賴套件")
        print("執行: pip install -r requirements.txt")
        return
    
    # 創建目錄
    create_directories()
    
    # 創建環境變數檔案
    create_env_file()
    
    # 檢查API金鑰
    if not check_api_key():
        print(f"\n{get_message('no_api_key_web', user_lang)}")
        print(get_message('api_key_web_help', user_lang))
    
    # 啟動應用
    start_web_app()

def is_first_run():
    """檢查是否為首次運行"""
    try:
        from utils.desktop_manager import DesktopManager
        desktop_manager = DesktopManager()
        
        # 檢查設定檔案
        config_file = desktop_manager.workspace_dir / "startup_config.json"
        return not config_file.exists()
        
    except Exception:
        return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        user_lang = get_user_language()
        print(f"\n{get_message('thanks', user_lang)}")
    except Exception as e:
        user_lang = get_user_language()
        print(f"\n{get_message('error', user_lang)}: {e}")
        sys.exit(1)
