#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多AI模型客戶端
支援OpenAI、Claude等多個AI模型
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union, List
from dotenv import load_dotenv
from abc import ABC, abstractmethod

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

class BaseAIClient(ABC):
    """AI客戶端基類"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    
    @abstractmethod
    def extract_data(self, prompt: str, max_tokens: int = 4000) -> str:
        """提取結構化資料"""
        pass
    
    @abstractmethod
    def generate_content(self, prompt: str, max_tokens: int = 2000) -> str:
        """生成內容"""
        pass
    
    @abstractmethod
    def get_pricing(self) -> Dict[str, float]:
        """獲取定價資訊"""
        pass

class OpenAIClient(BaseAIClient):
    """OpenAI客戶端"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """初始化OpenAI客戶端"""
        try:
            import openai
            return openai.OpenAI(api_key=self.api_key)
        except ImportError:
            logger.error("OpenAI package not installed, please run: pip install openai")
            raise
        except Exception as e:
            logger.error(f"OpenAI client initialization failed: {e}")
            raise
    
    def _parse_prompt_into_messages(self, prompt: str) -> List[Dict[str, str]]:
        """將提示詞解析為 messages（完全不分離）"""
        # 完全不分離，直接使用原始提示詞
        return [{"role": "user", "content": prompt}]
    
    def extract_data(self, prompt: str, max_tokens: int = 4000) -> str:
        """提取結構化資料"""
        try:
            # 完全不分離，直接使用原始提示詞
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI data extraction failed: {e}")
            raise
    
    def generate_content(self, prompt: str, max_tokens: int = 2000) -> str:
        """生成內容"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI content generation failed: {e}")
            raise
    
    def check_content_safety(self, content: str) -> Dict[str, Any]:
        """檢查內容安全性（使用 OpenAI 進行安全檢查）"""
        try:
            # 構建安全檢查提示詞
            safety_prompt = f"""
請檢查以下內容是否適合用於文檔處理任務，特別是化妝品產品資訊檔案（PIF）的資料提取。

內容：
{content}

請評估：
1. 內容是否包含不當或敏感資訊
2. 是否適合用於商業文檔處理
3. 是否有任何安全風險

請以 JSON 格式回應：
{{
    "is_safe": true/false,
    "risk_level": "low/medium/high/critical",
    "risk_factors": ["具體風險因素列表"],
    "suggestions": ["改進建議列表"],
    "confidence": 0.0-1.0
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一個內容安全檢查專家，專門評估文檔處理內容的安全性。"},
                    {"role": "user", "content": safety_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 嘗試解析 JSON 回應
            try:
                import json
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError:
                # 如果無法解析 JSON，返回預設安全結果
                return {
                    'is_safe': True,
                    'risk_level': 'low',
                    'risk_factors': [],
                    'suggestions': ['無法解析 AI 回應，預設為安全'],
                    'confidence': 0.5
                }
                
        except Exception as e:
            logger.error(f"OpenAI safety check failed: {e}")
            return {
                'is_safe': True,
                'risk_level': 'low',
                'risk_factors': [],
                'suggestions': [],
                'confidence': 0.0,
                'error': str(e)
            }

    def get_pricing(self) -> Dict[str, float]:
        """獲取OpenAI定價"""
        pricing = {
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
            'gpt-3.5-turbo': {'input': 0.001, 'output': 0.002}
        }
        return pricing.get(self.model, {'input': 0.03, 'output': 0.06})

class ClaudeClient(BaseAIClient):
    """Claude客戶端"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        super().__init__(api_key, model)
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """初始化Claude客戶端"""
        try:
            import anthropic
            return anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            logger.error("Anthropic package not installed, please run: pip install anthropic")
            raise
        except Exception as e:
            logger.error(f"Claude client initialization failed: {e}")
            raise
    
    def _parse_prompt_into_messages(self, prompt: str) -> List[Dict[str, str]]:
        """將提示詞解析為分離的 messages（Claude 格式）"""
        # 檢查是否包含文檔內容分隔符（基於成功驗證的分隔標記）
        if "=== 文檔內容 ===" in prompt:
            parts = prompt.split("=== 文檔內容 ===")
            instruction_part = parts[0].strip()
            content_part = "=== 文檔內容 ===" + parts[1] if len(parts) > 1 else ""
            
            return [
                {"role": "user", "content": instruction_part},
                {"role": "assistant", "content": "好的，我理解了您的任務。請提供要處理的文檔內容。"},
                {"role": "user", "content": content_part}
            ]
        else:
            # 沒有分隔符，使用原始方式
            return [{"role": "user", "content": prompt}]
    
    def extract_data(self, prompt: str, max_tokens: int = 4000) -> str:
        """提取結構化資料"""
        try:
            # 完全不分離，直接使用原始提示詞
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Claude data extraction failed: {e}")
            raise
    
    def generate_content(self, prompt: str, max_tokens: int = 2000) -> str:
        """生成內容"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Claude content generation failed: {e}")
            raise
    
    def check_content_safety(self, content: str) -> Dict[str, Any]:
        """檢查內容安全性（使用 Claude 進行安全檢查）"""
        try:
            # 構建安全檢查提示詞
            safety_prompt = f"""
請檢查以下內容是否適合用於文檔處理任務，特別是化妝品產品資訊檔案（PIF）的資料提取。

內容：
{content}

請評估：
1. 內容是否包含不當或敏感資訊
2. 是否適合用於商業文檔處理
3. 是否有任何安全風險

請以 JSON 格式回應：
{{
    "is_safe": true/false,
    "risk_level": "low/medium/high/critical",
    "risk_factors": ["具體風險因素列表"],
    "suggestions": ["改進建議列表"],
    "confidence": 0.0-1.0
}}
"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.1,
                system="你是一個內容安全檢查專家，專門評估文檔處理內容的安全性。",
                messages=[
                    {"role": "user", "content": safety_prompt}
                ]
            )
            
            result_text = response.content[0].text.strip()
            
            # 嘗試解析 JSON 回應
            try:
                import json
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError:
                # 如果無法解析 JSON，返回預設安全結果
                return {
                    'is_safe': True,
                    'risk_level': 'low',
                    'risk_factors': [],
                    'suggestions': ['無法解析 AI 回應，預設為安全'],
                    'confidence': 0.5
                }
                
        except Exception as e:
            logger.error(f"Claude safety check failed: {e}")
            return {
                'is_safe': True,
                'risk_level': 'low',
                'risk_factors': [],
                'suggestions': [],
                'confidence': 0.0,
                'error': str(e)
            }

    def get_pricing(self) -> Dict[str, float]:
        """獲取Claude定價"""
        pricing = {
            'claude-3-opus-20240229': {'input': 0.015, 'output': 0.075},
            'claude-3-sonnet-20240229': {'input': 0.003, 'output': 0.015},
            'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125}
        }
        return pricing.get(self.model, {'input': 0.003, 'output': 0.015})

class GeminiClient(BaseAIClient):
    """Gemini客戶端"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        super().__init__(api_key, model)
        self.client = self._initialize_client()
        # 初始化安全預檢查器
        try:
            from .safety_precheck import SafetyPrecheckManager
            self.safety_manager = SafetyPrecheckManager()
            self.enable_safety_precheck = True
        except ImportError:
            logger.warning("Safety pre-check module not found, will skip pre-check")
            self.safety_manager = None
            self.enable_safety_precheck = False
    
    def _initialize_client(self):
        """初始化Gemini客戶端"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            return genai.GenerativeModel(self.model)
        except ImportError:
            logger.error("Google Generative AI package not installed, please run: pip install google-generativeai")
            raise
        except Exception as e:
            logger.error(f"Gemini client initialization failed: {e}")
            raise
    
    def _parse_prompt_into_parts(self, prompt: str) -> List[str]:
        """將提示詞解析為 parts（Gemini 格式，完全不分離）"""
        # 完全不分離，直接使用原始提示詞
        return [prompt]
    
    def extract_data(self, prompt: str, max_tokens: int = 4000) -> str:
        """提取結構化資料"""
        try:
            # 添加內容診斷
            self._log_content_analysis(prompt)
            
            # 完全不分離，直接使用原始提示詞
            response = self.client.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": max_tokens,
                    "top_p": 0.8,
                    "top_k": 40
                },
                safety_settings=[]  # 完全關閉安全過濾器
            )
            
            # 檢查響應是否有效
            if not response.candidates:
                logger.warning("Gemini response has no candidate results")
                return '{"error": "API響應無效，沒有返回內容"}'
            
            candidate = response.candidates[0]
            
            # 檢查finish_reason
            if candidate.finish_reason == 2:  # SAFETY
                logger.error("Gemini response was blocked by safety filters")
                raise Exception("Gemini安全過濾器阻止了內容處理。請手動選擇其他AI模型或調整提示詞內容")
            elif candidate.finish_reason == 3:  # RECITATION
                logger.error("Gemini response was blocked by citation filters")
                raise Exception("Gemini引用過濾器阻止了內容處理。請手動選擇其他AI模型或調整提示詞內容")
            elif candidate.finish_reason == 4:  # OTHER
                logger.error("Gemini response was blocked for other reasons")
                raise Exception("Gemini因其他原因阻止了內容處理。請手動選擇其他AI模型或調整提示詞內容")
            
            # 檢查是否有內容
            if not candidate.content or not candidate.content.parts:
                logger.warning("Gemini response has no content parts")
                return '{"error": "API響應沒有內容，請嘗試調整提示詞"}'
            
            # 安全地獲取文本內容
            try:
                text_content = candidate.content.parts[0].text
                if not text_content or not text_content.strip():
                    logger.warning("Gemini response content is empty")
                    return '{"error": "API響應內容為空，請嘗試調整提示詞"}'
                return text_content.strip()
            except Exception as e:
                logger.error(f"Failed to parse Gemini response content: {e}")
                return '{"error": "解析API響應失敗，請嘗試調整提示詞"}'
                
        except Exception as e:
            logger.error(f"Gemini data extraction failed: {e}")
            raise
    
    def generate_content(self, prompt: str, max_tokens: int = 2000) -> str:
        """生成內容"""
        try:
            response = self.client.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": max_tokens
                },
                safety_settings=[]  # 完全關閉安全過濾器
            )
            
            # 檢查響應是否有效
            if not response.candidates:
                logger.warning("Gemini response has no candidate results")
                return "API響應無效，沒有返回內容"
            
            candidate = response.candidates[0]
            
            # 檢查finish_reason
            if candidate.finish_reason == 2:  # SAFETY
                logger.error("Gemini response was blocked by safety filters")
                raise Exception("Gemini安全過濾器阻止了內容處理。請手動選擇其他AI模型或調整提示詞內容")
            elif candidate.finish_reason == 3:  # RECITATION
                logger.error("Gemini response was blocked by citation filters")
                raise Exception("Gemini引用過濾器阻止了內容處理。請手動選擇其他AI模型或調整提示詞內容")
            elif candidate.finish_reason == 4:  # OTHER
                logger.error("Gemini response was blocked for other reasons")
                raise Exception("Gemini因其他原因阻止了內容處理。請手動選擇其他AI模型或調整提示詞內容")
            
            # 檢查是否有內容
            if not candidate.content or not candidate.content.parts:
                logger.warning("Gemini response has no content parts")
                return "API響應沒有內容，請嘗試調整提示詞"
            
            # 安全地獲取文本內容
            try:
                text_content = candidate.content.parts[0].text
                if not text_content or not text_content.strip():
                    logger.warning("Gemini response content is empty")
                    return "API響應內容為空，請嘗試調整提示詞"
                return text_content.strip()
            except Exception as e:
                logger.error(f"Failed to parse Gemini response content: {e}")
                return "解析API響應失敗，請嘗試調整提示詞"
                
        except Exception as e:
            logger.error(f"Gemini content generation failed: {e}")
            raise
    
    def test_simple_extraction(self, content: str) -> str:
        """測試簡單提取功能"""
        try:
            # 使用簡化的測試提示詞
            test_prompt = f"""
請從以下文檔中提取基本產品資訊：

文檔內容：
{content}

請以 JSON 格式輸出：
{{
  "產品名稱": "產品名稱",
  "產品類別": "產品類別", 
  "製造商": "製造商名稱",
  "主要成分": "主要成分列表",
  "使用說明": "使用說明"
}}

請開始提取：
"""
            
            response = self.client.generate_content(
                test_prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 1000
                },
                safety_settings=[]  # 完全關閉安全過濾器
            )
            
            # 檢查響應
            if not response.candidates:
                return '{"error": "API響應無效"}'
            
            candidate = response.candidates[0]
            
            # 檢查finish_reason
            if candidate.finish_reason == 2:  # SAFETY
                logger.error("Gemini test response was blocked by safety filters")
                return '{"error": "安全過濾器阻止"}'
            elif candidate.finish_reason == 3:  # RECITATION
                logger.error("Gemini test response was blocked by citation filters")
                return '{"error": "引用過濾器阻止"}'
            elif candidate.finish_reason == 4:  # OTHER
                logger.error("Gemini test response was blocked for other reasons")
                return '{"error": "其他原因阻止"}'
            
            # 獲取內容
            if candidate.content and candidate.content.parts:
                text_content = candidate.content.parts[0].text
                return text_content.strip() if text_content else '{"error": "內容為空"}'
            else:
                return '{"error": "沒有內容"}'
                
        except Exception as e:
            logger.error(f"Gemini test extraction failed: {e}")
            return f'{{"error": "提取失敗: {str(e)}"}}'
    
    def _log_content_analysis(self, prompt: str) -> None:
        """記錄內容分析，幫助診斷安全過濾器問題"""
        try:
            # 檢查可能觸發安全過濾器的關鍵詞
            sensitive_keywords = [
                '毒理', '毒性', '致癌', '致畸', '致敏', '刺激', '過敏',
                '危險', '有害', '化學', '成分', '含量', '濃度',
                '皮膚', '接觸', '吸入', '攝入', '暴露'
            ]
            
            found_keywords = []
            for keyword in sensitive_keywords:
                if keyword in prompt:
                    found_keywords.append(keyword)
            
            if found_keywords:
                logger.info(f"Gemini content analysis - Found potentially sensitive keywords: {found_keywords}")
                logger.info(f"Gemini content analysis - Prompt length: {len(prompt)} characters")
                logger.info(f"Gemini content analysis - First 200 characters of prompt: {prompt[:200]}...")
                
                # 記錄提示詞使用情況
                logger.info("Gemini content analysis - Using user-specified prompt")
            else:
                logger.info("Gemini content analysis - No obvious sensitive keywords found")

        except Exception as e:
            logger.warning(f"Content analysis failed: {e}")

    def check_content_safety(self, content: str) -> Dict[str, Any]:
        """檢查內容安全性（使用 Gemini 進行安全檢查）"""
        try:
            # 構建安全檢查提示詞
            safety_prompt = f"""
請檢查以下內容是否適合用於文檔處理任務，特別是化妝品產品資訊檔案（PIF）的資料提取。

內容：
{content}

請評估：
1. 內容是否包含不當或敏感資訊
2. 是否適合用於商業文檔處理
3. 是否有任何安全風險

請以 JSON 格式回應：
{{
    "is_safe": true/false,
    "risk_level": "low/medium/high/critical",
    "risk_factors": ["具體風險因素列表"],
    "suggestions": ["改進建議列表"],
    "confidence": 0.0-1.0
}}
"""
            
            response = self.client.generate_content(
                safety_prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 500
                },
                safety_settings=[]  # 完全關閉安全過濾器
            )
            
            # 檢查響應
            if not response.candidates:
                return {
                    'is_safe': True,
                    'risk_level': 'low',
                    'risk_factors': [],
                    'suggestions': [],
                    'confidence': 0.0,
                    'error': 'API 響應無效'
                }
            
            candidate = response.candidates[0]
            
            # 檢查是否被安全過濾器阻止
            if candidate.finish_reason == 2:  # SAFETY
                return {
                    'is_safe': False,
                    'risk_level': 'high',
                    'risk_factors': ['內容被 Gemini 安全過濾器阻止'],
                    'suggestions': ['建議修改內容或使用其他模型'],
                    'confidence': 0.9
                }
            
            # 獲取文本內容
            if not candidate.content or not candidate.content.parts:
                return {
                    'is_safe': True,
                    'risk_level': 'low',
                    'risk_factors': [],
                    'suggestions': [],
                    'confidence': 0.0,
                    'error': 'API 響應沒有內容'
                }
            
            result_text = candidate.content.parts[0].text.strip()
            
            # 嘗試解析 JSON 回應
            try:
                import json
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError:
                # 如果無法解析 JSON，返回預設安全結果
                return {
                    'is_safe': True,
                    'risk_level': 'low',
                    'risk_factors': [],
                    'suggestions': ['無法解析 AI 回應，預設為安全'],
                    'confidence': 0.5
                }
                
        except Exception as e:
            logger.error(f"Gemini safety check failed: {e}")
            return {
                'is_safe': True,
                'risk_level': 'low',
                'risk_factors': [],
                'suggestions': [],
                'confidence': 0.0,
                'error': str(e)
            }

    def get_pricing(self) -> Dict[str, float]:
        """獲取Gemini定價"""
        pricing = {
            'gemini-pro': {'input': 0.0005, 'output': 0.0015},
            'gemini-pro-vision': {'input': 0.0005, 'output': 0.0015}
        }
        return pricing.get(self.model, {'input': 0.0005, 'output': 0.0015})

class GrokClient(BaseAIClient):
    """Grok客戶端"""
    
    def __init__(self, api_key: str, model: str = "grok-beta"):
        super().__init__(api_key, model)
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """初始化Grok客戶端"""
        try:
            import openai
            # Grok API與OpenAI SDK兼容，使用不同的base_url
            return openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1"  # Grok API的base URL
            )
        except ImportError:
            logger.error("OpenAI package not installed, please run: pip install openai")
            raise
        except Exception as e:
            logger.error(f"Grok client initialization failed: {e}")
            raise
    
    def _parse_prompt_into_messages(self, prompt: str) -> List[Dict[str, str]]:
        """將提示詞解析為 messages（完全不分離）"""
        # 完全不分離，直接使用原始提示詞
        return [{"role": "user", "content": prompt}]
    
    def extract_data(self, prompt: str, max_tokens: int = 4000) -> str:
        """提取結構化資料"""
        try:
            # 完全不分離，直接使用原始提示詞
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Grok data extraction failed: {e}")
            raise
    
    def generate_content(self, prompt: str, max_tokens: int = 2000) -> str:
        """生成內容"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Grok content generation failed: {e}")
            raise
    
    def check_content_safety(self, content: str) -> Dict[str, Any]:
        """檢查內容安全性（使用 Grok 進行安全檢查）"""
        try:
            # 構建安全檢查提示詞
            safety_prompt = f"""
請檢查以下內容是否適合用於文檔處理任務，特別是化妝品產品資訊檔案（PIF）的資料提取。

內容：
{content}

請評估：
1. 內容是否包含不當或敏感資訊
2. 是否適合用於商業文檔處理
3. 是否有任何安全風險

請以 JSON 格式回應：
{{
    "is_safe": true/false,
    "risk_level": "low/medium/high/critical",
    "risk_factors": ["具體風險因素列表"],
    "suggestions": ["改進建議列表"],
    "confidence": 0.0-1.0
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一個內容安全檢查專家，專門評估文檔處理內容的安全性。"},
                    {"role": "user", "content": safety_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 嘗試解析 JSON 回應
            try:
                import json
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError:
                # 如果無法解析 JSON，返回預設安全結果
                return {
                    'is_safe': True,
                    'risk_level': 'low',
                    'risk_factors': [],
                    'suggestions': ['無法解析 AI 回應，預設為安全'],
                    'confidence': 0.5
                }
                
        except Exception as e:
            logger.error(f"Grok safety check failed: {e}")
            return {
                'is_safe': True,
                'risk_level': 'low',
                'risk_factors': [],
                'suggestions': [],
                'confidence': 0.0,
                'error': str(e)
            }

    def get_pricing(self) -> Dict[str, float]:
        """獲取Grok定價"""
        # 根據xAI的實際定價更新
        pricing = {
            'grok-beta': {'input': 0.01, 'output': 0.03},
            'grok-2-vision-latest': {'input': 0.02, 'output': 0.06}
        }
        return pricing.get(self.model, {'input': 0.01, 'output': 0.03})

class CopilotClient(BaseAIClient):
    """Microsoft Copilot客戶端"""
    
    def __init__(self, api_key: str, model: str = "copilot-gpt-4"):
        super().__init__(api_key, model)
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """初始化Copilot客戶端"""
        try:
            import openai
            # Microsoft Copilot使用OpenAI API格式
            return openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.copilot.microsoft.com/v1"
            )
        except ImportError:
            logger.error("OpenAI package not installed, please run: pip install openai")
            raise
        except Exception as e:
            logger.error(f"Copilot client initialization failed: {e}")
            raise
    
    def _parse_prompt_into_messages(self, prompt: str) -> List[Dict[str, str]]:
        """將提示詞解析為 messages（完全不分離）"""
        # 完全不分離，直接使用原始提示詞
        return [{"role": "user", "content": prompt}]
    
    def extract_data(self, prompt: str, max_tokens: int = 4000) -> str:
        """提取結構化資料"""
        try:
            # 完全不分離，直接使用原始提示詞
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Copilot data extraction failed: {e}")
            raise
    
    def generate_content(self, prompt: str, max_tokens: int = 2000) -> str:
        """生成內容"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Copilot content generation failed: {e}")
            raise
    
    def check_content_safety(self, content: str) -> Dict[str, Any]:
        """檢查內容安全性（使用 Copilot 進行安全檢查）"""
        try:
            # 構建安全檢查提示詞
            safety_prompt = f"""
請檢查以下內容是否適合用於文檔處理任務，特別是化妝品產品資訊檔案（PIF）的資料提取。

內容：
{content}

請評估：
1. 內容是否包含不當或敏感資訊
2. 是否適合用於商業文檔處理
3. 是否有任何安全風險

請以 JSON 格式回應：
{{
    "is_safe": true/false,
    "risk_level": "low/medium/high/critical",
    "risk_factors": ["具體風險因素列表"],
    "suggestions": ["改進建議列表"],
    "confidence": 0.0-1.0
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一個內容安全檢查專家，專門評估文檔處理內容的安全性。"},
                    {"role": "user", "content": safety_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 嘗試解析 JSON 回應
            try:
                import json
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError:
                # 如果無法解析 JSON，返回預設安全結果
                return {
                    'is_safe': True,
                    'risk_level': 'low',
                    'risk_factors': [],
                    'suggestions': ['無法解析 AI 回應，預設為安全'],
                    'confidence': 0.5
                }
                
        except Exception as e:
            logger.error(f"Copilot safety check failed: {e}")
            return {
                'is_safe': True,
                'risk_level': 'low',
                'risk_factors': [],
                'suggestions': [],
                'confidence': 0.0,
                'error': str(e)
            }

    def get_pricing(self) -> Dict[str, float]:
        """獲取定價資訊"""
        return {
            "input": 0.03,  # 每1K tokens
            "output": 0.06,  # 每1K tokens
            "context_window": 128000
        }

class MultiAIClient:
    """多AI模型客戶端管理器"""
    
    def __init__(self, settings: Dict[str, Any]):
        """
        初始化多AI客戶端
        
        Args:
            settings: 設定字典，包含API金鑰和模型選擇
        """
        self.settings = settings
        self.clients = {}
        self.current_provider = settings.get('ai_provider', 'openai')
        self.current_model = settings.get('ai_model', 'gpt-4')
        
        # 初始化可用的客戶端
        self._initialize_clients()
        
        logger.info(f"Multi-AI client initialized, current provider: {self.current_provider}, model: {self.current_model}")
    
    def _initialize_clients(self):
        """初始化所有可用的AI客戶端"""
        # OpenAI客戶端
        openai_key = self.settings.get('openai_api_key', '')
        if openai_key:
            try:
                # 使用當前設定的模型，如果沒有則使用預設
                openai_model = self.settings.get('ai_model', 'gpt-4') if self.current_provider == 'openai' else self.settings.get('openai_model', 'gpt-4')
                self.clients['openai'] = OpenAIClient(openai_key, openai_model)
                logger.info(f"OpenAI client initialized, model: {openai_model}")
            except Exception as e:
                logger.warning(f"OpenAI client initialization failed: {e}")
        
        # Claude客戶端
        claude_key = self.settings.get('claude_api_key', '')
        if claude_key:
            try:
                # 使用當前設定的模型，如果沒有則使用預設
                claude_model = self.settings.get('ai_model', 'claude-3-sonnet-20240229') if self.current_provider == 'claude' else self.settings.get('claude_model', 'claude-3-sonnet-20240229')
                self.clients['claude'] = ClaudeClient(claude_key, claude_model)
                logger.info(f"Claude client initialized, model: {claude_model}")
            except Exception as e:
                logger.warning(f"Claude client initialization failed: {e}")
        
        # Gemini客戶端
        gemini_key = self.settings.get('gemini_api_key', '')
        if gemini_key:
            try:
                # 使用當前設定的模型，如果沒有則使用預設
                ai_model = self.settings.get('ai_model', 'gemini-2.5-flash')
                gemini_model = ai_model if self.current_provider == 'gemini' else self.settings.get('gemini_model', 'gemini-2.5-flash')
                self.clients['gemini'] = GeminiClient(gemini_key, gemini_model)
                logger.info(f"Gemini客戶端已初始化，模型: {gemini_model}")
            except Exception as e:
                logger.warning(f"Gemini客戶端初始化失敗: {e}")
        
        # Grok客戶端
        grok_key = self.settings.get('grok_api_key', '')
        if grok_key:
            try:
                # 使用當前設定的模型，如果沒有則使用預設
                grok_model = self.settings.get('ai_model', 'grok-beta') if self.current_provider == 'grok' else self.settings.get('grok_model', 'grok-beta')
                self.clients['grok'] = GrokClient(grok_key, grok_model)
                logger.info(f"Grok客戶端已初始化，模型: {grok_model}")
            except Exception as e:
                logger.warning(f"Grok客戶端初始化失敗: {e}")
        
        # Microsoft Copilot客戶端
        copilot_key = self.settings.get('copilot_api_key', '')
        if copilot_key:
            try:
                # 使用當前設定的模型，如果沒有則使用預設
                copilot_model = self.settings.get('ai_model', 'copilot-gpt-4') if self.current_provider == 'microsoft' else self.settings.get('copilot_model', 'copilot-gpt-4')
                self.clients['microsoft'] = CopilotClient(copilot_key, copilot_model)
                logger.info(f"Microsoft Copilot客戶端已初始化，模型: {copilot_model}")
            except Exception as e:
                logger.warning(f"Microsoft Copilot客戶端初始化失敗: {e}")
    
    def get_available_providers(self) -> list:
        """獲取可用的AI提供者"""
        return list(self.clients.keys())
    
    def get_available_models(self, provider: str = None) -> Dict[str, list]:
        """獲取可用的模型列表"""
        if provider:
            return {provider: self._get_models_for_provider(provider)}
        
        models = {}
        for provider_name in self.clients.keys():
            models[provider_name] = self._get_models_for_provider(provider_name)
        return models
    
    def _get_models_for_provider(self, provider: str) -> list:
        """獲取特定提供者的模型列表"""
        provider_info = get_available_providers()
        if provider in provider_info:
            return provider_info[provider]['models']
        return []
    
    def switch_provider(self, provider: str, model: str = None):
        """切換AI提供者"""
        if provider not in self.clients:
            raise ValueError(f"提供者 {provider} 不可用")
        
        self.current_provider = provider
        if model:
            self.current_model = model
        
        logger.info(f"已切換到 {provider}，模型: {self.current_model}")
    
    def get_current_client(self) -> BaseAIClient:
        """獲取當前客戶端"""
        if self.current_provider not in self.clients:
            raise ValueError(f"當前提供者 {self.current_provider} 不可用")
        
        return self.clients[self.current_provider]
    
    def extract_data(self, prompt: str, max_tokens: int = 4000, provider: str = None) -> str:
        """提取結構化資料"""
        client = self.get_current_client() if not provider else self.clients.get(provider)
        if not client:
            raise ValueError(f"提供者 {provider or self.current_provider} 不可用")
        
        return client.extract_data(prompt, max_tokens)
    
    def generate_content(self, prompt: str, max_tokens: int = 2000, provider: str = None) -> str:
        """生成內容"""
        client = self.get_current_client() if not provider else self.clients.get(provider)
        if not client:
            raise ValueError(f"提供者 {provider or self.current_provider} 不可用")
        
        return client.generate_content(prompt, max_tokens)
    
    def get_pricing_info(self, provider: str = None) -> Dict[str, Any]:
        """獲取定價資訊"""
        if provider:
            client = self.clients.get(provider)
            if not client:
                return {}
            return {provider: client.get_pricing()}
        
        pricing = {}
        for provider_name, client in self.clients.items():
            pricing[provider_name] = client.get_pricing()
        return pricing
    
    def estimate_cost(self, content: str, provider: str = None) -> Dict[str, Any]:
        """估算成本"""
        # 簡單的token估算（實際應該使用tiktoken等工具）
        estimated_tokens = len(content.split()) * 1.3  # 粗略估算
        
        if provider:
            client = self.clients.get(provider)
            if not client:
                return {}
            
            pricing = client.get_pricing()
            cost = (estimated_tokens / 1000) * (pricing['input'] + pricing['output'])
            
            return {
                'provider': provider,
                'estimated_tokens': int(estimated_tokens),
                'estimated_cost': round(cost, 4),
                'pricing': pricing
            }
        
        # 估算所有提供者的成本
        costs = {}
        for provider_name, client in self.clients.items():
            pricing = client.get_pricing()
            cost = (estimated_tokens / 1000) * (pricing['input'] + pricing['output'])
            costs[provider_name] = {
                'estimated_tokens': int(estimated_tokens),
                'estimated_cost': round(cost, 4),
                'pricing': pricing
            }
        
        return costs

# 便利函數
def create_ai_client(settings: Dict[str, Any]) -> MultiAIClient:
    """創建多AI客戶端"""
    return MultiAIClient(settings)

def get_available_providers() -> Dict[str, Dict[str, Any]]:
    """獲取所有可用的AI提供者資訊"""
    return {
        'openai': {
            'name': 'OpenAI (ChatGPT)',
            'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
            'default_model': 'gpt-4o',
            'api_key_env': 'OPENAI_API_KEY',
            'description': '通用性強，適合各種任務'
        },
        'claude': {
            'name': 'Claude (Anthropic)',
            'models': ['claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022', 'claude-3-opus-20240229'],
            'default_model': 'claude-3-5-sonnet-20241022',
            'api_key_env': 'CLAUDE_API_KEY',
            'description': '在文檔分析任務中表現良好'
        },
        'gemini': {
            'name': 'Gemini (Google)',
            'models': ['gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-pro'],
            'default_model': 'gemini-2.5-flash',
            'api_key_env': 'GEMINI_API_KEY',
            'description': 'Google的多模態AI模型'
        },
        'grok': {
            'name': 'Grok (xAI)',
            'models': ['grok-2', 'grok-beta'],
            'default_model': 'grok-beta',
            'api_key_env': 'GROK_API_KEY',
            'description': 'xAI的AI助手，支援多模態處理'
        },
        'microsoft': {
            'name': 'Microsoft Copilot',
            'models': ['copilot-gpt-4', 'copilot-gpt-4-turbo'],
            'default_model': 'copilot-gpt-4',
            'api_key_env': 'COPILOT_API_KEY',
            'description': 'Microsoft的AI助手，基於Azure OpenAI'
        }
    }
