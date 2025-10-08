#!/usr/bin/env python3
"""
創建簡單的 ICO 圖標
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_simple_icon():
    """創建簡單的 ProDocuX 圖標"""
    try:
        # 創建一個 256x256 的圖像
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 繪製背景圓角矩形
        margin = 20
        draw.rounded_rectangle(
            [margin, margin, size-margin, size-margin],
            radius=30,
            fill=(30, 60, 120, 255)  # 深藍色背景
        )
        
        # 繪製文檔圖標
        doc_width = 120
        doc_height = 150
        doc_x = (size - doc_width) // 2
        doc_y = (size - doc_height) // 2 - 10
        
        # 文檔背景
        draw.rectangle(
            [doc_x, doc_y, doc_x + doc_width, doc_y + doc_height],
            fill=(255, 255, 255, 255)
        )
        
        # 文檔折角
        corner_size = 30
        draw.polygon([
            (doc_x + doc_width - corner_size, doc_y),
            (doc_x + doc_width, doc_y),
            (doc_x + doc_width, doc_y + corner_size)
        ], fill=(200, 200, 200, 255))
        
        # 繪製文字 "P"
        try:
            # 嘗試使用系統字體
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            # 如果沒有字體，使用預設字體
            font = ImageFont.load_default()
        
        text = "P"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = doc_x + (doc_width - text_width) // 2
        text_y = doc_y + (doc_height - text_height) // 2
        
        draw.text((text_x, text_y), text, fill=(30, 60, 120, 255), font=font)
        
        # 保存為 ICO 格式
        script_dir = Path(__file__).parent
        ico_path = script_dir / "icon.ico"
        
        # 創建多個尺寸的圖標
        sizes = [16, 32, 48, 64, 128, 256]
        img.save(ico_path, format='ICO', sizes=[(s, s) for s in sizes])
        
        print(f"簡單圖標已創建: {ico_path}")
        return True
        
    except Exception as e:
        print(f"創建圖標失敗: {e}")
        return False

if __name__ == "__main__":
    create_simple_icon()
