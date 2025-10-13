#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定管理器
管理ProDocuX的配置設定
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from .desktop_manager import DesktopManager

logger = logging.getLogger(__name__)

class SettingsManager:
    """設定管理器"""
    
    def __init__(self, config_file: str = "config.json", workspace_path: str = None):
        """
        初始化設定管理器
        
        Args:
            config_file: 設定檔案路徑
            workspace_path: 工作空間路徑（可選）
        """
        # 先嘗試從多個可能的位置載入啟動設定
        startup_config = self._load_startup_config_from_multiple_locations(workspace_path)
        
        if startup_config:
            # 使用啟動設定
            selected_shortcuts = startup_config.get('selected_shortcuts', [])
            config_workspace_path = startup_config.get('workspace_path')
            
            # 使用啟動設定中的工作空間路徑
            if config_workspace_path:
                self.desktop_manager = DesktopManager(workspace_path=config_workspace_path)
            elif workspace_path:
                self.desktop_manager = DesktopManager(workspace_path=workspace_path)
            else:
                self.desktop_manager = DesktopManager()
            
            # 只有在工作空間不存在時才設置
            if not self.desktop_manager.workspace_dir.exists():
                if isinstance(selected_shortcuts, list):
                    self.workspace_dirs = self.desktop_manager.setup_workspace(
                        selected_shortcuts=selected_shortcuts
                    )
                else:
                    self.workspace_dirs = self.desktop_manager.setup_workspace()
            else:
                # 工作空間已存在，直接獲取目錄路徑
                self.workspace_dirs = self.desktop_manager.get_workspace_directories()
        else:
            # 使用傳入的工作空間路徑或預設設定
            if workspace_path:
                self.desktop_manager = DesktopManager(workspace_path=workspace_path)
            else:
                self.desktop_manager = DesktopManager()
            
            # 只有在工作空間不存在時才設置
            if not self.desktop_manager.workspace_dir.exists():
                self.workspace_dirs = self.desktop_manager.setup_workspace()
            else:
                # 工作空間已存在，直接獲取目錄路徑
                self.workspace_dirs = self.desktop_manager.get_workspace_directories()
        
        # 設定檔案放在工作目錄中
        self.config_file = Path(self.workspace_dirs["cache"]) / config_file
        self.default_settings = self._get_default_settings()
        self.settings = self._load_settings()
        
        # 確保所有目錄存在
        self.ensure_directories()
        
        logger.info("設定管理器已初始化")
    
    def _load_startup_config_from_multiple_locations(self, workspace_path: str = None):
        """從多個可能的位置載入啟動設定"""
        # 可能的啟動設定檔案位置
        possible_locations = []
        
        # 1. 如果提供了工作空間路徑，優先檢查該路徑
        if workspace_path:
            possible_locations.append(Path(workspace_path) / "startup_config.json")
        
        # 2. 檢查用戶文檔目錄下的 ProDocuX_Workspace
        documents_dir = Path.home() / "Documents"
        if not documents_dir.exists():
            documents_dir = Path.home() / "文檔"
        if documents_dir.exists():
            possible_locations.append(documents_dir / "ProDocuX_Workspace" / "startup_config.json")
        
        # 3. 檢查應用程式目錄下的 ProDocuX_Workspace（僅用於開發環境）
        app_dir = Path(__file__).parent.parent
        # 注意：打包後的程式不應該在應用程式目錄下創建工作空間
        if not getattr(sys, 'frozen', False):  # 只在開發環境中檢查
            possible_locations.append(app_dir / "ProDocuX_Workspace" / "startup_config.json")
        
        # 4. 檢查當前目錄
        possible_locations.append(Path.cwd() / "startup_config.json")
        
        # 嘗試從每個位置載入
        for config_file in possible_locations:
            try:
                if config_file.exists():
                    import json
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        logger.info(f"從 {config_file} 載入啟動設定")
                        return config
            except Exception as e:
                logger.debug(f"無法從 {config_file} 載入啟動設定: {e}")
                continue
        
        logger.info("未找到啟動設定檔案")
        return None
    
    def _load_startup_config(self):
        """載入啟動設定（向後兼容）"""
        try:
            config_file = self.desktop_manager.workspace_dir / "startup_config.json"
            if config_file.exists():
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"載入啟動設定失敗: {e}")
        return None
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """獲取預設設定"""
        return {
            "input_dir": str(self.workspace_dirs["input"]),
            "output_dir": str(self.workspace_dirs["output"]), 
            "template_dir": str(self.workspace_dirs["template"]),
            "cache_dir": str(self.workspace_dirs["cache"]),
            "ai_provider": "openai",
            "ai_model": "gpt-4",
            "openai_api_key": self._load_api_key_from_env(),
            "claude_api_key": self._load_claude_key_from_env(),
            "gemini_api_key": self._load_gemini_key_from_env(),
            "grok_api_key": self._load_grok_key_from_env(),
            "openai_model": "gpt-4",
            "claude_model": "claude-3-sonnet-20240229",
            "gemini_model": "gemini-pro",
            "grok_model": "grok-beta",
            "max_file_size": 50,  # MB
            "auto_cleanup": True,
            "cleanup_days": 7,
            "batch_mode": False,
            "watch_folder": False,
            "api_settings": {
                "model": "gpt-4",
                "max_tokens": 4000,
                "temperature": 0.1,
                # 新增 AI 行為控制（預設保守）
                "force_json": False,
                "max_tokens_cap": 4000,
                "retry": {"enabled": False, "max_attempts": 1, "backoff_seconds": 0}
            },
            "processing_settings": {
                # 分頁與截斷預設交由使用者決定
                "use_page_extraction": True,
                "page_selection": {"mode": "manual", "max_pages": 10, "truncate_chars": 0},
                "confidence_threshold": 0.7,
                # 合併策略預設完整複製（不去重）
                "merge_strategy": {
                    "ingredients": "copy_as_is",
                    "strings": "append",
                    "dict": "prefer_non_empty"
                },
                # 提示詞注入
                "prompt": {
                    "inject_page_meta": False, 
                    "simplify_profile": False,
                    "profile_strategy": "auto"  # 'never' | 'always' | 'auto'
                }
            },
            "cost_settings": {
                "max_cost_per_request": 1.0,
                "daily_cost_limit": 10.0,
                "enable_cost_tracking": True,
                # 定價與估算（可調）
                "pricing": {"input_per_1k": 0.03, "output_per_1k": 0.06, "output_guess_tokens": 1000}
            },
            # 模板/回退/供應商等策略
            "template_settings": {"auto_guess": False, "fallback_replace": False},
            "fallbacks": {"openai_json_fallback": False, "templating_fallback": False}
        }
    
    def _load_api_key_from_env(self) -> str:
        """從.env檔案載入OpenAI API金鑰"""
        try:
            dir_paths = self.get_directory_paths()
            env_file = dir_paths["cache"].parent / ".env"
            if env_file.exists():
                from dotenv import load_dotenv
                load_dotenv(env_file)
                return os.getenv('OPENAI_API_KEY', '')
        except Exception:
            pass
        return ''
    
    def _load_claude_key_from_env(self) -> str:
        """從.env檔案載入Claude API金鑰"""
        try:
            dir_paths = self.get_directory_paths()
            env_file = dir_paths["cache"].parent / ".env"
            if env_file.exists():
                from dotenv import load_dotenv
                load_dotenv(env_file)
                return os.getenv('CLAUDE_API_KEY', '')
        except Exception:
            pass
        return ''
    
    def _load_gemini_key_from_env(self) -> str:
        """從.env檔案載入Gemini API金鑰"""
        try:
            dir_paths = self.get_directory_paths()
            env_file = dir_paths["cache"].parent / ".env"
            if env_file.exists():
                from dotenv import load_dotenv
                load_dotenv(env_file)
                return os.getenv('GEMINI_API_KEY', '')
        except Exception:
            pass
        return ''
    
    def _load_grok_key_from_env(self) -> str:
        """從.env檔案載入Grok API金鑰"""
        try:
            dir_paths = self.get_directory_paths()
            env_file = dir_paths["cache"].parent / ".env"
            if env_file.exists():
                from dotenv import load_dotenv
                load_dotenv(env_file)
                return os.getenv('GROK_API_KEY', '')
        except Exception:
            pass
        return ''
    
    def _load_settings(self) -> Dict[str, Any]:
        """載入設定"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # 合併預設設定和載入的設定
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                
                logger.info(f"設定已載入: {self.config_file}")
                return settings
            else:
                # 創建預設設定檔案
                self._save_settings(self.default_settings)
                logger.info("已創建預設設定檔案")
                return self.default_settings
                
        except Exception as e:
            logger.error(f"設定載入失敗: {e}")
            return self.default_settings
    
    def _save_settings(self, settings: Dict[str, Any]) -> bool:
        """保存設定"""
        try:
            # 確保目錄存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 添加時間戳
            settings["last_updated"] = datetime.now().isoformat()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            logger.info(f"設定已保存: {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"設定保存失敗: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """獲取單個設定值"""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """設定單個設定值"""
        try:
            self.settings[key] = value
            return self._save_settings(self.settings)
        except Exception as e:
            logger.error(f"設定更新失敗: {e}")
            return False
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """更新多個設定"""
        try:
            # 如果更新了API金鑰，同時更新.env檔案
            if 'openai_api_key' in new_settings and new_settings['openai_api_key']:
                self._save_api_key_to_env(new_settings['openai_api_key'])
            
            if 'claude_api_key' in new_settings and new_settings['claude_api_key']:
                self._save_claude_key_to_env(new_settings['claude_api_key'])
            
            self.settings.update(new_settings)
            return self._save_settings(self.settings)
        except Exception as e:
            logger.error(f"設定更新失敗: {e}")
            return False
    
    def _save_api_key_to_env(self, api_key: str):
        """保存API金鑰到.env檔案"""
        try:
            dir_paths = self.get_directory_paths()
            env_file = dir_paths["cache"].parent / ".env"
            
            # 讀取現有.env檔案內容
            env_content = ""
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    env_content = f.read()
            
            # 清理重複的API_KEY行並更新
            lines = env_content.split('\n')
            cleaned_lines = []
            openai_updated = False
            iopenai_updated = False
            
            for line in lines:
                if line.startswith('OPENAI_API_KEY='):
                    cleaned_lines.append(f"OPENAI_API_KEY={api_key}")
                    openai_updated = True
                elif line.startswith('IOPENAI_API_KEY='):
                    # 跳過重複的IOPENAI_API_KEY行，只保留第一個
                    if not iopenai_updated:
                        cleaned_lines.append(f"IOPENAI_API_KEY={api_key}")
                        iopenai_updated = True
                else:
                    cleaned_lines.append(line)
            
            # 如果沒有找到現有的API_KEY行，則添加
            if not openai_updated:
                cleaned_lines.append(f"OPENAI_API_KEY={api_key}")
            if not iopenai_updated:
                cleaned_lines.append(f"IOPENAI_API_KEY={api_key}")
            
            # 寫入檔案
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(cleaned_lines))
            
            logger.info("API金鑰已保存到.env檔案")
            
        except Exception as e:
            logger.error(f"保存API金鑰失敗: {e}")
    
    def _save_claude_key_to_env(self, api_key: str):
        """保存Claude API金鑰到.env檔案"""
        try:
            dir_paths = self.get_directory_paths()
            env_file = dir_paths["cache"].parent / ".env"
            
            # 讀取現有.env檔案內容
            env_content = ""
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    env_content = f.read()
            
            # 更新或添加Claude API金鑰
            lines = env_content.split('\n')
            updated = False
            
            for i, line in enumerate(lines):
                if line.startswith('CLAUDE_API_KEY='):
                    lines[i] = f"CLAUDE_API_KEY={api_key}"
                    updated = True
                    break
            
            if not updated:
                lines.append(f"CLAUDE_API_KEY={api_key}")
            
            # 寫入檔案
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            logger.info("Claude API金鑰已保存到.env檔案")
            
        except Exception as e:
            logger.error(f"保存Claude API金鑰失敗: {e}")
    
    def reset_settings(self) -> bool:
        """重置為預設設定"""
        try:
            self.settings = self.default_settings.copy()
            return self._save_settings(self.settings)
        except Exception as e:
            logger.error(f"設定重置失敗: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """獲取所有設定"""
        return self.settings.copy()
    
    def validate_settings(self) -> Dict[str, Any]:
        """驗證設定"""
        errors = []
        warnings = []
        
        # 檢查目錄設定
        dir_settings = ["input_dir", "output_dir", "template_dir", "cache_dir"]
        for dir_key in dir_settings:
            dir_path = Path(self.settings.get(dir_key, ""))
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    warnings.append(f"目錄已創建: {dir_path}")
                except Exception as e:
                    errors.append(f"無法創建目錄 {dir_path}: {e}")
        
        # 檢查檔案大小設定
        max_file_size = self.settings.get("max_file_size", 50)
        if not isinstance(max_file_size, (int, float)) or max_file_size <= 0:
            errors.append("max_file_size 必須是正數")
        
        # 檢查清理天數設定
        cleanup_days = self.settings.get("cleanup_days", 7)
        if not isinstance(cleanup_days, int) or cleanup_days < 1:
            errors.append("cleanup_days 必須是正整數")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_directory_paths(self) -> Dict[str, Path]:
        """獲取目錄路徑"""
        # 使用工作空間的絕對路徑
        workspace_dir = self.desktop_manager.workspace_dir
        
        # 確保 workspace_dir 是 Path 對象
        if isinstance(workspace_dir, str):
            workspace_dir = Path(workspace_dir)
        
        # 如果工作空間目錄不存在，嘗試使用 app_dir 下的 ProDocuX_Workspace
        if not workspace_dir.exists():
            app_workspace = self.desktop_manager.app_dir / "ProDocuX_Workspace"
            if app_workspace.exists():
                workspace_dir = app_workspace
                logger.info(f"使用應用程式目錄下的工作空間: {workspace_dir}")
        
        return {
            "input": workspace_dir / "input",
            "output": workspace_dir / "output", 
            "template": workspace_dir / "templates",
            "cache": workspace_dir / "cache",
            "profiles": workspace_dir / "profiles",
            "prompts": workspace_dir / "prompts",
            "uploads": workspace_dir / "uploads"
        }
    
    def ensure_directories(self) -> bool:
        """確保所有目錄存在"""
        try:
            dir_paths = self.get_directory_paths()
            for name, path in dir_paths.items():
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"目錄已確保存在: {name} -> {path}")

            # 如果是已有的工作空間，但 profiles/prompts/templates 為空，補齊預設檔案
            try:
                from .desktop_manager import DesktopManager
                desktop_manager = self.desktop_manager

                def _is_dir_empty(p: Path) -> bool:
                    try:
                        return not any(p.iterdir())
                    except Exception:
                        return True

                needs_copy = False
                for key in ("profiles", "prompts", "template"):
                    p = dir_paths[key]
                    if not p.exists() or _is_dir_empty(p):
                        needs_copy = True
                        break

                if needs_copy:
                    logger.info("檢測到 profiles/prompts/templates 為空，複製預設檔案到工作空間")
                    desktop_manager._copy_default_files()
            except Exception as e:
                logger.warning(f"補齊預設檔案時出錯: {e}")

            return True
        except Exception as e:
            logger.error(f"目錄創建失敗: {e}")
            return False
    
    def get_file_handling_config(self) -> Dict[str, Any]:
        """獲取檔案處理配置"""
        return {
            "max_file_size": self.settings.get("max_file_size", 50) * 1024 * 1024,  # 轉換為位元組
            "auto_cleanup": self.settings.get("auto_cleanup", True),
            "cleanup_days": self.settings.get("cleanup_days", 7),
            "batch_mode": self.settings.get("batch_mode", False),
            "watch_folder": self.settings.get("watch_folder", False)
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """獲取API配置"""
        return self.settings.get("api_settings", {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """獲取處理配置"""
        return self.settings.get("processing_settings", {})
    
    def get_cost_config(self) -> Dict[str, Any]:
        """獲取成本配置"""
        return self.settings.get("cost_settings", {})
    
    def get_works(self) -> list:
        """獲取工作列表"""
        try:
            # 使用 get_directory_paths 獲取正確的目錄路徑
            dir_paths = self.get_directory_paths()
            cache_dir = dir_paths["cache"]
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            works_file = cache_dir / "works.json"
            if works_file.exists():
                with open(works_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"載入工作列表失敗: {e}")
            return []
    
    def save_work(self, work: Dict[str, Any]) -> bool:
        """保存工作（支援新增和更新）"""
        try:
            works = self.get_works()
            work_id = work.get('id')
            
            # 檢查是否為更新現有工作
            existing_work_index = None
            if work_id:
                for i, existing_work in enumerate(works):
                    if existing_work.get('id') == work_id:
                        existing_work_index = i
                        break
            
            if existing_work_index is not None:
                # 更新現有工作
                works[existing_work_index] = work
                logger.info(f"工作已更新: {work['name']} (ID: {work_id})")
            else:
                # 新增工作
                works.append(work)
                logger.info(f"工作已新增: {work['name']}")
            
            # 使用 get_directory_paths 獲取正確的目錄路徑
            dir_paths = self.get_directory_paths()
            cache_dir = dir_paths["cache"]
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            works_file = cache_dir / "works.json"
            with open(works_file, 'w', encoding='utf-8') as f:
                json.dump(works, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"保存工作失敗: {e}")
            return False
    
    def update_work(self, work_id: str, updates: Dict[str, Any]) -> bool:
        """更新工作（支援版本管理）"""
        try:
            works = self.get_works()
            for i, work in enumerate(works):
                if work['id'] == work_id:
                    # 保存歷史版本
                    self._save_work_version_history(work, updates)
                    
                    # 更新當前版本
                    works[i].update(updates)
                    works[i]['last_updated'] = datetime.now().isoformat()
                    break
            else:
                return False
            
            dir_paths = self.get_directory_paths()
            works_file = dir_paths["cache"] / "works.json"
            with open(works_file, 'w', encoding='utf-8') as f:
                json.dump(works, f, ensure_ascii=False, indent=2)
            
            logger.info(f"工作已更新: {work_id}")
            return True
        except Exception as e:
            logger.error(f"更新工作失敗: {e}")
            return False
    
    def _save_work_version_history(self, work: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """保存工作版本歷史"""
        try:
            # 初始化版本歷史
            if 'version_history' not in work:
                work['version_history'] = []
            
            # 檢查是否有配置變更
            config_changed = False
            version_data = {
                'timestamp': datetime.now().isoformat(),
                'changes': {}
            }
            
            # 檢查profile變更
            if 'profile' in updates and updates['profile'] != work.get('profile'):
                config_changed = True
                version_data['changes']['profile'] = {
                    'old': work.get('profile'),
                    'new': updates['profile']
                }
            
            # 檢查prompt變更
            if 'prompt' in updates and updates['prompt'] != work.get('prompt'):
                config_changed = True
                version_data['changes']['prompt'] = {
                    'old': work.get('prompt'),
                    'new': updates['prompt']
                }
            
            # 檢查template變更
            if 'template' in updates and updates['template'] != work.get('template'):
                config_changed = True
                version_data['changes']['template'] = {
                    'old': work.get('template'),
                    'new': updates['template']
                }
            
            # 如果有配置變更，保存版本歷史
            if config_changed:
                work['version_history'].append(version_data)
                
                # 限制歷史版本數量（保留最近10個版本）
                if len(work['version_history']) > 10:
                    work['version_history'] = work['version_history'][-10:]
                
                logger.info(f"保存工作版本歷史: {work['id']}")
                
        except Exception as e:
            logger.error(f"保存版本歷史失敗: {e}")
    
    def get_work_version_history(self, work_id: str) -> List[Dict[str, Any]]:
        """獲取工作版本歷史"""
        try:
            works = self.get_works()
            for work in works:
                if work['id'] == work_id:
                    return work.get('version_history', [])
            return []
        except Exception as e:
            logger.error(f"獲取版本歷史失敗: {e}")
            return []
    
    def rollback_work_version(self, work_id: str, version_index: int) -> bool:
        """回滾工作到指定版本"""
        try:
            works = self.get_works()
            for i, work in enumerate(works):
                if work['id'] == work_id:
                    version_history = work.get('version_history', [])
                    
                    if version_index < 0 or version_index >= len(version_history):
                        logger.error(f"無效的版本索引: {version_index}")
                        return False
                    
                    # 獲取指定版本的變更
                    version_data = version_history[version_index]
                    changes = version_data.get('changes', {})
                    
                    # 回滾變更
                    for field, change_data in changes.items():
                        if field in ['profile', 'prompt', 'template']:
                            works[i][field] = change_data.get('old')
                    
                    works[i]['last_updated'] = datetime.now().isoformat()
                    
                    # 保存回滾後的狀態
                    dir_paths = self.get_directory_paths()
                    works_file = dir_paths["cache"] / "works.json"
                    with open(works_file, 'w', encoding='utf-8') as f:
                        json.dump(works, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"工作已回滾到版本 {version_index}: {work_id}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"回滾工作版本失敗: {e}")
            return False
    
    def delete_work(self, work_id: str) -> bool:
        """刪除工作"""
        try:
            works = self.get_works()
            works = [work for work in works if work['id'] != work_id]
            
            dir_paths = self.get_directory_paths()
            works_file = dir_paths["cache"] / "works.json"
            with open(works_file, 'w', encoding='utf-8') as f:
                json.dump(works, f, ensure_ascii=False, indent=2)
            
            logger.info(f"工作已刪除: {work_id}")
            return True
        except Exception as e:
            logger.error(f"刪除工作失敗: {e}")
            return False
    
    def get_work(self, work_id: str) -> Optional[Dict[str, Any]]:
        """獲取單個工作"""
        try:
            works = self.get_works()
            for work in works:
                if work['id'] == work_id:
                    return work
            return None
        except Exception as e:
            logger.error(f"獲取工作失敗: {e}")
            return None
