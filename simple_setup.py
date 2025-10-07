#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProDocuX 簡化啟動設定
不依賴GUI的設定介面
"""

import os
import sys
import json
from pathlib import Path

def show_welcome():
    """顯示歡迎訊息"""
    print("=" * 60)
    print("🚀 ProDocuX 初始設定")
    print("=" * 60)
    print("歡迎使用ProDocuX！")
    print("")
    print("📋 我們將一步步引導您完成初始設定，請按照提示操作：")
    print("   • 每個步驟都會有清楚的說明")
    print("   • 如果不知道如何選擇，可以使用預設選項")
    print("   • 設定完成後可以隨時在Web介面中修改")
    print("")
    input("按 Enter 鍵開始設定...")
    print()

def get_workspace_path():
    """獲取工作空間路徑"""
    print("📁 步驟 1/4: 工作空間設定")
    print("=" * 40)
    print("ProDocuX需要一個工作目錄來存放您的檔案和設定。")
    print("這個目錄將包含：")
    print("  • 上傳的文檔")
    print("  • 處理後的結果")
    print("  • 系統設定檔案")
    print("  • 學習資料")
    print()
    
    # 預設路徑
    documents_dir = Path.home() / "Documents"
    if not documents_dir.exists():
        documents_dir = Path.home() / "文檔"
    
    default_path = documents_dir / "ProDocuX_Workspace"
    print(f"💡 建議位置: {default_path}")
    print("   (這是您的文檔資料夾，方便找到)")
    print()
    
    while True:
        choice = input("是否使用建議位置？(y/n): ").lower().strip()
        if choice in ['y', 'yes', '是', '']:
            print(f"✅ 已選擇: {default_path}")
            return str(default_path)
        elif choice in ['n', 'no', '否']:
            print("請輸入自定義路徑（例如: C:\\MyDocuments\\ProDocuX）:")
            custom_path = input("路徑: ").strip()
            if custom_path:
                print(f"✅ 已選擇: {custom_path}")
                return custom_path
            else:
                print("❌ 路徑不能為空，請重新輸入")
        else:
            print("❌ 請輸入 y 或 n")
        print()

def get_ai_provider():
    """獲取AI提供者選擇"""
    print("\n🤖 步驟 2/4: AI提供者選擇")
    print("=" * 40)
    print("ProDocuX需要AI服務來處理您的文檔。")
    print("請選擇您有API金鑰的AI提供者：")
    print()
    print("1. OpenAI (ChatGPT)")
    print("   • 最受歡迎的AI服務")
    print("   • 功能強大，支援多種任務")
    print("   • 需要OpenAI API金鑰")
    print()
    print("2. Claude (Anthropic)")
    print("   • 擅長文檔分析和理解")
    print("   • 對中文支援良好")
    print("   • 需要Anthropic API金鑰")
    print()
    print("3. Gemini (Google)")
    print("   • Google的AI服務")
    print("   • 免費額度較大")
    print("   • 需要Google API金鑰")
    print()
    print("4. Grok (xAI)")
    print("   • 新興的AI服務")
    print("   • 價格相對便宜")
    print("   • 需要xAI API金鑰")
    print()
    print("5. Microsoft Copilot")
    print("   • 微軟的AI服務")
    print("   • 企業級安全性和合規性")
    print("   • 需要Azure OpenAI API金鑰")
    print()
    
    while True:
        choice = input("請選擇AI提供者 (1-5): ").strip()
        if choice == '1':
            print("✅ 已選擇: OpenAI")
            return 'openai'
        elif choice == '2':
            print("✅ 已選擇: Claude")
            return 'claude'
        elif choice == '3':
            print("✅ 已選擇: Gemini")
            return 'gemini'
        elif choice == '4':
            print("✅ 已選擇: Grok")
            return 'grok'
        elif choice == '5':
            print("✅ 已選擇: Microsoft Copilot")
            return 'microsoft'
        else:
            print("❌ 請輸入 1-5")
        print()

def get_api_keys(provider):
    """獲取API金鑰"""
    print(f"\n🔑 {provider.upper()} API金鑰設定")
    
    provider_info = {
        'openai': {
            'name': 'OpenAI',
            'urls': ['https://platform.openai.com/api-keys', 'https://iopena.com/'],
            'prefixes': ['sk-', 'iopena-']
        },
        'claude': {
            'name': 'Claude',
            'urls': ['https://console.anthropic.com/'],
            'prefixes': ['sk-ant-']
        },
        'gemini': {
            'name': 'Gemini',
            'urls': ['https://makersuite.google.com/app/apikey'],
            'prefixes': ['AI']
        },
        'grok': {
            'name': 'Grok',
            'urls': ['https://console.x.ai/', 'https://x.ai/'],
            'prefixes': ['xai-', 'grok-']
        },
        'microsoft': {
            'name': 'Microsoft Copilot',
            'urls': ['https://portal.azure.com/', 'https://azure.microsoft.com/services/cognitive-services/openai-service/'],
            'prefixes': ['sk-', 'azure-']
        }
    }
    
    info = provider_info.get(provider, {'name': provider.upper(), 'urls': [], 'prefixes': []})
    
    print(f"您可以在以下位置獲取{info['name']} API金鑰：")
    for url in info['urls']:
        print(f"• {url}")
    
    print()
    
    while True:
        api_key = input(f"請輸入您的{info['name']} API金鑰: ").strip()
        
        if not api_key:
            print("❌ API金鑰不能為空，請重新輸入")
            continue
        
        if len(api_key) < 10:
            print("❌ API金鑰格式不正確，請檢查後重新輸入")
            continue
        
        # 驗證API金鑰格式
        valid_format = False
        for prefix in info['prefixes']:
            if api_key.startswith(prefix):
                valid_format = True
                break
        
        if valid_format:
            print(f"✅ {info['name']} API金鑰格式正確")
            return api_key
        else:
            print("⚠️  API金鑰格式可能不正確，但仍會保存")
            confirm = input("確定要使用此API金鑰嗎？(y/n): ").lower().strip()
            if confirm in ['y', 'yes', '是', '']:
                return api_key

def get_shortcut_selection():
    """獲取快捷方式選擇"""
    print("\n🔗 桌面快捷方式設定")
    print("選擇要在桌面創建的快捷方式：")
    print()
    
    shortcuts = [
        ("workspace", "工作目錄", "開啟整個工作目錄"),
        ("input", "輸入資料夾", "快速存取輸入檔案"),
        ("output", "輸出資料夾", "快速存取處理結果"),
        ("template", "模板資料夾", "管理輸出模板")
    ]
    
    selected = []
    
    for key, name, desc in shortcuts:
        while True:
            choice = input(f"創建「{name}」快捷方式？({desc}) (y/n): ").lower().strip()
            if choice in ['y', 'yes', '是', '']:
                selected.append(key)
                break
            elif choice in ['n', 'no', '否']:
                break
            else:
                print("❌ 請輸入 y 或 n")
    
    return selected

def show_workspace_info(workspace_path, selected_shortcuts, ai_config):
    """顯示工作空間資訊"""
    print("\n📋 設定摘要")
    print("=" * 40)
    print(f"工作空間位置: {workspace_path}")
    print(f"AI提供者: {ai_config['provider'].upper()}")
    print(f"AI模型: {ai_config['model']}")
    print(f"API金鑰: {ai_config['api_key'][:8]}...{ai_config['api_key'][-4:]} (已隱藏)")
    print(f"快捷方式數量: {len(selected_shortcuts)} 個")
    
    if selected_shortcuts:
        print("將創建的快捷方式:")
        shortcut_names = {
            "workspace": "工作目錄",
            "input": "輸入資料夾", 
            "output": "輸出資料夾",
            "template": "模板資料夾"
        }
        
        for shortcut in selected_shortcuts:
            print(f"  • {shortcut_names.get(shortcut, shortcut)}")
    
    print("\n💡 提示:")
    print("• 工作目錄將存放所有ProDocuX的檔案和設定")
    print("• API金鑰已安全保存，可以隨時在設定中修改")
    print("• 可以隨時在設定中修改這些選項")
    print("• 快捷方式可以幫助您快速存取常用資料夾")
    print("• 建議MSDS轉PIF任務使用Claude模型")
    print()

def save_setup(workspace_path, selected_shortcuts, ai_config):
    """保存設定"""
    try:
        # 創建工作目錄
        workspace_dir = Path(workspace_path)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # 創建子目錄
        subdirs = ["input", "output", "templates", "cache", "profiles", "prompts"]
        for subdir in subdirs:
            (workspace_dir / subdir).mkdir(exist_ok=True)
        
        # 複製env_example.txt到工作空間並更新API金鑰
        env_example_file = Path(__file__).parent / "env_example.txt"
        env_file = workspace_dir / ".env"
        
        if env_example_file.exists():
            # 讀取範例檔案
            with open(env_example_file, 'r', encoding='utf-8') as f:
                env_content = f.read()
            
            # 替換API金鑰
            if ai_config['provider'] == 'openai':
                env_content = env_content.replace('your_openai_api_key_here', ai_config['api_key'])
                env_content = env_content.replace('your_iopenai_api_key_here', ai_config['api_key'])
            else:
                env_content = env_content.replace('your_openai_api_key_here', 'your_openai_api_key_here')
                env_content = env_content.replace('your_iopenai_api_key_here', 'your_iopenai_api_key_here')
            
            if ai_config['provider'] == 'claude':
                env_content = env_content.replace('your_claude_api_key_here', ai_config['api_key'])
            else:
                env_content = env_content.replace('your_claude_api_key_here', 'your_claude_api_key_here')
            
            if ai_config['provider'] == 'gemini':
                env_content = env_content.replace('your_gemini_api_key_here', ai_config['api_key'])
            else:
                env_content = env_content.replace('your_gemini_api_key_here', 'your_gemini_api_key_here')
            
            if ai_config['provider'] == 'grok':
                env_content = env_content.replace('your_grok_api_key_here', ai_config['api_key'])
            else:
                env_content = env_content.replace('your_grok_api_key_here', 'your_grok_api_key_here')
            
            if ai_config['provider'] == 'microsoft':
                env_content = env_content.replace('your_copilot_api_key_here', ai_config['api_key'])
            else:
                env_content = env_content.replace('your_copilot_api_key_here', 'your_copilot_api_key_here')
            
            # 更新模型設定
            if ai_config['provider'] == 'openai':
                env_content = env_content.replace('gpt-4', ai_config['model'])
            elif ai_config['provider'] == 'claude':
                env_content = env_content.replace('claude-3-sonnet-20240229', ai_config['model'])
            elif ai_config['provider'] == 'gemini':
                env_content = env_content.replace('gemini-pro', ai_config['model'])
            elif ai_config['provider'] == 'grok':
                env_content = env_content.replace('grok-beta', ai_config['model'])
            elif ai_config['provider'] == 'microsoft':
                env_content = env_content.replace('copilot-gpt-4', ai_config['model'])
            
            # 寫入.env檔案
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
        else:
            # 如果沒有範例檔案，創建基本.env檔案
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(f"""# ProDocuX 環境變數設定
# 此檔案由ProDocuX自動生成，請勿手動修改

# OpenAI API設定
OPENAI_API_KEY={'sk-your-key-here' if ai_config['provider'] != 'openai' else ai_config['api_key']}
IOPENAI_API_KEY={'sk-your-key-here' if ai_config['provider'] != 'openai' else ai_config['api_key']}

# Claude API設定
CLAUDE_API_KEY={'sk-ant-your-key-here' if ai_config['provider'] != 'claude' else ai_config['api_key']}

# Gemini API設定
GEMINI_API_KEY={'AI-your-key-here' if ai_config['provider'] != 'gemini' else ai_config['api_key']}

# Grok API設定
GROK_API_KEY={'grok-your-key-here' if ai_config['provider'] != 'grok' else ai_config['api_key']}

# Microsoft Copilot API設定
COPILOT_API_KEY={'copilot-your-key-here' if ai_config['provider'] != 'microsoft' else ai_config['api_key']}

# 模型設定
OPENAI_MODEL={ai_config['model'] if ai_config['provider'] == 'openai' else 'gpt-4o'}
CLAUDE_MODEL={ai_config['model'] if ai_config['provider'] == 'claude' else 'claude-3-5-sonnet-20241022'}
GEMINI_MODEL={ai_config['model'] if ai_config['provider'] == 'gemini' else 'gemini-2.5-pro'}
GROK_MODEL={ai_config['model'] if ai_config['provider'] == 'grok' else 'grok-2'}
COPILOT_MODEL={ai_config['model'] if ai_config['provider'] == 'microsoft' else 'copilot-gpt-4-turbo'}

# 其他設定
MAX_CHUNK_SIZE=8000
CONFIDENCE_THRESHOLD=0.7
""")
        
        # 保存設定檔案
        config = {
            "workspace_path": workspace_path,
            "selected_shortcuts": selected_shortcuts,
            "ai_provider": ai_config['provider'],
            "ai_model": ai_config['model'],
            "api_key_configured": True,
            "setup_completed": True
        }
        
        config_file = workspace_dir / "startup_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # 創建說明檔案
        create_readme(workspace_dir, selected_shortcuts)
        
        print("✅ 設定已保存完成！")
        return True
        
    except Exception as e:
        print(f"❌ 保存設定失敗: {e}")
        return False

def create_readme(workspace_dir, selected_shortcuts):
    """創建說明檔案"""
    try:
        from datetime import datetime
        
        readme_content = f"""# ProDocuX 工作目錄

這是ProDocuX的工作目錄，包含以下資料夾：

## 📁 目錄說明

- **input/** - 將要處理的檔案放在這裡
- **output/** - 處理完成的檔案會出現在這裡
- **templates/** - 輸出模板檔案
- **cache/** - 系統快取檔案（可忽略）
- **profiles/** - 提取規則配置
- **prompts/** - AI提示詞配置

## 🚀 使用方法

### 方法1：使用桌面快捷方式
桌面會自動創建以下快捷方式：
"""
        
        shortcut_names = {
            "workspace": "工作目錄",
            "input": "輸入資料夾",
            "output": "輸出資料夾", 
            "template": "模板資料夾"
        }
        
        for shortcut in selected_shortcuts:
            readme_content += f"- \"ProDocuX {shortcut_names.get(shortcut, shortcut)}\"\n"
        
        readme_content += f"""
### 方法2：手動開啟資料夾
1. 開啟檔案總管
2. 在地址欄輸入：{workspace_dir}
3. 進入對應的資料夾

### 方法3：從ProDocuX程式開啟
1. 啟動ProDocuX程式
2. 在Web介面中點擊「開啟資料夾」按鈕
3. 系統會自動開啟對應的資料夾

## ⚠️ 注意事項

- 請勿刪除此目錄中的系統檔案
- 定期清理 `cache/` 目錄以節省空間
- 重要檔案請及時從 `output/` 目錄移出
- 如果移動了工作目錄，請重新運行程式

---
ProDocuX v1.0.0
工作目錄創建時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
工作目錄路徑: {workspace_dir}
"""
        
        readme_file = workspace_dir / "README.txt"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
    except Exception as e:
        print(f"⚠️  創建說明檔案失敗: {e}")

def main():
    """主函數"""
    show_welcome()
    
    # 獲取工作空間路徑
    workspace_path = get_workspace_path()
    
    # 獲取AI提供者選擇
    provider = get_ai_provider()
    
    # 獲取API金鑰
    api_key = get_api_keys(provider)
    
    # 根據提供者選擇預設模型（選擇最新且平衡的版本）
    default_models = {
        'openai': 'gpt-4o',                    # 最新版本，性能好且相對便宜
        'claude': 'claude-3-5-sonnet-20241022', # 最新版本，文檔處理能力強
        'gemini': 'gemini-2.5-pro',            # 最新版本，免費額度大
        'grok': 'grok-2',                      # 最新版本
        'microsoft': 'copilot-gpt-4-turbo'     # Turbo版本，性價比更好
    }
    model = default_models.get(provider, 'gpt-4')
    
    ai_config = {
        'provider': provider,
        'model': model,
        'api_key': api_key
    }
    
    # 獲取快捷方式選擇
    selected_shortcuts = get_shortcut_selection()
    
    # 顯示設定摘要
    show_workspace_info(workspace_path, selected_shortcuts, ai_config)
    
    # 確認設定
    while True:
        choice = input("確認以上設定？(y/n): ").lower().strip()
        if choice in ['y', 'yes', '是', '']:
            break
        elif choice in ['n', 'no', '否']:
            print("重新設定...")
            return main()
        else:
            print("❌ 請輸入 y 或 n")
    
    # 保存設定
    if save_setup(workspace_path, selected_shortcuts, ai_config):
        print("\n🎉 設定完成！正在啟動ProDocuX...")
        
        # 設定環境變數
        os.environ['PRODOCUX_WORKSPACE'] = workspace_path
        os.environ['PRODOCUX_SHORTCUTS'] = ','.join(selected_shortcuts)
        os.environ['AI_PROVIDER'] = provider
        os.environ['AI_MODEL'] = model
        
        if provider == 'openai':
            os.environ['OPENAI_API_KEY'] = api_key
            os.environ['IOPENAI_API_KEY'] = api_key
        elif provider == 'claude':
            os.environ['CLAUDE_API_KEY'] = api_key
        elif provider == 'gemini':
            os.environ['GEMINI_API_KEY'] = api_key
        elif provider == 'grok':
            os.environ['GROK_API_KEY'] = api_key
        elif provider == 'microsoft':
            os.environ['COPILOT_API_KEY'] = api_key
        
        # 設定完成，提示用戶
        print("✅ 設定已保存到工作空間")
        print("🌐 請重新啟動ProDocuX以載入新設定")
        print("   或直接前往Web介面進行進階設定")
    else:
        print("❌ 設定失敗，請重新執行")

if __name__ == "__main__":
    from datetime import datetime
    main()
