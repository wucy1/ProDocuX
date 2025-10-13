#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面管理器
處理桌面環境下的目錄管理
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DesktopManager:
    """桌面管理器"""
    
    def __init__(self, workspace_path=None):
        """初始化桌面管理器"""
        self.is_desktop_environment = self._detect_desktop_environment()
        self.app_dir = self._get_app_directory()
        
        if workspace_path:
            self.workspace_dir = Path(workspace_path)
        else:
            self.workspace_dir = self._get_workspace_directory()
        
        logger.info(f"桌面管理器已初始化，工作目錄: {self.workspace_dir}")
    
    def _detect_desktop_environment(self) -> bool:
        """檢測是否在桌面環境中運行"""
        try:
            import platform
            
            # 在 Windows 環境下，總是啟用桌面功能
            if platform.system() == "Windows":
                return True
            
            # 檢查是否在桌面目錄
            current_dir = Path.cwd()
            desktop_paths = [
                Path.home() / "Desktop",
                Path.home() / "桌面",
                Path.home() / "デスクトップ",  # 日文
                Path.home() / "바탕화면",      # 韓文
            ]
            
            for desktop_path in desktop_paths:
                if desktop_path.exists() and current_dir.samefile(desktop_path):
                    return True
            
            # 檢查父目錄是否為桌面
            parent_dir = current_dir.parent
            for desktop_path in desktop_paths:
                if desktop_path.exists() and parent_dir.samefile(desktop_path):
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _get_app_directory(self) -> Path:
        """獲取應用程式目錄"""
        if getattr(sys, 'frozen', False):
            # 打包後的執行檔
            return Path(sys.executable).parent
        else:
            # 開發環境
            return Path(__file__).parent.parent
    
    def _get_workspace_directory(self) -> Path:
        """獲取工作目錄"""
        if self.is_desktop_environment:
            # 在桌面環境中，預設在用戶文檔目錄創建工作區
            documents_dir = Path.home() / "Documents"
            if not documents_dir.exists():
                documents_dir = Path.home() / "文檔"
            
            workspace_name = "ProDocuX_Workspace"
            workspace_dir = documents_dir / workspace_name
            
            return workspace_dir
        else:
            # 非桌面環境，使用應用程式目錄
            return self.app_dir
    
    def _is_on_desktop(self) -> bool:
        """檢查應用程式是否在桌面"""
        try:
            current_dir = Path.cwd()
            desktop_paths = [
                Path.home() / "Desktop",
                Path.home() / "桌面",
                Path.home() / "デスクトップ",
                Path.home() / "바탕화면",
            ]
            
            for desktop_path in desktop_paths:
                if desktop_path.exists() and current_dir.samefile(desktop_path):
                    return True
            return False
        except Exception:
            return False
    
    def setup_workspace(self, selected_shortcuts=None) -> Dict[str, Path]:
        """設置工作空間"""
        try:
            # 創建工作目錄
            self.workspace_dir.mkdir(parents=True, exist_ok=True)
            
            # 創建子目錄
            directories = {
                "input": self.workspace_dir / "input",
                "output": self.workspace_dir / "output", 
                "template": self.workspace_dir / "templates",
                "cache": self.workspace_dir / "cache",
                "profiles": self.workspace_dir / "profiles",
                "prompts": self.workspace_dir / "prompts"
            }
            
            for name, path in directories.items():
                path.mkdir(exist_ok=True)
                logger.info(f"工作目錄已創建: {name} -> {path}")
            
            # 複製預設檔案
            self._copy_default_files()
            
            # 創建桌面快捷方式（根據使用者選擇）
            if self.is_desktop_environment:
                self._create_desktop_shortcuts(selected_shortcuts)
            
            # 創建說明檔案
            self._create_workspace_info()
            
            return directories
            
        except Exception as e:
            logger.error(f"工作空間設置失敗: {e}")
            raise
    
    def _copy_default_files(self):
        """複製預設檔案到工作空間"""
        try:
            # 獲取應用程式目錄中的預設檔案
            app_profiles_dir = self.app_dir / "profiles"
            app_prompts_dir = self.app_dir / "prompts"
            app_templates_dir = self.app_dir / "templates"
            
            # 複製 profiles 檔案
            if app_profiles_dir.exists():
                profiles_dest = self.workspace_dir / "profiles"
                for profile_file in app_profiles_dir.glob("*.yml"):
                    dest_file = profiles_dest / profile_file.name
                    if not dest_file.exists():  # 只複製不存在的檔案
                        shutil.copy2(profile_file, dest_file)
                        logger.info(f"已複製預設配置檔案: {profile_file.name}")
            
            # 複製 prompts 檔案
            if app_prompts_dir.exists():
                prompts_dest = self.workspace_dir / "prompts"
                for prompt_file in app_prompts_dir.glob("*.md"):
                    dest_file = prompts_dest / prompt_file.name
                    if not dest_file.exists():  # 只複製不存在的檔案
                        shutil.copy2(prompt_file, dest_file)
                        logger.info(f"已複製預設提示詞檔案: {prompt_file.name}")
                
                # 也複製 .yaml 檔案
                for prompt_file in app_prompts_dir.glob("*.yaml"):
                    dest_file = prompts_dest / prompt_file.name
                    if not dest_file.exists():  # 只複製不存在的檔案
                        shutil.copy2(prompt_file, dest_file)
                        logger.info(f"已複製預設提示詞檔案: {prompt_file.name}")
            
            # 複製 templates 檔案
            if app_templates_dir.exists():
                templates_dest = self.workspace_dir / "templates"
                for template_file in app_templates_dir.glob("*"):
                    if template_file.is_file():  # 只複製檔案，不複製目錄
                        dest_file = templates_dest / template_file.name
                        if not dest_file.exists():  # 只複製不存在的檔案
                            shutil.copy2(template_file, dest_file)
                            logger.info(f"已複製預設模板檔案: {template_file.name}")
            
            logger.info("預設檔案複製完成")
            
        except Exception as e:
            logger.warning(f"複製預設檔案失敗: {e}")
    
    def _create_desktop_shortcuts(self, selected_shortcuts=None):
        """創建桌面快捷方式"""
        try:
            if self.is_desktop_environment and selected_shortcuts:
                desktop_dir = self._get_desktop_directory()
                if desktop_dir:
                    # 根據使用者選擇創建快捷方式
                    shortcut_options = {
                        "workspace": ("ProDocuX 工作目錄", self.workspace_dir),
                        "input": ("ProDocuX 輸入檔案", self.workspace_dir / "input"),
                        "output": ("ProDocuX 輸出結果", self.workspace_dir / "output"),
                        "template": ("ProDocuX 模板", self.workspace_dir / "templates")
                    }
                    
                    created_count = 0
                    for shortcut_type in selected_shortcuts:
                        if shortcut_type in shortcut_options:
                            name, target_path = shortcut_options[shortcut_type]
                            self._create_shortcut(desktop_dir, name, target_path)
                            created_count += 1
                    
                    logger.info(f"桌面快捷方式已創建: {created_count} 個")
        except Exception as e:
            logger.warning(f"桌面快捷方式創建失敗: {e}")
    
    def _create_shortcut(self, desktop_dir: Path, name: str, target_path: Path):
        """創建單個快捷方式"""
        try:
            import platform
            
            if platform.system() == "Windows":
                # Windows快捷方式
                shortcut_path = desktop_dir / f"{name}.lnk"
                self._create_windows_shortcut(shortcut_path, target_path)
            else:
                # Unix/Linux桌面檔案
                shortcut_path = desktop_dir / f"{name}.desktop"
                self._create_unix_shortcut(shortcut_path, target_path)
                
        except Exception as e:
            logger.warning(f"創建快捷方式失敗 {name}: {e}")
    
    def _create_windows_shortcut(self, shortcut_path: Path, target_path: Path):
        """創建Windows快捷方式"""
        try:
            import win32com.client
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(target_path)
            shortcut.WorkingDirectory = str(target_path)
            shortcut.IconLocation = str(target_path)
            shortcut.save()
            logger.info(f"Windows快捷方式已創建: {shortcut_path}")
            
        except ImportError:
            logger.warning("win32com模組未安裝，使用批次檔替代")
            # 如果沒有win32com，創建批次檔
            batch_path = shortcut_path.with_suffix('.bat')
            with open(batch_path, 'w', encoding='utf-8') as f:
                f.write(f'@echo off\ncd /d "{target_path}"\nstart .\n')
        except Exception as e:
            logger.warning(f"Windows快捷方式創建失敗: {e}")
    
    def _create_unix_shortcut(self, shortcut_path: Path, target_path: Path):
        """創建Unix桌面檔案"""
        try:
            desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={shortcut_path.stem}
Comment=ProDocuX工作目錄
Exec=xdg-open "{target_path}"
Icon=folder
Terminal=false
Categories=Utility;
"""
            with open(shortcut_path, 'w', encoding='utf-8') as f:
                f.write(desktop_entry)
            
            # 設定執行權限
            os.chmod(shortcut_path, 0o755)
            
        except Exception as e:
            logger.warning(f"Unix快捷方式創建失敗: {e}")
    
    def _get_desktop_directory(self) -> Optional[Path]:
        """獲取桌面目錄"""
        desktop_paths = [
            Path.home() / "Desktop",
            Path.home() / "桌面",
            Path.home() / "デスクトップ",
            Path.home() / "바탕화면",
        ]
        
        for desktop_path in desktop_paths:
            if desktop_path.exists():
                return desktop_path
        return None
    
    def _create_workspace_info(self):
        """創建工作空間說明檔案"""
        try:
            # 獲取完整路徑
            input_path = self.workspace_dir / "input"
            output_path = self.workspace_dir / "output"
            template_path = self.workspace_dir / "templates"
            
            info_content = f"""# ProDocuX 工作目錄

這是ProDocuX的工作目錄，包含以下資料夾：

## 📁 目錄說明

- **input/** - 將要處理的檔案放在這裡
  完整路徑: {input_path}
  
- **output/** - 處理完成的檔案會出現在這裡
  完整路徑: {output_path}
  
- **templates/** - 輸出模板檔案
  完整路徑: {template_path}
  
- **cache/** - 系統快取檔案（可忽略）
- **profiles/** - 提取規則配置
- **prompts/** - AI提示詞配置

## 🚀 使用方法

### 方法1：使用桌面快捷方式（推薦）
桌面會自動創建以下快捷方式：
- "ProDocuX 工作目錄" - 開啟整個工作目錄
- "ProDocuX 輸入檔案" - 直接開啟input資料夾
- "ProDocuX 輸出結果" - 直接開啟output資料夾
- "ProDocuX 模板" - 直接開啟templates資料夾

### 方法2：手動開啟資料夾
1. 開啟檔案總管
2. 在地址欄輸入：{self.workspace_dir}
3. 進入對應的資料夾

### 方法3：從ProDocuX程式開啟
1. 啟動ProDocuX程式
2. 在Web介面中點擊「開啟資料夾」按鈕
3. 系統會自動開啟對應的資料夾

## 📂 快速存取

### 輸入檔案
- 將要處理的PDF、DOCX等檔案放入input資料夾
- 支援拖拽操作
- 支援批量處理

### 輸出結果
- 處理完成的檔案會自動出現在output資料夾
- 包含JSON格式的提取結果
- 包含Word/PDF格式的轉換結果

### 模板檔案
- 可以自定義輸出模板
- 支援Word格式(.docx)
- 可以修改模板樣式

## ⚠️ 注意事項

- 請勿刪除此目錄中的系統檔案
- 定期清理 `cache/` 目錄以節省空間
- 重要檔案請及時從 `output/` 目錄移出
- 如果移動了工作目錄，請重新運行程式

## 🔧 故障排除

### 找不到檔案？
1. 檢查桌面快捷方式是否正確
2. 確認檔案是否在正確的資料夾中
3. 重新運行程式重新創建快捷方式

### 無法開啟資料夾？
1. 手動在檔案總管中輸入路徑
2. 檢查資料夾權限設定
3. 重新運行程式

---
ProDocuX v1.0.0
工作目錄創建時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
工作目錄路徑: {self.workspace_dir}
"""
            
            info_file = self.workspace_dir / "README.txt"
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(info_content)
                
        except Exception as e:
            logger.warning(f"工作空間說明檔案創建失敗: {e}")
    
    def get_workspace_directories(self) -> Dict[str, str]:
        """獲取工作空間目錄"""
        return {
            "input": str(self.workspace_dir / "input"),
            "output": str(self.workspace_dir / "output"),
            "template": str(self.workspace_dir / "templates"), 
            "cache": str(self.workspace_dir / "cache"),
            "profiles": str(self.workspace_dir / "profiles"),
            "prompts": str(self.workspace_dir / "prompts")
        }
    
    def cleanup_workspace(self, days: int = 7) -> int:
        """清理工作空間"""
        try:
            cleaned_count = 0
            cache_dir = self.workspace_dir / "cache"
            
            if cache_dir.exists():
                import time
                current_time = time.time()
                cutoff_time = current_time - (days * 24 * 60 * 60)
                
                for file_path in cache_dir.iterdir():
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
                
                logger.info(f"工作空間已清理 {cleaned_count} 個舊檔案")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"工作空間清理失敗: {e}")
            return 0
    
    def get_workspace_info(self) -> Dict[str, Any]:
        """獲取工作空間資訊"""
        return {
            "workspace_dir": str(self.workspace_dir),
            "is_desktop_environment": self.is_desktop_environment,
            "app_dir": str(self.app_dir),
            "directories": self.get_workspace_directories()
        }

