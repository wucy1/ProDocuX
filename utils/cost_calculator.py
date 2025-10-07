#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成本計算器
估算AI處理的成本和時間
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)

class CostCalculator:
    """成本計算器"""
    
    def __init__(self):
        """初始化成本計算器"""
        # OpenAI GPT-4 定價 (每1000 tokens)
        self.pricing = {
            'gpt-4': {
                'input': 0.03,   # $0.03 per 1K tokens
                'output': 0.06   # $0.06 per 1K tokens
            },
            'gpt-3.5-turbo': {
                'input': 0.001,  # $0.001 per 1K tokens
                'output': 0.002  # $0.002 per 1K tokens
            }
        }
        
        # 預設模型
        self.default_model = 'gpt-4'
        
        logger.info("成本計算器已初始化")
    
    def estimate_cost(self, file_path: Path, profile_name: str = "default") -> Dict[str, Any]:
        """
        估算處理成本
        
        Args:
            file_path: 檔案路徑
            profile_name: Profile名稱
            
        Returns:
            成本估算資訊
        """
        try:
            # 讀取文檔內容
            content = self._read_document(file_path)
            if not content:
                return self._create_error_response("無法讀取文檔內容")
            
            # 估算token數量
            estimated_tokens = self._estimate_tokens(content)
            
            # 計算成本
            cost_info = self._calculate_cost(estimated_tokens)
            
            # 估算處理時間
            estimated_time = self._estimate_processing_time(estimated_tokens)
            
            return {
                'success': True,
                'file_size': len(content),
                'estimated_tokens': estimated_tokens,
                'estimated_cost': cost_info['total_cost'],
                'input_cost': cost_info['input_cost'],
                'output_cost': cost_info['output_cost'],
                'estimated_time': estimated_time,
                'model': self.default_model,
                'profile': profile_name
            }
            
        except Exception as e:
            logger.error(f"成本估算失敗: {e}")
            return self._create_error_response(str(e))
    
    def _read_document(self, file_path: Path) -> str:
        """讀取文檔內容"""
        file_type = file_path.suffix.lower()
        
        if file_type == '.pdf':
            return self._read_pdf(file_path)
        elif file_type in ['.docx', '.doc']:
            return self._read_word(file_path)
        elif file_type == '.txt':
            return self._read_text(file_path)
        else:
            raise ValueError(f"不支援的檔案格式: {file_type}")
    
    def _read_pdf(self, file_path: Path) -> str:
        """讀取PDF檔案"""
        try:
            with pdfplumber.open(file_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                return '\n'.join(text_parts)
        except Exception as e:
            logger.error(f"PDF讀取失敗: {e}")
            return ""
    
    def _read_word(self, file_path: Path) -> str:
        """讀取Word檔案"""
        try:
            doc = Document(file_path)
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            return '\n'.join(text_parts)
        except Exception as e:
            logger.error(f"Word讀取失敗: {e}")
            return ""
    
    def _read_text(self, file_path: Path) -> str:
        """讀取文字檔案"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"文字檔案讀取失敗: {e}")
            return ""
    
    def _estimate_tokens(self, content: str) -> int:
        """
        估算token數量
        
        Args:
            content: 文檔內容
            
        Returns:
            估算的token數量
        """
        # 簡單的token估算：約4個字符 = 1個token
        # 實際的token計算會更複雜，這裡使用簡化版本
        
        # 基本token估算
        basic_tokens = len(content) // 4
        
        # 考慮中文和英文的差異
        chinese_chars = sum(1 for char in content if '\u4e00' <= char <= '\u9fff')
        english_chars = len(content) - chinese_chars
        
        # 中文通常需要更多tokens
        estimated_tokens = int(english_chars / 4 + chinese_chars / 2)
        
        # 加上提示詞的token消耗（約1000-2000 tokens）
        prompt_tokens = 1500
        
        # 加上輸出token估算（約500-1000 tokens）
        output_tokens = 750
        
        total_tokens = estimated_tokens + prompt_tokens + output_tokens
        
        return total_tokens
    
    def _calculate_cost(self, tokens: int) -> Dict[str, float]:
        """
        計算成本
        
        Args:
            tokens: token數量
            
        Returns:
            成本資訊
        """
        model_pricing = self.pricing[self.default_model]
        
        # 假設輸入和輸出各佔一半
        input_tokens = int(tokens * 0.7)  # 70% 輸入
        output_tokens = int(tokens * 0.3)  # 30% 輸出
        
        input_cost = (input_tokens / 1000) * model_pricing['input']
        output_cost = (output_tokens / 1000) * model_pricing['output']
        total_cost = input_cost + output_cost
        
        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost
        }
    
    def _estimate_processing_time(self, tokens: int) -> int:
        """
        估算處理時間（秒）
        
        Args:
            tokens: token數量
            
        Returns:
            估算的處理時間（秒）
        """
        # 基於token數量的處理時間估算
        # 假設每秒處理約1000 tokens
        base_time = tokens / 1000
        
        # 加上網路延遲和API處理時間
        network_delay = 2  # 2秒網路延遲
        api_processing = 1  # 1秒API處理時間
        
        total_time = base_time + network_delay + api_processing
        
        return max(int(total_time), 3)  # 最少3秒
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """創建錯誤回應"""
        return {
            'success': False,
            'error': error_message,
            'estimated_tokens': 0,
            'estimated_cost': 0.0,
            'estimated_time': 0
        }
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """獲取定價資訊"""
        return {
            'models': self.pricing,
            'default_model': self.default_model,
            'currency': 'USD',
            'note': '定價可能會有變動，請以OpenAI官方為準'
        }
    
    def calculate_batch_cost(self, file_paths: list, profile_name: str = "default") -> Dict[str, Any]:
        """
        計算批量處理成本
        
        Args:
            file_paths: 檔案路徑列表
            profile_name: Profile名稱
            
        Returns:
            批量成本資訊
        """
        total_tokens = 0
        total_cost = 0.0
        total_time = 0
        file_costs = []
        
        for file_path in file_paths:
            cost_info = self.estimate_cost(Path(file_path), profile_name)
            
            if cost_info['success']:
                total_tokens += cost_info['estimated_tokens']
                total_cost += cost_info['estimated_cost']
                total_time += cost_info['estimated_time']
                
                file_costs.append({
                    'file': str(file_path),
                    'tokens': cost_info['estimated_tokens'],
                    'cost': cost_info['estimated_cost'],
                    'time': cost_info['estimated_time']
                })
        
        return {
            'success': True,
            'total_files': len(file_paths),
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'total_time': total_time,
            'average_cost_per_file': total_cost / len(file_paths) if file_paths else 0,
            'file_costs': file_costs
        }






