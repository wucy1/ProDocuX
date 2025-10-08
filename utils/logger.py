#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日誌設定工具
統一管理應用日誌
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = "prodocux", level: str = "INFO") -> logging.Logger:
    """
    設定日誌器
    
    Args:
        name: 日誌器名稱
        level: 日誌級別
        
    Returns:
        配置好的日誌器
    """
    # 創建日誌器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 避免重複添加處理器
    if logger.handlers:
        return logger
    
    # 創建日誌目錄
    # 對於打包版本，使用工作空間的 logs 目錄
    if getattr(sys, 'frozen', False):
        try:
            from utils.desktop_manager import DesktopManager
            dm = DesktopManager()
            log_dir = dm.workspace_dir / "logs"
        except:
            log_dir = Path("logs")
    else:
        log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 創建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 檔案處理器 - 所有日誌
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "prodocux.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 錯誤日誌檔案
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # 處理日誌檔案
    process_handler = logging.handlers.RotatingFileHandler(
        log_dir / "process.log",
        maxBytes=20*1024*1024,  # 20MB
        backupCount=10
    )
    process_handler.setLevel(logging.INFO)
    process_handler.setFormatter(formatter)
    logger.addHandler(process_handler)
    
    return logger

def get_logger(name: str = "prodocux") -> logging.Logger:
    """獲取日誌器"""
    return logging.getLogger(name)

def log_function_call(func):
    """函數調用日誌裝飾器"""
    def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.debug(f"調用函數: {func.__name__}, 參數: {args}, {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函數 {func.__name__} 執行成功")
            return result
        except Exception as e:
            logger.error(f"函數 {func.__name__} 執行失敗: {e}")
            raise
    return wrapper

def log_processing_start(file_path: str, profile: str = "default"):
    """記錄處理開始"""
    logger = get_logger()
    logger.info(f"開始處理文檔: {file_path}, Profile: {profile}")

def log_processing_end(file_path: str, success: bool, duration: float = None):
    """記錄處理結束"""
    logger = get_logger()
    status = "成功" if success else "失敗"
    duration_str = f", 耗時: {duration:.2f}秒" if duration else ""
    logger.info(f"文檔處理{status}: {file_path}{duration_str}")

def log_api_call(api_name: str, tokens: int, cost: float, duration: float):
    """記錄API調用"""
    logger = get_logger()
    logger.info(f"API調用: {api_name}, Tokens: {tokens}, 成本: ${cost:.4f}, 耗時: {duration:.2f}秒")

def log_learning_update(profile: str, rules_count: int):
    """記錄學習更新"""
    logger = get_logger()
    logger.info(f"Profile學習更新: {profile}, 新增規則: {rules_count}")

def cleanup_old_logs(days: int = 30):
    """清理舊日誌檔案"""
    logger = get_logger()
    # 對於打包版本，使用工作空間的 logs 目錄
    if getattr(sys, 'frozen', False):
        try:
            from utils.desktop_manager import DesktopManager
            dm = DesktopManager()
            log_dir = dm.workspace_dir / "logs"
        except:
            log_dir = Path("logs")
    else:
        log_dir = Path("logs")
    
    if not log_dir.exists():
        return
    
    import time
    current_time = time.time()
    cutoff_time = current_time - (days * 24 * 60 * 60)
    
    cleaned_count = 0
    for log_file in log_dir.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_time:
            log_file.unlink()
            cleaned_count += 1
    
    if cleaned_count > 0:
        logger.info(f"已清理 {cleaned_count} 個舊日誌檔案")






