"""
AI供應商定價管理器
負責管理各AI供應商的定價資訊，並提供統一的定價查詢接口
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class PricingManager:
    """AI供應商定價管理器"""
    
    def __init__(self, pricing_file: str = None):
        """
        初始化定價管理器
        
        Args:
            pricing_file: 定價配置文件路徑，預設為 config/ai_pricing.json
        """
        if pricing_file is None:
            # 預設路徑
            current_dir = Path(__file__).parent
            pricing_file = current_dir.parent / "config" / "ai_pricing.json"
        
        self.pricing_file = Path(pricing_file)
        self.pricing_data = self._load_pricing_data()
    
    def _load_pricing_data(self) -> Dict[str, Any]:
        """載入定價數據"""
        try:
            if self.pricing_file.exists():
                with open(self.pricing_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"定價文件不存在: {self.pricing_file}")
                return self._get_default_pricing()
        except Exception as e:
            logger.error(f"載入定價文件失敗: {e}")
            return self._get_default_pricing()
    
    def _get_default_pricing(self) -> Dict[str, Any]:
        """獲取預設定價數據"""
        return {
            "last_updated": "2025-09-24",
            "source": "Default fallback pricing",
            "note": "使用預設定價，建議更新到最新版本",
            "providers": {
                "openai": {
                    "name": "OpenAI",
                    "models": {
                        "gpt-4o": {
                            "input_per_1k": 0.005,
                            "output_per_1k": 0.015,
                            "context_window": 128000
                        },
                        "gpt-3.5-turbo": {
                            "input_per_1k": 0.0005,
                            "output_per_1k": 0.0015,
                            "context_window": 16000
                        }
                    }
                }
            }
        }
    
    def get_pricing_info(self, provider: str = None, model: str = None) -> Dict[str, Any]:
        """
        獲取定價資訊
        
        Args:
            provider: 供應商名稱 (openai, anthropic, google, xai)
            model: 模型名稱
            
        Returns:
            定價資訊字典
        """
        if provider and model:
            # 獲取特定供應商的特定模型定價
            provider_data = self.pricing_data.get("providers", {}).get(provider, {})
            model_data = provider_data.get("models", {}).get(model, {})
            if model_data:
                return {
                    "provider": provider,
                    "model": model,
                    "input_per_1k": model_data.get("input_per_1k", 0),
                    "output_per_1k": model_data.get("output_per_1k", 0),
                    "context_window": model_data.get("context_window", 0),
                    "description": model_data.get("description", ""),
                    "last_updated": self.pricing_data.get("last_updated", ""),
                    "source": self.pricing_data.get("source", "")
                }
            return {}
        elif provider:
            # 獲取特定供應商的所有模型定價
            return self.pricing_data.get("providers", {}).get(provider, {})
        else:
            # 獲取所有定價資訊
            return self.pricing_data
    
    def get_model_pricing(self, model_name: str) -> Dict[str, float]:
        """
        根據模型名稱獲取定價（支援模糊匹配）
        
        Args:
            model_name: 模型名稱，如 "gpt-4o", "claude-3.5-sonnet" 等
            
        Returns:
            包含 input_per_1k 和 output_per_1k 的字典
        """
        model_name_lower = model_name.lower()
        
        # 遍歷所有供應商尋找匹配的模型
        for provider, provider_data in self.pricing_data.get("providers", {}).items():
            models = provider_data.get("models", {})
            for model_key, model_data in models.items():
                if (model_name_lower in model_key.lower() or 
                    model_key.lower() in model_name_lower):
                    return {
                        "input_per_1k": model_data.get("input_per_1k", 0),
                        "output_per_1k": model_data.get("output_per_1k", 0),
                        "context_window": model_data.get("context_window", 0),
                        "provider": provider,
                        "model": model_key,
                        "description": model_data.get("description", "")
                    }
        
        # 如果找不到，返回預設定價
        logger.warning(f"找不到模型 {model_name} 的定價資訊，使用預設定價")
        return {
            "input_per_1k": 0.03,  # GPT-4 預設定價
            "output_per_1k": 0.06,
            "context_window": 128000,
            "provider": "unknown",
            "model": model_name,
            "description": "預設定價"
        }
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model_name: str) -> Dict[str, Any]:
        """
        計算成本
        
        Args:
            input_tokens: 輸入token數量
            output_tokens: 輸出token數量
            model_name: 模型名稱
            
        Returns:
            成本計算結果
        """
        pricing = self.get_model_pricing(model_name)
        
        input_cost = (input_tokens / 1000) * pricing["input_per_1k"]
        output_cost = (output_tokens / 1000) * pricing["output_per_1k"]
        total_cost = input_cost + output_cost
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "model": model_name,
            "provider": pricing["provider"],
            "pricing": pricing,
            "last_updated": self.pricing_data.get("last_updated", ""),
            "source": self.pricing_data.get("source", "")
        }
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """獲取所有可用的模型列表"""
        models = []
        for provider, provider_data in self.pricing_data.get("providers", {}).items():
            for model_key, model_data in provider_data.get("models", {}).items():
                models.append({
                    "provider": provider,
                    "provider_name": provider_data.get("name", provider),
                    "model": model_key,
                    "input_per_1k": model_data.get("input_per_1k", 0),
                    "output_per_1k": model_data.get("output_per_1k", 0),
                    "context_window": model_data.get("context_window", 0),
                    "description": model_data.get("description", "")
                })
        return models
    
    def get_pricing_summary(self) -> Dict[str, Any]:
        """獲取定價摘要資訊"""
        return {
            "last_updated": self.pricing_data.get("last_updated", ""),
            "source": self.pricing_data.get("source", ""),
            "note": self.pricing_data.get("note", ""),
            "total_providers": len(self.pricing_data.get("providers", {})),
            "total_models": sum(
                len(provider_data.get("models", {})) 
                for provider_data in self.pricing_data.get("providers", {}).values()
            )
        }

# 全域實例
_pricing_manager = None

def get_pricing_manager() -> PricingManager:
    """獲取全域定價管理器實例"""
    global _pricing_manager
    if _pricing_manager is None:
        _pricing_manager = PricingManager()
    return _pricing_manager





















