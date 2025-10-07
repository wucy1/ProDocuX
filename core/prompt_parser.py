#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能提示詞解析器
解析使用者的質樸需求，轉化為精確的處理指令
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class FieldType(Enum):
    """欄位類型"""
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    LIST = "list"
    NUMBER = "number"
    DATE = "date"

class ProcessingAction(Enum):
    """處理動作"""
    EXTRACT = "extract"
    TRANSLATE = "translate"
    FORMAT = "format"
    REPLACE = "replace"
    COPY = "copy"

@dataclass
class FieldInstruction:
    """欄位處理指令"""
    field_name: str
    field_type: FieldType
    source_location: str  # 如 "第1頁", "第2頁第3段", "表格第2行"
    target_location: str  # 如 "模板第1頁", "模板第2頁第3欄"
    action: ProcessingAction
    translation_target: Optional[str] = None  # 翻譯目標語言
    format_rule: Optional[str] = None  # 格式化規則
    color_highlight: Optional[str] = None  # 著色標記

class IntelligentPromptParser:
    """智能提示詞解析器"""
    
    def __init__(self):
        self.field_patterns = {
            # 頁面引用模式
            r"第(\d+)頁": self._parse_page_reference,
            r"第(\d+)頁第(\d+)段": self._parse_page_paragraph_reference,
            r"第(\d+)頁第(\d+)行": self._parse_page_paragraph_reference,
            r"第(\d+)頁表格第(\d+)行": self._parse_page_table_reference,
            
            # 欄位引用模式
            r"(\w+)欄位": self._parse_field_reference,
            r"(\w+)部分": self._parse_section_reference,
            r"(\w+)區域": self._parse_area_reference,
            
            # 著色模式
            r"著色的(\w+)": self._parse_colored_field,
            r"標記的(\w+)": self._parse_marked_field,
            r"高亮的(\w+)": self._parse_highlighted_field,
            
            # 翻譯模式
            r"把(\w+)翻譯成(\w+)": self._parse_translation_instruction,
            r"(\w+)轉成(\w+)": self._parse_conversion_instruction,
            r"(\w+)保持(\w+)": self._parse_language_preservation,
        }
        
        self.action_keywords = {
            "取出": ProcessingAction.EXTRACT,
            "提取": ProcessingAction.EXTRACT,
            "拿": ProcessingAction.EXTRACT,
            "翻譯": ProcessingAction.TRANSLATE,
            "轉換": ProcessingAction.TRANSLATE,
            "替換": ProcessingAction.REPLACE,
            "換": ProcessingAction.REPLACE,
            "複製": ProcessingAction.COPY,
            "拷貝": ProcessingAction.COPY,
            "格式化": ProcessingAction.FORMAT,
            "整理": ProcessingAction.FORMAT,
        }
    
    def parse_user_prompt(self, prompt: str) -> List[FieldInstruction]:
        """
        解析使用者提示詞
        
        Args:
            prompt: 使用者輸入的提示詞
            
        Returns:
            解析後的欄位處理指令列表
        """
        instructions = []
        
        # 按句子分割
        sentences = self._split_sentences(prompt)
        
        for sentence in sentences:
            instruction = self._parse_sentence(sentence)
            if instruction:
                instructions.append(instruction)
        
        return instructions
    
    def _split_sentences(self, text: str) -> List[str]:
        """分割句子"""
        # 簡單的句子分割，可以根據需要改進
        sentences = re.split(r'[。！？；\n]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _parse_sentence(self, sentence: str) -> Optional[FieldInstruction]:
        """解析單個句子"""
        sentence = sentence.strip()
        
        # 嘗試匹配各種模式
        for pattern, parser_func in self.field_patterns.items():
            match = re.search(pattern, sentence)
            if match:
                try:
                    return parser_func(sentence, match)
                except Exception as e:
                    logger.warning(f"解析句子失敗: {sentence}, 錯誤: {e}")
                    continue
        
        # 嘗試解析動作指令
        return self._parse_action_instruction(sentence)
    
    def _parse_page_reference(self, sentence: str, match) -> FieldInstruction:
        """解析頁面引用：第X頁"""
        page_num = int(match.group(1))
        
        # 提取欄位名稱
        field_name = self._extract_field_name(sentence)
        
        return FieldInstruction(
            field_name=field_name or f"第{page_num}頁內容",
            field_type=FieldType.TEXT,
            source_location=f"第{page_num}頁",
            target_location="模板對應位置",
            action=ProcessingAction.EXTRACT
        )
    
    def _parse_page_paragraph_reference(self, sentence: str, match) -> FieldInstruction:
        """解析頁面段落引用：第X頁第Y段"""
        page_num = int(match.group(1))
        para_num = int(match.group(2))
        
        field_name = self._extract_field_name(sentence)
        
        return FieldInstruction(
            field_name=field_name or f"第{page_num}頁第{para_num}段",
            field_type=FieldType.TEXT,
            source_location=f"第{page_num}頁第{para_num}段",
            target_location="模板對應位置",
            action=ProcessingAction.EXTRACT
        )
    
    def _parse_page_table_reference(self, sentence: str, match) -> FieldInstruction:
        """解析頁面表格引用：第X頁表格第Y行"""
        page_num = int(match.group(1))
        row_num = int(match.group(2))
        
        field_name = self._extract_field_name(sentence)
        
        return FieldInstruction(
            field_name=field_name or f"第{page_num}頁表格第{row_num}行",
            field_type=FieldType.TABLE,
            source_location=f"第{page_num}頁表格第{row_num}行",
            target_location="模板對應位置",
            action=ProcessingAction.EXTRACT
        )
    
    def _parse_field_reference(self, sentence: str, match) -> FieldInstruction:
        """解析欄位引用：XXX欄位"""
        field_name = match.group(1)
        
        return FieldInstruction(
            field_name=field_name,
            field_type=FieldType.TEXT,
            source_location="文檔中搜尋",
            target_location="模板對應位置",
            action=ProcessingAction.EXTRACT
        )
    
    def _parse_colored_field(self, sentence: str, match) -> FieldInstruction:
        """解析著色欄位：著色的XXX"""
        field_name = match.group(1)
        
        return FieldInstruction(
            field_name=field_name,
            field_type=FieldType.TEXT,
            source_location="文檔中著色文字",
            target_location="模板對應位置",
            action=ProcessingAction.EXTRACT,
            color_highlight="colored"
        )
    
    def _parse_translation_instruction(self, sentence: str, match) -> FieldInstruction:
        """解析翻譯指令：把XXX翻譯成YYY"""
        field_name = match.group(1)
        target_lang = match.group(2)
        
        return FieldInstruction(
            field_name=field_name,
            field_type=FieldType.TEXT,
            source_location="文檔中搜尋",
            target_location="模板對應位置",
            action=ProcessingAction.TRANSLATE,
            translation_target=target_lang
        )
    
    def _parse_action_instruction(self, sentence: str) -> Optional[FieldInstruction]:
        """解析動作指令"""
        for keyword, action in self.action_keywords.items():
            if keyword in sentence:
                field_name = self._extract_field_name(sentence)
                if field_name:
                    return FieldInstruction(
                        field_name=field_name,
                        field_type=FieldType.TEXT,
                        source_location="文檔中搜尋",
                        target_location="模板對應位置",
                        action=action
                    )
        return None
    
    def _extract_field_name(self, sentence: str) -> Optional[str]:
        """從句子中提取欄位名稱"""
        # 移除常見的動詞和介詞
        cleaned = re.sub(r'[把從在到給讓使讓]', '', sentence)
        
        # 提取可能的欄位名稱
        field_candidates = re.findall(r'[\u4e00-\u9fff\w]+', cleaned)
        
        # 過濾掉常見的停用詞
        stop_words = {'的', '了', '是', '在', '有', '和', '與', '或', '但', '而', '所以', '因為', '如果', '當', '時', '候'}
        field_candidates = [word for word in field_candidates if word not in stop_words]
        
        return field_candidates[0] if field_candidates else None
    
    def generate_ai_prompt(self, instructions: List[FieldInstruction], 
                          document_content: str, template_info: str) -> str:
        """
        根據解析的指令生成AI提示詞
        
        Args:
            instructions: 欄位處理指令列表
            document_content: 文檔內容
            template_info: 模板資訊
            
        Returns:
            生成的AI提示詞
        """
        prompt_parts = [
            "你是一個專業的文檔處理專家，需要根據以下指令處理文檔：",
            "",
            "## 文檔內容",
            document_content,
            "",
            "## 模板資訊", 
            template_info,
            "",
            "## 處理指令"
        ]
        
        for i, instruction in enumerate(instructions, 1):
            prompt_parts.append(f"{i}. {self._format_instruction(instruction)}")
        
        prompt_parts.extend([
            "",
            "## 輸出要求",
            "請按照指令處理文檔，並以JSON格式輸出結果：",
            "{",
            "  \"處理結果\": {",
            "    \"欄位名稱\": \"提取的內容\",",
            "    \"...\": \"...\"",
            "  }",
            "}",
            "",
            "注意：",
            "- 如果找不到指定欄位，請輸出空字串",
            "- 需要翻譯的欄位請提供翻譯結果",
            "- 保持原始格式和結構"
        ])
        
        return "\n".join(prompt_parts)
    
    def _format_instruction(self, instruction: FieldInstruction) -> str:
        """格式化單個指令"""
        action_desc = {
            ProcessingAction.EXTRACT: "提取",
            ProcessingAction.TRANSLATE: "翻譯",
            ProcessingAction.REPLACE: "替換",
            ProcessingAction.COPY: "複製",
            ProcessingAction.FORMAT: "格式化"
        }
        
        desc = f"{action_desc[instruction.action]}「{instruction.field_name}」"
        desc += f"（來源：{instruction.source_location}）"
        
        if instruction.translation_target:
            desc += f"，翻譯成{instruction.translation_target}"
        
        if instruction.color_highlight:
            desc += f"，注意著色標記"
        
        return desc
    
    def _parse_section_reference(self, sentence: str, match) -> FieldInstruction:
        """解析區域引用：XXX區域"""
        field_name = match.group(1)
        
        return FieldInstruction(
            field_name=field_name,
            field_type=FieldType.TEXT,
            source_location="文檔中搜尋",
            target_location="模板對應位置",
            action=ProcessingAction.EXTRACT
        )
    
    def _parse_area_reference(self, sentence: str, match) -> FieldInstruction:
        """解析區域引用：XXX區域"""
        field_name = match.group(1)
        
        return FieldInstruction(
            field_name=field_name,
            field_type=FieldType.TEXT,
            source_location="文檔中搜尋",
            target_location="模板對應位置",
            action=ProcessingAction.EXTRACT
        )
    
    def _parse_marked_field(self, sentence: str, match) -> FieldInstruction:
        """解析標記欄位：標記的XXX"""
        field_name = match.group(1)
        
        return FieldInstruction(
            field_name=field_name,
            field_type=FieldType.TEXT,
            source_location="文檔中標記文字",
            target_location="模板對應位置",
            action=ProcessingAction.EXTRACT,
            color_highlight="marked"
        )
    
    def _parse_highlighted_field(self, sentence: str, match) -> FieldInstruction:
        """解析高亮欄位：高亮的XXX"""
        field_name = match.group(1)
        
        return FieldInstruction(
            field_name=field_name,
            field_type=FieldType.TEXT,
            source_location="文檔中高亮文字",
            target_location="模板對應位置",
            action=ProcessingAction.EXTRACT,
            color_highlight="highlighted"
        )
    
    def _parse_conversion_instruction(self, sentence: str, match) -> FieldInstruction:
        """解析轉換指令：XXX轉成YYY"""
        field_name = match.group(1)
        target_format = match.group(2)
        
        return FieldInstruction(
            field_name=field_name,
            field_type=FieldType.TEXT,
            source_location="文檔中搜尋",
            target_location="模板對應位置",
            action=ProcessingAction.FORMAT,
            format_rule=target_format
        )
    
    def _parse_language_preservation(self, sentence: str, match) -> FieldInstruction:
        """解析語言保持指令：XXX保持YYY"""
        field_name = match.group(1)
        language = match.group(2)
        
        return FieldInstruction(
            field_name=field_name,
            field_type=FieldType.TEXT,
            source_location="文檔中搜尋",
            target_location="模板對應位置",
            action=ProcessingAction.COPY
        )
