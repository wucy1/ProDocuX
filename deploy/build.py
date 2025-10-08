#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProDocuX 打包腳本
使用PyInstaller創建可執行檔案
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import platform

def clean_build_dirs():
    """清理建構目錄"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"已清理 {dir_name} 目錄")

def create_spec_file():
    """創建PyInstaller規格檔案"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web/templates', 'web/templates'),
        ('web/static', 'web/static'),
        ('profiles', 'profiles'),
        ('templates', 'templates'),
        ('utils', 'utils'),
        ('core', 'core'),
        ('config', 'config'),
        ('locale', 'locale'),
    ],
    hiddenimports=[
        'flask',
        'openai',
        'pdfplumber',
        'docx',
        'docxtpl',
        'yaml',
        'pydantic',
        'dotenv',
        'docx2pdf',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='ProDocuX',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # 改為無控制台視窗
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='assets/icon.ico' if Path('assets/icon.ico').exists() else None,
    )
'''
    
    with open('ProDocuX.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("已創建 PyInstaller 規格檔案")

def build_executable():
    """建構可執行檔案"""
    try:
        print("開始建構可執行檔案...")
        
        # 使用PyInstaller建構
        # 獲取圖標檔案的絕對路徑
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        print(f"圖標路徑: {icon_path}")
        print(f"圖標檔案存在: {os.path.exists(icon_path)}")
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', 'ProDocuX',
            '--icon', icon_path,
            '--add-data', 'web/templates;web/templates',
            '--add-data', 'web/static;web/static',
            '--add-data', 'profiles;profiles',
            '--add-data', 'templates;templates',
            '--add-data', 'utils;utils',
            '--add-data', 'core;core',
            '--add-data', 'config;config',
            '--add-data', 'locale;locale',
            '--hidden-import', 'flask',
            '--hidden-import', 'openai',
            '--hidden-import', 'pdfplumber',
            '--hidden-import', 'docx',
            '--hidden-import', 'docxtpl',
            '--hidden-import', 'yaml',
            '--hidden-import', 'pydantic',
            '--hidden-import', 'dotenv',
            '--hidden-import', 'docx2pdf',
            'run.py'
        ]
        
        # Windows特定設定
        if platform.system() == 'Windows':
            cmd.extend(['--console', '--noconfirm'])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("可執行檔案建構成功")
            return True
        else:
            print(f"建構失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"建構過程發生錯誤: {e}")
        return False

def create_installer_script():
    """創建安裝腳本"""
    if platform.system() == 'Windows':
        # Windows批次檔
        batch_content = '''@echo off
echo ========================================
echo ProDocuX 安裝程式
echo ========================================
echo.

echo 正在檢查Python環境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 未找到Python環境
    echo 請先安裝Python 3.8或更高版本
    pause
    exit /b 1
)

echo 正在安裝依賴套件...
pip install -r requirements.txt

echo 正在創建必要目錄...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "cache" mkdir cache
if not exist "logs" mkdir logs

echo 正在創建環境變數檔案...
if not exist ".env" (
    echo # ProDocuX 環境變數設定 > .env
    echo OPENAI_API_KEY=your_openai_api_key_here >> .env
    echo IOPENAI_API_KEY=your_iopenai_api_key_here >> .env
)

echo.
echo ========================================
echo 安裝完成！
echo ========================================
echo.
echo 請編輯 .env 檔案，填入您的OpenAI API金鑰
echo 然後執行 run.py 啟動ProDocuX
echo.
pause
'''
        
        with open('install.bat', 'w', encoding='utf-8') as f:
            f.write(batch_content)
    
    else:
        # Unix shell腳本
        shell_content = '''#!/bin/bash
echo "========================================"
echo "ProDocuX 安裝程式"
echo "========================================"
echo

echo "正在檢查Python環境..."
if ! command -v python3 &> /dev/null; then
    echo "錯誤: 未找到Python3環境"
    echo "請先安裝Python 3.8或更高版本"
    exit 1
fi

echo "正在安裝依賴套件..."
pip3 install -r requirements.txt

echo "正在創建必要目錄..."
mkdir -p uploads outputs cache logs

echo "正在創建環境變數檔案..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# ProDocuX 環境變數設定
OPENAI_API_KEY=your_openai_api_key_here
IOPENAI_API_KEY=your_iopenai_api_key_here
EOF
fi

echo
echo "========================================"
echo "安裝完成！"
echo "========================================"
echo
echo "請編輯 .env 檔案，填入您的OpenAI API金鑰"
echo "然後執行 python3 run.py 啟動ProDocuX"
echo
'''
        
        with open('install.sh', 'w', encoding='utf-8') as f:
            f.write(shell_content)
        
        # 設定執行權限
        os.chmod('install.sh', 0o755)
    
    print("已創建安裝腳本")

def create_release_package():
    """創建發布套件"""
    release_dir = Path("release")
    release_dir.mkdir(exist_ok=True)
    
    # 複製可執行檔案
    exe_name = "ProDocuX.exe" if platform.system() == 'Windows' else "ProDocuX"
    exe_path = Path("dist") / exe_name
    
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / exe_name)
        print(f"已複製可執行檔案: {exe_name}")
    
    # 複製必要檔案
    files_to_copy = [
        'README.md',
        'requirements.txt',
        'install.bat' if platform.system() == 'Windows' else 'install.sh',
        '.env.example'
    ]
    
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, release_dir / file_name)
            print(f"已複製檔案: {file_name}")
    
    # 創建使用說明
    usage_content = '''# ProDocuX 使用說明

## 快速開始

1. 執行安裝腳本
   - Windows: 雙擊 install.bat
   - Linux/Mac: 執行 ./install.sh

2. 設定API金鑰
   - 編輯 .env 檔案
   - 填入您的 OpenAI API 金鑰

3. 啟動應用
   - 雙擊 ProDocuX.exe (Windows)
   - 或執行 ./ProDocuX (Linux/Mac)

4. 在瀏覽器中開啟 http://localhost:5000

## 功能特色

- AI智能文檔提取
- 多格式支援 (PDF, DOCX, DOC)
- 自動學習優化
- 成本估算
- 批量處理

## 技術支援

如有問題，請訪問 GitHub: https://github.com/wucy1/ProDocuX
'''
    
    with open(release_dir / '使用說明.txt', 'w', encoding='utf-8') as f:
        f.write(usage_content)
    
    print("已創建發布套件")

def main():
    """主函數"""
    print("=" * 60)
    print("ProDocuX 打包工具")
    print("=" * 60)
    
    # 清理建構目錄
    clean_build_dirs()
    
    # 創建安裝腳本
    create_installer_script()
    
    # 建構可執行檔案
    if build_executable():
        # 創建發布套件
        create_release_package()
        print("\n打包完成！")
        print("發布檔案位於 release/ 目錄")
    else:
        print("\n打包失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
