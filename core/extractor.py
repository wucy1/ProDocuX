#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用文檔提取器
支援多種文檔格式的智能提取
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import pdfplumber
from docx import Document

from utils.ai_client import AIClient
from utils.file_handler import FileHandler
from .profile_manager import ProfileManager
from .prompt_parser import IntelligentPromptParser

logger = logging.getLogger(__name__)

class DocumentExtractor:
    """通用文檔提取器"""
    
    def __init__(self, profile_path: Optional[str] = None, work_id: Optional[str] = None, 
                 work_data: Optional[Dict[str, Any]] = None, ai_provider: Optional[str] = None,
                 ai_model: Optional[str] = None, user_prompt: Optional[str] = None):
        """
        初始化文檔提取器
        
        Args:
            profile_path: Profile檔案路徑（舊版相容）
            work_id: 工作ID（新版分層Profile）
            work_data: 工作資料（新版分層Profile）
            ai_provider: AI提供者（優先使用，否則使用預設）
            ai_model: AI模型（優先使用，否則使用預設）
            user_prompt: 使用者指定的提示詞
        """
        self.profile_manager = ProfileManager()
        self.file_handler = FileHandler()
        self.prompt_parser = IntelligentPromptParser()
        
        # 設定AI提供者和模型（優先使用傳入參數，否則使用預設）
        self.ai_provider = ai_provider
        self.ai_model = ai_model
        
        # 保存使用者提示詞
        self.user_prompt = user_prompt
        
        # 延遲初始化AIClient，避免在沒有API金鑰時出錯
        self.ai_client = None
        
        # 如果指定了AI設定，記錄日誌
        if ai_provider and ai_model:
            logger.info(f"DocumentExtractor using specified AI settings: {ai_provider}/{ai_model}")
        else:
            logger.info(f"DocumentExtractor using default AI settings")
        
        # 載入Profile（嚴格按照使用者指定）
        if work_id and work_data:
            # 新版：使用分層Profile
            self.profile = self.profile_manager.load_work_profile(work_id, work_data)
            logger.info(f"Document extractor initialized with hierarchical profile: {work_id}")
        elif profile_path:
            # 舊版：直接載入Profile檔案
            self.profile = self.profile_manager.load_profile(profile_path)
            logger.info(f"Document extractor initialized with profile: {self.profile.get('name', 'default')}")
        else:
            # 如果沒有指定Profile，直接報錯
            raise ValueError("必須指定Profile路徑或工作資料。系統不會使用預設Profile。")
    
    def _get_ai_client(self):
        """延遲初始化AIClient"""
        if self.ai_client is None:
            try:
                from utils.multi_ai_client import MultiAIClient
                from utils.settings_manager import SettingsManager
                
                # 獲取設定
                settings_manager = SettingsManager()
                settings = settings_manager.get_all_settings()
                
                # 如果指定了AI設定，覆蓋預設設定
                if self.ai_provider and self.ai_model:
                    settings['ai_provider'] = self.ai_provider
                    settings['ai_model'] = self.ai_model
                    logger.info(f"Using specified AI settings: {self.ai_provider}/{self.ai_model}")
                else:
                    logger.info("Using default AI settings")
                
                self.ai_client = MultiAIClient(settings)
                # 從MultiAIClient獲取實際的AI提供者和模型
                self.ai_provider = self.ai_client.current_provider
                self.ai_model = self.ai_client.current_model
                logger.info("MultiAIClient lazy initialization successful")
            except Exception as e:
                logger.warning(f"MultiAIClient initialization failed: {e}")
                # 創建一個假的AIClient，避免後續錯誤
                self.ai_client = type('MockAIClient', (), {
                    'extract_data': lambda *args, **kwargs: {"error": "AI客戶端未正確初始化"},
                    'generate_content': lambda *args, **kwargs: "AI客戶端未正確初始化"
                })()
        return self.ai_client
    
    def extract(self, file_path: Union[str, Path], output_format: str = "json", 
                user_prompt: Optional[str] = None, selected_pages: List[int] = None) -> Dict[str, Any]:
        """
        提取文檔結構化資料
        
        Args:
            file_path: 文檔檔案路徑
            output_format: 輸出格式 (json, dict)
            user_prompt: 使用者自定義提示詞
            selected_pages: 用戶選擇的頁面列表
            
        Returns:
            提取的結構化資料
        """
        try:
            # 存儲使用者提示詞到實例變數
            self.user_prompt = user_prompt
            
            # 讀取文檔內容
            content = self._read_document(file_path)
            if not content:
                raise ValueError(f"無法讀取文檔: {file_path}")
            
            # 如果有使用者提示詞，使用智能解析
            if user_prompt:
                structured_data = self._extract_with_intelligent_prompt(
                    content, file_path, user_prompt, selected_pages
                )
            else:
                # 智能分頁處理
                if self.profile.get('use_page_extraction', True):
                    structured_data = self._extract_by_pages(content, file_path, selected_pages)
                else:
                    structured_data = self._extract_whole_document(content)
            
            # 後處理
            structured_data = self._post_process(structured_data)
            
            # 格式化輸出
            if output_format == "json":
                return structured_data
            elif output_format == "dict":
                return structured_data
            else:
                raise ValueError(f"不支援的輸出格式: {output_format}")
                
        except Exception as e:
            logger.error(f"Document extraction failed: {e}")
            raise
    
    def _extract_with_intelligent_prompt(self, content: str, file_path: Path, 
                                       user_prompt: str, selected_pages: List[int] = None) -> Dict[str, Any]:
        """
        使用智能提示詞提取文檔
        
        Args:
            content: 文檔內容
            file_path: 文檔路徑
            user_prompt: 使用者提示詞
            
        Returns:
            提取的結構化資料
        """
        try:
            # 設置使用者提示詞到實例變數
            self.user_prompt = user_prompt
            
            # 根據是否有選定頁面決定使用哪種方法
            if selected_pages:
                logger.info("🔍 使用分頁提取方法，確保使用者提示詞不被覆蓋")
                return self._extract_by_pages(content, file_path, selected_pages)
            else:
                logger.info("🔍 使用整份文檔提取方法，確保使用者提示詞不被覆蓋")
                return self._extract_whole_document(content)
            
        except Exception as e:
            logger.error(f"智能提示詞提取失敗: {e}")
            # 直接拋出異常，不使用回退機制
            raise Exception(f"智能提示詞提取失敗，請檢查提示詞內容或AI模型設定: {e}")
    
    def _get_template_info(self) -> str:
        """獲取模板資訊"""
        # 這裡可以從Profile中獲取模板資訊
        template_info = "使用預設模板格式"
        
        if 'template_info' in self.profile:
            template_info = self.profile['template_info']
        
        return template_info
    
    def _read_document(self, file_path: Union[str, Path]) -> str:
        """讀取文檔內容"""
        file_path = Path(file_path)
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
    
    def _read_pdf_by_pages(self, file_path: Path, selected_pages: List[int] = None) -> List[Dict[str, Any]]:
        """按頁面讀取PDF檔案，只讀取選定的頁面"""
        try:
            pages_data = []
            with pdfplumber.open(file_path) as pdf:
                logger.info(f"🔍 PDF總頁數: {len(pdf.pages)}")
                
                # 只讀取選定的頁面
                pages_to_read = selected_pages if selected_pages else range(1, len(pdf.pages) + 1)
                
                for page_num in pages_to_read:
                    if page_num > len(pdf.pages):
                        logger.warning(f"🔍 第 {page_num} 頁超出範圍，跳過")
                        continue
                        
                    page = pdf.pages[page_num - 1]  # 頁面索引從0開始
                    # 優先提取表格內容
                    tables = page.extract_tables()
                    page_text = page.extract_text()
                    
                    # 如果有表格，將表格內容轉換為文本
                    table_text = ""
                    if tables:
                        for table in tables:
                            for row in table:
                                if row:  # 確保行不為空
                                    table_text += " | ".join([cell or "" for cell in row]) + "\n"
                    
                    # 合併文本和表格內容
                    combined_content = ""
                    if page_text:
                        combined_content += page_text + "\n"
                    if table_text:
                        combined_content += "\n=== 表格內容 ===\n" + table_text
                    
                    
                    if combined_content.strip():
                        # 提取圖片位置（如果有）
                        images = []
                        if hasattr(page, 'images'):
                            images = page.images
                        
                        
                        pages_data.append({
                            'page_number': page_num,
                            'content': combined_content,
                            'tables': tables or [],
                            'images': images or [],
                            'paragraphs': self._split_into_paragraphs(combined_content)
                        })
                    else:
                        logger.warning(f"🔍 第 {page_num} 頁沒有提取到任何內容")
            logger.info(f"🔍 成功讀取 {len(pages_data)} 個有內容的頁面")
            return pages_data
        except Exception as e:
            logger.error(f"PDF分頁讀取失敗: {e}")
            return []
    
    def _split_into_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """將文字分割為段落"""
        paragraphs = []
        lines = text.split('\n')
        current_para = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if line:
                current_para.append(line)
            else:
                if current_para:
                    paragraphs.append({
                        'paragraph_number': len(paragraphs) + 1,
                        'line_number': line_num - len(current_para),
                        'content': '\n'.join(current_para)
                    })
                    current_para = []
        
        # 處理最後一個段落
        if current_para:
            paragraphs.append({
                'paragraph_number': len(paragraphs) + 1,
                'line_number': len(lines) - len(current_para),
                'content': '\n'.join(current_para)
            })
        
        return paragraphs
    
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
    
    def _read_docx_by_pages(self, file_path: Path, selected_pages: List[int] = None) -> List[Dict[str, Any]]:
        """按頁面讀取DOCX檔案，只讀取選定的頁面（模擬分頁）"""
        try:
            doc = Document(file_path)
            pages_data = []
            
            # 由於DOCX沒有明確的頁面概念，我們按段落分組來模擬分頁
            current_page = 1
            current_content = []
            paragraphs_per_page = 10  # 每頁大約10個段落
            
            for i, paragraph in enumerate(doc.paragraphs):
                if paragraph.text.strip():
                    current_content.append(paragraph.text)
                
                # 每10個段落或遇到分頁符時創建新頁面
                if (i + 1) % paragraphs_per_page == 0 or i == len(doc.paragraphs) - 1:
                    if current_content:
                        page_text = '\n'.join(current_content)
                        pages_data.append({
                            'page_number': current_page,
                            'content': page_text,
                            'tables': [],  # DOCX表格處理較複雜，暫時留空
                            'images': [],  # 圖片處理較複雜，暫時留空
                            'paragraphs': self._split_into_paragraphs(page_text)
                        })
                        current_page += 1
                        current_content = []
            
            # 如果沒有內容，至少返回一頁
            if not pages_data:
                pages_data.append({
                    'page_number': 1,
                    'content': '檔案內容為空',
                    'tables': [],
                    'images': [],
                    'paragraphs': []
                })
            
            return pages_data
        except Exception as e:
            logger.error(f"DOCX分頁讀取失敗: {e}")
            return []
    
    def _read_text(self, file_path: Path) -> str:
        """讀取文字檔案"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"文字檔案讀取失敗: {e}")
            return ""
    
    def _extract_by_pages(self, content: str, file_path: Path, selected_pages: List[int] = None) -> Dict[str, Any]:
        """分頁提取（智能識別頁面類型）"""
        try:
            # 確保 user_prompt 已設置（從調用者傳遞）
            if not hasattr(self, 'user_prompt') or not self.user_prompt:
                raise ValueError("分頁提取需要使用者提示詞，但未提供")
            
            # 檢查是否啟用分頁提取
            # 如果用戶選擇了頁面，強制使用分頁提取
            use_page_extraction = self.profile.get('use_page_extraction', True)
            if not use_page_extraction and not selected_pages:
                logger.info("分頁提取未啟用且未選擇頁面，使用整份文檔提取")
                return self._extract_whole_document(content)
            
            # 讀取頁面：有選定就按選擇，沒選定就全部
            file_type = file_path.suffix.lower()
            if file_type == '.pdf':
                important_pages = self._read_pdf_by_pages(file_path, selected_pages)
            elif file_type in ['.docx', '.doc']:
                important_pages = self._read_docx_by_pages(file_path, selected_pages)
            else:
                logger.warning(f"不支援分頁處理的檔案格式: {file_type}")
                return self._extract_whole_document(content)
            
            if not important_pages:
                logger.error("無法讀取頁面，請檢查文檔格式或檔案完整性")
                raise Exception("無法讀取文檔頁面，請檢查文檔格式是否正確")
            
            if selected_pages:
                logger.info(f"用戶選擇了 {len(important_pages)} 個頁面進行處理: {selected_pages}")
            else:
                logger.info(f"用戶未選擇頁面，使用全部 {len(important_pages)} 個頁面")
            
            # 讀取處理設定
            try:
                from utils.settings_manager import SettingsManager
                proc_cfg = SettingsManager().get_processing_config()
            except Exception:
                proc_cfg = {"page_selection": {"mode": "manual", "truncate_chars": 0}, "merge_strategy": {"ingredients": "copy_as_is", "strings": "append", "dict": "prefer_non_empty"}, "prompt": {"inject_page_meta": False, "simplify_profile": False}}

            # important_pages 已經在讀取頁面時定義了，這裡只需要記錄日誌
            if selected_pages:
                logger.info(f"用戶選擇了 {len(important_pages)} 個頁面進行處理: {selected_pages}")
            else:
                logger.info(f"用戶未選擇頁面，使用全部 {len(important_pages)} 個頁面")
            
            # 估算成本
            estimated_cost = self._estimate_processing_cost(important_pages)
            logger.info(f"預估處理成本: ${estimated_cost:.2f}")
            
            # 預先檢查是否需要分段處理（基於不同AI模型的特性）
            # 確保AI客戶端已初始化，以便獲取正確的ai_provider
            self._get_ai_client()
            ai_provider = getattr(self, 'ai_provider', '')
            total_content_length = sum(len(page_data.get('content', '')) for page_data in important_pages)
            should_chunk = self._should_use_chunking(ai_provider, total_content_length)
            
            if should_chunk:
                logger.info(f"檢測到長文檔（{total_content_length} 字符），使用分段處理策略")
                # 使用簡化的合併邏輯創建內容用於分段處理
                merged_content = self._simple_merge_pages(important_pages, file_type)
                merged_result = self._extract_document_in_chunks(merged_content)
                merged_result['_processed_pages'] = [p['page_number'] for p in important_pages]
            else:
                # 簡化頁面合併策略
                logger.info(f"使用簡化頁面合併策略，合併 {len(important_pages)} 個頁面")
                
                # 使用簡化的合併邏輯
                merged_content = self._simple_merge_pages(important_pages, file_type)
                
                # 構建提示詞
                merged_prompt = self._build_extraction_prompt(merged_content)
                
                try:
                    # 調用AI API處理合併內容
                    ai_client = self._get_ai_client()
                    merged_response = ai_client.extract_data(merged_prompt)
                    merged_result = self._parse_ai_response(merged_response)
                    merged_result['_raw_response'] = merged_response
                    merged_result['_processed_pages'] = [p['page_number'] for p in important_pages]
                    
                except Exception as e:
                    logger.error(f"頁面處理失敗: {e}")
                    raise e
            
            # 後處理合併結果
            return self._post_process_results(merged_result)
            
        except Exception as e:
            logger.error(f"分頁提取失敗: {e}")
            # 直接拋出異常，不使用回退機制
            raise Exception(f"分頁提取失敗，請檢查文檔格式或頁面選擇: {e}")
    
    def _extract_whole_document(self, content: str) -> Dict[str, Any]:
        """整份文檔提取"""
        # 檢查是否需要分段處理（基於不同AI模型的特性）
        # 確保AI客戶端已初始化，以便獲取正確的ai_provider
        self._get_ai_client()
        ai_provider = getattr(self, 'ai_provider', '')
        should_chunk = self._should_use_chunking(ai_provider, len(content))
        if should_chunk:
            logger.info(f"檢測到長文檔（{len(content)} 字符），使用分段處理策略")
            return self._extract_document_in_chunks(content)
        
        # 構建提示詞
        prompt = self._build_extraction_prompt(content)
        
        # 調用AI API
        ai_client = self._get_ai_client()
        response = ai_client.extract_data(prompt)
        
        # 解析回應
        structured_data = self._parse_ai_response(response)
        structured_data['_raw_response'] = response  # 保存原始響應
        return structured_data
    
    def _extract_document_in_chunks(self, content: str, chunk_size: int = 40000) -> Dict[str, Any]:
        """分段處理長文檔"""
        try:
            # 將文檔分成多個段落
            chunks = self._split_content_into_chunks(content, chunk_size)
            logger.info(f"文檔已分成 {len(chunks)} 個段落進行處理")
            
            # 處理每個段落
            all_results = []
            successful_chunks = 0
            
            for i, chunk in enumerate(chunks):
                logger.info(f"正在處理第 {i+1}/{len(chunks)} 個段落")
                try:
                    # 構建段落提示詞
                    prompt = self._build_chunk_extraction_prompt(chunk, i+1, len(chunks))
                    
                    # 調用AI API
                    ai_client = self._get_ai_client()
                    response = ai_client.extract_data(prompt)
                    
                    # 解析回應
                    chunk_result = self._parse_ai_response(response)
                    # 保存原始響應
                    chunk_result['_raw_response'] = response
                    all_results.append(chunk_result)
                    successful_chunks += 1
                    logger.info(f"第 {i+1} 個段落處理成功")
                    
                except Exception as e:
                    logger.warning(f"第 {i+1} 個段落處理失敗: {e}")
                    # 創建空的結果以保持結構
                    empty_result = {
                        '_raw_response': '',
                        '_chunk_index': i,
                        '_chunk_error': str(e)
                    }
                    all_results.append(empty_result)
                    continue
            
            # 檢查是否有成功的段落
            if successful_chunks == 0:
                logger.error("所有段落處理都失敗了")
                raise Exception("所有段落處理都失敗了")
            elif successful_chunks < len(chunks):
                logger.warning(f"只有 {successful_chunks}/{len(chunks)} 個段落處理成功")
            
            # 合併所有結果
            return self._merge_chunk_results(all_results)
                
        except Exception as e:
            logger.error(f"分段處理失敗: {e}")
            raise
    
    def _split_content_into_chunks(self, content: str, chunk_size: int) -> List[str]:
        """將內容分成多個段落，智能避免分割成分表"""
        # 檢測成分表區域
        lines = content.split('\n')
        ingredient_section_start = -1
        ingredient_section_end = -1
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            # 檢測成分表開始 - 放寬檢測條件
            if ('inci' in line_lower or 'composizione' in line_lower or 'ingredient' in line_lower or '成分' in line_lower):
                ingredient_section_start = i
            # 檢測成分表結束（遇到空行或新章節）
            elif ingredient_section_start >= 0 and (line.strip() == '' or line.startswith('PIF:') or line.startswith('PARTE')):
                ingredient_section_end = i
                break
        
        # 如果找到成分表區域，確保不被分割
        if ingredient_section_start >= 0:
            logger.info(f"檢測到成分表區域：行 {ingredient_section_start} 到 {ingredient_section_end}")
            
            # 將成分表區域作為一個整體段落
            ingredient_lines = lines[ingredient_section_start:ingredient_section_end] if ingredient_section_end > 0 else lines[ingredient_section_start:]
            ingredient_chunk = '\n'.join(ingredient_lines)
            
            # 處理成分表之前的內容
            before_lines = lines[:ingredient_section_start]
            before_chunk = '\n'.join(before_lines)
            
            # 處理成分表之後的內容
            after_lines = lines[ingredient_section_end:] if ingredient_section_end > 0 else []
            after_chunk = '\n'.join(after_lines)
            
            # 分別處理各個部分
            chunks = []
            if before_chunk.strip():
                chunks.extend(self._split_content_simple(before_chunk, chunk_size))
            
            if ingredient_chunk.strip():
                chunks.append(ingredient_chunk)
            
            if after_chunk.strip():
                chunks.extend(self._split_content_simple(after_chunk, chunk_size))
            
            return chunks
        
        # 如果沒有檢測到成分表，使用簡單分割
        return self._split_content_simple(content, chunk_size)
    
    def _split_content_simple(self, content: str, chunk_size: int) -> List[str]:
        """簡單的內容分割"""
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            
            # 如果不是最後一個段落，嘗試在句號或換行處分割
            if end < len(content):
                # 尋找最近的句號或換行
                for i in range(end, start + chunk_size - 1000, -1):
                    if content[i] in ['。', '\n', '\r']:
                        end = i + 1
                        break
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end
        
        return chunks
    
    def _build_extraction_prompt(self, content: str) -> str:
        """構建提取提示詞"""
        # 嚴格使用使用者指定的提示詞
        if not hasattr(self, 'user_prompt') or not self.user_prompt:
            raise ValueError("必須提供使用者提示詞。系統不會使用預設提示詞。")
        
        prompt_template = self.user_prompt
        
        # 確保提示詞模板有正確的結構分隔
        if "{{content}}" in prompt_template:
            # 替換佔位符，但保持content在最後（避免AI混淆）
            prompt = prompt_template.replace("{{content}}", "[文檔內容將在下方提供]")
            
            # 處理Profile佔位符（考慮settings設定）
            if "{{profile}}" in prompt:
                if self._should_attach_profile(prompt_template):
                    prompt = prompt.replace("{{profile}}", f"\n\n=== Profile配置 ===\n{json.dumps(self.profile, ensure_ascii=False, indent=2)}\n\n=== Profile配置結束 ===")
                else:
                    prompt = prompt.replace("{{profile}}", "[Profile配置已省略]")
            
            # 在最後附加實際內容
            prompt = prompt + f"\n\n=== 需要處理的文檔內容 ===\n{content}\n\n=== 文檔內容結束 ==="
        else:
            # 如果沒有模板變數，在最後附加內容
            prompt = prompt_template + f"\n\n=== 需要處理的文檔內容 ===\n{content}\n\n=== 文檔內容結束 ==="
        
        # 添加調試日誌
        logger.info(f"🔍 構建的提示詞長度: {len(prompt)} 字符")
        logger.info(f"🔍 提示詞前500字符: {prompt[:500]}...")
        
        # 檢查Profile內容
        logger.info(f"🔍 Profile內容: {json.dumps(self.profile, ensure_ascii=False, indent=2)[:200]}...")
        
        return prompt
    
    def _build_chunk_extraction_prompt(self, chunk: str, chunk_num: int, total_chunks: int) -> str:
        """構建段落提取提示詞"""
        return self._build_extraction_prompt(chunk)
    
    def _build_extraction_prompt_with_filename(self, filename: str, file_path: Path = None, content: str = None) -> str:
        """構建提取提示詞 - 解決AI混淆問題"""
        # 嚴格使用使用者指定的提示詞
        if not hasattr(self, 'user_prompt') or not self.user_prompt or self.user_prompt.strip() == '':
            raise ValueError("必須提供使用者提示詞。系統不會使用預設提示詞。")
        
        prompt_template = self.user_prompt
        
        # 策略：使用成功驗證的分隔標記（基於2025-10-01成功實現）
        if "{{content}}" in prompt_template:
            # 替換佔位符，使用成功驗證的分隔標記
            prompt = prompt_template.replace("{{content}}", 
                f"\n\n=== 文檔內容 ===\n"
                f"檔案名稱：{filename}\n"
                f"資料內容：\n{content}\n"
                f"=== 文檔內容結束 ===\n")
        else:
            # 沒有佔位符時，在最後附加內容，使用成功驗證的分隔標記
            prompt = prompt_template + f"\n\n=== 文檔內容 ===\n檔案名稱：{filename}\n資料內容：\n{content}\n=== 文檔內容結束 ===\n"
        
        # Profile 處理：檢查是否需要附加
        if "{{profile}}" in prompt:
            essential_profile = {
                "name": self.profile.get('name', 'default'),
                "fields": self.profile.get('fields', [])
            }
            prompt = prompt.replace("{{profile}}", 
                f"\n\n=== Profile 配置 ===\n"
                f"配置資料：\n{json.dumps(essential_profile, ensure_ascii=False, indent=2)}\n"
                f"=== Profile 配置結束 ===\n")
        else:
            # 檢查是否需要附加Profile
            if self._should_attach_profile(prompt_template):
                essential_profile = {
                    "name": self.profile.get('name', 'default'),
                    "fields": self.profile.get('fields', [])
                }
                prompt += f"\n\n=== Profile 配置 ===\n配置資料：\n{json.dumps(essential_profile, ensure_ascii=False, indent=2)}\n=== Profile 配置結束 ===\n"
        
        return prompt
    
    def _should_use_chunking(self, ai_provider: str, content_length: int) -> bool:
        """判斷是否需要使用分段處理（基於不同AI模型的特性）"""
        try:
            # 根據不同AI模型的實際上下文限制設置閾值（讓AI模型處理，不要攬過來）
            chunking_thresholds = {
                # OpenAI GPT 系列 - 根據實際上下文限制
                'openai': 96000,  # 128K tokens ≈ 96K 字符
                'gpt-4': 96000,  # GPT-4: 128K tokens
                'gpt-4o': 96000,  # GPT-4o: 128K tokens
                'gpt-4o-mini': 96000,  # GPT-4o-mini: 128K tokens
                'gpt-4-turbo': 96000,  # GPT-4 Turbo: 128K tokens
                'gpt-3.5-turbo': 12000,  # GPT-3.5: 16K tokens ≈ 12K 字符
                
                # Anthropic Claude 系列 - 根據實際上下文限制 (200K tokens ≈ 150K 字符)
                'anthropic': 150000,
                'claude': 150000,
                'claude-3': 150000,
                'claude-3-sonnet': 150000,
                'claude-3-haiku': 150000,
                'claude-3-opus': 150000,
                'claude-3-5-sonnet-20241022': 150000,  # Claude 3.5 Sonnet: 200K tokens
                'claude-3-5-haiku-20241022': 150000,  # Claude 3.5 Haiku: 200K tokens
                'claude-3-opus-20240229': 150000,  # Claude 3 Opus: 200K tokens
                
                # Google Gemini 系列 - 根據實際上下文限制
                'google': 1500000,
                'gemini': 1500000,
                'gemini-pro': 23000,  # Gemini Pro: 30K tokens ≈ 23K 字符
                'gemini-2.5-pro': 1500000,  # Gemini 2.5 Pro: 2M tokens
                'gemini-2.5-flash': 750000,  # Gemini 2.5 Flash: 1M tokens ≈ 750K 字符
                'gemini-2.0-flash': 1000000,  # Gemini 2.0 Flash: 1M tokens
                'gemini-2.0-flash-lite': 1000000,  # Gemini 2.0 Flash Lite: 1M tokens
                
                # xAI Grok 系列 - 根據實際上下文限制 (128K tokens ≈ 96K 字符)
                'xai': 96000,
                'grok': 96000,
                'grok-2': 96000,  # Grok-2: 128K tokens
                'grok-beta': 96000,  # Grok Beta: 128K tokens
                
                # Microsoft Copilot 系列 - 根據實際上下文限制 (128K tokens ≈ 96K 字符)
                'microsoft': 96000,
                'copilot': 96000,
                'copilot-gpt-4': 96000,  # Copilot GPT-4: 128K tokens
                'copilot-gpt-4-turbo': 96000,  # Copilot GPT-4 Turbo: 128K tokens
                
                # 預設閾值
                'default': 150000
            }
            
            # 獲取對應的閾值
            provider_key = ai_provider.lower() if ai_provider else 'default'
            threshold = chunking_thresholds.get(provider_key, chunking_thresholds['default'])
            
            # 檢查是否需要分段處理
            should_chunk = content_length > threshold
            
            if should_chunk:
                logger.info(f"AI模型 {ai_provider} 的內容長度 {content_length} 超過閾值 {threshold}，建議使用分段處理")
            else:
                logger.debug(f"AI模型 {ai_provider} 的內容長度 {content_length} 在閾值 {threshold} 內，使用單次處理")
            
            return should_chunk
            
        except Exception as e:
            logger.warning(f"判斷分段處理策略失敗: {e}")
            # 預設使用較保守的閾值
            return content_length > 30000
    
    def _simple_merge_pages(self, pages_data: List[Dict[str, Any]], file_type: str) -> str:
        """簡化的頁面合併邏輯"""
        merged = []
        for page_data in pages_data:
            if file_type == '.pdf':
                merged.append(f"=== 第 {page_data['page_number']} 頁 ===")
            else:
                merged.append(f"=== 段落 {page_data['page_number']} ===")
            merged.append(page_data['content'])
            merged.append("")  # 空行分隔
        
        return "\n".join(merged)
    
    def _should_attach_profile(self, prompt_template: str) -> bool:
        """讓使用者決定是否附加Profile"""
        try:
            from utils.settings_manager import SettingsManager
            settings = SettingsManager().get_all_settings()
            profile_strategy = settings.get('prompt', {}).get('profile_strategy', 'auto')
            
            if profile_strategy == 'never':
                return False
            elif profile_strategy == 'always':
                return True
            elif profile_strategy == 'auto':
                # 自動判斷：檢查提示詞是否已包含Profile資訊
                profile_indicators = ['profile', '配置', 'fields', '欄位', '結構', 'schema']
                # 使用更精確的匹配，避免部分匹配
                has_profile_info = any(f' {indicator}' in f' {prompt_template.lower()} ' for indicator in profile_indicators)
                return not has_profile_info
            else:
                return True  # 預設附加
        except Exception as e:
            logger.warning(f"檢查Profile策略失敗: {e}")
            return True  # 預設附加
    
    def _build_extraction_prompt_with_content(self, content: str, file_path: Path = None) -> str:
        """構建提取提示詞（使用內容替換策略）"""
        # 嚴格使用使用者指定的提示詞
        if not hasattr(self, 'user_prompt') or not self.user_prompt or self.user_prompt.strip() == '':
            raise ValueError("必須提供使用者提示詞。系統不會使用預設提示詞。")
        
        prompt_template = self.user_prompt
        
        # 處理佔位符：替換為實際內容，使用明確的分隔標記
        if "{{content}}" in prompt_template:
            # 明確告訴AI這不是提示詞，是文檔內容
            prompt = prompt_template.replace("{{content}}", f"\n\n【重要：以下不是提示詞，是要處理的文檔內容】\n{content}\n\n【文檔內容結束，請開始提取資料】")
            
            if "{{profile}}" in prompt:
                # 明確告訴AI這不是提示詞，是Profile配置
                prompt = prompt.replace("{{profile}}", f"\n\n【重要：以下不是提示詞，是Profile配置】\n{json.dumps(self.profile, ensure_ascii=False, indent=2)}\n\n【Profile配置結束】")
            
            # 在最後面附加完整內容
            prompt += f"\n\n【重要：以下不是提示詞，是Profile配置】\n{json.dumps(self.profile, ensure_ascii=False, indent=2)}\n\n【Profile配置結束】"
            prompt += f"\n\n【重要：以下不是提示詞，是要處理的文檔內容】\n{content}\n\n【文檔內容結束，請開始提取資料】"
        else:
            # 沒有佔位符時：在提示詞後面附加profile和content
            prompt = prompt_template
            prompt += f"\n\n【重要：以下不是提示詞，是Profile配置】\n{json.dumps(self.profile, ensure_ascii=False, indent=2)}\n\n【Profile配置結束】"
            prompt += f"\n\n【重要：以下不是提示詞，是要處理的文檔內容】\n{content}\n\n【文檔內容結束，請開始提取資料】"
        
        return prompt
        
    
    def _merge_chunk_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合併多個段落的結果"""
        merged = {}
        successful_results = [r for r in results if not r.get('_chunk_error')]
        
        logger.info(f"合併 {len(successful_results)}/{len(results)} 個成功段落的結果")
        
        # 合併所有原始響應
        raw_responses = []
        for result in results:
            if isinstance(result, dict) and not result.get('_chunk_error'):
                if '_raw_response' in result and result['_raw_response']:
                    raw_responses.append(result['_raw_response'])
        
        # 合併原始響應
        if raw_responses:
            merged['_raw_response'] = '\n\n--- 段落分隔線 ---\n\n'.join(raw_responses)
            logger.info(f"合併了 {len(raw_responses)} 個原始響應")
        
        # 收集所有成分表，用於去重
        all_ingredients = []
        
        for result in results:
            if isinstance(result, dict) and not result.get('_chunk_error'):
                for key, value in result.items():
                    if key.startswith('_') and key != '_raw_response':  # 跳過內部欄位，但保留 _raw_response
                        continue
                    
                    # 特殊處理成分表
                    if key == '成分表' and isinstance(value, list):
                        all_ingredients.extend(value)
                        continue
                        
                    if key not in merged:
                        merged[key] = value
                    elif isinstance(value, list) and isinstance(merged[key], list):
                        # 對於一般列表，合併
                        merged[key].extend(value)
                    elif isinstance(value, dict) and isinstance(merged[key], dict):
                        # 合併字典
                        merged[key].update(value)
                    elif value and not merged[key]:
                        # 如果原值為空，使用新值
                        merged[key] = value
        
        # 去重成分表
        if all_ingredients:
            unique_ingredients = self._deduplicate_ingredients(all_ingredients)
            merged['成分表'] = unique_ingredients
            logger.info(f"成分表去重：原始 {len(all_ingredients)} 個，去重後 {len(unique_ingredients)} 個")
        
        # 添加處理統計資訊
        merged['_processing_stats'] = {
            'total_chunks': len(results),
            'successful_chunks': len(successful_results),
            'failed_chunks': len(results) - len(successful_results)
        }
        
        return merged
    
    def _deduplicate_ingredients(self, ingredients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重成分表，基於INCI名稱和CAS號碼"""
        seen = set()
        unique_ingredients = []
        
        for ingredient in ingredients:
            if not isinstance(ingredient, dict):
                continue
                
            # 創建唯一標識符
            inci_name = ingredient.get('INCI名稱', '').strip().upper()
            cas_number = ingredient.get('CAS號碼', '').strip()
            
            # 使用INCI名稱作為主要標識符，CAS號碼作為輔助
            identifier = f"{inci_name}|{cas_number}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique_ingredients.append(ingredient)
            else:
                logger.debug(f"跳過重複成分: {inci_name} ({cas_number})")
        
        return unique_ingredients
    
    
    def _load_prompt_template(self, template_name: str) -> str:
        """載入提示詞模板"""
        prompt_file = Path("prompts") / f"{template_name}.md"
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"提示詞模板不存在: {prompt_file}")
            raise ValueError(f"必須提供有效的提示詞模板: {template_name}。系統不會使用預設提示詞。")
    
    def _get_default_prompt(self) -> str:
        """獲取預設提示詞"""
        return """
請從以下文檔內容中提取結構化資料，並以JSON格式輸出：

文檔內容：
{{content}}

請按照以下格式輸出：
{
  "基本資訊": {
    "標題": "文檔標題",
    "類型": "文檔類型"
  },
  "主要內容": {
    "摘要": "內容摘要",
    "關鍵資訊": "重要資訊"
  }
}
"""
    
    def _is_document_content_response(self, response: str) -> bool:
        """檢查AI是否忽略了提示，直接回應了文檔內容"""
        # 檢查是否包含文檔格式的關鍵字
        document_indicators = [
            # PDF相關
            'PDF', 'Portable Document Format', 'Adobe', 'Acrobat',
            # Word相關
            'Microsoft Word', 'DOCX', 'DOC', 'Office', 'Word Document',
            # 文檔結構相關
            'Page', 'Header', 'Footer', 'Table of Contents', 'Index',
            # 格式相關
            'Font', 'Size', 'Bold', 'Italic', 'Underline', 'Color',
            # 文檔內容相關
            'Document Properties', 'Metadata', 'Author', 'Title', 'Subject'
        ]
        
        # 檢查是否包含文檔格式的標記
        if any(indicator in response for indicator in document_indicators):
            return True
            
        # 檢查是否回應了原始文檔內容而非提取的結構化資料
        if len(response) > 5000 and not any(marker in response for marker in ['{', '}', 'json', '```']):
            return True
            
        return False
    
    def _is_file_output_response(self, response: str) -> bool:
        """檢查AI是否直接輸出了檔案（PDF/Word等）"""
        # 檢查是否包含檔案輸出的指示
        file_output_indicators = [
            # 直接檔案輸出指示
            '直接輸出PDF', '直接輸出Word', '生成PDF檔案', '生成Word檔案',
            '輸出PDF格式', '輸出Word格式', 'PDF檔案', 'Word檔案',
            '下載PDF', '下載Word', 'PDF下載', 'Word下載', '下載', 'download',
            # 檔案格式指示
            'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword', 'Content-Type: application/pdf', 'Content-Type: application/msword',
            # 二進制數據指示
            'base64', 'binary', 'binary data', '檔案數據', '檔案內容',
            # 檔案下載指示
            'attachment', '檔案下載', '下載檔案'
        ]
        
        # 檢查是否包含檔案輸出的關鍵字
        if any(indicator in response for indicator in file_output_indicators):
            return True
            
        # 檢查是否包含base64編碼的檔案數據
        if 'base64' in response and len(response) > 1000:
            return True
            
        # 檢查是否包含檔案格式的MIME類型
        if any(mime_type in response for mime_type in [
            'application/pdf', 'application/msword', 'application/vnd.openxmlformats'
        ]):
            return True
            
        return False
    
    def _extract_file_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """從AI回應中提取檔案"""
        try:
            import base64
            import re
            
            # 檢查是否包含base64編碼的檔案
            base64_match = re.search(r'base64[:\s]*([A-Za-z0-9+/=]+)', response, re.IGNORECASE)
            if base64_match:
                base64_data = base64_match.group(1)
                try:
                    file_data = base64.b64decode(base64_data)
                    
                    # 檢測檔案類型
                    file_type = self._detect_file_type(file_data)
                    
                    return {
                        'file_data': file_data,
                        'file_type': file_type,
                        'file_size': len(file_data),
                        'extraction_method': 'base64'
                    }
                except Exception as e:
                    logger.warning(f"Base64解碼失敗: {e}")
            
            # 檢查是否包含檔案下載連結
            download_match = re.search(r'(?:下載|download)[:\s]+([^\s]+\.(?:pdf|docx?|doc))', response, re.IGNORECASE)
            if download_match:
                file_path = download_match.group(1)
                return {
                    'file_path': file_path,
                    'file_type': self._get_file_type_from_extension(file_path),
                    'extraction_method': 'download_link'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"檔案提取失敗: {e}")
            return None
    
    def _detect_file_type(self, file_data: bytes) -> str:
        """檢測檔案類型"""
        # PDF檔案標記
        if file_data.startswith(b'%PDF'):
            return 'pdf'
        
        # Word檔案標記
        if file_data.startswith(b'PK') and b'word/' in file_data[:1000]:
            return 'docx'
        
        # 舊版Word檔案標記
        if file_data.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
            return 'doc'
        
        return 'unknown'
    
    def _get_file_type_from_extension(self, file_path: str) -> str:
        """從檔案副檔名獲取檔案類型"""
        ext = file_path.lower().split('.')[-1]
        if ext == 'pdf':
            return 'pdf'
        elif ext in ['docx', 'doc']:
            return 'docx' if ext == 'docx' else 'doc'
        return 'unknown'
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """解析AI回應"""
        try:
            import re
            
            # 記錄原始回應以便調試
            logger.info(f"AI原始回應長度: {len(response)} 字符")
            logger.info(f"AI原始回應前500字符: {response[:500]}...")
            
            # 檢查AI是否直接輸出了檔案
            if self._is_file_output_response(response):
                logger.info("📁 AI直接輸出了檔案，嘗試提取檔案")
                file_info = self._extract_file_from_response(response)
                if file_info:
                    logger.info(f"✅ 成功提取檔案，類型: {file_info['file_type']}, 大小: {file_info.get('file_size', 'unknown')}")
                    return {
                        '_file_output': True,
                        '_file_info': file_info,
                        '_raw_response': response,
                        '_extraction_method': 'file_output'
                    }
                else:
                    logger.warning("⚠️ 檢測到檔案輸出指示但無法提取檔案")
            
            # 檢查AI是否忽略了提示，直接回應了文檔內容
            if self._is_document_content_response(response):
                logger.warning("⚠️ AI忽略了提示，直接回應了文檔內容")
                raise Exception("AI忽略了提示，直接回應了文檔內容而非JSON格式。請檢查提示詞或嘗試其他AI模型。")
            
            # 首先嘗試直接解析整個回應
            try:
                parsed_data = json.loads(response)
                logger.info(f"✅ 直接JSON解析成功，數據結構: {list(parsed_data.keys())}")
                return parsed_data
            except json.JSONDecodeError as e:
                logger.warning(f"❌ 直接JSON解析失敗: {e}")
                logger.info(f"嘗試其他解析方法...")
            
            # 嘗試提取代碼塊中的JSON
            # 先移除代碼塊標記，然後提取JSON
            if '```json' in response:
                # 移除 ```json 和 ``` 標記
                json_start = response.find('```json') + 7
                json_end = response.rfind('```')
                if json_end > json_start:
                    json_str = response[json_start:json_end].strip()
                    try:
                        parsed_data = json.loads(json_str)
                        logger.info(f"✅ 代碼塊JSON解析成功，數據結構: {list(parsed_data.keys())}")
                        return parsed_data
                    except json.JSONDecodeError as e:
                        logger.warning(f"❌ 代碼塊JSON解析失敗: {e}")
                        logger.info(f"代碼塊內容前100字符: {json_str[:100]}...")
            elif '```' in response:
                # 處理沒有json標記的代碼塊
                json_start = response.find('```') + 3
                json_end = response.rfind('```')
                if json_end > json_start:
                    json_str = response[json_start:json_end].strip()
                    try:
                        parsed_data = json.loads(json_str)
                        logger.info(f"✅ 代碼塊JSON解析成功，數據結構: {list(parsed_data.keys())}")
                        return parsed_data
                    except json.JSONDecodeError as e:
                        logger.warning(f"❌ 代碼塊JSON解析失敗: {e}")
                        logger.info(f"代碼塊內容前100字符: {json_str[:100]}...")
            
            # 嘗試提取JSON對象（更寬鬆的匹配）
            # 使用更強的方法來匹配多層嵌套的JSON
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    parsed_data = json.loads(json_str)
                    logger.info(f"✅ JSON對象解析成功，數據結構: {list(parsed_data.keys())}")
                    return parsed_data
                except json.JSONDecodeError as e:
                    logger.warning(f"❌ JSON對象解析失敗: {e}")
                    logger.info(f"JSON對象內容前100字符: {json_str[:100]}...")
            
            # 如果所有JSON解析都失敗，嘗試創建一個基本的回應結構
            logger.warning("無法從AI回應中提取JSON，創建基本回應結構")
            
            # 檢查是否為GPT-4o的特殊回應格式（將提示詞當作JSON鍵名）
            if "處理結果" in response and any(keyword in response for keyword in [
                "你是一個專業的香水產品資訊檔案", "將AZMAN官方英文", "INCI", "關鍵", "所有", "Profile"
            ]):
                logger.warning("⚠️ 檢測到GPT-4o特殊回應格式，嘗試修復...")
                logger.warning(f"⚠️ GPT-4o回應內容: {response[:200]}...")
                
                # 這表明GPT-4o將提示詞內容當作了JSON鍵名
                # 我們需要創建一個空的回應結構，讓系統知道沒有提取到實際資料
                return {
                    "處理結果": {
                        "產品名稱": "",
                        "產品類別": "",
                        "產品劑型": "",
                        "產品用途": "",
                        "製造商名稱": "",
                        "製造商地址": "",
                        "製造商聯絡方式": "",
                        "輸入商名稱": "",
                        "輸入商地址": "",
                        "輸入商電話": "",
                        "原產地": "",
                        "容量": "",
                        "製造日期": "",
                        "有效期限": "",
                        "批號": "",
                        "使用部位": "",
                        "使用方式": "",
                        "適用對象": "",
                        "注意事項": "",
                        "安全評估結果": "",
                        "成分安全性": "",
                        "使用限制": "",
                        "成分表": [],
                        "主要成分": "",
                        "_raw_response": response,
                        "_parse_method": "gpt4o_error",
                        "_extraction_status": "failed",
                        "_error_reason": "GPT-4o將提示詞內容當作JSON鍵名，無法正確提取資料"
                    }
                }
            
            # 嘗試從回應中提取一些基本信息
            basic_info = {}
            
            # 提取產品名稱
            product_match = re.search(r'(?:產品名稱|Product Name)[:：]\s*(.+)', response, re.IGNORECASE)
            if product_match:
                basic_info['產品名稱'] = product_match.group(1).strip()
            
            # 提取製造商
            manufacturer_match = re.search(r'(?:製造業者|Manufacturer)[:：]\s*(.+)', response, re.IGNORECASE)
            if manufacturer_match:
                basic_info['製造業者'] = manufacturer_match.group(1).strip()
            
            # 如果找到任何基本信息，返回它們
            if basic_info:
                basic_info['_raw_response'] = response
                basic_info['_extraction_method'] = 'text_parsing'
                return basic_info
            
            # 直接拋出異常，不使用回退機制
            raise Exception(f"無法解析AI回應為JSON格式。原始回應: {response[:200]}...")
            
        except Exception as e:
            logger.error(f"AI回應解析失敗: {e}")
            logger.debug(f"AI回應內容: {response[:500]}...")
            # 直接拋出異常，不使用回退機制
            raise Exception(f"AI回應解析失敗: {e}")
    
    def _post_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """後處理提取的資料"""
        # 這裡可以添加資料清理、驗證等邏輯
        return data
    
    def learn_from_corrections(self, original_data: Dict[str, Any], 
                             corrected_data: Dict[str, Any]) -> bool:
        """
        從修正中學習
        
        Args:
            original_data: 原始提取資料
            corrected_data: 修正後的資料
            
        Returns:
            學習是否成功
        """
        try:
            # 分析差異
            differences = self._analyze_differences(original_data, corrected_data)
            
            # 更新Profile規則
            self.profile_manager.update_profile_from_learning(
                self.profile, differences
            )
            
            logger.info("學習完成，Profile已更新")
            return True
            
        except Exception as e:
            logger.error(f"學習失敗: {e}")
            return False
    
    def _analyze_differences(self, original: Dict[str, Any], 
                           corrected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析原始資料與修正資料的差異"""
        differences = []
        
        def compare_dict(orig: Dict, corr: Dict, path: str = ""):
            for key in corr:
                current_path = f"{path}.{key}" if path else key
                
                if key not in orig:
                    differences.append({
                        "type": "added",
                        "path": current_path,
                        "original": None,
                        "corrected": corr[key]
                    })
                elif isinstance(corr[key], dict) and isinstance(orig[key], dict):
                    compare_dict(orig[key], corr[key], current_path)
                elif orig[key] != corr[key]:
                    differences.append({
                        "type": "modified",
                        "path": current_path,
                        "original": orig[key],
                        "corrected": corr[key]
                    })
        
        compare_dict(original, corrected)
        return differences
    
    def _build_page_extraction_prompt(self, page_content: str, page_num: int, page_data: Dict[str, Any], file_path: Path = None) -> str:
        """構建單頁提取提示詞（統一使用檔名替換策略）"""
        # 統一使用檔名替換策略，避免直接嵌入內容
        filename = f"page_{page_num}"
        return self._build_extraction_prompt(page_content)
    
    def _identify_page_type(self, page_content: str, page_data: Dict[str, Any]) -> str:
        """識別頁面類型"""
        page_identification = self.profile.get('page_identification', {})
        
        for page_type, config in page_identification.items():
            keywords = config.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in page_content.lower():
                    return page_type
        
        return "general"
    
    def _merge_page_results(self, merged_result: Dict[str, Any], page_result: Dict[str, Any], page_num: int) -> Dict[str, Any]:
        """合併頁面結果"""
        if not merged_result:
            merged_result = page_result.copy()
            merged_result['_metadata'] = {
                'extraction_method': 'page_by_page',
                'total_pages': 0,
                'processed_pages': []
            }
        
        # 更新元資料
        if '_metadata' not in merged_result:
            merged_result['_metadata'] = {'extraction_method': 'page_by_page', 'total_pages': 0, 'processed_pages': []}
        
        merged_result['_metadata']['processed_pages'].append(page_num)
        merged_result['_metadata']['total_pages'] = len(merged_result['_metadata']['processed_pages'])
        
        # 合併資料欄位
        for key, value in page_result.items():
            if key == '_metadata':
                continue
                
            if key not in merged_result:
                merged_result[key] = value
            elif isinstance(value, list) and isinstance(merged_result[key], list):
                # 智能合併列表（特別處理成分表）
                if key == '成分表':
                    merged_result[key] = self._merge_ingredients(merged_result[key], value)
                else:
                    merged_result[key].extend(value)
            elif isinstance(value, dict) and isinstance(merged_result[key], dict):
                # 合併字典
                merged_result[key] = self._merge_dicts(merged_result[key], value)
            elif isinstance(value, str) and isinstance(merged_result[key], str):
                # 合併字串（避免重複，優先使用非空值）
                if value and value.strip() and (not merged_result[key] or not merged_result[key].strip()):
                    merged_result[key] = value
                elif value and value.strip() and value not in merged_result[key]:
                    merged_result[key] += f"\n{value}"
        
        return merged_result
    
    def _merge_ingredients(self, existing_ingredients: List[Dict[str, Any]], new_ingredients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """智能合併成分表，避免重複"""
        # 創建成分索引（基於INCI名稱和CAS號碼）
        ingredient_index = {}
        
        # 處理現有成分
        for ingredient in existing_ingredients:
            key = self._get_ingredient_key(ingredient)
            if key:
                ingredient_index[key] = ingredient
        
        # 處理新成分
        for ingredient in new_ingredients:
            key = self._get_ingredient_key(ingredient)
            if key:
                if key in ingredient_index:
                    # 合併現有成分（優先使用更完整的資料）
                    ingredient_index[key] = self._merge_ingredient_data(ingredient_index[key], ingredient)
                else:
                    # 添加新成分
                    ingredient_index[key] = ingredient
        
        # 返回去重後的成分列表
        return list(ingredient_index.values())
    
    def _get_ingredient_key(self, ingredient: Dict[str, Any]) -> str:
        """獲取成分的唯一鍵"""
        inci_name = ingredient.get('INCI名稱', '').strip().upper()
        cas_number = ingredient.get('CAS號碼', '').strip()
        
        if inci_name:
            return f"{inci_name}_{cas_number}" if cas_number else inci_name
        return ""
    
    def _merge_ingredient_data(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """合併成分資料，優先使用非空值"""
        merged = existing.copy()
        
        for key, value in new.items():
            if value and str(value).strip() and (not existing.get(key) or not str(existing.get(key)).strip()):
                merged[key] = value
            elif key == '功能' and value and str(value).strip():
                # 合併功能描述
                existing_func = existing.get(key, '')
                if existing_func and str(existing_func).strip():
                    if str(value).strip() not in str(existing_func):
                        merged[key] = f"{existing_func}, {value}"
                else:
                    merged[key] = value
        
        return merged
    
    def _merge_dicts(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """合併字典，優先使用非空值"""
        merged = existing.copy()
        
        for key, value in new.items():
            if value and str(value).strip() and (not existing.get(key) or not str(existing.get(key)).strip()):
                merged[key] = value
            elif isinstance(value, str) and isinstance(existing.get(key), str):
                # 合併字串
                existing_val = existing.get(key, '')
                if value.strip() and value.strip() not in existing_val:
                    merged[key] = f"{existing_val}\n{value}".strip()
        
        return merged
    
    def _select_important_pages(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """選擇重要頁面進行處理"""
        max_pages = self.profile.get('max_pages', 10)
        
        # 策略1: 基於Profile配置的頁面識別規則
        if self.profile.get('page_identification'):
            return self._select_pages_by_profile_rules(pages_data, max_pages)
        
        # 策略2: 基於內容密度的智能選擇
        return self._select_pages_by_content_density(pages_data, max_pages)
    
    def _select_pages_by_profile_rules(self, pages_data: List[Dict[str, Any]], max_pages: int) -> List[Dict[str, Any]]:
        """基於Profile規則選擇頁面"""
        page_identification = self.profile.get('page_identification', {})
        selected_pages = []
        
        # 按優先級處理頁面類型
        for page_type, config in sorted(page_identification.items(), key=lambda x: x[1].get('priority', 999)):
            keywords = config.get('keywords', [])
            
            for page_data in pages_data:
                if len(selected_pages) >= max_pages:
                    break
                    
                content = page_data.get('content', '').lower()
                if any(keyword.lower() in content for keyword in keywords):
                    if page_data not in selected_pages:
                        selected_pages.append(page_data)
        
        # 如果選中的頁面不足，補充前幾頁
        if len(selected_pages) < max_pages:
            for page_data in pages_data:
                if len(selected_pages) >= max_pages:
                    break
                if page_data not in selected_pages:
                    selected_pages.append(page_data)
        
        return selected_pages[:max_pages]
    
    def _select_pages_by_content_density(self, pages_data: List[Dict[str, Any]], max_pages: int) -> List[Dict[str, Any]]:
        """基於內容密度選擇頁面"""
        # 計算每頁的內容密度
        page_densities = []
        for page_data in pages_data:
            content = page_data.get('content', '')
            # 內容密度 = 文字長度 + 表格數量 + 關鍵詞密度
            density = len(content)
            
            # 檢查是否有表格
            if page_data.get('tables'):
                density += len(page_data['tables']) * 100
            
            # 檢查是否有結構化內容（如成分表）
            if any(keyword in content.lower() for keyword in ['成分', 'ingredients', 'cas', 'inci']):
                density += 200
            
            page_densities.append((density, page_data))
        
        # 按密度排序
        page_densities.sort(key=lambda x: x[0], reverse=True)
        
        # 選擇密度最高的頁面
        selected_pages = [page_data for _, page_data in page_densities[:max_pages]]
        
        return selected_pages
    
    def _calculate_page_importance(self, page_data: Dict[str, Any]) -> int:
        """計算頁面重要性分數"""
        content = page_data.get('content', '').lower()
        score = 0
        
        # 關鍵詞評分
        important_keywords = {
            '產品名稱': 10,
            'product name': 10,
            '成分': 8,
            'ingredients': 8,
            '製造業者': 7,
            'manufacturer': 7,
            '使用方法': 6,
            'usage': 6,
            '安全': 5,
            'safety': 5,
            'cas': 4,
            'inci': 4,
            '含量': 3,
            'concentration': 3
        }
        
        for keyword, points in important_keywords.items():
            if keyword in content:
                score += points
        
        # 頁面位置評分（前幾頁通常更重要）
        page_num = page_data.get('page_number', 0)
        if page_num <= 3:
            score += 5
        elif page_num <= 10:
            score += 2
        
        # 內容長度評分（內容越多可能越重要）
        content_length = len(content)
        if content_length > 500:
            score += 3
        elif content_length > 200:
            score += 1
        
        return score
    
    def _estimate_processing_cost(self, pages_data: List[Dict[str, Any]]) -> float:
        """估算處理成本（與前端計算邏輯一致）"""
        try:
            # 獲取當前AI模型的定價資訊
            ai_provider = getattr(self, 'ai_provider', 'openai')
            ai_model = getattr(self, 'ai_model', 'gpt-4o')
            
            # 根據AI模型獲取定價
            pricing_info = self._get_model_pricing(ai_provider, ai_model)
            input_cost_per_1k = pricing_info.get('input_per_1k', 0.03)
            output_cost_per_1k = pricing_info.get('output_per_1k', 0.06)
            
            total_input_tokens = 0
            total_output_tokens = 0
            
            for page_data in pages_data:
                content = page_data.get('content', '')
                if not content:
                    continue
                
                # 更準確的token估算：中文字符約1.8個token，英文字符約0.75個token
                chinese_chars = len([c for c in content if '\u4e00' <= c <= '\u9fff'])
                english_chars = len(content) - chinese_chars
                page_tokens = int(chinese_chars * 1.8 + english_chars * 0.75)
                
                # 輸出tokens估算：基於實際經驗，PIF轉換輸出通常是輸入的30-50%
                output_tokens = int(page_tokens * 0.4)
                
                total_input_tokens += page_tokens
                total_output_tokens += output_tokens
            
            # 添加系統提示詞和模板提示詞的估算
            system_prompt_tokens = 2000  # 系統提示詞約2000 tokens
            template_prompt_tokens = 1000  # 模板提示詞約1000 tokens
            total_system_tokens = system_prompt_tokens + template_prompt_tokens
            
            # 計算總成本
            total_input_tokens_with_system = total_input_tokens + total_system_tokens
            input_cost = (total_input_tokens_with_system / 1000) * input_cost_per_1k
            output_cost = (total_output_tokens / 1000) * output_cost_per_1k
            
            total_cost = input_cost + output_cost
            
            logger.debug(f"成本估算詳情: 輸入tokens={total_input_tokens_with_system}, 輸出tokens={total_output_tokens}, "
                        f"輸入成本=${input_cost:.4f}, 輸出成本=${output_cost:.4f}, 總成本=${total_cost:.4f}")
            
            return total_cost
            
        except Exception as e:
            logger.error(f"成本估算失敗: {e}")
            # 直接拋出異常，不使用回退機制
            raise Exception(f"成本估算失敗，請檢查AI模型設定或文檔內容: {e}")
    
    def _get_model_pricing(self, ai_provider: str, ai_model: str) -> Dict[str, float]:
        """獲取AI模型的定價資訊"""
        # 根據不同AI模型返回定價資訊
        pricing_map = {
            # OpenAI GPT 系列
            'gpt-4o': {'input_per_1k': 0.005, 'output_per_1k': 0.015},
            'gpt-4-turbo': {'input_per_1k': 0.01, 'output_per_1k': 0.03},
            'gpt-4': {'input_per_1k': 0.03, 'output_per_1k': 0.06},
            'gpt-3.5-turbo': {'input_per_1k': 0.0005, 'output_per_1k': 0.0015},
            
            # Claude 系列
            'claude-3-opus': {'input_per_1k': 0.015, 'output_per_1k': 0.075},
            'claude-3-sonnet': {'input_per_1k': 0.003, 'output_per_1k': 0.015},
            'claude-3-haiku': {'input_per_1k': 0.00025, 'output_per_1k': 0.00125},
            
            # Gemini 系列
            'gemini-2.5-pro': {'input_per_1k': 0.00125, 'output_per_1k': 0.01},
            'gemini-2.5-flash': {'input_per_1k': 0.0003, 'output_per_1k': 0.0025},
            'gemini-2.5-flash-lite': {'input_per_1k': 0.0001, 'output_per_1k': 0.0004},
            'gemini-2.0-flash': {'input_per_1k': 0.0001, 'output_per_1k': 0.0004},
            'gemini-2.0-flash-lite': {'input_per_1k': 0.000075, 'output_per_1k': 0.0003},
            'gemini-pro': {'input_per_1k': 0.0005, 'output_per_1k': 0.0015},
            
            # Grok 系列
            'grok-2': {'input_per_1k': 0.0003, 'output_per_1k': 0.001},
            'grok-beta': {'input_per_1k': 0.0002, 'output_per_1k': 0.0015},
            
            # Microsoft Copilot 系列
            'copilot-gpt-4': {'input_per_1k': 0.005, 'output_per_1k': 0.015},
            'copilot-gpt-4-turbo': {'input_per_1k': 0.01, 'output_per_1k': 0.03},
            
            # 預設定價
            'default': {'input_per_1k': 0.03, 'output_per_1k': 0.06}
        }
        
        # 嘗試匹配精確模型名稱
        if ai_model in pricing_map:
            return pricing_map[ai_model]
        
        # 嘗試匹配提供者
        provider_key = f"{ai_provider.lower()}-default"
        if provider_key in pricing_map:
            return pricing_map[provider_key]
        
        # 返回預設定價
        return pricing_map['default']
    
    def _post_process_results(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """後處理結果"""
        post_process_config = self.profile.get('post_process', {})
        
        if post_process_config.get('clean_text', False):
            result = self._clean_text_fields(result)
        
        if post_process_config.get('normalize_format', False):
            result = self._normalize_format(result)
        
        if post_process_config.get('validate_data', False):
            result = self._validate_data(result)
        
        if post_process_config.get('merge_similar_fields', False):
            result = self._merge_similar_fields(result)
        
        return result
    
    def _clean_text_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清理文字欄位"""
        for key, value in data.items():
            if isinstance(value, str):
                # 移除多餘空白
                data[key] = ' '.join(value.split())
            elif isinstance(value, dict):
                data[key] = self._clean_text_fields(value)
            elif isinstance(value, list):
                data[key] = [self._clean_text_fields(item) if isinstance(item, dict) else item for item in value]
        
        return data
    
    def _normalize_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """標準化格式"""
        # 這裡可以添加格式標準化邏輯
        return data
    
    def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """驗證資料"""
        # 這裡可以添加資料驗證邏輯
        return data
    
    def _merge_similar_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """合併相似欄位"""
        # 這裡可以添加欄位合併邏輯
        return data


