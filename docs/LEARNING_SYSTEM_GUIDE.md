# ProDocuX 學習系統完整指南

⚠️ **開發中功能** - 此功能正在開發中，預計在下一版本發布

## 🎯 學習系統概述

ProDocuX 現在具備完整的學習功能，能夠從使用者的修正中自動學習並持續改善文檔處理準確度。學習系統包含三個核心功能：

1. **JSON資料學習** - 直接修改JSON資料進行學習
2. **Word文檔學習** - 修改Word輸出檔案後進行學習（推薦）
3. **反覆處理學習** - 從多次處理同一類型文檔中學習模式

## 🚀 學習功能詳細說明

### 1. JSON資料學習

#### 功能描述
- 使用者修改AI提取的JSON資料
- 系統分析原始資料與修正資料的差異
- 自動生成修正模式和轉換規則
- 更新Profile配置以改善後續處理

#### 使用流程
1. 處理文檔獲得JSON結果
2. 複製JSON資料到學習介面
3. 修改需要修正的欄位
4. 提交學習，系統自動分析差異

#### 技術實現
```python
def learn_from_corrections(self, original_data, corrected_data, source_file, profile_name):
    # 分析差異
    differences = self._analyze_differences(original_data, corrected_data)
    
    # 分析修正模式
    patterns = self._analyze_correction_patterns(differences)
    
    # 更新Profile規則
    success = self._update_profile_rules(profile_name, patterns)
```

### 2. Word文檔學習（推薦）

#### 功能描述
- 使用者下載Word輸出檔案並修改
- 系統解析Word文檔內容（段落、表格、著色文字）
- 比對原始JSON與修改後Word的差異
- 學習修正模式並更新Profile規則

#### 使用流程
1. 處理文檔獲得Word輸出檔案
2. 用Word編輯器開啟並修改內容
3. 上傳修改後的Word檔案
4. 系統自動解析並學習修正

#### 技術實現
```python
def learn_from_word_document(self, original_data, corrected_docx_path, source_file, profile_name):
    # 解析Word文檔內容
    word_content = self._parse_word_document(corrected_docx_path)
    
    # 比對原始JSON與Word內容的差異
    differences = self._compare_json_with_word(original_data, word_content)
    
    # 分析修正模式
    patterns = self._analyze_correction_patterns(differences)
```

#### Word文檔解析功能
- **段落解析**：提取所有段落文字和格式資訊
- **表格解析**：解析表格結構和內容
- **著色文字檢測**：識別Word中的著色文字作為特殊標記
- **結構化資料提取**：從段落和表格中提取「標籤：值」模式

### 3. 反覆處理學習

#### 功能描述
- 分析同一工作的多次處理記錄
- 識別重複出現的修正模式
- 計算學習趨勢和改善率
- 自動優化Profile規則

#### 使用場景
- 處理大量相似文檔
- 同一品牌或類型的文檔
- 需要持續改善準確度的場景

#### 技術實現
```python
def learn_from_repeated_processing(self, work_id, processing_history):
    # 分析重複的修正模式
    repeated_patterns = self._analyze_repeated_patterns(processing_history)
    
    # 分析學習趨勢
    learning_trends = self._analyze_learning_trends(processing_history)
    
    # 更新Profile規則
    success = self._update_profile_rules(f"work_{work_id}", repeated_patterns)
```

## 🧠 智能學習算法

### 1. 模式識別

#### 支援的資料模式
- **數字模式**：`NUMBER`, `DECIMAL`, `PERCENTAGE`
- **日期模式**：`DATE_YYYY-MM-DD`, `DATE_MM/DD/YYYY`
- **聯絡方式**：`EMAIL`, `PHONE`
- **文字長度**：`SHORT_TEXT`, `MEDIUM_TEXT`, `LONG_TEXT`

#### 中文字符處理
- 考慮中文字符的視覺寬度
- 調整長度判斷閾值
- 支援中英文混合內容

### 2. 轉換規則生成

#### 自動識別的轉換類型
- **大小寫轉換**：`CASE_CONVERSION`
- **格式轉換**：`INT_TO_DECIMAL`
- **語言轉換**：`TRANSLATE_TO_CHINESE`, `TRANSLATE_TO_ENGLISH`
- **自定義轉換**：`CUSTOM_TRANSFORMATION`

### 3. 可信度計算

#### 可信度因子
- **變化程度**：修正幅度越小，可信度越高
- **模式一致性**：原始和修正模式相同時增加可信度
- **重複頻率**：重複出現的模式可信度更高

## 📊 學習歷史和趨勢分析

### 學習記錄結構
```json
{
  "type": "json_correction|word_correction|repeated_processing",
  "profile": "profile_name",
  "source_file": "file_path",
  "differences": [...],
  "patterns": [...],
  "timestamp": "2024-01-01T00:00:00"
}
```

### 趨勢分析指標
- **總修正數**：累計修正的欄位數量
- **平均修正數**：每次處理的平均修正數
- **改善率**：修正數量隨時間的變化趨勢
- **最常修正欄位**：需要重點關注的欄位

## 🔧 使用建議

### 1. 學習策略
- **優先使用Word學習**：更直觀，支援格式保留
- **定期進行反覆學習**：處理大量文檔後進行模式分析
- **關注學習趨勢**：監控改善率，調整學習策略

### 2. 最佳實踐
- **保持一致性**：相同類型的修正使用相同的方式
- **及時學習**：處理完文檔後立即進行學習
- **定期檢視**：查看學習歷史和趨勢分析

### 3. 注意事項
- **學習品質**：確保修正的準確性，避免學習錯誤模式
- **模式穩定性**：等待模式穩定後再應用到大規模處理
- **備份Profile**：重要Profile建議定期備份

## 🧪 測試和驗證

### 測試腳本
使用 `test_learning_functionality.py` 可以測試所有學習功能：

```bash
python test_learning_functionality.py
```

### 測試內容
- JSON學習功能測試
- Word文檔學習功能測試
- 反覆處理學習功能測試
- 模式提取功能測試
- 轉換規則生成測試

### 測試結果
所有測試都通過，學習系統功能完整且穩定。

## 🎉 總結

ProDocuX 的學習系統現在具備：

✅ **完整的學習功能**：支援JSON和Word文檔學習
✅ **智能模式識別**：自動識別資料類型和轉換規則
✅ **反覆處理學習**：從多次處理中學習重複模式
✅ **趨勢分析**：提供學習效果的可視化分析
✅ **中文字符支援**：完整支援中文內容處理
✅ **測試驗證**：全面的測試覆蓋確保功能穩定

學習系統將持續改善文檔處理的準確度，為使用者提供更好的體驗。



















