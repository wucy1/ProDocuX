#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProDocuX RC1 快速驗證腳本
驗證打包後的可執行檔是否正常運作
"""

import os
import sys
import time
import requests
import subprocess
import json
from pathlib import Path
import tempfile
import shutil

def check_exe_exists():
    """檢查可執行檔是否存在"""
    exe_path = Path("dist/ProDocuX.exe")
    if exe_path.exists():
        print(f"可執行檔存在: {exe_path}")
        return True
    else:
        print(f"可執行檔不存在: {exe_path}")
        return False

def start_application():
    """啟動應用程式"""
    print("啟動 ProDocuX...")
    exe_path = Path("dist/ProDocuX.exe")
    
    try:
        # 啟動應用程式
        process = subprocess.Popen([str(exe_path)], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 等待應用程式啟動
        time.sleep(5)
        
        # 檢查進程是否還在運行
        if process.poll() is None:
            print("應用程式啟動成功")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"應用程式啟動失敗")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"啟動應用程式時發生錯誤: {e}")
        return None

def test_health_check():
    """測試健康檢查端點"""
    print("測試健康檢查...")
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"健康檢查通過: {data}")
            return True
        else:
            print(f"健康檢查失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"健康檢查請求失敗: {e}")
        return False

def test_setup_page():
    """測試設定頁面"""
    print("測試設定頁面...")
    
    try:
        response = requests.get("http://localhost:5000/setup", timeout=10)
        if response.status_code == 200:
            print("設定頁面可訪問")
            return True
        else:
            print(f"設定頁面訪問失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"設定頁面請求失敗: {e}")
        return False

def test_main_page():
    """測試主頁面"""
    print("測試主頁面...")
    
    try:
        response = requests.get("http://localhost:5000/", timeout=10)
        if response.status_code == 200:
            print("主頁面可訪問")
            return True
        else:
            print(f"主頁面訪問失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"主頁面請求失敗: {e}")
        return False

def test_settings_api():
    """測試設定 API"""
    print("測試設定 API...")
    
    try:
        response = requests.get("http://localhost:5000/api/settings", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("設定 API 正常")
                return True
            else:
                print(f"設定 API 返回錯誤: {data}")
                return False
        else:
            print(f"設定 API 請求失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"設定 API 請求異常: {e}")
        return False

def test_ai_models_api():
    """測試 AI 模型 API"""
    print("測試 AI 模型 API...")
    
    try:
        response = requests.get("http://localhost:5000/api/ai-models", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'models' in data:
                print(f"AI 模型 API 正常，找到 {len(data['models'])} 個模型")
                return True
            else:
                print(f"AI 模型 API 返回錯誤: {data}")
                return False
        else:
            print(f"AI 模型 API 請求失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"AI 模型 API 請求異常: {e}")
        return False

def test_workspace_creation():
    """測試工作空間創建"""
    print("測試工作空間創建...")
    
    try:
        # 創建測試工作空間
        test_workspace = Path(tempfile.mkdtemp(prefix="ProDocuX_test_"))
        
        # 測試設定工作空間
        settings_data = {
            "workspace_path": str(test_workspace),
            "ai_provider": "openai",
            "ai_model": "gpt-3.5-turbo",
            "openai_api_key": "test-key-12345"
        }
        
        response = requests.post("http://localhost:5000/api/setup", 
                               json=settings_data, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("工作空間創建成功")
                
                # 檢查目錄是否創建
                expected_dirs = ['input', 'output', 'templates', 'cache', 'profiles', 'prompts']
                for dir_name in expected_dirs:
                    dir_path = test_workspace / dir_name
                    if dir_path.exists():
                        print(f"  目錄 {dir_name} 已創建")
                    else:
                        print(f"  目錄 {dir_name} 未創建")
                
                # 清理測試目錄
                shutil.rmtree(test_workspace)
                return True
            else:
                print(f"工作空間創建失敗: {data}")
                return False
        else:
            print(f"工作空間創建請求失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"工作空間創建測試異常: {e}")
        return False

def cleanup_process(process):
    """清理進程"""
    if process:
        try:
            process.terminate()
            process.wait(timeout=5)
            print("應用程式已關閉")
        except subprocess.TimeoutExpired:
            process.kill()
            print("強制關閉應用程式")
        except Exception as e:
            print(f"關閉應用程式時發生錯誤: {e}")

def main():
    """主函數"""
    print("=" * 60)
    print("ProDocuX RC1 快速驗證")
    print("=" * 60)
    
    # 檢查可執行檔
    if not check_exe_exists():
        print("驗證失敗：可執行檔不存在")
        return False
    
    # 啟動應用程式
    process = start_application()
    if not process:
        print("驗證失敗：無法啟動應用程式")
        return False
    
    try:
        # 等待應用程式完全啟動
        time.sleep(3)
        
        # 執行測試
        tests = [
            test_health_check,
            test_main_page,
            test_setup_page,
            test_settings_api,
            test_ai_models_api,
            test_workspace_creation
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # 空行分隔
        
        # 顯示結果
        print("=" * 60)
        print(f"驗證結果: {passed}/{total} 測試通過")
        
        if passed == total:
            print("所有測試通過！RC1 打包成功！")
            return True
        else:
            print("部分測試失敗，請檢查問題")
            return False
            
    finally:
        # 清理
        cleanup_process(process)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
