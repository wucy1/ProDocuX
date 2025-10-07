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
        print("🔧 正在安裝依賴套件...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                *missing_packages, "--quiet"
            ])
            print("✅ 依賴套件安裝完成")
        except subprocess.CalledProcessError as e:
            print(f"❌ 依賴套件安裝失敗: {e}")
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
        print("⚠️  未設定OpenAI API金鑰")
        print("請在首次啟動時設定API金鑰，或手動設定環境變數")
        print("環境變數: OPENAI_API_KEY 或 IOPENAI_API_KEY")
        return False
    
    return True

def create_directories():
    """創建必要的目錄"""
    try:
        from utils.desktop_manager import DesktopManager
        
        desktop_manager = DesktopManager()
        workspace_dirs = desktop_manager.setup_workspace()
        
        print(f"✅ 工作目錄已準備完成: {desktop_manager.workspace_dir}")
        
        if desktop_manager.is_desktop_environment:
            print("🖥️  桌面環境檢測完成，已創建專用工作目錄")
        
        return True
        
    except Exception as e:
        print(f"❌ 目錄創建失敗: {e}")
        # 回退到傳統方式
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
        
        print("✅ 目錄結構已準備完成（傳統模式）")
        return True

def create_env_file():
    """創建環境變數範例檔案"""
    env_file = Path('.env')
    if not env_file.exists():
        # 嘗試複製env_example.txt
        env_example_file = Path('env_example.txt')
        if env_example_file.exists():
            import shutil
            shutil.copy2(env_example_file, env_file)
            print("📝 已從 env_example.txt 創建 .env 檔案，請填入您的API金鑰")
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
            print("📝 已創建 .env 範例檔案，請填入您的API金鑰")

def start_web_app():
    """啟動Web應用"""
    try:
        from web.app import create_app
        
        app = create_app()
        
        print("🚀 啟動ProDocuX Web服務...")
        print("🌐 請在瀏覽器開啟: http://localhost:5000")
        print("⏹️  按 Ctrl+C 停止服務")
        
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
        print(f"❌ 模組導入失敗: {e}")
        print("請確保所有依賴套件已正確安裝")
    except Exception as e:
        print(f"❌ 應用啟動失敗: {e}")

def main():
    """主函數"""
    print("=" * 60)
    print("🚀 ProDocuX - AI文檔智能轉換平台")
    print("=" * 60)
    
    # 檢查是否為首次啟動
    if is_first_run():
        print("🆕 檢測到首次啟動，正在進行初始設定...")
        print("📋 為了確保ProDocuX正常運作，我們需要完成以下設定：")
        print("   1. 工作空間目錄設定")
        print("   2. AI提供者選擇")
        print("   3. API金鑰配置")
        print("   4. 桌面快捷方式選擇")
        print("")
        print("💡 建議使用以下方式進行設定：")
        print("   方法1: 運行 'python simple_setup.py' 進行命令行設定")
        print("   方法2: 啟動Web介面後在設定頁面中配置")
        print("")
        print("🌐 正在啟動Web設定介面...")
        print("   請在瀏覽器中前往: http://localhost:5000/setup")
        print("")
    else:
        print("🚀 啟動ProDocuX Web應用...")
    
    # 檢查依賴
    if not check_dependencies():
        print("❌ 依賴檢查失敗，請手動安裝依賴套件")
        print("執行: pip install -r requirements.txt")
        return
    
    # 創建目錄
    create_directories()
    
    # 創建環境變數檔案
    create_env_file()
    
    # 檢查API金鑰
    if not check_api_key():
        print("\n⚠️  未設定API金鑰，將啟動Web應用讓您在設定頁面中配置")
        print("💡 您可以在Web介面的設定頁面中輸入API金鑰")
    
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
        print("\n👋 感謝使用ProDocuX！")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        sys.exit(1)
