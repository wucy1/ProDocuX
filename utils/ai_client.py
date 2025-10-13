#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI客戶端
統一管理AI API調用
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 載入環境變數（將在初始化時從正確的位置載入）

logger = logging.getLogger(__name__)

JSON_ENFORCE_PREFIX = (
    "你必須嚴格輸出純 JSON。不要輸出任何解說、標點、程式碼區塊標記、前後綴文字。"
    "若無法找到欄位，請以空字串或空陣列填入。回傳物件的最外層必須是 JSON 物件。"
)

class AIClient:
    """AI客戶端"""
    
    def __init__(self, model: str = "gpt-4"):
        """
        初始化AI客戶端
        
        Args:
            model: 使用的AI模型
        """
        self.model = model
        self.api_key = self._get_api_key()
        self.client = self._initialize_client()
        # 讀取設定（保守預設）
        try:
            from .settings_manager import SettingsManager
        except Exception:
            from utils.settings_manager import SettingsManager  # type: ignore
        api_cfg = SettingsManager().get_api_config()
        self.force_json = bool(api_cfg.get("force_json", False))
        self.max_tokens_cap = int(api_cfg.get("max_tokens_cap", 4000))
        self.retry_cfg = api_cfg.get("retry", {"enabled": False, "max_attempts": 1, "backoff_seconds": 0})
        
        logger.info(f"AI客戶端已初始化，模型: {model}")
    
    def _get_api_key(self) -> str:
        """獲取API金鑰"""
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('IOPENAI_API_KEY')
        if not api_key:
            raise ValueError("請設定 OPENAI_API_KEY 或 IOPENAI_API_KEY 環境變數")
        return api_key
    
    def _initialize_client(self):
        """初始化AI客戶端"""
        try:
            import openai
            return openai.OpenAI(api_key=self.api_key)
        except ImportError:
            logger.error("OpenAI套件未安裝，請執行: pip install openai")
            raise
        except Exception as e:
            logger.error(f"AI客戶端初始化失敗: {e}")
            raise

    def _ensure_json(self, text: str) -> str:
        """嘗試從回覆中抽取並修復為合法 JSON 物件字串。"""
        try:
            # 先嘗試直接 parse
            return json.dumps(json.loads(text), ensure_ascii=False)
        except Exception:
            pass
        # 抽取第一段看似 JSON 的片段
        try:
            import re
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                snippet = m.group(0)
                json.loads(snippet)  # 驗證
                return snippet
        except Exception:
            pass
        # 最後回退：包一層模型修復（可選：這裡直接回原文）
        logger.warning("無法嚴格解析為 JSON，回傳原始文本供上游容錯")
        return text
    
    def extract_data(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        提取結構化資料
        
        Args:
            prompt: 提示詞
            max_tokens: 最大token數
            
        Returns:
            AI回應（盡可能為 JSON 字串）
        """
        try:
            messages = [
                {"role": "system", "content": JSON_ENFORCE_PREFIX},
                {"role": "user", "content": prompt}
            ]

            # 根據設定決定是否強制 JSON、是否重試
            response = None
            attempt = 0
            max_tokens = min(max_tokens, self.max_tokens_cap)
            while True:
                attempt += 1
                try:
                    if self.force_json:
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            temperature=0.1,
                            max_tokens=max_tokens,
                            response_format={"type": "json_object"}
                        )
                    else:
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            temperature=0.1,
                            max_tokens=max_tokens
                        )
                    break
                except Exception as err:
                    if not self.retry_cfg.get("enabled") or attempt >= int(self.retry_cfg.get("max_attempts", 1)):
                        raise err
                    import time
                    time.sleep(float(self.retry_cfg.get("backoff_seconds", 0)))
            text = response.choices[0].message.content.strip()
            return self._ensure_json(text)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                logger.warning(f"API限制錯誤，嘗試減少token使用: {e}")
                # 嘗試減少max_tokens
                if max_tokens > 1000:
                    logger.info("嘗試使用較少的max_tokens重新請求")
                    return self.extract_data(prompt, max_tokens // 2)
                else:
                    logger.error("即使減少token也無法處理，檔案可能太大")
                    # 提供更具體的建議
                    suggestions = [
                        "1. 請先使用頁面預覽功能選擇要處理的特定頁面",
                        "2. 將分頁模式改為 'auto' 或 'all' 以自動選擇頁面",
                        "3. 嘗試處理較小的檔案",
                        "4. 檢查是否選擇了正確的AI模型（某些模型有較高的token限制）"
                    ]
                    suggestion_text = "\n".join(suggestions)
                    raise Exception(f"檔案太大，無法處理。\n\n建議解決方案：\n{suggestion_text}\n\n原始錯誤: {e}")
            else:
                logger.error(f"AI資料提取失敗: {e}")
                raise

    def generate_content(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        生成內容
        
        Args:
            prompt: 提示詞
            max_tokens: 最大token數
            
        Returns:
            生成的內容
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": JSON_ENFORCE_PREFIX},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            return self._ensure_json(response.choices[0].message.content.strip())
            
        except Exception as e:
            logger.error(f"AI內容生成失敗: {e}")
            raise

    def analyze_document(self, content: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        分析文檔
        
        Args:
            content: 文檔內容
            analysis_type: 分析類型
            
        Returns:
            分析結果
        """
        try:
            prompt = self._build_analysis_prompt(content, analysis_type)
            response = self.extract_data(prompt)
            # 解析JSON回應
            try:
                return json.loads(response)
            except Exception:
                return self._parse_json_response(response)
            
        except Exception as e:
            logger.error(f"文檔分析失敗: {e}")
            return {}
    
    def _build_analysis_prompt(self, content: str, analysis_type: str) -> str:
        """構建分析提示詞"""
        prompts = {
            "general": f"""
請分析以下文檔內容，提取關鍵資訊：

文檔內容：
{content}

請以JSON格式輸出分析結果：
{{
  "文檔類型": "文檔類型",
  "主要內容": "內容摘要",
  "關鍵資訊": ["關鍵資訊1", "關鍵資訊2"],
  "建議": "處理建議"
}}
""",
            "structure": f"""
請分析以下文檔的結構：

文檔內容：
{content}

請以JSON格式輸出結構分析：
{{
  "標題": "文檔標題",
  "章節": [
    {{"名稱": "章節名稱", "內容": "章節摘要"}}
  ],
  "表格": [
    {{"標題": "表格標題", "列數": 0, "欄數": 0}}
  ]
}}
""",
            "extraction": f"""
請從以下文檔中提取結構化資料：

文檔內容：
{content}

請按照標準格式提取資料，以JSON格式輸出。
"""
        }
        
        return prompts.get(analysis_type, prompts["general"])
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析JSON回應"""
        try:
            import re
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                logger.error("無法從AI回應中提取JSON")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失敗: {e}")
            return {}
    
    def estimate_tokens(self, text: str) -> int:
        """
        估算token數量
        
        Args:
            text: 文字內容
            
        Returns:
            估算的token數量
        """
        # 簡單的token估算：約4個字符 = 1個token
        return len(text) // 4
    
    def get_usage_info(self) -> Dict[str, Any]:
        """獲取使用資訊"""
        return {
            "model": self.model,
            "api_key_set": bool(self.api_key),
            "client_initialized": self.client is not None
        }




