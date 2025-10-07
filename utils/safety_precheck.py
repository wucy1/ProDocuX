#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 安全過濾機制預檢查模組
在實際 API 調用前預先檢查內容是否可能觸發安全過濾器
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SafetyRiskLevel(Enum):
    """安全風險等級"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SafetyCheckResult:
    """安全檢查結果"""
    is_safe: bool
    risk_level: SafetyRiskLevel
    risk_factors: List[str]
    suggestions: List[str]
    confidence: float  # 0.0-1.0

class GeminiSafetyPrechecker:
    """Gemini 安全過濾預檢查器"""
    
    def __init__(self):
        """初始化預檢查器"""
        self.risk_patterns = self._load_risk_patterns()
        self.whitelist_patterns = self._load_whitelist_patterns()
        self.context_weights = self._load_context_weights()
        
    def _load_risk_patterns(self) -> Dict[str, List[str]]:
        """載入風險模式"""
        return {
            "hate_speech": [
                r"(?i)(hate|hatred|discrimination|racist|sexist)",
                r"(?i)(violence|violent|harm|hurt|kill|murder)",
                r"(?i)(threat|threaten|intimidate|bully)",
            ],
            "harassment": [
                r"(?i)(harass|stalk|intimidate|bully|abuse)",
                r"(?i)(sexual.*harass|inappropriate.*content)",
                r"(?i)(personal.*attack|target.*individual)",
            ],
            "sexually_explicit": [
                r"(?i)(sexual|sex|porn|nude|naked|explicit)",
                r"(?i)(adult.*content|mature.*content)",
                r"(?i)(intimate|private.*parts)",
            ],
            "dangerous_content": [
                r"(?i)(dangerous|hazardous|toxic|poison|lethal)",
                r"(?i)(weapon|bomb|explosive|chemical.*weapon)",
                r"(?i)(self.*harm|suicide|self.*injury)",
                r"(?i)(illegal.*activity|criminal.*act)",
            ],
            "medical_risks": [
                r"(?i)(medical.*emergency|life.*threatening)",
                r"(?i)(overdose|poisoning|toxic.*reaction)",
                r"(?i)(allergic.*reaction|anaphylaxis)",
                r"(?i)(contraindication|adverse.*effect)",
            ],
            "chemical_safety": [
                r"(?i)(flammable|explosive|corrosive|toxic)",
                r"(?i)(hazardous.*chemical|dangerous.*substance)",
                r"(?i)(carcinogen|mutagen|teratogen)",
                r"(?i)(acute.*toxicity|chronic.*toxicity)",
            ]
        }
    
    def _load_whitelist_patterns(self) -> List[str]:
        """載入白名單模式（化妝品相關安全內容）"""
        return [
            r"(?i)(cosmetic|beauty|skincare|makeup|perfume)",
            r"(?i)(ingredient|component|formula|recipe)",
            r"(?i)(safety.*assessment|toxicological.*evaluation)",
            r"(?i)(allergen|sensitivity|irritation)",
            r"(?i)(concentration|percentage|dosage)",
            r"(?i)(manufacturer|producer|supplier)",
            r"(?i)(regulatory|compliance|standard)",
            r"(?i)(clinical.*test|safety.*test)",
            r"(?i)(patch.*test|sensitivity.*test)",
            r"(?i)(preservative|antioxidant|emulsifier)",
        ]
    
    def _load_context_weights(self) -> Dict[str, float]:
        """載入上下文權重"""
        return {
            "cosmetic_context": 0.3,  # 化妝品上下文降低風險
            "scientific_context": 0.2,  # 科學上下文降低風險
            "regulatory_context": 0.1,  # 監管上下文大幅降低風險
            "medical_context": 0.5,  # 醫療上下文增加風險
            "general_context": 1.0,  # 一般上下文保持原風險
        }
    
    def check_content_safety(self, content: str, context_type: str = "cosmetic_context") -> SafetyCheckResult:
        """
        檢查內容安全性
        
        Args:
            content: 要檢查的內容
            context_type: 上下文類型
            
        Returns:
            SafetyCheckResult: 安全檢查結果
        """
        try:
            # 基本清理
            cleaned_content = self._clean_content(content)
            
            # 檢查白名單（如果是化妝品相關內容，降低風險）
            is_whitelisted = self._check_whitelist(cleaned_content)
            
            # 檢查風險模式
            risk_factors = []
            total_risk_score = 0.0
            
            for category, patterns in self.risk_patterns.items():
                category_risks = self._check_category_risks(cleaned_content, patterns, category)
                if category_risks:
                    risk_factors.extend(category_risks)
                    total_risk_score += len(category_risks)
            
            # 應用上下文權重
            context_weight = self.context_weights.get(context_type, 1.0)
            if is_whitelisted:
                context_weight *= 0.5  # 白名單內容進一步降低風險
            
            adjusted_risk_score = total_risk_score * context_weight
            
            # 計算風險等級
            risk_level, confidence = self._calculate_risk_level(adjusted_risk_score, len(cleaned_content))
            
            # 生成建議
            suggestions = self._generate_suggestions(risk_factors, risk_level, is_whitelisted)
            
            # 判斷是否安全
            is_safe = risk_level in [SafetyRiskLevel.LOW, SafetyRiskLevel.MEDIUM]
            
            return SafetyCheckResult(
                is_safe=is_safe,
                risk_level=risk_level,
                risk_factors=risk_factors,
                suggestions=suggestions,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"安全檢查失敗: {e}")
            return SafetyCheckResult(
                is_safe=False,
                risk_level=SafetyRiskLevel.HIGH,
                risk_factors=[f"檢查過程發生錯誤: {str(e)}"],
                suggestions=["請檢查內容格式或聯繫技術支援"],
                confidence=0.0
            )
    
    def _clean_content(self, content: str) -> str:
        """清理內容"""
        # 移除多餘空白
        cleaned = re.sub(r'\s+', ' ', content.strip())
        # 移除特殊字符但保留基本標點
        cleaned = re.sub(r'[^\w\s\u4e00-\u9fff.,;:!?()\[\]{}"-]', '', cleaned)
        return cleaned
    
    def _check_whitelist(self, content: str) -> bool:
        """檢查是否為白名單內容"""
        content_lower = content.lower()
        for pattern in self.whitelist_patterns:
            if re.search(pattern, content_lower):
                return True
        return False
    
    def _check_category_risks(self, content: str, patterns: List[str], category: str) -> List[str]:
        """檢查特定類別的風險"""
        risks = []
        content_lower = content.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                risks.append(f"{category}: {', '.join(matches[:3])}")  # 只顯示前3個匹配
        
        return risks
    
    def _calculate_risk_level(self, risk_score: float, content_length: int) -> Tuple[SafetyRiskLevel, float]:
        """計算風險等級和信心度"""
        # 根據內容長度調整閾值
        length_factor = min(content_length / 1000, 2.0)  # 內容越長，閾值越高
        
        if risk_score == 0:
            return SafetyRiskLevel.LOW, 0.9
        elif risk_score <= 2 * length_factor:
            return SafetyRiskLevel.MEDIUM, 0.7
        elif risk_score <= 5 * length_factor:
            return SafetyRiskLevel.HIGH, 0.8
        else:
            return SafetyRiskLevel.CRITICAL, 0.9
    
    def _generate_suggestions(self, risk_factors: List[str], risk_level: SafetyRiskLevel, is_whitelisted: bool) -> List[str]:
        """生成改進建議"""
        suggestions = []
        
        if risk_level == SafetyRiskLevel.LOW:
            suggestions.append("內容安全，可以正常處理")
        elif risk_level == SafetyRiskLevel.MEDIUM:
            suggestions.append("內容風險較低，建議使用保守的安全設定")
            if not is_whitelisted:
                suggestions.append("考慮添加更多化妝品相關的上下文描述")
        elif risk_level == SafetyRiskLevel.HIGH:
            suggestions.append("內容風險較高，建議調整提示詞或使用替代模型")
            suggestions.append("考慮分段處理或移除敏感詞彙")
            if not is_whitelisted:
                suggestions.append("添加明確的化妝品/科學文檔上下文")
        else:  # CRITICAL
            suggestions.append("內容風險極高，不建議使用 Gemini 處理")
            suggestions.append("建議使用其他 AI 模型或人工處理")
            suggestions.append("檢查內容是否包含不當資訊")
        
        return suggestions
    
    def get_safe_prompt_suggestions(self, original_prompt: str, risk_result: SafetyCheckResult) -> str:
        """獲取安全的提示詞建議"""
        if risk_result.is_safe:
            return original_prompt
        
        # 添加安全上下文
        safety_context = """
請注意：這是一個化妝品產品資訊檔案（PIF）的科學文檔分析任務。
內容涉及化妝品成分、安全評估和監管合規性，屬於正常的商業和科學用途。
請專注於提取結構化的技術資料，避免任何不當解讀。
"""
        
        return safety_context + "\n\n" + original_prompt

class SafetyPrecheckManager:
    """安全預檢查管理器"""
    
    def __init__(self):
        self.prechecker = GeminiSafetyPrechecker()
        self.cache = {}  # 簡單的結果快取
    
    def check_prompt_safety(self, prompt: str, context_type: str = "cosmetic_context") -> SafetyCheckResult:
        """檢查提示詞安全性"""
        # 檢查快取
        cache_key = hash(prompt + context_type)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 執行檢查
        result = self.prechecker.check_content_safety(prompt, context_type)
        
        # 快取結果
        self.cache[cache_key] = result
        
        return result
    
    def get_alternative_strategies(self, risk_result: SafetyCheckResult) -> List[Dict[str, Any]]:
        """獲取替代策略"""
        strategies = []
        
        if risk_result.risk_level == SafetyRiskLevel.LOW:
            strategies.append({
                "strategy": "direct_processing",
                "description": "直接使用 Gemini 處理",
                "confidence": 0.9
            })
        elif risk_result.risk_level == SafetyRiskLevel.MEDIUM:
            strategies.append({
                "strategy": "conservative_settings",
                "description": "使用保守的安全設定",
                "confidence": 0.7
            })
            strategies.append({
                "strategy": "prompt_modification",
                "description": "修改提示詞添加安全上下文",
                "confidence": 0.8
            })
        elif risk_result.risk_level == SafetyRiskLevel.HIGH:
            strategies.append({
                "strategy": "chunked_processing",
                "description": "分段處理內容",
                "confidence": 0.6
            })
            strategies.append({
                "strategy": "alternative_model",
                "description": "使用替代 AI 模型",
                "confidence": 0.8
            })
        else:  # CRITICAL
            strategies.append({
                "strategy": "manual_review",
                "description": "人工審查後處理",
                "confidence": 0.9
            })
            strategies.append({
                "strategy": "alternative_model",
                "description": "使用替代 AI 模型",
                "confidence": 0.7
            })
        
        return strategies

