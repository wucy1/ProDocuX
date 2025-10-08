#!/usr/bin/env python3
"""
將 PNG 圖標轉換為 ICO 格式
"""

from PIL import Image
import os
from pathlib import Path

def convert_png_to_ico(png_path, ico_path, sizes=[16, 32, 48, 64, 128, 256]):
    """將 PNG 轉換為 ICO 格式"""
    try:
        # 打開 PNG 圖片
        img = Image.open(png_path)
        
        # 創建 ICO 圖標，包含多個尺寸
        img.save(ico_path, format='ICO', sizes=[(size, size) for size in sizes])
        
        print(f"圖標轉換成功: {png_path} -> {ico_path}")
        return True
        
    except Exception as e:
        print(f"圖標轉換失敗: {e}")
        return False

def main():
    # 設定路徑
    script_dir = Path(__file__).parent
    png_path = script_dir.parent / "web" / "static" / "images" / "logo.png"
    ico_path = script_dir / "icon.ico"
    
    # 檢查 PNG 檔案是否存在
    if not png_path.exists():
        print(f"PNG 檔案不存在: {png_path}")
        return False
    
    # 轉換圖標
    success = convert_png_to_ico(png_path, ico_path)
    
    if success:
        print(f"ICO 檔案已創建: {ico_path}")
        print(f"檔案大小: {ico_path.stat().st_size} bytes")
    
    return success

if __name__ == "__main__":
    main()
