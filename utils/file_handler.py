#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案處理工具
統一管理檔案讀寫操作
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import shutil

logger = logging.getLogger(__name__)

class FileHandler:
    """檔案處理工具"""
    
    def __init__(self):
        """初始化檔案處理工具"""
        # 與工作空間對齊的目錄，避免在專案目錄下創建任何資料夾
        try:
            from .settings_manager import SettingsManager  # 相對於 utils 模組
        except Exception:
            # 從 Web 應用相對路徑導入
            from utils.settings_manager import SettingsManager  # type: ignore
        sm = SettingsManager()
        dirs = sm.get_directory_paths()

        # uploads 放在工作空間根目錄下的 uploads/
        workspace_dir = sm.desktop_manager.workspace_dir
        self.upload_dir = Path(workspace_dir) / "uploads"
        self.output_dir = Path(dirs["output"])  # 工作空間的 output/
        self.cache_dir = Path(dirs["cache"])    # 工作空間的 cache/
        
        # 創建必要目錄（只在工作空間內）
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("檔案處理工具已初始化 (workspace-aligned)")
    
    def save_uploaded_file(self, file_data: bytes, filename: str) -> Path:
        """
        保存上傳的檔案
        
        Args:
            file_data: 檔案資料
            filename: 檔案名稱
            
        Returns:
            保存的檔案路徑
        """
        try:
            file_path = self.upload_dir / filename
            logger.info(f"準備保存檔案到: {file_path}")
            logger.info(f"上傳目錄存在: {self.upload_dir.exists()}")
            logger.info(f"檔案資料大小: {len(file_data)} bytes")
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # 驗證檔案是否真的保存成功
            if file_path.exists():
                actual_size = file_path.stat().st_size
                logger.info(f"檔案已保存: {file_path}, 大小: {actual_size} bytes")
                return file_path
            else:
                logger.error(f"檔案保存後不存在: {file_path}")
                raise Exception(f"檔案保存失敗: {file_path}")
            
        except Exception as e:
            logger.error(f"檔案保存失敗: {e}", exc_info=True)
            raise
    
    def save_json_data(self, data: Dict[str, Any], filename: str) -> Path:
        """
        保存JSON資料
        
        Args:
            data: JSON資料
            filename: 檔案名稱
            
        Returns:
            保存的檔案路徑
        """
        try:
            file_path = self.output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON資料已保存: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"JSON保存失敗: {e}")
            raise
    
    def load_json_data(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        載入JSON資料
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            JSON資料
        """
        try:
            file_path = Path(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"JSON載入失敗: {e}")
            return {}
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        獲取檔案資訊
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            檔案資訊
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {}
            
            stat = file_path.stat()
            
            return {
                "name": file_path.name,
                "size": stat.st_size,
                "extension": file_path.suffix,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "path": str(file_path)
            }
            
        except Exception as e:
            logger.error(f"檔案資訊獲取失敗: {e}")
            return {}
    
    def list_files(self, directory: Union[str, Path], 
                  pattern: str = "*") -> List[Dict[str, Any]]:
        """
        列出目錄中的檔案
        
        Args:
            directory: 目錄路徑
            pattern: 檔案模式
            
        Returns:
            檔案列表
        """
        try:
            directory = Path(directory)
            
            if not directory.exists():
                return []
            
            files = []
            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    files.append(self.get_file_info(file_path))
            
            return sorted(files, key=lambda x: x["modified"], reverse=True)
            
        except Exception as e:
            logger.error(f"檔案列表獲取失敗: {e}")
            return []
    
    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        刪除檔案
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            刪除是否成功
        """
        try:
            file_path = Path(file_path)
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"檔案已刪除: {file_path}")
                return True
            else:
                logger.warning(f"檔案不存在: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"檔案刪除失敗: {e}")
            return False
    
    def copy_file(self, src_path: Union[str, Path], 
                 dst_path: Union[str, Path]) -> bool:
        """
        複製檔案
        
        Args:
            src_path: 來源檔案路徑
            dst_path: 目標檔案路徑
            
        Returns:
            複製是否成功
        """
        try:
            src_path = Path(src_path)
            dst_path = Path(dst_path)
            
            # 確保目標目錄存在
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_path, dst_path)
            logger.info(f"檔案已複製: {src_path} -> {dst_path}")
            return True
            
        except Exception as e:
            logger.error(f"檔案複製失敗: {e}")
            return False
    
    def move_file(self, src_path: Union[str, Path], 
                 dst_path: Union[str, Path]) -> bool:
        """
        移動檔案
        
        Args:
            src_path: 來源檔案路徑
            dst_path: 目標檔案路徑
            
        Returns:
            移動是否成功
        """
        try:
            src_path = Path(src_path)
            dst_path = Path(dst_path)
            
            # 確保目標目錄存在
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src_path), str(dst_path))
            logger.info(f"檔案已移動: {src_path} -> {dst_path}")
            return True
            
        except Exception as e:
            logger.error(f"檔案移動失敗: {e}")
            return False
    
    def create_directory(self, directory: Union[str, Path]) -> bool:
        """
        創建目錄
        
        Args:
            directory: 目錄路徑
            
        Returns:
            創建是否成功
        """
        try:
            directory = Path(directory)
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"目錄已創建: {directory}")
            return True
            
        except Exception as e:
            logger.error(f"目錄創建失敗: {e}")
            return False
    
    def cleanup_old_files(self, directory: Union[str, Path], 
                         max_age_days: int = 7) -> int:
        """
        清理舊檔案
        
        Args:
            directory: 目錄路徑
            max_age_days: 最大保留天數
            
        Returns:
            清理的檔案數量
        """
        try:
            import time
            
            directory = Path(directory)
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60
            
            cleaned_count = 0
            
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        cleaned_count += 1
            
            logger.info(f"已清理 {cleaned_count} 個舊檔案")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"檔案清理失敗: {e}")
            return 0




