"""
工作流程偏好設定管理器
負責管理用戶對個別工作流程的偏好設定
"""

import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WorkflowPreferencesManager:
    """工作流程偏好設定管理器"""
    
    def __init__(self, preferences_file: str = None):
        """
        初始化偏好設定管理器
        
        Args:
            preferences_file: 偏好設定文件路徑，如果為 None 則使用工作空間路徑
        """
        if preferences_file is None:
            # 對於打包版本，使用工作空間路徑
            if getattr(sys, 'frozen', False):
                # 獲取工作空間路徑
                workspace_path = os.getenv('PRODOCUX_WORKSPACE_PATH')
                if not workspace_path:
                    # 嘗試從啟動設定獲取
                    from utils.desktop_manager import DesktopManager
                    dm = DesktopManager()
                    workspace_path = str(dm.workspace_dir)
                self.preferences_file = Path(workspace_path) / "workflow_preferences.json"
            else:
                self.preferences_file = Path("workflow_preferences.json")
        else:
            self.preferences_file = Path(preferences_file)
        self.preferences_data = self._load_preferences()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """載入偏好設定數據"""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.info("偏好設定文件不存在，創建新的偏好設定")
                return {"workflows": {}, "last_updated": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"載入偏好設定失敗: {e}")
            return {"workflows": {}, "last_updated": datetime.now().isoformat()}
    
    def _save_preferences(self) -> bool:
        """保存偏好設定數據"""
        try:
            self.preferences_data["last_updated"] = datetime.now().isoformat()
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存偏好設定失敗: {e}")
            return False
    
    def get_workflow_preferences(self, work_id: str) -> Dict[str, Any]:
        """
        獲取指定工作流程的偏好設定
        
        Args:
            work_id: 工作流程ID
            
        Returns:
            偏好設定字典
        """
        return self.preferences_data.get("workflows", {}).get(work_id, {})
    
    def save_workflow_preferences(self, work_id: str, preferences: Dict[str, Any]) -> bool:
        """
        保存指定工作流程的偏好設定
        
        Args:
            work_id: 工作流程ID
            preferences: 偏好設定字典
            
        Returns:
            是否保存成功
        """
        try:
            if "workflows" not in self.preferences_data:
                self.preferences_data["workflows"] = {}
            
            # 添加時間戳
            preferences["last_saved"] = datetime.now().isoformat()
            
            self.preferences_data["workflows"][work_id] = preferences
            
            return self._save_preferences()
        except Exception as e:
            logger.error(f"保存工作流程偏好設定失敗: {e}")
            return False
    
    def update_workflow_preference(self, work_id: str, key: str, value: Any) -> bool:
        """
        更新指定工作流程的單個偏好設定
        
        Args:
            work_id: 工作流程ID
            key: 偏好設定鍵
            value: 偏好設定值
            
        Returns:
            是否更新成功
        """
        try:
            if "workflows" not in self.preferences_data:
                self.preferences_data["workflows"] = {}
            
            if work_id not in self.preferences_data["workflows"]:
                self.preferences_data["workflows"][work_id] = {}
            
            self.preferences_data["workflows"][work_id][key] = value
            self.preferences_data["workflows"][work_id]["last_saved"] = datetime.now().isoformat()
            
            return self._save_preferences()
        except Exception as e:
            logger.error(f"更新工作流程偏好設定失敗: {e}")
            return False
    
    def get_all_workflow_preferences(self) -> Dict[str, Dict[str, Any]]:
        """
        獲取所有工作流程的偏好設定
        
        Returns:
            所有工作流程偏好設定的字典
        """
        return self.preferences_data.get("workflows", {})
    
    def delete_workflow_preferences(self, work_id: str) -> bool:
        """
        刪除指定工作流程的偏好設定
        
        Args:
            work_id: 工作流程ID
            
        Returns:
            是否刪除成功
        """
        try:
            if work_id in self.preferences_data.get("workflows", {}):
                del self.preferences_data["workflows"][work_id]
                return self._save_preferences()
            return True
        except Exception as e:
            logger.error(f"刪除工作流程偏好設定失敗: {e}")
            return False
    
    def get_default_preferences(self) -> Dict[str, Any]:
        """
        獲取預設偏好設定
        
        Returns:
            預設偏好設定字典
        """
        return {
            "ai_provider": "",
            "ai_model": "",
            "output_format": "docx",
            "output_folder": "output",
            "auto_cost_estimate": True,
            "page_selection_mode": "all",  # all, manual, range
            "default_pages": [],  # 預設選中的頁面
            "cost_threshold": 1.0,  # 成本警告閾值
            "context_window_warning": 80,  # context window警告百分比
            "auto_save_preferences": True,  # 是否自動保存偏好
            "show_advanced_options": False,  # 是否顯示進階選項
            "last_used": datetime.now().isoformat()
        }

# 全域實例
_preferences_manager = None

def get_preferences_manager() -> WorkflowPreferencesManager:
    """獲取全域偏好設定管理器實例"""
    global _preferences_manager
    if _preferences_manager is None:
        # 對於打包版本，嘗試獲取工作空間路徑
        preferences_file = None
        if getattr(sys, 'frozen', False):
            workspace_path = os.getenv('PRODOCUX_WORKSPACE_PATH')
            if not workspace_path:
                # 嘗試從啟動設定獲取
                try:
                    from utils.desktop_manager import DesktopManager
                    dm = DesktopManager()
                    workspace_path = str(dm.workspace_dir)
                except:
                    pass
            if workspace_path:
                preferences_file = str(Path(workspace_path) / "workflow_preferences.json")
        _preferences_manager = WorkflowPreferencesManager(preferences_file)
    return _preferences_manager






