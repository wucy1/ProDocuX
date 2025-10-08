#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Profile管理器
管理文檔提取的配置和規則
"""

import os
import sys
import yaml
import json
import logging
import copy
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class ProfileManager:
    """Profile管理器"""
    
    def __init__(self, workspace_profiles_dir=None):
        """初始化Profile管理器"""
        # 工作空間的 profiles 目錄（用於 AI 生成的 profiles）
        if workspace_profiles_dir:
            self.workspace_profiles_dir = Path(workspace_profiles_dir)
            # 如果沒有提供工作空間路徑，使用預設的 profiles 目錄
            self.profiles_dir = self.workspace_profiles_dir
        else:
            # 回退到預設目錄
            if getattr(sys, 'frozen', False):
                # 對於打包版本，嘗試獲取工作空間路徑
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
                    self.workspace_profiles_dir = Path(workspace_path) / "profiles"
                else:
                    self.workspace_profiles_dir = Path("profiles")
            else:
                self.workspace_profiles_dir = Path("profiles")
            self.profiles_dir = self.workspace_profiles_dir
        
        # 對於打包版本，不應該在 dist 目錄創建 profiles
        if not getattr(sys, 'frozen', False):
            self.profiles_dir.mkdir(exist_ok=True)
        
        # 創建子目錄結構
        self.base_profiles_dir = self.profiles_dir / "base"
        self.brand_profiles_dir = self.profiles_dir / "brand"
        self.work_profiles_dir = self.profiles_dir / "work"
        
        # 對於打包版本，不應該在 dist 目錄創建子目錄
        if not getattr(sys, 'frozen', False):
            for dir_path in [self.base_profiles_dir, self.brand_profiles_dir, self.work_profiles_dir]:
                dir_path.mkdir(exist_ok=True)
        
        # 載入預設Profile（僅在非打包版本中）
        if not getattr(sys, 'frozen', False):
            self._create_default_profile()
        logger.info("Profile管理器已初始化（支援分層架構）")
    
    def get_default_profile(self) -> Dict[str, Any]:
        """獲取預設Profile"""
        default_profile_path = self.base_profiles_dir / "default.yml"
        
        if default_profile_path.exists():
            return self.load_profile(str(default_profile_path))
        else:
            return self._create_default_profile()
    
    def load_profile(self, profile_path: Union[str, Path]) -> Dict[str, Any]:
        """
        載入Profile
        
        Args:
            profile_path: Profile檔案路徑
            
        Returns:
            Profile配置
        """
        try:
            profile_path = Path(profile_path)
            
            # 如果路徑不包含副檔名，嘗試添加 .yml
            if not profile_path.suffix:
                profile_path = profile_path.with_suffix('.yml')
            
            # 如果路徑是相對路徑，嘗試在profiles目錄中查找
            if not profile_path.is_absolute():
                # 嘗試在base目錄中查找
                base_path = self.base_profiles_dir / profile_path.name
                if base_path.exists():
                    profile_path = base_path
                else:
                    # 嘗試在brand目錄中查找
                    brand_path = self.brand_profiles_dir / profile_path.name
                    if brand_path.exists():
                        profile_path = brand_path
                    else:
                        # 嘗試在work目錄中查找
                        work_path = self.work_profiles_dir / profile_path.name
                        if work_path.exists():
                            profile_path = work_path
            
            logger.info(f"載入Profile檔案: {profile_path}")
            
            if profile_path.suffix.lower() == '.yml':
                with open(profile_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            elif profile_path.suffix.lower() == '.json':
                with open(profile_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                raise ValueError(f"不支援的Profile格式: {profile_path.suffix}")
                
        except Exception as e:
            logger.error(f"Profile載入失敗: {e}")
            raise ValueError(f"無法載入指定的Profile: {profile_path}。請檢查檔案路徑和格式是否正確。")
    
    def save_profile(self, profile: Dict[str, Any], 
                    profile_path: Union[str, Path]) -> bool:
        """
        保存Profile
        
        Args:
            profile: Profile配置
            profile_path: 保存路徑
            
        Returns:
            保存是否成功
        """
        try:
            profile_path = Path(profile_path)
            profile_path.parent.mkdir(parents=True, exist_ok=True)
            
            if profile_path.suffix.lower() == '.yml':
                with open(profile_path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(profile, f, allow_unicode=True, indent=2)
            elif profile_path.suffix.lower() == '.json':
                with open(profile_path, 'w', encoding='utf-8') as f:
                    json.dump(profile, f, ensure_ascii=False, indent=2)
            else:
                raise ValueError(f"不支援的Profile格式: {profile_path.suffix}")
            
            logger.info(f"Profile已保存: {profile_path}")
            return True
            
        except Exception as e:
            logger.error(f"Profile保存失敗: {e}")
            return False
    
    def list_profiles(self) -> List[Dict[str, str]]:
        """列出所有可用的Profile"""
        profiles = []
        
        if self.profiles_dir.exists():
            for profile_file in self.profiles_dir.glob("*.yml"):
                try:
                    profile = self.load_profile(profile_file)
                    profiles.append({
                        "filename": profile_file.name,
                        "name": profile.get("name", profile_file.stem),
                        "path": str(profile_file),
                        "description": profile.get("description", ""),
                        "version": profile.get("version", "1.0.0")
                    })
                except Exception as e:
                    logger.warning(f"無法載入Profile: {profile_file}, {e}")
        
        return profiles
    
    def create_profile(self, name: str, description: str = "", 
                      base_profile: Optional[str] = None) -> bool:
        """
        創建新Profile
        
        Args:
            name: Profile名稱
            description: Profile描述
            base_profile: 基礎Profile名稱
            
        Returns:
            創建是否成功
        """
        try:
            if base_profile:
                base_profile_data = self.load_profile(f"profiles/{base_profile}.yml")
            else:
                raise ValueError("必須指定基礎Profile。系統不會使用預設Profile。")
            
            # 創建新Profile
            new_profile = base_profile_data.copy()
            new_profile["name"] = name
            new_profile["description"] = description
            new_profile["version"] = "1.0.0"
            
            # 保存Profile
            profile_path = self.profiles_dir / f"{name}.yml"
            return self.save_profile(new_profile, profile_path)
            
        except Exception as e:
            logger.error(f"Profile創建失敗: {e}")
            return False
    
    def update_profile_from_learning(self, profile: Dict[str, Any], 
                                   differences: List[Dict[str, Any]]) -> bool:
        """
        從學習結果更新Profile
        
        Args:
            profile: 當前Profile
            differences: 學習到的差異
            
        Returns:
            更新是否成功
        """
        try:
            # 分析差異並更新Profile規則
            for diff in differences:
                if diff["type"] == "modified":
                    # 更新對應的規則
                    self._update_rule_from_difference(profile, diff)
                elif diff["type"] == "added":
                    # 添加新規則
                    self._add_rule_from_difference(profile, diff)
            
            # 更新版本號
            current_version = profile.get("version", "1.0.0")
            major, minor, patch = map(int, current_version.split("."))
            profile["version"] = f"{major}.{minor}.{patch + 1}"
            
            logger.info("Profile已從學習結果更新")
            return True
            
        except Exception as e:
            logger.error(f"Profile學習更新失敗: {e}")
            return False
    
    def _update_rule_from_difference(self, profile: Dict[str, Any], 
                                   diff: Dict[str, Any]) -> None:
        """從差異更新規則"""
        # 這裡可以實現具體的規則更新邏輯
        logger.info(f"更新規則: {diff['path']}")
    
    def _add_rule_from_difference(self, profile: Dict[str, Any], 
                                diff: Dict[str, Any]) -> None:
        """從差異添加規則"""
        # 這裡可以實現具體的規則添加邏輯
        logger.info(f"添加規則: {diff['path']}")
    
    def _create_default_profile(self) -> Dict[str, Any]:
        """創建預設Profile"""
        default_profile = {
            "name": "default",
            "description": "通用文檔提取Profile",
            "version": "1.0.0",
            "use_page_extraction": True,
            "max_pages": 10,
            "extraction_rules": {
                "basic_info": {
                    "patterns": [
                        r"標題[:：]\s*(.+)",
                        r"title[:：]\s*(.+)",
                        r"名稱[:：]\s*(.+)"
                    ]
                },
                "content": {
                    "patterns": [
                        r"內容[:：]\s*(.+)",
                        r"content[:：]\s*(.+)",
                        r"摘要[:：]\s*(.+)"
                    ]
                }
            },
            "post_process": {
                "clean_text": True,
                "normalize_format": True,
                "validate_data": True
            }
        }
        
        # 保存預設Profile
        default_path = self.base_profiles_dir / "default.yml"
        self.save_profile(default_profile, default_path)
        
        return default_profile
    
    def load_work_profile(self, work_id: str, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        載入工作專屬Profile（支援分層繼承）
        
        Args:
            work_id: 工作ID
            work_data: 工作資料
            
        Returns:
            合併後的Profile配置
        """
        try:
            # 1. 載入基礎Profile（嚴格要求工作資料指定）
            base_profile_name = work_data.get('base_profile')
            if not base_profile_name:
                raise ValueError("工作資料中必須指定base_profile。系統不會使用預設Profile。")
            base_profile = self.load_profile(self.base_profiles_dir / f"{base_profile_name}.yml")
            
            # 2. 載入品牌Profile（如果存在）
            brand = work_data.get('brand', '').lower().replace(' ', '_')
            work_type = work_data.get('type', '').lower().replace(' ', '_')
            brand_profile_name = f"{brand}_{work_type}"
            brand_profile_path = self.brand_profiles_dir / f"{brand_profile_name}.yml"
            
            if brand_profile_path.exists():
                brand_profile = self.load_profile(brand_profile_path)
                base_profile = self._merge_profiles(base_profile, brand_profile)
                logger.info(f"已載入品牌Profile: {brand_profile_name}")
            
            # 3. 載入工作專屬Profile（如果存在）
            work_profile_name = f"work_{work_id}_profile"
            work_profile_path = self.work_profiles_dir / f"{work_profile_name}.yml"
            
            if work_profile_path.exists():
                work_profile = self.load_profile(work_profile_path)
                base_profile = self._merge_profiles(base_profile, work_profile)
                logger.info(f"已載入工作專屬Profile: {work_profile_name}")
            
            # 4. 設定Profile來源資訊
            base_profile['_profile_sources'] = {
                'base': base_profile_name,
                'brand': brand_profile_name if brand_profile_path.exists() else None,
                'work': work_profile_name if work_profile_path.exists() else None
            }
            
            return base_profile
            
        except Exception as e:
            logger.error(f"載入工作Profile失敗: {e}")
            raise ValueError(f"無法載入工作Profile (work_id: {work_id})。請檢查Profile設定是否正確。")
    
    # 品牌Profile功能已移除，品牌僅作為資訊欄位
    
    def create_work_profile(self, work_id: str, work_data: Dict[str, Any]) -> bool:
        """
        創建工作專屬Profile
        
        Args:
            work_id: 工作ID
            work_data: 工作資料
            
        Returns:
            創建是否成功
        """
        try:
            work_profile_name = f"work_{work_id}_profile"
            work_profile_path = self.work_profiles_dir / f"{work_profile_name}.yml"
            
            if work_profile_path.exists():
                logger.info(f"工作Profile已存在: {work_profile_name}")
                return True
            
            # 載入當前工作Profile（包含基礎+品牌）
            current_profile = self.load_work_profile(work_id, work_data)
            
            # 創建工作專屬Profile
            work_profile = copy.deepcopy(current_profile)
            work_profile.update({
                "name": work_profile_name,
                "description": f"工作 {work_data.get('name', work_id)} 專用Profile",
                "version": "1.0.0",
                "work_id": work_id,
                "profile_type": "work"
            })
            
            # 保存工作Profile
            success = self.save_profile(work_profile, work_profile_path)
            if success:
                logger.info(f"工作Profile創建成功: {work_profile_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"創建工作Profile失敗: {e}")
            return False
    
    def _merge_profiles(self, base_profile: Dict[str, Any], 
                       override_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        合併Profile配置（深度合併）
        
        Args:
            base_profile: 基礎Profile
            override_profile: 覆蓋Profile
            
        Returns:
            合併後的Profile
        """
        try:
            merged = copy.deepcopy(base_profile)
            
            for key, value in override_profile.items():
                if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                    # 遞歸合併字典
                    merged[key] = self._merge_profiles(merged[key], value)
                else:
                    # 直接覆蓋
                    merged[key] = copy.deepcopy(value)
            
            return merged
            
        except Exception as e:
            logger.error(f"Profile合併失敗: {e}")
            return base_profile
    
    # 品牌Profile學習功能已移除
    
    def update_work_profile_from_learning(self, work_id: str, work_data: Dict[str, Any],
                                        learning_data: Dict[str, Any]) -> bool:
        """
        從學習結果更新工作Profile
        
        Args:
            work_id: 工作ID
            work_data: 工作資料
            learning_data: 學習資料
            
        Returns:
            更新是否成功
        """
        try:
            work_profile_name = f"work_{work_id}_profile"
            work_profile_path = self.work_profiles_dir / f"{work_profile_name}.yml"
            
            if not work_profile_path.exists():
                # 如果工作Profile不存在，先創建
                self.create_work_profile(work_id, work_data)
            
            # 載入工作Profile
            work_profile = self.load_profile(work_profile_path)
            
            # 更新Profile
            success = self.update_profile_from_learning(work_profile, learning_data.get('differences', []))
            
            if success:
                # 保存更新後的Profile
                self.save_profile(work_profile, work_profile_path)
                logger.info(f"工作Profile已更新: {work_profile_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"更新工作Profile失敗: {e}")
            return False

    def save_ai_generated_profile(self, work_id: str, profile: Dict[str, Any]) -> bool:
        """保存AI生成的Profile"""
        try:
            # 創建AI生成的Profile目錄（在工作空間中）
            ai_profiles_dir = self.workspace_profiles_dir / "ai_generated"
            ai_profiles_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存Profile
            profile_path = ai_profiles_dir / f"work_{work_id}_profile.json"
            
            profile_data = {
                'work_id': work_id,
                'created_date': self._get_current_timestamp(),
                'ai_generated': True,
                'profile': profile
            }
            
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已保存AI生成的Profile: {profile_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存AI生成Profile失敗: {e}")
            return False
    
    def load_ai_generated_profile(self, work_id: str) -> Optional[Dict[str, Any]]:
        """載入AI生成的Profile"""
        try:
            ai_profiles_dir = self.workspace_profiles_dir / "ai_generated"
            profile_path = ai_profiles_dir / f"work_{work_id}_profile.json"
            
            if not profile_path.exists():
                return None
            
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            return profile_data.get('profile')
            
        except Exception as e:
            logger.error(f"載入AI生成Profile失敗: {e}")
            return None
    
    def validate_ai_profile_structure(self, profile: Dict[str, Any]) -> bool:
        """驗證AI生成的Profile結構"""
        try:
            # 檢查必要欄位
            if not profile.get('name') or not profile.get('fields'):
                return False
            
            # 檢查欄位定義
            for field in profile['fields']:
                if not field.get('name') or not field.get('type'):
                    return False
                
                # 檢查欄位類型是否有效
                valid_types = ['text', 'number', 'date', 'list', 'boolean']
                if field.get('type') not in valid_types:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_ai_generated_profiles(self) -> List[Dict[str, Any]]:
        """獲取所有AI生成的Profile列表"""
        try:
            ai_profiles_dir = self.workspace_profiles_dir / "ai_generated"
            
            if not ai_profiles_dir.exists():
                return []
            
            profiles = []
            for profile_file in ai_profiles_dir.glob("work_*_profile.json"):
                try:
                    with open(profile_file, 'r', encoding='utf-8') as f:
                        profile_data = json.load(f)
                    
                    profiles.append({
                        'work_id': profile_data.get('work_id'),
                        'name': profile_data.get('profile', {}).get('name', 'Unknown'),
                        'created_date': profile_data.get('created_date'),
                        'ai_generated': True
                    })
                except Exception as e:
                    logger.warning(f"載入AI Profile檔案失敗 {profile_file}: {e}")
                    continue
            
            return profiles
            
        except Exception as e:
            logger.error(f"獲取AI生成Profile列表失敗: {e}")
            return []
    
    def delete_ai_generated_profile(self, work_id: str) -> bool:
        """刪除AI生成的Profile"""
        try:
            ai_profiles_dir = self.workspace_profiles_dir / "ai_generated"
            profile_path = ai_profiles_dir / f"work_{work_id}_profile.json"
            
            if profile_path.exists():
                profile_path.unlink()
                logger.info(f"已刪除AI生成的Profile: {profile_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"刪除AI生成Profile失敗: {e}")
            return False
    
    def _get_current_timestamp(self) -> str:
        """獲取當前時間戳"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


