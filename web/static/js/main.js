// ProDocuX 主要JavaScript RC1

class ProDocuX {
    constructor() {
        this.uploadedFiles = [];
        this.currentFileId = null;
        this.currentWork = null;
        this.works = []; // 工作列表
        this.selectedPagesMap = {}; // 每個檔案的頁面選擇 {fileId: [pageNumbers]}
        this.pagePreviewData = {}; // 頁面預覽資料 {fileId: {pages: [...]}}
        this.workflowPreferences = {}; // 工作流程偏好設定
        this.currentLanguage = 'en'; // 當前語言
        this.translations = {}; // 翻譯資料
        
        // 設置全域 currentLang 變數
        window.currentLang = this.currentLanguage;
        this.initAsync();
    }
    
    async initAsync() {
        await this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.detectLanguageFromURL();
        await this.loadTranslations();
        this.loadWorks();
        this.loadProfiles();
        this.loadAIOptions();
        
        // 檢查關鍵 DOM 元素是否存在
        this.checkDOMElements();
    }

    // 國際化相關方法
    async detectLanguageFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const urlLang = urlParams.get('lang');
        if (urlLang && ['zh_TW', 'en'].includes(urlLang)) {
            this.currentLanguage = urlLang;
            window.currentLang = urlLang; // 更新全域變數
        } else {
            // 如果URL沒有語言參數，嘗試從session獲取
            try {
                const response = await fetch('/api/language');
                const data = await response.json();
                if (data.language && ['zh_TW', 'en'].includes(data.language)) {
                    this.currentLanguage = data.language;
                    window.currentLang = data.language; // 更新全域變數
                }
            } catch (error) {
                console.log('無法從session獲取語言，使用預設語言:', this.currentLanguage);
            }
        }
    }

    async loadTranslations() {
        try {
            const response = await fetch(`/api/i18n/${this.currentLanguage}`);
            if (response.ok) {
                this.translations = await response.json();
                this.updateUI();
            }
        } catch (error) {
            console.error('載入翻譯失敗:', error);
        }
    }

    async switchLanguage(lang) {
        try {
            const response = await fetch('/api/language', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ language: lang })
            });
            
            if (response.ok) {
                this.currentLanguage = lang;
                window.currentLang = lang; // 更新全域變數
                await this.loadTranslations();
                // 更新URL參數
                const url = new URL(window.location);
                url.searchParams.set('lang', lang);
                window.history.replaceState({}, '', url);
            }
        } catch (error) {
            console.error('語言切換失敗:', error);
        }
    }

    updateUI() {
        // 更新所有帶有 data-i18n 屬性的元素
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.getTranslation(key);
            if (translation) {
                if (element.tagName === 'INPUT' && element.type === 'text') {
                    element.placeholder = translation;
                } else {
                    element.textContent = translation;
                }
            }
        });
        
        // 更新所有帶有 data-i18n-placeholder 屬性的元素
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            const translation = this.getTranslation(key);
            if (translation) {
                element.placeholder = translation;
            }
        });
        
        // 更新頁面標題
        const titleElement = document.querySelector('title[data-i18n]');
        if (titleElement) {
            const translation = this.getTranslation('app.title');
            if (translation) {
                document.title = translation;
            }
        }
    }

    getTranslation(key) {
        const keys = key.split('.');
        let value = this.translations;
        for (const k of keys) {
            value = value?.[k];
        }
        return value || key;
    }

    checkDOMElements() {
        // 檢查關鍵 DOM 元素是否存在
        const criticalElements = [
            'costEstimateContainer',
            'estimatedTokens',
            'estimatedCost',
            'estimatedTime',
            'fileSize',
            'aiModel',
            'profileName'
        ];
        
        const missingElements = [];
        criticalElements.forEach(id => {
            const element = document.getElementById(id);
            if (!element) {
                missingElements.push(id);
            }
        });
        
        if (missingElements.length > 0) {
            console.warn('缺少關鍵 DOM 元素:', missingElements);
            console.log('當前頁面版本:', document.title);
            console.log('頁面載入時間:', new Date().toLocaleString());
        } else {
            console.log('✅ 所有關鍵 DOM 元素都存在');
        }
    }

    setupEventListeners() {
        // 語言切換
        const langBtn = document.getElementById('langBtn');
        const langDropdown = document.getElementById('langDropdown');
        
        if (langBtn && langDropdown) {
            langBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                langDropdown.style.display = langDropdown.style.display === 'block' ? 'none' : 'block';
            });
            
            langDropdown.addEventListener('click', (e) => {
                e.stopPropagation();
                const lang = e.target.getAttribute('data-lang');
                if (lang) {
                    this.switchLanguage(lang);
                    langDropdown.style.display = 'none';
                }
            });
            
            // 點擊其他地方關閉下拉選單
            document.addEventListener('click', () => {
                langDropdown.style.display = 'none';
            });
        }

        // 檔案上傳
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');

        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
            console.log('檔案選擇事件監聽器已綁定');
        } else {
            console.error('找不到檔案輸入元素 #fileInput');
        }
        
        if (uploadArea) {
            // 拖拽上傳
            uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
            uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
            uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
            console.log('拖拽上傳事件監聽器已綁定');
        } else {
            console.error('找不到上傳區域元素 #uploadArea');
        }

        // 從 input 載入
        const importFromInputBtn = document.getElementById('importFromInputBtn');
        if (importFromInputBtn) {
            importFromInputBtn.addEventListener('click', () => this.openImportFromInput());
        }

        // 處理按鈕
        document.getElementById('processBtn').addEventListener('click', () => this.processDocument());
        document.getElementById('estimateBtn').addEventListener('click', () => this.estimateCost());
        document.getElementById('downloadBtn').addEventListener('click', () => this.downloadResult());
        // 學習功能暫時停用
        // document.getElementById('learnBtn').addEventListener('click', () => this.showLearnModal());
        
        // 工作選擇
        document.getElementById('workSelect').addEventListener('change', (e) => this.selectWork(e.target.value));
        
        // 偏好設定自動保存
        this.setupPreferenceAutoSave();
    }

    async loadWorks() {
        try {
            console.log('開始載入工作列表...');
            const response = await fetch('/api/works');
            console.log('API 響應狀態:', response.status, response.statusText);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('工作列表 API 響應:', data);
            
            if (data.success) {
                this.works = data.works || [];
                console.log('設置 works 數組:', this.works);
                console.log('works 數組類型:', typeof this.works, '是否為數組:', Array.isArray(this.works));
                this.updateWorkSelect();
                console.log('工作列表載入完成，共', this.works.length, '個工作');
            } else {
                console.error('工作列表 API 返回錯誤:', data.error);
                this.works = [];
                this.updateWorkSelect();
            }
        } catch (error) {
            console.error('載入工作列表失敗:', error);
            this.works = [];
            this.updateWorkSelect();
        }
    }

    async openImportFromInput() {
        try {
            const res = await fetch('/api/input/list');
            const data = await res.json();
            if (!data.success) {
                const errorMsg = data.error || (currentLang === 'en' ? 'Unable to get input directory file list' : '無法取得 input 目錄檔案清單');
                this.showError(errorMsg);
                return;
            }

            if (!data.files || data.files.length === 0) {
                const warningMsg = currentLang === 'en' ? 'No available files in input directory' : 'input 目錄沒有可用檔案';
                showNotification(warningMsg, 'warning');
                return;
            }

            // 簡易選擇介面（prompt）；之後可改成 modal 多選
            const names = data.files.map(f => f.name).join('\n');
            const promptText = currentLang === 'en' 
                ? `Please enter the filenames to import (multiple separated by commas):\n\n${names}`
                : `請輸入要匯入的檔名（多個以逗號分隔）：\n\n${names}`;
            const pick = prompt(promptText);
            if (pick === null) return;
            const selected = pick.split(',').map(s => s.trim()).filter(Boolean);
            if (selected.length === 0) return;

            const res2 = await fetch('/api/input/import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filenames: selected })
            });
            const data2 = await res2.json();
            if (!data2.success) {
                const errorMsg = data2.error || (currentLang === 'en' ? 'Import failed' : '匯入失敗');
                this.showError(errorMsg);
                return;
            }

            // 將匯入檔加入 uploadedFiles
            (data2.files || []).forEach(f => {
                this.uploadedFiles.push({ id: f.file_id, name: f.filename, size: f.size || 0, path: f.file_path });
            });
            this.updateFileList();
            this.updateProcessButton();
            const successMsg = currentLang === 'en' 
                ? `Successfully imported ${data2.files.length} files`
                : `已匯入 ${data2.files.length} 個檔案`;
            showNotification(successMsg, 'success');
        } catch (e) {
            console.error(e);
            const errorMsg = currentLang === 'en' 
                ? 'Import error: ' + e.message
                : '匯入發生錯誤: ' + e.message;
            this.showError(errorMsg);
        }
    }
    
    updateWorkSelect() {
        const workSelect = document.getElementById('workSelect');
        if (!workSelect) {
            console.error('找不到 workSelect 元素');
            return;
        }
        
        workSelect.innerHTML = '<option value="" data-i18n="placeholders.selectOrCreateWork">請選擇或創建新工作...</option>';
        
        console.log('更新工作選擇下拉選單，works 數組:', this.works);
        console.log('works 長度:', this.works ? this.works.length : 'undefined');
        
        if (this.works && Array.isArray(this.works)) {
            this.works.forEach((work, index) => {
                console.log(`工作 ${index}:`, work);
                const option = document.createElement('option');
                option.value = work.id;
                option.textContent = `${work.name} (${work.type})`;
                // 將完整的工作資料存儲到dataset中
                option.dataset.workData = JSON.stringify(work);
                workSelect.appendChild(option);
            });
            console.log(`已添加 ${this.works.length} 個工作選項到下拉選單`);
        } else {
            console.warn('works 不是有效的數組:', this.works);
        }
        
        // 重新應用翻譯到新創建的元素
        this.updateUI();
    }
    
    async loadProfiles() {
        try {
            const response = await fetch('/api/profiles');
            const data = await response.json();
            
            if (data.success) {
                this.profiles = data.profiles;
                this.updateProfileSelect();
            } else {
                console.error('載入Profile失敗:', data.error);
            }
        } catch (error) {
            console.error('載入Profile失敗:', error);
        }
    }
    
    async loadAIOptions() {
        try {
            const response = await fetch('/api/settings');
            const data = await response.json();
            
            if (data.success) {
                const settings = data.settings;
                this.populateAIProviders(settings);
                this.populateAIModels(settings);
            }
        } catch (error) {
            console.error('載入AI選項失敗:', error);
        }
    }

    populateAIProviders(settings) {
        const providerSelect = document.getElementById('workflowAiProvider');
        if (!providerSelect) return;

        // 清空現有選項
        providerSelect.innerHTML = '<option value="" data-i18n="settings.useDefault">使用預設設定</option>';

        // 檢查哪些提供者有API金鑰
        const apiKeys = {
            'openai': settings.openai_api_key || '',
            'claude': settings.claude_api_key || '',
            'gemini': settings.gemini_api_key || '',
            'grok': settings.grok_api_key || '',
            'microsoft': settings.microsoft_api_key || ''
        };

        const providerNames = {
            'openai': 'OpenAI (ChatGPT)',
            'claude': 'Claude (Anthropic)',
            'gemini': 'Gemini (Google)',
            'grok': 'Grok (xAI)',
            'microsoft': 'Microsoft Copilot'
        };

        // 只添加有API金鑰的提供者
        Object.keys(apiKeys).forEach(provider => {
            if (apiKeys[provider].trim()) {
                const option = document.createElement('option');
                option.value = provider;
                option.textContent = providerNames[provider];
                providerSelect.appendChild(option);
            }
        });

        // 如果沒有任何API金鑰，顯示提示
        if (providerSelect.children.length === 1) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = currentLang === 'en' ? 'Please configure API keys in settings first' : '請先在設定中配置API金鑰';
            option.disabled = true;
            providerSelect.appendChild(option);
        }
        
        // 重新應用翻譯到新創建的元素
        this.updateUI();
    }

    populateAIModels(settings) {
        const modelSelect = document.getElementById('workflowAiModel');
        if (!modelSelect) return;

        // 清空現有選項
        modelSelect.innerHTML = '<option value="" data-i18n="settings.useDefault">使用預設設定</option>';

        // 模型選項配置
        const modelOptions = {
            'openai': [
                { value: 'gpt-4o', text: 'GPT-4o' },
                { value: 'gpt-4o-mini', text: 'GPT-4o Mini' },
                { value: 'gpt-4-turbo', text: 'GPT-4 Turbo' },
                { value: 'gpt-3.5-turbo', text: 'GPT-3.5 Turbo' }
            ],
            'claude': [
                { value: 'claude-3-5-sonnet-20241022', text: 'Claude 3.5 Sonnet' },
                { value: 'claude-3-5-haiku-20241022', text: 'Claude 3.5 Haiku' },
                { value: 'claude-3-opus-20240229', text: 'Claude 3 Opus' }
            ],
            'gemini': [
                { value: 'gemini-2.5-pro', text: 'Gemini 2.5 Pro' },
                { value: 'gemini-2.5-flash', text: 'Gemini 2.5 Flash' },
                { value: 'gemini-2.5-flash-lite', text: 'Gemini 2.5 Flash Lite' },
                { value: 'gemini-2.0-flash', text: 'Gemini 2.0 Flash' },
                { value: 'gemini-2.0-flash-lite', text: 'Gemini 2.0 Flash Lite' },
                { value: 'gemini-pro', text: 'Gemini Pro' }
            ],
            'grok': [
                { value: 'grok-2', text: 'Grok-2' },
                { value: 'grok-beta', text: 'Grok Beta' }
            ],
            'microsoft': [
                { value: 'copilot-gpt-4', text: 'Copilot GPT-4' },
                { value: 'copilot-gpt-4-turbo', text: 'Copilot GPT-4 Turbo' }
            ]
        };

        // 根據當前選擇的提供者更新模型選項
        const selectedProvider = document.getElementById('workflowAiProvider').value;
        if (selectedProvider && modelOptions[selectedProvider]) {
            modelOptions[selectedProvider].forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.text;
                modelSelect.appendChild(optionElement);
            });
        }
        
        // 重新應用翻譯到新創建的元素
        this.updateUI();
    }

    updateWorkflowModelOptions() {
        const providerSelect = document.getElementById('workflowAiProvider');
        const modelSelect = document.getElementById('workflowAiModel');
        
        if (!providerSelect || !modelSelect) return;

        const selectedProvider = providerSelect.value;
        
        // 清空現有選項
        modelSelect.innerHTML = '<option value="" data-i18n="settings.useDefault">使用預設設定</option>';

        if (!selectedProvider) return;

        // 模型選項配置
        const modelOptions = {
            'openai': [
                { value: 'gpt-4o', text: 'GPT-4o' },
                { value: 'gpt-4o-mini', text: 'GPT-4o Mini' },
                { value: 'gpt-4-turbo', text: 'GPT-4 Turbo' },
                { value: 'gpt-3.5-turbo', text: 'GPT-3.5 Turbo' }
            ],
            'claude': [
                { value: 'claude-3-5-sonnet-20241022', text: 'Claude 3.5 Sonnet' },
                { value: 'claude-3-5-haiku-20241022', text: 'Claude 3.5 Haiku' },
                { value: 'claude-3-opus-20240229', text: 'Claude 3 Opus' }
            ],
            'gemini': [
                { value: 'gemini-2.5-pro', text: 'Gemini 2.5 Pro' },
                { value: 'gemini-2.5-flash', text: 'Gemini 2.5 Flash' },
                { value: 'gemini-2.5-flash-lite', text: 'Gemini 2.5 Flash Lite' },
                { value: 'gemini-2.0-flash', text: 'Gemini 2.0 Flash' },
                { value: 'gemini-2.0-flash-lite', text: 'Gemini 2.0 Flash Lite' },
                { value: 'gemini-pro', text: 'Gemini Pro' }
            ],
            'grok': [
                { value: 'grok-2', text: 'Grok-2' },
                { value: 'grok-beta', text: 'Grok Beta' }
            ],
            'microsoft': [
                { value: 'copilot-gpt-4', text: 'Copilot GPT-4' },
                { value: 'copilot-gpt-4-turbo', text: 'Copilot GPT-4 Turbo' }
            ]
        };

        // 根據選擇的提供者更新模型選項
        if (modelOptions[selectedProvider]) {
            modelOptions[selectedProvider].forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.text;
                modelSelect.appendChild(optionElement);
            });
        }
        
        // 重新應用翻譯到新創建的元素
        this.updateUI();
    }

    // 獲取AI設定（優先使用工作流程指定，否則使用預設）
    getAISettings() {
        const workflowProvider = document.getElementById('workflowAiProvider')?.value;
        const workflowModel = document.getElementById('workflowAiModel')?.value;
        
        return {
            provider: workflowProvider || '', // 空值表示使用預設
            model: workflowModel || '' // 空值表示使用預設
        };
    }
    
    updateProfileSelect() {
        // 這個函數已經不再需要，因為我們移除了profileSelect元素
        // 保留函數以避免錯誤，但不執行任何操作
        console.log('updateProfileSelect: 已棄用，使用新的當前設定顯示');
    }
    
    getRecommendedProfiles(workType, brand) {
        if (!this.profiles) return [];
        
        const recommendations = [];
        
        // 根據工作類型推薦
        this.profiles.forEach(profile => {
            let score = 0;
            let recommended = false;
            
            // 類型匹配
            if (profile.type === workType) {
                score += 10;
                recommended = true;
            }
            
            // 品牌匹配
            if (brand && profile.brand === brand) {
                score += 5;
                recommended = true;
            }
            
            // 通用配置
            if (profile.name === 'default') {
                score += 1;
            }
            
            recommendations.push({
                ...profile,
                score,
                recommended
            });
        });
        
        // 按分數排序
        return recommendations.sort((a, b) => b.score - a.score);
    }
    
    async selectWork(workId) {
        if (!workId) {
            this.currentWork = null;
            this.hideWorkInfo();
            this.updateProfileSelect();
            this.clearWorkSettings();
            return;
        }
        
        // 確保 works 數組存在
        if (!this.works || !Array.isArray(this.works)) {
            console.error('works 數組未初始化或不是數組:', this.works);
            return;
        }
        
        this.currentWork = this.works.find(work => work.id === workId);
        if (this.currentWork) {
            this.showWorkInfo();
            this.updateProfileSelect();
            this.loadWorkSettings();
            loadTemplates(); // 載入模板選項
            loadPrompts(); // 載入提示詞選項
            
            // 載入並應用工作流程偏好設定
            await this.applyWorkflowPreferences(workId);
        } else {
            console.error('找不到工作 ID:', workId, '在 works 數組中:', this.works);
        }
    }
    
    // 載入工作的預設設定
    loadWorkSettings() {
        if (!this.currentWork) return;
        
        console.log('載入工作設定:', this.currentWork);
        
        // 延遲設定，確保選項已載入
        setTimeout(() => {
            // profileSelect 元素已移除，不再需要設定
            console.log('Profile設定已移至當前設定顯示區域');
            
            // 這些元素已經被移除，不再需要設定
            // 設定現在通過新的當前設定顯示來處理
            console.log('工作設定載入完成，使用新的當前設定顯示');
            
            // 顯示載入的設定
            const notificationText = currentLang === 'en' 
                ? `Loaded default settings for "${this.currentWork.name}"`
                : `已載入「${this.currentWork.name}」的預設設定`;
            showNotification(notificationText, 'info');
        }, 500); // 延遲500ms確保選項已載入
    }
    
    // 清空工作設定
    clearWorkSettings() {
        // 這些元素已經被移除，不再需要清空
        // 只清空仍然存在的元素
        const outputFolder = document.getElementById('outputFolder');
        if (outputFolder) {
            outputFolder.value = 'output';
        }
    }
    
    showWorkInfo() {
        console.log('顯示工作信息:', this.currentWork);
        const workInfo = document.getElementById('workInfo');
        const workName = document.getElementById('workNameDisplay');
        const workDescription = document.getElementById('workDescriptionDisplay');
        const processedCount = document.getElementById('processedCount');
        const learningCount = document.getElementById('learningCount');
        const createdDate = document.getElementById('createdDate');
        
        console.log('元素檢查:', {
            workInfo: !!workInfo,
            workName: !!workName,
            workDescription: !!workDescription,
            processedCount: !!processedCount,
            learningCount: !!learningCount,
            createdDate: !!createdDate
        });
        
        if (!workInfo) {
            console.error('找不到 workInfo 元素');
            return;
        }
        
        if (!workName) {
            console.error('找不到 workName 元素');
            return;
        }
        
        if (!workDescription) {
            console.error('找不到 workDescription 元素');
            return;
        }
        
        console.log('設置工作信息:', {
            name: this.currentWork.name,
            description: this.currentWork.description
        });
        
        workName.textContent = this.currentWork.name || '';
        workDescription.textContent = this.currentWork.description || '';
        processedCount.textContent = this.currentWork.processed_count || 0;
        // 學習功能開發中，暫時註解
        // learningCount.textContent = this.currentWork.learning_count || 0;
        // 格式化創建時間
        const createTime = this.currentWork.created_at || this.currentWork.created_date;
        if (createTime) {
            try {
                const date = new Date(createTime);
                createdDate.textContent = date.toLocaleString('zh-TW');
            } catch (e) {
                createdDate.textContent = createTime;
            }
        } else {
            createdDate.textContent = '-';
        }
        
        workInfo.style.display = 'block';
        console.log('工作信息區域已顯示');
        
        // 更新當前設定顯示
        this.updateCurrentSettings();
    }
    
    updateCurrentSettings() {
        // 更新當前配置顯示
        const profileDisplay = document.getElementById('currentProfileDisplay');
        if (profileDisplay) {
            if (typeof this.currentWork.profile === 'object' && this.currentWork.profile) {
                const profileName = this.currentWork.profile.name || (this.currentLanguage === 'en' ? 'Custom Configuration' : '自定義配置');
                const simplifiedName = profileName.replace('資料提取Profile', '').replace('Profile', '').trim();
                const createTime = this.currentWork.profile.created_at || this.currentWork.created_at || (this.currentLanguage === 'en' ? 'Unknown Time' : '未知時間');
                const displayTime = new Date(createTime).toLocaleString(this.currentLanguage === 'en' ? 'en-US' : 'zh-TW');
                const createLabel = this.currentLanguage === 'en' ? 'Created' : '創建';
                profileDisplay.innerHTML = `<span class="setting-value current">${simplifiedName || (this.currentLanguage === 'en' ? 'Custom Configuration' : '自定義配置')} (${createLabel}: ${displayTime})</span>`;
            } else if (typeof this.currentWork.profile === 'string' && this.currentWork.profile) {
                const createTime = this.currentWork.created_at || (this.currentLanguage === 'en' ? 'Unknown Time' : '未知時間');
                const displayTime = new Date(createTime).toLocaleString(this.currentLanguage === 'en' ? 'en-US' : 'zh-TW');
                const createLabel = this.currentLanguage === 'en' ? 'Created' : '創建';
                profileDisplay.innerHTML = `<span class="setting-value current">${this.currentWork.profile} (${createLabel}: ${displayTime})</span>`;
            } else {
                const emptyText = this.currentLanguage === 'en' ? 'No Configuration' : '無配置';
                profileDisplay.innerHTML = `<span class="setting-value empty">${emptyText}</span>`;
            }
        }

        // 更新當前模板顯示
        const templateDisplay = document.getElementById('currentTemplateDisplay');
        if (templateDisplay) {
            if (typeof this.currentWork.template === 'string' && this.currentWork.template) {
                const templateName = this.currentWork.template;
                
                // 如果是完整路徑，提取文件名；否則直接使用
                let fileName = templateName;
                if (templateName.includes('\\') || templateName.includes('/')) {
                    fileName = templateName.split(/[\\\/]/).pop();
                }
                
                // 移除文件擴展名用於顯示
                const displayName = fileName.replace(/\.(docx|doc|pdf)$/i, '');
                
                const createTime = this.currentWork.created_at || (this.currentLanguage === 'en' ? 'Unknown Time' : '未知時間');
                const displayTime = new Date(createTime).toLocaleString(this.currentLanguage === 'en' ? 'en-US' : 'zh-TW');
                const uploadLabel = this.currentLanguage === 'en' ? 'Uploaded' : '上傳';

                templateDisplay.innerHTML = `<span class="setting-value current">${displayName} (${uploadLabel}: ${displayTime})</span>`;
            } else {
                const emptyText = this.currentLanguage === 'en' ? 'No Template' : '無模板';
                templateDisplay.innerHTML = `<span class="setting-value empty">${emptyText}</span>`;
            }
        }

        // 更新當前提示詞顯示
        const promptDisplay = document.getElementById('currentPromptDisplay');
        if (promptDisplay) {
            if (typeof this.currentWork.prompt === 'string' && this.currentWork.prompt) {
                const prompt = this.currentWork.prompt;
                const createTime = this.currentWork.created_at || (this.currentLanguage === 'en' ? 'Unknown Time' : '未知時間');
                const displayTime = new Date(createTime).toLocaleString(this.currentLanguage === 'en' ? 'en-US' : 'zh-TW');

                if (prompt.includes('.md')) {
                    const fileName = prompt.replace('.md', '');
                    const createLabel = this.currentLanguage === 'en' ? 'Created' : '創建';
                    promptDisplay.innerHTML = `<span class="setting-value current">${fileName} (${createLabel}: ${displayTime})</span>`;
                } else {
                    const promptLength = prompt.length;
                    const customPromptLabel = this.currentLanguage === 'en' ? 'Custom Prompt' : '自定義提示詞';
                    const wordLabel = this.currentLanguage === 'en' ? 'chars' : '字';
                    const createLabel = this.currentLanguage === 'en' ? 'Created' : '創建';
                    promptDisplay.innerHTML = `<span class="setting-value current">${customPromptLabel} (${promptLength}${wordLabel}) (${createLabel}: ${displayTime})</span>`;
                }
            } else {
                const emptyText = this.currentLanguage === 'en' ? 'No Prompt' : '無提示詞';
                promptDisplay.innerHTML = `<span class="setting-value empty">${emptyText}</span>`;
            }
        }
    }
    
    clearCurrentSettings() {
        // 清空當前設定顯示
        const profileDisplay = document.getElementById('currentProfileDisplay');
        const templateDisplay = document.getElementById('currentTemplateDisplay');
        
        if (profileDisplay) {
            const selectWorkText = this.currentLanguage === 'en' ? 'Please select a work first' : '請先選擇工作';
            profileDisplay.innerHTML = `<span class="setting-value empty">${selectWorkText}</span>`;
        }
        
        if (templateDisplay) {
            const selectWorkText = this.currentLanguage === 'en' ? 'Please select a work first' : '請先選擇工作';
            templateDisplay.innerHTML = `<span class="setting-value empty">${selectWorkText}</span>`;
        }
        
        const promptDisplay = document.getElementById('currentPromptDisplay');
        if (promptDisplay) {
            const selectWorkText = this.currentLanguage === 'en' ? 'Please select a work first' : '請先選擇工作';
            promptDisplay.innerHTML = `<span class="setting-value empty">${selectWorkText}</span>`;
        }
        
        // 檢查編輯和刪除按鈕是否存在
        const editBtn = workInfo.querySelector('button[onclick="editWork()"]');
        const deleteBtn = workInfo.querySelector('button[onclick="deleteWork()"]');
        console.log('編輯按鈕存在:', !!editBtn);
        console.log('刪除按鈕存在:', !!deleteBtn);
        
        // 如果按鈕不存在，嘗試其他選擇器
        if (!editBtn || !deleteBtn) {
            console.log('嘗試其他選擇器...');
            const allButtons = workInfo.querySelectorAll('button');
            console.log('工作信息區域中的所有按鈕:', allButtons.length);
            allButtons.forEach((btn, index) => {
                console.log(`按鈕 ${index}:`, btn.outerHTML);
            });
            
            // 嘗試直接通過 ID 查找
            const workActions = workInfo.querySelector('.work-actions');
            console.log('work-actions 元素存在:', !!workActions);
            if (workActions) {
                const actionButtons = workActions.querySelectorAll('button');
                console.log('work-actions 中的按鈕數量:', actionButtons.length);
            }
        }
    }
    
    hideWorkInfo() {
        const workInfo = document.getElementById('workInfo');
        workInfo.style.display = 'none';
    }

    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        this.uploadFiles(files);
    }

    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('dragover');
    }

    handleDragLeave(event) {
        event.currentTarget.classList.remove('dragover');
    }

    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
        
        const files = Array.from(event.dataTransfer.files);
        this.uploadFiles(files);
    }

    async uploadFiles(files) {
        for (const file of files) {
            if (this.validateFile(file)) {
                await this.uploadFile(file);
            }
        }
    }

    validateFile(file) {
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        const maxSize = 50 * 1024 * 1024; // 50MB

        if (!allowedTypes.includes(file.type)) {
            const errorMsg = currentLang === 'en' ? 'Unsupported file format, please select PDF, DOCX or DOC files' : '不支援的檔案格式，請選擇 PDF、DOCX 或 DOC 檔案';
            this.showError(errorMsg);
            return false;
        }

        if (file.size > maxSize) {
            const errorMsg = currentLang === 'en' ? 'File size exceeds 50MB limit' : '檔案大小超過 50MB 限制';
            this.showError(errorMsg);
            return false;
        }

        return true;
    }

    async uploadFile(file) {
        try {
            console.log('開始上傳檔案:', file.name, '大小:', file.size);
            
            const formData = new FormData();
            formData.append('file', file);

            console.log('發送上傳請求到 /upload');
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            console.log('上傳響應狀態:', response.status);
            const data = await response.json();
            console.log('上傳響應數據:', data);

            if (data.success) {
                console.log('檔案上傳成功:', data);
                this.uploadedFiles.push({
                    id: data.file_id,
                    name: data.filename,
                    size: file.size,
                    path: data.file_path
                });
                this.updateFileList();
                this.updateProcessButton();
                const successMsg = currentLang === 'en' 
                    ? `File "${file.name}" uploaded successfully`
                    : `檔案「${file.name}」上傳成功`;
                showNotification(successMsg, 'success');
            } else {
                console.error('檔案上傳失敗:', data.error);
                const errorMsg = data.error || (currentLang === 'en' ? 'File upload failed' : '檔案上傳失敗');
                this.showError(errorMsg);
            }
        } catch (error) {
            console.error('檔案上傳錯誤:', error);
            const errorMsg = currentLang === 'en' 
                ? 'File upload failed: ' + error.message
                : '檔案上傳失敗: ' + error.message;
            this.showError(errorMsg);
        }
    }

    updateFileList() {
        const fileList = document.getElementById('fileList');
        const fileItems = document.getElementById('fileItems');

        if (this.uploadedFiles.length > 0) {
            fileList.style.display = 'block';
            fileItems.innerHTML = '';

            this.uploadedFiles.forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                
                // 檢查是否有選擇的頁面
                const hasSelectedPages = this.selectedPagesMap[file.id] && this.selectedPagesMap[file.id].length > 0;
                const selectedPagesText = hasSelectedPages ? ` (${this.selectedPagesMap[file.id].length} 頁)` : '';
                
                fileItem.innerHTML = `
                    <div class="file-info">
                        <i class="fas fa-file-alt file-icon"></i>
                        <span class="file-name">${file.name}${selectedPagesText}</span>
                        <span class="file-size">${this.formatFileSize(file.size)}</span>
                    </div>
                    <div class="file-item-actions">
                        <button class="page-select-btn" onclick="prodocux.openSingleFilePagePicker('${file.id}')" title="${currentLang === 'en' ? 'Select Pages' : '選擇頁面'}">
                            <i class="fas fa-list-check"></i>
                            ${currentLang === 'en' ? 'Select Pages' : '選擇頁面'}
                        </button>
                        <button class="remove-file" onclick="prodocux.removeFile('${file.id}')" title="${currentLang === 'en' ? 'Remove File' : '移除檔案'}">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                `;
                fileItems.appendChild(fileItem);
            });
        } else {
            fileList.style.display = 'none';
        }
    }

    removeFile(fileId) {
        this.uploadedFiles = this.uploadedFiles.filter(file => file.id !== fileId);
        this.updateFileList();
        this.updateProcessButton();
    }

    updateProcessButton() {
        const processBtn = document.getElementById('processBtn');
        const costPanel = document.getElementById('costPanel');
        
        // 檢查是否滿足處理條件
        const hasFiles = this.uploadedFiles.length > 0;
        const hasCostEstimate = costPanel && costPanel.style.display !== 'none';
        
        if (!hasFiles) {
            processBtn.disabled = true;
            processBtn.title = currentLang === 'en' ? 'Please select files first' : '請先選擇檔案';
            const processText = currentLang === 'en' ? 'Start Processing' : '開始處理';
            processBtn.innerHTML = `<i class="fas fa-play"></i> ${processText}`;
        } else if (!hasCostEstimate) {
            processBtn.disabled = true;
            processBtn.title = currentLang === 'en' ? 'Please perform cost estimation first' : '請先進行成本估算';
            const estimateText = currentLang === 'en' ? 'Please Estimate Cost' : '請先估算成本';
            processBtn.innerHTML = `<i class="fas fa-calculator"></i> ${estimateText}`;
        } else {
            // 成本估算已完成，檢查context window限制
            // 這個檢查會在showCostPanel中進行
            processBtn.disabled = false;
            processBtn.title = currentLang === 'en' ? 'Can start processing' : '可以開始處理';
            const processText = currentLang === 'en' ? 'Start Processing' : '開始處理';
            processBtn.innerHTML = `<i class="fas fa-play"></i> ${processText}`;
        }
    }

    async processDocument() {
        if (this.uploadedFiles.length === 0) {
            const errorMsg = currentLang === 'en' ? 'Please select files first' : '請先選擇檔案';
            this.showError(errorMsg);
            return;
        }

        // 檢查是否已進行成本估算
        const costPanel = document.getElementById('costPanel');
        if (!costPanel || costPanel.style.display === 'none') {
            const errorMsg = currentLang === 'en' 
                ? 'Please perform cost estimation first, confirm processing parameters before starting'
                : '請先進行成本估算，確認處理參數後再開始處理';
            this.showError(errorMsg);
            return;
        }

        // 檢查是否超過context window限制
        const processBtn = document.getElementById('processBtn');
        if (processBtn && processBtn.disabled) {
            const errorMsg = currentLang === 'en'
                ? 'Input tokens exceed model limit, cannot process. Please reduce selected pages or choose a model with larger context window'
                : '輸入tokens超過模型限制，無法處理。請減少選中的頁數或選擇支援更大上下文的模型';
            this.showError(errorMsg);
            return;
        }

        try {
            this.showProgress(true);
            const progressText = currentLang === 'en' ? 'Starting batch processing...' : '開始批量處理...';
            this.updateProgress(0, progressText);
            const initText = currentLang === 'en' ? 'Initializing processing workflow...' : '正在初始化處理流程...';
            this.addLogEntry(initText, 'info');

            // 使用當前工作的設定
            const profile = prodocux.currentWork ? prodocux.currentWork.profile : '';
            const format = document.getElementById('formatSelect').value;
            const template = prodocux.currentWork ? prodocux.currentWork.template : '';
            // 優先從工作流程獲取提示詞，否則從DOM元素獲取
            let userPrompt = '';
            const workflowCheckText = currentLang === 'en' 
                ? `🔍 Check workflow prompt: ${prodocux.currentWork ? 'has workflow' : 'no workflow'}`
                : `🔍 檢查工作流程提示詞: ${prodocux.currentWork ? '有工作流程' : '無工作流程'}`;
            this.addLogEntry(workflowCheckText, 'info');
            if (prodocux.currentWork) {
                const promptFieldText = currentLang === 'en' 
                    ? `🔍 Workflow prompt field: ${prodocux.currentWork.prompt ? 'has prompt' : 'no prompt'}`
                    : `🔍 工作流程prompt欄位: ${prodocux.currentWork.prompt ? '有prompt' : '無prompt'}`;
                this.addLogEntry(promptFieldText, 'info');
                if (prodocux.currentWork.prompt) {
                    const promptPreviewText = currentLang === 'en' 
                        ? `🔍 Prompt content first 100 chars: ${prodocux.currentWork.prompt.substring(0, 100)}...`
                        : `🔍 prompt內容前100字符: ${prodocux.currentWork.prompt.substring(0, 100)}...`;
                    this.addLogEntry(promptPreviewText, 'info');
                }
            }
            
            if (prodocux.currentWork && prodocux.currentWork.prompt) {
                // 如果prompt是檔案名稱，需要載入實際內容
                if (prodocux.currentWork.prompt.endsWith('.yaml') || prodocux.currentWork.prompt.endsWith('.md')) {
                    this.addLogEntry(`🔍 檢測到提示詞檔案名稱: ${prodocux.currentWork.prompt}`, 'info');
                    try {
                        const response = await fetch(`/api/prompts/${prodocux.currentWork.prompt}`);
                        const data = await response.json();
                        if (data.success && data.prompt.content) {
                            userPrompt = data.prompt.content;
                            this.addLogEntry(`✅ 已載入工作流程提示詞: ${prodocux.currentWork.prompt}`, 'info');
                        } else {
                            this.addLogEntry(`❌ 無法載入提示詞內容: ${prodocux.currentWork.prompt}`, 'warning');
                            // 不要回退到空字符串，保持原始提示詞
                            userPrompt = prodocux.currentWork.prompt;
                        }
                    } catch (error) {
                        this.addLogEntry(`❌ 載入提示詞失敗: ${error.message}`, 'error');
                        // 不要回退到空字符串，保持原始提示詞
                        userPrompt = prodocux.currentWork.prompt;
                    }
                } else {
                    // 直接是提示詞內容
                    userPrompt = prodocux.currentWork.prompt;
                    const directUseText = currentLang === 'en' 
                        ? `✅ Directly using workflow prompt content`
                        : `✅ 直接使用工作流程提示詞內容`;
                    this.addLogEntry(directUseText, 'info');
                }
            } else {
                userPrompt = document.getElementById('userPrompt') ? document.getElementById('userPrompt').value : '';
                this.addLogEntry(`⚠️ 使用DOM元素提示詞或空提示詞`, 'warning');
            }
            
            const finalLengthText = currentLang === 'en' 
                ? `🔍 Final userPrompt length: ${userPrompt.length} chars`
                : `🔍 最終userPrompt長度: ${userPrompt.length} 字符`;
            this.addLogEntry(finalLengthText, 'info');
            
            const finalPreviewText = currentLang === 'en' 
                ? `🔍 Final userPrompt first 100 chars: ${userPrompt.substring(0, 100)}...`
                : `🔍 最終userPrompt前100字符: ${userPrompt.substring(0, 100)}...`;
            this.addLogEntry(finalPreviewText, 'info');

            // 獲取AI設定（優先使用工作流程指定，否則使用預設）
            const aiSettings = this.getAISettings();
            const aiSettingsText = currentLang === 'en' 
                ? `Using AI settings: ${aiSettings.provider || 'default provider'}, ${aiSettings.model || 'default model'}`
                : `使用AI設定: ${aiSettings.provider || '預設提供者'}, ${aiSettings.model || '預設模型'}`;
            this.addLogEntry(aiSettingsText, 'info');

            // 獲取所有檔案ID
            const fileIds = this.uploadedFiles.map(file => file.id);
            const prepareFilesText = currentLang === 'en' 
                ? `Preparing to process ${fileIds.length} files`
                : `準備處理 ${fileIds.length} 個檔案`;
            this.addLogEntry(prepareFilesText, 'info');
            
            // 獲取工作資料（如果有的話）
            const workId = this.getCurrentWorkId();
            const workData = this.getCurrentWorkData();

            // 根據是否有工作流程來決定profile參數
            let profileParam = null; // 不使用預設profile
            if (workId && workData) {
                // 新版：使用工作流程，不需要profile參數
                profileParam = null;
            } else {
                // 舊版：使用傳統profile，需要字符串格式
                if (typeof profile === 'object' && profile && profile.name) {
                    profileParam = profile.name;
                } else if (typeof profile === 'string' && profile.trim() !== '') {
                    profileParam = profile;
                } else {
                    profileParam = null;
                }
            }

            // 更新進度：開始處理
            const processingText = currentLang === 'en' ? 'Processing files...' : '正在處理檔案...';
            this.updateProgress(10, processingText);
            this.addLogEntry(processingText, 'info');

            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    file_ids: fileIds,
                    profile: profileParam,
                    format: format,
                    template: template,
                    user_prompt: userPrompt,
                    work_id: workId,
                    work_data: workData,
                    selected_pages_map: this.selectedPagesMap,
                    ai_provider: aiSettings.provider,
                    ai_model: aiSettings.model
                })
            });

            // 更新進度：收到響應
            const responseText = currentLang === 'en' ? 'Received response from server...' : '收到服務器響應...';
            this.updateProgress(50, responseText);
            this.addLogEntry(responseText, 'info');

            const data = await response.json();

            // 更新進度：解析響應
            const parsingText = currentLang === 'en' ? 'Parsing response...' : '解析響應中...';
            this.updateProgress(75, parsingText);
            this.addLogEntry(parsingText, 'info');

            if (data.success) {
                const completeText = currentLang === 'en' ? 'Batch processing completed' : '批量處理完成';
                this.updateProgress(100, completeText);
                
                if (data.batch_processing) {
                    // 批量處理結果
                    this.showBatchResults(data);
                } else {
                    // 單檔處理結果（向後相容）
                    this.showResults(data.data, data.download_url);
                }
            } else {
                const errorMsg = data.error || (currentLang === 'en' ? 'Document processing failed' : '文檔處理失敗');
                this.showError(errorMsg, data.errors);
            }
        } catch (error) {
            console.error('處理錯誤:', error);
            const errorMsg = currentLang === 'en' ? 'Document processing failed' : '文檔處理失敗';
            this.showError(errorMsg);
        } finally {
            this.showProgress(false);
        }
    }

    async estimateCost() {
        if (this.uploadedFiles.length === 0) {
            const errorMsg = currentLang === 'en' ? 'Please select files first' : '請先選擇檔案';
            this.showError(errorMsg);
            return;
        }

        if (!this.currentWork) {
            const errorMsg = currentLang === 'en' ? 'Please select a work first' : '請先選擇一個工作';
            this.showError(errorMsg);
            return;
        }

        const estimateBtn = document.getElementById('estimateBtn');

        try {
            // 顯示載入狀態
            estimateBtn.disabled = true;
            const estimatingText = currentLang === 'en' ? 'Estimating...' : '估算中...';
            estimateBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${estimatingText}`;
            
            // 從當前工作獲取profile，不再從profileSelect元素獲取
            const profile = this.currentWork ? this.currentWork.profile : '';
            
            // 獲取AI設定（優先使用工作流程指定，否則使用預設）
            const aiSettings = this.getAISettings();
            console.log('成本估算使用AI設定:', aiSettings);
            
            // 獲取工作資料（如果有的話）
            const workId = this.getCurrentWorkId();
            const workData = this.getCurrentWorkData();
            
            // 根據是否有工作流程來決定profile參數
            let profileParam = null; // 不使用預設profile
            if (workId && workData) {
                // 新版：使用工作流程，不需要profile參數
                profileParam = null;
            } else {
                // 舊版：使用傳統profile，需要字符串格式
                if (typeof profile === 'object' && profile && profile.name) {
                    profileParam = profile.name;
                } else if (typeof profile === 'string' && profile.trim() !== '') {
                    profileParam = profile;
                } else {
                    profileParam = null;
                }
            }
            
            // 計算總體成本估算
            await this.calculateBatchCostEstimate(profileParam, aiSettings);
            
            const successMsg = currentLang === 'en' ? 'Cost estimation completed!' : '成本估算完成！';
            this.showSuccess(successMsg);
        } catch (error) {
            console.error('成本估算錯誤:', error);
            const errorMsg = currentLang === 'en' ? 'Cost estimation failed' : '成本估算失敗';
            this.showError(errorMsg);
        } finally {
            // 恢復按鈕狀態
            estimateBtn.disabled = false;
            const estimateText = currentLang === 'en' ? 'Estimate Cost' : '估算成本';
            estimateBtn.innerHTML = `<i class="fas fa-calculator"></i> ${estimateText}`;
        }
    }

    async calculateBatchCostEstimate(profile, aiSettings = {}) {
        try {
            // 獲取設定資訊
            const settingsResponse = await fetch('/api/settings');
            const settingsData = await settingsResponse.json();
            
            if (!settingsData.success) {
                throw new Error('無法獲取設定資訊');
            }
            
            const settings = settingsData.settings;
            const costSettings = settings.cost_settings || {};
            const apiSettings = settings.api_settings || {};
            
            // 確定使用的AI提供者和模型（優先使用工作流程指定，否則使用預設）
            const finalProvider = aiSettings.provider || settings.ai_provider || 'openai';
            const finalModel = aiSettings.model || settings.ai_model || 'gpt-4o';
            
            console.log(`成本估算使用AI: ${finalProvider}/${finalModel}`);
            
            // 計算每個檔案的頁面資訊
            let totalFiles = this.uploadedFiles.length;
            let totalPages = 0;
            let selectedPages = 0;
            let totalInputTokens = 0;
            let totalOutputTokens = 0;
            
            // 載入頁面預覽資料（成本估算需要精準資料）
            console.log('開始載入頁面資料進行成本估算...');
            const promises = this.uploadedFiles.map(async (file) => {
                try {
                    await this.loadFilePages(file.id);
                } catch (error) {
                    console.warn(`載入檔案 ${file.id} 頁面預覽失敗:`, error);
                }
            });
            await Promise.all(promises);
            console.log('頁面資料載入完成');
            
            for (const file of this.uploadedFiles) {
                const previewData = this.pagePreviewData[file.id];
                if (previewData && previewData.pages) {
                    totalPages += previewData.pages.length;
                    
                    // 計算選中的頁面
                    const selectedPagesForFile = this.selectedPagesMap[file.id] || [];
                    const hasSelectedPages = selectedPagesForFile.length > 0;
                    
                    // 如果沒有選擇頁面，預設選擇全部頁面
                    if (!hasSelectedPages) {
                        selectedPages += previewData.pages.length;
                    } else {
                        selectedPages += selectedPagesForFile.length;
                    }
                    
                    // 估算tokens（基於頁面內容長度）
                    const pagesToProcess = hasSelectedPages ? 
                        previewData.pages.filter(p => selectedPagesForFile.includes(p.page_number)) :
                        previewData.pages;
                    
                    for (const page of pagesToProcess) {
                        // 確保page.content存在
                        const pageContent = page.content || '';
                        const contentLength = page.content_length || pageContent.length;
                        
                        // 更準確的token估算：中文字符約1.5-2個token，英文約0.75個token
                        const chineseChars = (pageContent.match(/[\u4e00-\u9fff]/g) || []).length;
                        const englishChars = contentLength - chineseChars;
                        const pageTokens = Math.ceil(chineseChars * 1.8 + englishChars * 0.75);
                        totalInputTokens += pageTokens;
                        
                        // 輸出tokens估算：基於實際經驗，PIF轉換輸出通常是輸入的30-50%
                        // 考慮到結構化數據的複雜性，使用40%作為估算
                        totalOutputTokens += Math.ceil(pageTokens * 0.4);
                    }
                }
            }
            
            // 添加系統提示詞和模板提示詞的估算
            const systemPromptTokens = 2000; // 系統提示詞約2000 tokens
            const templatePromptTokens = 1000; // 模板提示詞約1000 tokens
            const totalSystemTokens = systemPromptTokens + templatePromptTokens;
            
            const totalTokens = totalInputTokens + totalOutputTokens + totalSystemTokens;
            
            // 使用新的定價API獲取準確的定價資訊
            const model = finalModel; // 使用前面確定的最終模型
            let inputPrice, outputPrice, pricingInfo;
            
            try {
                // 從新的定價API獲取定價資訊
                const pricingResponse = await fetch(`/api/pricing?model=${encodeURIComponent(model)}`);
                const pricingData = await pricingResponse.json();
                
                console.log('定價API響應:', pricingData);
                
                if (pricingData.success) {
                    pricingInfo = pricingData.pricing;
                    inputPrice = pricingInfo.input_per_1k || 0.03;
                    outputPrice = pricingInfo.output_per_1k || 0.06;
                    console.log(`使用定價: ${model} - 輸入: $${inputPrice}/1K, 輸出: $${outputPrice}/1K`);
                } else {
                    // 回退到舊的定價邏輯
                    const pricing = costSettings.pricing || {};
                    inputPrice = pricing.input_per_1k || 0.03;
                    outputPrice = pricing.output_per_1k || 0.06;
                    pricingInfo = { provider: 'unknown', last_updated: 'unknown' };
                    console.log('定價API失敗，使用回退定價:', inputPrice, outputPrice);
                }
            } catch (error) {
                console.warn('無法獲取最新定價資訊，使用預設定價:', error);
                // 回退到預設定價
                inputPrice = 0.03;
                outputPrice = 0.06;
                pricingInfo = { provider: 'fallback', last_updated: 'unknown' };
            }
            
            // 計算成本（包含系統提示詞）
            const totalInputTokensWithSystem = totalInputTokens + totalSystemTokens;
            const inputCost = (totalInputTokensWithSystem / 1000) * inputPrice;
            const outputCost = (totalOutputTokens / 1000) * outputPrice;
            const averageCost = inputCost + outputCost;
            
            // 全部頁面成本估算（基於當前選中頁面的tokens密度）
            const actualTokensPerPage = selectedPages > 0 ? totalInputTokens / selectedPages : 800;
            const actualOutputTokensPerPage = selectedPages > 0 ? totalOutputTokens / selectedPages : actualTokensPerPage * 0.4;
            
            const allPagesInputTokens = totalPages * actualTokensPerPage + totalSystemTokens;
            const allPagesOutputTokens = totalPages * actualOutputTokensPerPage;
            const allPagesInputCost = (allPagesInputTokens / 1000) * inputPrice;
            const allPagesOutputCost = (allPagesOutputTokens / 1000) * outputPrice;
            const allPagesCost = allPagesInputCost + allPagesOutputCost;
            
            // 如果選中頁數等於總頁數，全部頁面成本等於平均成本
            const finalAllPagesCost = selectedPages === totalPages ? averageCost : allPagesCost;
            
            // 檢查context window限制
            const contextWindowCheck = this.checkContextWindowLimit(totalInputTokensWithSystem, model, pricingInfo);
            
            // 顯示成本面板
            this.showCostPanel({
                totalFiles,
                totalPages,
                selectedPages,
                inputTokens: totalInputTokensWithSystem,
                outputTokens: totalOutputTokens,
                totalTokens,
                averageCost,
                maxCost: finalAllPagesCost,
                model,
                systemTokens: totalSystemTokens,
                inputPrice,
                outputPrice,
                pricingInfo: pricingInfo,
                contextWindowCheck: contextWindowCheck
            });
            
        } catch (error) {
            console.error('批量成本估算失敗:', error);
            throw error;
        }
    }
    
    checkContextWindowLimit(inputTokens, model, pricingInfo) {
        // 檢查是否超過AI模型的context window限制
        const contextWindow = pricingInfo?.context_window || 0;
        
        if (!contextWindow) {
            return {
                status: 'unknown',
                message: currentLang === 'en' 
                    ? 'Unable to get model context window limit'
                    : '無法獲取模型的上下文窗口限制',
                recommendation: currentLang === 'en' 
                    ? 'Recommend choosing a model with larger context window'
                    : '建議選擇支援更大上下文的模型'
            };
        }
        
        const usagePercentage = (inputTokens / contextWindow) * 100;
        
        if (usagePercentage > 100) {
            return {
                status: 'exceeded',
                message: currentLang === 'en' 
                    ? `Input tokens (${inputTokens.toLocaleString()}) exceed model limit (${contextWindow.toLocaleString()})`
                    : `輸入tokens (${inputTokens.toLocaleString()}) 超過模型限制 (${contextWindow.toLocaleString()})`,
                recommendation: currentLang === 'en' 
                    ? 'Please reduce selected pages or choose a model with larger context window'
                    : '請減少選中的頁數或選擇支援更大上下文的模型',
                usagePercentage: usagePercentage,
                contextWindow: contextWindow
            };
        } else if (usagePercentage > 80) {
            return {
                status: 'warning',
                message: currentLang === 'en' 
                    ? `Input tokens (${inputTokens.toLocaleString()}) near model limit (${contextWindow.toLocaleString()})`
                    : `輸入tokens (${inputTokens.toLocaleString()}) 接近模型限制 (${contextWindow.toLocaleString()})`,
                recommendation: currentLang === 'en' 
                    ? 'Recommend reducing selected pages or choosing a model with larger context window'
                    : '建議減少選中的頁數或選擇支援更大上下文的模型',
                usagePercentage: usagePercentage,
                contextWindow: contextWindow
            };
        } else {
            return {
                status: 'ok',
                message: currentLang === 'en' 
                    ? `Input tokens (${inputTokens.toLocaleString()}) within model limit (${contextWindow.toLocaleString()})`
                    : `輸入tokens (${inputTokens.toLocaleString()}) 在模型限制內 (${contextWindow.toLocaleString()})`,
                recommendation: currentLang === 'en' ? 'Can process safely' : '可以安全處理',
                usagePercentage: usagePercentage,
                contextWindow: contextWindow
            };
        }
    }
    
    showCostPanel(costData) {
        const costPanel = document.getElementById('costPanel');
        
        // 更新摘要資訊
        document.getElementById('totalFiles').textContent = costData.totalFiles;
        document.getElementById('totalPages').textContent = costData.totalPages;
        document.getElementById('selectedPages').textContent = costData.selectedPages;
        
        // 更新token資訊
        document.getElementById('inputTokens').textContent = costData.inputTokens.toLocaleString();
        document.getElementById('outputTokens').textContent = costData.outputTokens.toLocaleString();
        document.getElementById('totalTokens').textContent = costData.totalTokens.toLocaleString();
        
        // 更新成本資訊
        document.getElementById('averageCost').textContent = `$${costData.averageCost.toFixed(4)}`;
        document.getElementById('maxCost').textContent = `$${costData.maxCost.toFixed(4)}`;
        document.getElementById('aiModel').textContent = costData.model;
        
        // 添加詳細說明
        const costDetails = document.getElementById('costDetails');
        if (costDetails) {
            // 根據語言生成成本估算說明
            let costDetailsHTML;
            
            if (currentLang === 'en') {
                costDetailsHTML = `
                <div class="cost-breakdown">
                    <h4>Cost Estimation Details</h4>
                    <div class="breakdown-item">
                        <strong>Input Token Calculation:</strong>
                        <ul>
                            <li>Document Content: ${(costData.inputTokens - costData.systemTokens).toLocaleString()} tokens</li>
                            <li>System Prompt: ${costData.systemTokens.toLocaleString()} tokens</li>
                            <li>Pricing: $${costData.inputPrice.toFixed(6)} per 1K tokens</li>
                        </ul>
                    </div>
                    <div class="breakdown-item">
                        <strong>Output Token Calculation:</strong>
                        <ul>
                            <li>Estimated Output: ${costData.outputTokens.toLocaleString()} tokens (approx. 40% of input)</li>
                            <li>Pricing: $${costData.outputPrice.toFixed(6)} per 1K tokens</li>
                        </ul>
                    </div>
                    <div class="breakdown-item">
                        <strong>Pricing Information Source:</strong>
                        <ul>
                            <li>Provider: ${costData.pricingInfo?.provider || 'Unknown'}</li>
                            <li>Last Updated: ${costData.pricingInfo?.last_updated || 'Unknown'}</li>
                            <li>Model: ${costData.pricingInfo?.model || costData.model}</li>
                        </ul>
                    </div>
                    <div class="breakdown-item">
                        <strong>Context Window Check:</strong>
                        <ul>
                            <li>${costData.contextWindowCheck.message}</li>
                            <li>Suggestion: ${costData.contextWindowCheck.recommendation}</li>
                            ${costData.contextWindowCheck.contextWindow ? 
                                `<li>Model Limit: ${costData.contextWindowCheck.contextWindow.toLocaleString()} tokens</li>` : ''}
                            ${costData.contextWindowCheck.usagePercentage ? 
                                `<li>Usage Rate: ${costData.contextWindowCheck.usagePercentage.toFixed(1)}%</li>` : ''}
                        </ul>
                    </div>
                    <div class="breakdown-item">
                        <strong>Important Notes:</strong>
                        <ul>
                            <li>This estimation is based on empirical values, actual costs may vary due to content complexity</li>
                            <li>Chinese characters are calculated at 1.8x, English characters at 0.75x</li>
                            <li>System prompts and template prompts are included in the calculation</li>
                            <li>Pricing information comes from official documentation and may change at any time</li>
                        </ul>
                    </div>
                </div>
            `;
            } else {
                costDetailsHTML = `
                <div class="cost-breakdown">
                    <h4>成本估算說明</h4>
                    <div class="breakdown-item">
                        <strong>輸入Token計算：</strong>
                        <ul>
                            <li>文檔內容：${(costData.inputTokens - costData.systemTokens).toLocaleString()} tokens</li>
                            <li>系統提示詞：${costData.systemTokens.toLocaleString()} tokens</li>
                            <li>定價：$${costData.inputPrice.toFixed(6)} per 1K tokens</li>
                        </ul>
                    </div>
                    <div class="breakdown-item">
                        <strong>輸出Token計算：</strong>
                        <ul>
                            <li>預估輸出：${costData.outputTokens.toLocaleString()} tokens (約輸入的40%)</li>
                            <li>定價：$${costData.outputPrice.toFixed(6)} per 1K tokens</li>
                        </ul>
                    </div>
                    <div class="breakdown-item">
                        <strong>定價資訊來源：</strong>
                        <ul>
                            <li>供應商：${costData.pricingInfo?.provider || '未知'}</li>
                            <li>最後更新：${costData.pricingInfo?.last_updated || '未知'}</li>
                            <li>模型：${costData.pricingInfo?.model || costData.model}</li>
                        </ul>
                    </div>
                    <div class="breakdown-item">
                        <strong>上下文窗口檢查：</strong>
                        <ul>
                            <li>${costData.contextWindowCheck.message}</li>
                            <li>建議：${costData.contextWindowCheck.recommendation}</li>
                            ${costData.contextWindowCheck.contextWindow ? 
                                `<li>模型限制：${costData.contextWindowCheck.contextWindow.toLocaleString()} tokens</li>` : ''}
                            ${costData.contextWindowCheck.usagePercentage ? 
                                `<li>使用率：${costData.contextWindowCheck.usagePercentage.toFixed(1)}%</li>` : ''}
                        </ul>
                    </div>
                    <div class="breakdown-item">
                        <strong>注意事項：</strong>
                        <ul>
                            <li>此估算基於經驗值，實際成本可能因內容複雜度而有所差異</li>
                            <li>中文字符按1.8倍計算，英文字符按0.75倍計算</li>
                            <li>系統提示詞和模板提示詞已包含在計算中</li>
                            <li>定價資訊來自官方文檔，可能隨時變動</li>
                        </ul>
                    </div>
                </div>
            `;
            }
            
            costDetails.innerHTML = costDetailsHTML;
        }
        
        // 檢查是否超過context window限制，決定是否禁用處理按鈕
        const processBtn = document.getElementById('processBtn');
        if (processBtn && costData.contextWindowCheck) {
            if (costData.contextWindowCheck.status === 'exceeded') {
                processBtn.disabled = true;
                processBtn.title = currentLang === 'en' 
                    ? 'Input tokens exceed model limit, cannot process'
                    : '輸入tokens超過模型限制，無法處理';
                const exceedText = currentLang === 'en' ? 'Exceeded Limit' : '超過限制';
                processBtn.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${exceedText}`;
            } else if (costData.contextWindowCheck.status === 'warning') {
                processBtn.disabled = false;
                processBtn.title = currentLang === 'en' 
                    ? 'Input tokens near model limit, recommend reducing pages'
                    : '輸入tokens接近模型限制，建議減少頁數';
                const processText = currentLang === 'en' ? 'Start Processing' : '開始處理';
                processBtn.innerHTML = `<i class="fas fa-play"></i> ${processText}`;
            } else {
                processBtn.disabled = false;
                processBtn.title = currentLang === 'en' ? 'Can process safely' : '可以安全處理';
                const processText = currentLang === 'en' ? 'Start Processing' : '開始處理';
                processBtn.innerHTML = `<i class="fas fa-play"></i> ${processText}`;
            }
        }
        
        // 顯示面板
        costPanel.style.display = 'block';
        
        // 滾動到面板
        costPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    async refreshCostEstimate() {
        if (this.uploadedFiles.length === 0) {
            const errorMsg = currentLang === 'en' ? 'Please select files first' : '請先選擇檔案';
            this.showError(errorMsg);
            return;
        }

        // 從當前工作獲取profile
        const profile = this.currentWork ? this.currentWork.profile : '';
        if (!profile) {
            const errorMsg = currentLang === 'en' ? 'Please select a configuration first' : '請先選擇配置';
            this.showError(errorMsg);
            return;
        }
        
        // 根據是否有工作流程來決定profile參數
        let profileParam = null; // 不使用預設profile
        if (typeof profile === 'object' && profile && profile.name) {
            profileParam = profile.name;
        } else if (typeof profile === 'string' && profile.trim() !== '') {
            profileParam = profile;
        } else {
            profileParam = null;
        }

        try {
            // 獲取AI設定（優先使用工作流程指定，否則使用預設）
            const aiSettings = this.getAISettings();
            await this.calculateBatchCostEstimate(profileParam, aiSettings);
            showNotification('成本估算已更新', 'success');
        } catch (error) {
            console.error('重新計算成本失敗:', error);
            const errorMsg = currentLang === 'en' ? 'Failed to recalculate cost' : '重新計算成本失敗';
            this.showError(errorMsg);
        }
    }

    showProgress(show) {
        const progressContainer = document.getElementById('progressContainer');
        progressContainer.style.display = show ? 'block' : 'none';
    }

    updateProgress(percentage, text) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const progressPercentage = document.getElementById('progressPercentage');

        progressFill.style.width = percentage + '%';
        progressText.textContent = text;
        if (progressPercentage) {
            progressPercentage.textContent = Math.round(percentage) + '%';
        }
    }

    addLogEntry(message, type = 'info') {
        const progressLog = document.getElementById('progressLog');
        if (progressLog) {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${type}`;
            logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            progressLog.appendChild(logEntry);
            progressLog.scrollTop = progressLog.scrollHeight;
        }
    }

    showResults(data, downloadUrl) {
        const resultsSection = document.getElementById('resultsSection');
        const resultPreview = document.getElementById('resultPreview');

        resultPreview.innerHTML = `
            <pre>${JSON.stringify(data, null, 2)}</pre>
        `;

        resultsSection.style.display = 'block';
        resultsSection.classList.add('fade-in');

        // 儲存下載URL
        this.downloadUrl = downloadUrl;
    }
    
    showBatchResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        const resultPreview = document.getElementById('resultPreview');

        let html;
        
        if (currentLang === 'en') {
            html = `
                <h3>Batch Processing Results</h3>
                <div class="batch-summary">
                    <p><strong>Total Files:</strong> ${data.total_files}</p>
                    <p><strong>Successfully Processed:</strong> ${data.successful_files}</p>
                    <p><strong>Failed:</strong> ${data.failed_files}</p>
                </div>
            `;
        } else {
            html = `
                <h3>批量處理結果</h3>
                <div class="batch-summary">
                    <p><strong>總檔案數：</strong> ${data.total_files}</p>
                    <p><strong>成功處理：</strong> ${data.successful_files}</p>
                    <p><strong>處理失敗：</strong> ${data.failed_files}</p>
                </div>
            `;
        }

        if (data.results && data.results.length > 0) {
            const successText = currentLang === 'en' ? 'Successfully Processed Files:' : '成功處理的檔案：';
            html += `<h4>${successText}</h4>`;
            data.results.forEach((result, index) => {
                const fileName = this.getFileNameById(result.file_id);
                html += `
                    <div class="file-result">
                        <h5>${fileName || result.file_id}</h5>
                        <pre>${JSON.stringify(result.data, null, 2)}</pre>
                        <!-- 下載按鈕已移至結果區域 -->
                    </div>
                `;
            });
        }

        if (data.errors && data.errors.length > 0) {
            const failedText = currentLang === 'en' ? 'Failed Files:' : '處理失敗的檔案：';
            html += `<h4>${failedText}</h4>`;
            html += '<ul class="error-list">';
            data.errors.forEach(error => {
                html += `<li class="text-danger">${error}</li>`;
            });
            html += '</ul>';
        }

        resultPreview.innerHTML = html;
        resultsSection.style.display = 'block';
        resultsSection.classList.add('fade-in');
        
        // 設置下載URL（如果有成功處理的檔案）
        if (data.results && data.results.length > 0) {
            // 使用第一個成功處理的檔案的下載URL
            this.downloadUrl = data.results[0].download_url;
        } else {
            this.downloadUrl = null;
        }
    }
    
    getFileNameById(fileId) {
        const file = this.uploadedFiles.find(f => f.id === fileId);
        return file ? file.name : null;
    }
    
    getCurrentWorkId() {
        // 從工作選擇下拉選單獲取當前工作ID
        const workSelect = document.getElementById('workSelect');
        return workSelect ? workSelect.value : null;
    }
    
    getCurrentWorkData() {
        // 從工作選擇下拉選單獲取當前工作資料
        const workSelect = document.getElementById('workSelect');
        if (!workSelect) return null;
        
        const selectedOption = workSelect.options[workSelect.selectedIndex];
        return selectedOption ? JSON.parse(selectedOption.dataset.workData || '{}') : null;
    }

    showCostEstimate(data) {
        console.log('顯示成本估算結果:', data);
        
        // 強制重新查找 DOM 元素
        let costContainer = document.getElementById('costEstimateContainer');
        
        // 如果找不到，嘗試其他方法
        if (!costContainer) {
            console.warn('第一次查找失敗，嘗試其他方法...');
            
            // 方法1: 通過 class 查找
            costContainer = document.querySelector('.cost-estimate-container');
            
            if (!costContainer) {
                // 方法2: 通過標籤查找
                const containers = document.querySelectorAll('div[id*="cost"], div[class*="cost"]');
                console.log('找到的成本相關元素:', containers);
                
                for (let container of containers) {
                    if (container.id === 'costEstimateContainer' || 
                        container.classList.contains('cost-estimate-container')) {
                        costContainer = container;
                        break;
                    }
                }
            }
        }
        
        if (!costContainer) {
            console.error('找不到 costEstimateContainer 元素，DOM 結構:', {
                allDivs: document.querySelectorAll('div').length,
                costElements: document.querySelectorAll('[id*="cost"], [class*="cost"]').length,
                bodyHTML: document.body.innerHTML.substring(0, 500)
            });
            
            // 如果找不到容器，嘗試動態創建
            console.log('嘗試動態創建成本估算容器...');
            this.createDynamicCostEstimate(data);
            return;
        }
        
        // 檢查各個元素是否存在
        const estimatedTokens = document.getElementById('estimatedTokens');
        const estimatedCost = document.getElementById('estimatedCost');
        const estimatedTime = document.getElementById('estimatedTime');
        const fileSize = document.getElementById('fileSize');
        const aiModel = document.getElementById('aiModel');
        const profileName = document.getElementById('profileName');
        
        console.log('DOM 元素檢查:', {
            costContainer: !!costContainer,
            estimatedTokens: !!estimatedTokens,
            estimatedCost: !!estimatedCost,
            estimatedTime: !!estimatedTime,
            fileSize: !!fileSize,
            aiModel: !!aiModel,
            profileName: !!profileName
        });
        
        // 更新成本估算結果
        if (estimatedTokens) {
            estimatedTokens.textContent = data.estimated_tokens.toLocaleString();
        } else {
            console.error('找不到 estimatedTokens 元素');
        }
        if (estimatedCost) {
            estimatedCost.textContent = `$${data.estimated_cost.toFixed(4)}`;
        } else {
            console.error('找不到 estimatedCost 元素');
        }
        if (estimatedTime) {
            estimatedTime.textContent = `${data.estimated_time} 秒`;
        } else {
            console.error('找不到 estimatedTime 元素');
        }
        if (fileSize) {
            fileSize.textContent = this.formatFileSize(data.file_size);
        } else {
            console.error('找不到 fileSize 元素');
        }
        if (aiModel) {
            aiModel.textContent = data.model || '未知模型';
        } else {
            console.error('找不到 aiModel 元素');
        }
        if (profileName) {
            profileName.textContent = data.profile || '預設配置';
        } else {
            console.error('找不到 profileName 元素');
        }
        
        // 顯示成本估算容器
        costContainer.style.display = 'block';
        console.log('成本估算容器已顯示');
        
        // 滾動到成本估算結果
        costContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    createDynamicCostEstimate(data) {
        // 動態創建成本估算顯示
        try {
            // 找到處理按鈕區域
            const processSection = document.querySelector('.process-section');
            if (!processSection) {
                console.error('找不到處理按鈕區域，使用 alert 顯示');
                this.showCostEstimateAlert(data);
                return;
            }
            
            // 創建成本估算容器
            const costContainer = document.createElement('div');
            costContainer.id = 'costEstimateContainer';
            costContainer.className = 'cost-estimate-container';
            costContainer.style.display = 'block';
            costContainer.style.margin = '20px 0';
            costContainer.style.padding = '20px';
            costContainer.style.background = 'linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%)';
            costContainer.style.border = '2px solid #4caf50';
            costContainer.style.borderRadius = '12px';
            costContainer.style.boxShadow = '0 4px 12px rgba(76, 175, 80, 0.15)';
            
            // 創建內容
            costContainer.innerHTML = `
                <h4 style="color: #2e7d32; margin-bottom: 15px; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-calculator"></i> 成本估算結果
                </h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(255, 255, 255, 0.7); border-radius: 8px; border-left: 4px solid #4caf50;">
                        <span style="font-weight: 600; color: #2e7d32; font-size: 0.9rem;">預估Token消耗:</span>
                        <span style="font-weight: 700; color: #1b5e20; font-size: 1rem;" id="estimatedTokens">${data.estimated_tokens.toLocaleString()}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(255, 255, 255, 0.7); border-radius: 8px; border-left: 4px solid #4caf50;">
                        <span style="font-weight: 600; color: #2e7d32; font-size: 0.9rem;">預估成本:</span>
                        <span style="font-weight: 700; color: #1b5e20; font-size: 1rem;" id="estimatedCost">$${data.estimated_cost.toFixed(4)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(255, 255, 255, 0.7); border-radius: 8px; border-left: 4px solid #4caf50;">
                        <span style="font-weight: 600; color: #2e7d32; font-size: 0.9rem;">處理時間:</span>
                        <span style="font-weight: 700; color: #1b5e20; font-size: 1rem;" id="estimatedTime">${data.estimated_time} 秒</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(255, 255, 255, 0.7); border-radius: 8px; border-left: 4px solid #4caf50;">
                        <span style="font-weight: 600; color: #2e7d32; font-size: 0.9rem;">檔案大小:</span>
                        <span style="font-weight: 700; color: #1b5e20; font-size: 1rem;" id="fileSize">${this.formatFileSize(data.file_size)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(255, 255, 255, 0.7); border-radius: 8px; border-left: 4px solid #4caf50;">
                        <span style="font-weight: 600; color: #2e7d32; font-size: 0.9rem;">AI模型:</span>
                        <span style="font-weight: 700; color: #1b5e20; font-size: 1rem;" id="aiModel">${data.model || '未知模型'}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(255, 255, 255, 0.7); border-radius: 8px; border-left: 4px solid #4caf50;">
                        <span style="font-weight: 600; color: #2e7d32; font-size: 0.9rem;">配置檔案:</span>
                        <span style="font-weight: 700; color: #1b5e20; font-size: 1rem;" id="profileName">${data.profile || '預設配置'}</span>
                    </div>
                </div>
            `;
            
            // 插入到處理按鈕下方
            processSection.insertAdjacentElement('afterend', costContainer);
            
            // 滾動到結果
            costContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
            console.log('✅ 動態創建成本估算容器成功');
            
        } catch (error) {
            console.error('動態創建成本估算容器失敗:', error);
            this.showCostEstimateAlert(data);
        }
    }
    
    showCostEstimateAlert(data) {
        // 使用 alert 顯示成本估算結果
        const resultText = `
成本估算結果：
預估Token消耗: ${data.estimated_tokens.toLocaleString()}
預估成本: $${data.estimated_cost.toFixed(4)}
處理時間: ${data.estimated_time} 秒
檔案大小: ${this.formatFileSize(data.file_size)}
AI模型: ${data.model || '未知模型'}
配置檔案: ${data.profile || '預設配置'}
        `;
        alert(resultText);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    downloadResult() {
        if (this.downloadUrl) {
            window.open(this.downloadUrl, '_blank');
        } else {
            const errorMsg = currentLang === 'en' ? 'No results available for download' : '沒有可下載的結果';
            this.showError(errorMsg);
        }
    }

    // 學習功能暫時停用
    /*
    showLearnModal() {
        const modal = document.getElementById('learnModal');
        modal.style.display = 'flex';
    }

    closeLearnModal() {
        const modal = document.getElementById('learnModal');
        modal.style.display = 'none';
    }
    */

    // 學習功能暫時停用
    /*
    async submitLearning() {
        const currentMode = this.currentLearnMode || 'json';
        
        if (currentMode === 'json') {
            await this.submitJsonLearning();
        } else if (currentMode === 'word') {
            await this.submitWordLearning();
        }
    }
    
    async submitJsonLearning() {
        const correctedData = document.getElementById('correctedData').value;

        if (!correctedData.trim()) {
            const errorMsg = currentLang === 'en' ? 'Please enter corrected data' : '請輸入修正後的資料';
            this.showError(errorMsg);
            return;
        }

        try {
            const originalData = this.lastProcessedData;
            const profile = this.currentWork ? this.currentWork.profile : '';
            
            // 根據是否有工作流程來決定profile參數
            let profileParam = '';
            if (typeof profile === 'object' && profile && profile.name) {
                profileParam = profile.name;
            } else if (typeof profile === 'string') {
                profileParam = profile;
            } else {
                profileParam = null;
            }

            const response = await fetch('/learn', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    original_data: originalData,
                    corrected_data: JSON.parse(correctedData),
                    source_file: this.uploadedFiles[0].path,
                    profile: profileParam
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess('學習完成，Profile已更新');
                this.closeLearnModal();
            } else {
                this.showError(data.error || '學習失敗');
            }
        } catch (error) {
            console.error('學習錯誤:', error);
            this.showError('學習失敗');
        }
    }
    
    async submitWordLearning() {
        const wordFile = document.getElementById('wordFileInput').files[0];
        
        if (!wordFile) {
            const errorMsg = currentLang === 'en' ? 'Please select a Word document' : '請選擇Word文檔';
            this.showError(errorMsg);
            return;
        }

        try {
            const originalData = this.lastProcessedData;
            const profile = this.currentWork ? this.currentWork.profile : '';
            
            // 根據是否有工作流程來決定profile參數
            let profileParam = '';
            if (typeof profile === 'object' && profile && profile.name) {
                profileParam = profile.name;
            } else if (typeof profile === 'string') {
                profileParam = profile;
            } else {
                profileParam = null;
            }
            
            const formData = new FormData();
            formData.append('file', wordFile);
            formData.append('original_data', JSON.stringify(originalData));
            formData.append('source_file', this.uploadedFiles[0].path);
            formData.append('profile', profileParam);

            const response = await fetch('/learn/word', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess('學習完成，Profile已更新');
                this.closeLearnModal();
            } else {
                this.showError(data.error || '學習失敗');
            }
        } catch (error) {
            console.error('學習錯誤:', error);
            this.showError('學習失敗');
        }
    }
    */

    showError(message, errors = null) {
        // 如果有詳細錯誤列表，顯示更詳細的訊息
        if (errors && Array.isArray(errors) && errors.length > 0) {
            this.showDetailedError(message, errors);
        } else {
            alert('錯誤: ' + message);
        }
    }

    showDetailedError(message, errors) {
        // 創建詳細錯誤模態框
        const modal = document.createElement('div');
        modal.className = 'error-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;

        const content = document.createElement('div');
        content.style.cssText = `
            background: white;
            border-radius: 8px;
            padding: 20px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        `;

        const title = document.createElement('h3');
        title.textContent = '❌ 處理失敗';
        title.style.cssText = `
            color: #dc3545;
            margin: 0 0 15px 0;
            font-size: 18px;
        `;

        const mainMessage = document.createElement('p');
        mainMessage.textContent = message;
        mainMessage.style.cssText = `
            margin: 0 0 15px 0;
            font-weight: bold;
        `;

        const errorList = document.createElement('div');
        errorList.style.cssText = `
            margin: 15px 0;
        `;

        const errorTitle = document.createElement('h4');
        errorTitle.textContent = '詳細錯誤訊息：';
        errorTitle.style.cssText = `
            margin: 0 0 10px 0;
            color: #333;
            font-size: 14px;
        `;

        const errorItems = document.createElement('ul');
        errorItems.style.cssText = `
            margin: 0;
            padding-left: 20px;
            color: #666;
        `;

        errors.forEach(error => {
            const li = document.createElement('li');
            li.textContent = error;
            li.style.cssText = `
                margin: 5px 0;
                line-height: 1.4;
            `;
            errorItems.appendChild(li);
        });

        errorList.appendChild(errorTitle);
        errorList.appendChild(errorItems);

        const closeBtn = document.createElement('button');
        closeBtn.textContent = '確定';
        closeBtn.style.cssText = `
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            float: right;
            margin-top: 15px;
        `;

        closeBtn.onclick = () => {
            document.body.removeChild(modal);
        };

        content.appendChild(title);
        content.appendChild(mainMessage);
        content.appendChild(errorList);
        content.appendChild(closeBtn);

        modal.appendChild(content);
        document.body.appendChild(modal);

        // 點擊背景關閉
        modal.onclick = (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        };
    }

    showSuccess(message) {
        // 簡單的成功提示，可以改為更美觀的提示框
        const prefix = this.currentLanguage === 'en' ? 'Success: ' : '成功: ';
        alert(prefix + message);
    }

    showLoadingIndicator(message = '載入中...') {
        // 創建載入指示器
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loadingIndicator';
        loadingDiv.className = 'loading-indicator';
        loadingDiv.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <div class="loading-text">${message}</div>
            </div>
        `;
        
        // 添加到頁面
        document.body.appendChild(loadingDiv);
    }

    hideLoadingIndicator() {
        const loadingDiv = document.getElementById('loadingIndicator');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }


    parsePageNumbers(input) {
        const pageNumbers = new Set();
        const parts = input.split(',');
        
        for (const part of parts) {
            const trimmed = part.trim();
            if (trimmed.includes('-')) {
                // 處理範圍，如 "5-8"
                const range = trimmed.split('-');
                if (range.length !== 2) {
                    throw new Error(`無效的範圍格式: ${trimmed}`);
                }
                const start = parseInt(range[0].trim());
                const end = parseInt(range[1].trim());
                
                if (isNaN(start) || isNaN(end) || start > end) {
                    throw new Error(`無效的範圍: ${trimmed}`);
                }
                
                for (let i = start; i <= end; i++) {
                    pageNumbers.add(i);
                }
            } else {
                // 處理單個頁碼
                const page = parseInt(trimmed);
                if (isNaN(page) || page < 1) {
                    throw new Error(`無效的頁碼: ${trimmed}`);
                }
                pageNumbers.add(page);
            }
        }
        
        return Array.from(pageNumbers).sort((a, b) => a - b);
    }

    resetPageSelection() {
        // 清空輸入框
        const input = document.getElementById('pageNumbersInput');
        if (input) {
            input.value = '';
        }
        
        // 隱藏選擇摘要
        const summary = document.getElementById('selectionSummary');
        if (summary) {
            summary.style.display = 'none';
        }
        
        // 清空選擇摘要計數
        const countElement = document.getElementById('selectedPagesCount');
        if (countElement) {
            countElement.textContent = '0';
        }
    }

    restorePageSelection() {
        if (!this.currentFileId) return;
        
        // 獲取之前保存的選擇
        const selectedPages = this.selectedPagesMap[this.currentFileId] || [];
        
        // 恢復輸入框內容
        const input = document.getElementById('pageNumbersInput');
        if (input && selectedPages.length > 0) {
            // 將頁面數組轉換為範圍字符串
            const pageRanges = this.pagesToRanges(selectedPages);
            input.value = pageRanges;
        } else if (input) {
            input.value = '';
        }
        
        // 更新選擇摘要
        this.updatePageSelectionSummary();
    }

    pagesToRanges(pages) {
        if (!pages || pages.length === 0) return '';
        
        // 排序頁面數組
        const sortedPages = [...pages].sort((a, b) => a - b);
        const ranges = [];
        let start = sortedPages[0];
        let end = sortedPages[0];
        
        for (let i = 1; i < sortedPages.length; i++) {
            if (sortedPages[i] === end + 1) {
                end = sortedPages[i];
            } else {
                if (start === end) {
                    ranges.push(start.toString());
                } else {
                    ranges.push(`${start}-${end}`);
                }
                start = sortedPages[i];
                end = sortedPages[i];
            }
        }
        
        if (start === end) {
            ranges.push(start.toString());
        } else {
            ranges.push(`${start}-${end}`);
        }
        
        return ranges.join(',');
    }

    applyPageSelection() {
        const input = document.getElementById('pageNumbersInput');
        if (!input || !input.value.trim()) {
            this.showError('請輸入頁碼');
            return;
        }

        try {
            const pageNumbers = this.parsePageNumbers(input.value.trim());
            if (pageNumbers.length === 0) {
                this.showError('請輸入有效的頁碼');
                return;
            }

            // 基本頁碼驗證（只檢查是否為正整數）
            const invalidPages = pageNumbers.filter(page => page < 1 || !Number.isInteger(page));
            if (invalidPages.length > 0) {
                this.showError(`頁碼 ${invalidPages.join(', ')} 無效，請輸入正整數`);
                return;
            }

            // 應用頁面選擇
            this.selectedPagesMap[this.currentFileId] = pageNumbers;
            
            // 更新選擇摘要
            this.updatePageSelectionSummary();
            
            // 更新檔案列表
            this.updateFileList();
            
            const message = this.currentLanguage === 'en' 
                ? `Selected ${pageNumbers.length} pages`
                : `已選擇 ${pageNumbers.length} 個頁面`;
            this.showSuccess(message);
            
        } catch (error) {
            this.showError('頁碼格式錯誤：' + error.message);
        }
    }

    clearPageSelection() {
        console.log('clearPageSelection 被調用');
        // 清空頁面選擇
        if (this.currentFileId) {
            this.selectedPagesMap[this.currentFileId] = [];
            
            // 清空輸入框
            const input = document.getElementById('pageNumbersInput');
            if (input) {
                input.value = '';
                console.log('已清空輸入框');
            } else {
                console.error('找不到輸入框');
            }
            
            // 更新選擇摘要
            this.updatePageSelectionSummary();
            
            // 更新檔案列表
            this.updateFileList();
            
            this.showSuccess('已清空頁面選擇');
        } else {
            console.error('currentFileId 不存在');
        }
    }

    updatePageSelectionSummary() {
        const countElement = document.getElementById('selectedPagesCount');
        const summaryElement = document.getElementById('selectionSummary');
        
        if (!this.currentFileId || !this.selectedPagesMap[this.currentFileId]) {
            if (countElement) {
                countElement.textContent = '0';
            }
            if (summaryElement) {
                summaryElement.style.display = 'none';
            }
            return;
        }
        
        const selectedPages = this.selectedPagesMap[this.currentFileId];
        const count = selectedPages ? selectedPages.length : 0;
        
        if (countElement) {
            countElement.textContent = count.toString();
        }
        
        if (summaryElement) {
            summaryElement.style.display = count > 0 ? 'block' : 'none';
        }
    }



    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // 頁面選擇相關方法
    async openSingleFilePagePicker(fileId) {
        const file = this.uploadedFiles.find(f => f.id === fileId);
        if (!file) {
            this.showError('找不到指定的檔案');
            return;
        }

        // 設置當前檔案
        this.currentFileId = fileId;
        
        // 立即顯示頁面選擇模態框，不需要載入
        this.showSingleFilePageSelectionModal(file);
    }


    showSingleFilePageSelectionModal(file) {
        const modal = document.getElementById('pageSelectionModal');
        if (!modal) {
            console.error('找不到頁面選擇模態框');
            return;
        }
        
        modal.style.display = 'flex';
        
        // 設置檔案信息
        const fileNameElement = document.getElementById('currentFileName');
        if (fileNameElement) {
            fileNameElement.textContent = file.name;
        }
        
        // 恢復之前保存的選擇
        this.restorePageSelection();
        
        // 更新頁面選擇摘要
        this.updatePageSelectionSummary();
        
        // 設置預設頁面範圍提示（基於檔案大小估算）
        const fileSize = file.size || 0;
        let estimatedPages = 1;
        
        // 簡單的頁面估算：每頁約50KB
        if (fileSize > 0) {
            estimatedPages = Math.max(1, Math.ceil(fileSize / 50000));
        }
        
        // 如果沒有保存的選擇，顯示預設範圍
        const input = document.getElementById('pageNumbersInput');
        if (input && !input.value) {
            const placeholderText = currentLang === 'en' 
                ? `e.g.: 1-${estimatedPages} (estimated ${estimatedPages} pages)`
                : `例如: 1-${estimatedPages} (預估 ${estimatedPages} 頁)`;
            input.placeholder = placeholderText;
        }
    }


    updateCurrentFileSelectionSummary() {
        if (!this.currentFileId) return;
        
        const selectedPages = this.selectedPagesMap[this.currentFileId] || [];
        const selectedPagesCountElement = document.getElementById('selectedPagesCount');
        
        if (selectedPagesCountElement) {
            selectedPagesCountElement.textContent = selectedPages.length;
        }
    }


    async loadFilePages(fileId) {
        // 檢查是否已經載入過
        if (this.pagePreviewData[fileId]) {
            return;
        }
        
        try {
            // 載入完整頁面資料（用於成本估算）
            const response = await fetch('/api/pages/preview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    file_id: fileId
                })
            });

            const data = await response.json();
            if (data.success) {
                this.pagePreviewData[fileId] = {
                    file_type: data.file_type,
                    total_pages: data.total_pages || 0,
                    pages: data.pages || []
                };
            } else {
                throw new Error(data.error || '載入檔案資訊失敗');
            }
            
        } catch (error) {
            console.error(`載入檔案 ${fileId} 資訊失敗:`, error);
            // 如果API失敗，使用預設值
            this.pagePreviewData[fileId] = {
                file_type: 'pdf',
                total_pages: 1,
                pages: [{ page_number: 1, content: '', content_length: 0 }]
            };
        }
    }


    togglePageSelection(fileId, pageNumber) {
        if (!this.selectedPagesMap[fileId]) {
            this.selectedPagesMap[fileId] = [];
        }

        const index = this.selectedPagesMap[fileId].indexOf(pageNumber);
        if (index > -1) {
            this.selectedPagesMap[fileId].splice(index, 1);
        } else {
            this.selectedPagesMap[fileId].push(pageNumber);
        }

        // 更新頁面卡片狀態
        const pagesGrid = document.getElementById(`pagesGrid_${fileId}`);
        if (pagesGrid) {
            const pageCards = pagesGrid.querySelectorAll('.page-card');
            pageCards.forEach(card => {
                const pageNumberElement = card.querySelector('.page-number');
                if (pageNumberElement) {
                    const pageNum = parseInt(pageNumberElement.textContent.match(/\d+/)[0]);
                    const isSelected = this.selectedPagesMap[fileId].includes(pageNum);
                    card.classList.toggle('selected', isSelected);
                    const checkbox = card.querySelector('input[type="checkbox"]');
                    if (checkbox) {
                        checkbox.checked = isSelected;
                    }
                }
            });
        }

        // 更新選擇摘要
        this.updateSelectionSummary();
        
        // 如果是當前檔案的頁面選擇，也更新當前檔案的摘要
        if (fileId === this.currentFileId) {
            this.updateCurrentFileSelectionSummary();
            this.updateFileList(); // 更新檔案列表顯示
        }
    }

    selectAllCurrentFilePages() {
        if (!this.currentFileId) return;
        
        const previewData = this.pagePreviewData[this.currentFileId];
        if (previewData && previewData.pages) {
            this.selectedPagesMap[this.currentFileId] = previewData.pages.map(page => page.page_number);
            
            // 更新頁面卡片狀態
            const pagesGrid = document.getElementById('currentFilePagesGrid');
            if (pagesGrid) {
                const pageCards = pagesGrid.querySelectorAll('.page-card');
                pageCards.forEach(card => {
                    card.classList.add('selected');
                    const checkbox = card.querySelector('input[type="checkbox"]');
                    if (checkbox) {
                        checkbox.checked = true;
                    }
                });
            }
            
            this.updateCurrentFileSelectionSummary();
            this.updateFileList(); // 更新檔案列表顯示
        } else {
            console.warn(`檔案 ${this.currentFileId} 的頁面資料尚未載入`);
        }
    }

    deselectAllCurrentFilePages() {
        if (!this.currentFileId) return;
        
        this.selectedPagesMap[this.currentFileId] = [];
        
        // 更新頁面卡片狀態
        const pagesGrid = document.getElementById('currentFilePagesGrid');
        if (pagesGrid) {
            const pageCards = pagesGrid.querySelectorAll('.page-card');
            pageCards.forEach(card => {
                card.classList.remove('selected');
                const checkbox = card.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.checked = false;
                }
            });
        }
        
        this.updateCurrentFileSelectionSummary();
        this.updateFileList(); // 更新檔案列表顯示
    }

    updateSelectionSummary() {
        const filesWithPages = Object.keys(this.selectedPagesMap).filter(fileId => 
            this.selectedPagesMap[fileId] && this.selectedPagesMap[fileId].length > 0
        );
        const totalPages = Object.values(this.selectedPagesMap).reduce((sum, pages) => sum + (pages ? pages.length : 0), 0);
        
        const selectedPagesCountElement = document.getElementById('selectedPagesCount');
        const totalSelectedPagesElement = document.getElementById('totalSelectedPages');
        
        if (selectedPagesCountElement) {
            selectedPagesCountElement.textContent = filesWithPages.length;
        }
        if (totalSelectedPagesElement) {
            totalSelectedPagesElement.textContent = totalPages;
        }
    }


    confirmPageSelection() {
        // 關閉模態框
        this.closePageSelectionModal();
        
        // 顯示選擇結果
        const totalSelected = Object.values(this.selectedPagesMap).reduce((sum, pages) => sum + (pages ? pages.length : 0), 0);
        const notificationMsg = currentLang === 'en' 
            ? `Selected ${totalSelected} pages for processing`
            : `已選擇 ${totalSelected} 個頁面進行處理`;
        showNotification(notificationMsg, 'success');
        
        // 重新計算成本估算
        this.updateCostEstimate();
        
        // 更新檔案列表顯示
        this.updateFileList();
    }

    closePageSelectionModal() {
        const modal = document.getElementById('pageSelectionModal');
        modal.style.display = 'none';
    }

    updateCostEstimate() {
        // 如果有成本估算面板，重新計算
        const costContainer = document.getElementById('costEstimateContainer');
        if (costContainer && costContainer.style.display !== 'none') {
            this.estimateCost();
        }
    }

    // 工作流程偏好設定管理
    async loadWorkflowPreferences(workId) {
        // 載入工作流程偏好設定
        try {
            const response = await fetch(`/api/workflow-preferences/${workId}`);
            const data = await response.json();
            
            if (data.success) {
                this.workflowPreferences[workId] = data.preferences;
                console.log(`已載入工作流程 ${workId} 的偏好設定:`, data.preferences);
                return data.preferences;
            } else {
                console.warn(`載入工作流程 ${workId} 偏好設定失敗:`, data.error);
                return {};
            }
        } catch (error) {
            console.error(`載入工作流程 ${workId} 偏好設定錯誤:`, error);
            return {};
        }
    }

    async saveWorkflowPreferences(workId, preferences) {
        // 保存工作流程偏好設定
        try {
            const response = await fetch(`/api/workflow-preferences/${workId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ preferences: preferences })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.workflowPreferences[workId] = preferences;
                console.log(`已保存工作流程 ${workId} 的偏好設定:`, preferences);
                return true;
            } else {
                console.error(`保存工作流程 ${workId} 偏好設定失敗:`, data.error);
                return false;
            }
        } catch (error) {
            console.error(`保存工作流程 ${workId} 偏好設定錯誤:`, error);
            return false;
        }
    }

    async updateWorkflowPreference(workId, key, value) {
        // 更新工作流程單個偏好設定
        try {
            const response = await fetch(`/api/workflow-preferences/${workId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ key: key, value: value })
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (!this.workflowPreferences[workId]) {
                    this.workflowPreferences[workId] = {};
                }
                this.workflowPreferences[workId][key] = value;
                console.log(`已更新工作流程 ${workId} 的偏好設定 ${key}:`, value);
                return true;
            } else {
                console.error(`更新工作流程 ${workId} 偏好設定失敗:`, data.error);
                return false;
            }
        } catch (error) {
            console.error(`更新工作流程 ${workId} 偏好設定錯誤:`, error);
            return false;
        }
    }

    getCurrentPreferences() {
        // 獲取當前工作流程的偏好設定
        if (!this.currentWork) return {};
        return this.workflowPreferences[this.currentWork.id] || {};
    }

    async applyWorkflowPreferences(workId) {
        // 應用工作流程偏好設定到界面
        const preferences = await this.loadWorkflowPreferences(workId);
        
        if (Object.keys(preferences).length === 0) {
            console.log(`工作流程 ${workId} 沒有偏好設定，使用預設值`);
            return;
        }

        console.log(`應用工作流程 ${workId} 的偏好設定:`, preferences);

        // 應用AI設定
        if (preferences.ai_provider) {
            const providerSelect = document.getElementById('workflowAiProvider');
            if (providerSelect) {
                providerSelect.value = preferences.ai_provider;
                this.updateWorkflowModelOptions();
            }
        }

        if (preferences.ai_model) {
            const modelSelect = document.getElementById('workflowAiModel');
            if (modelSelect) {
                modelSelect.value = preferences.ai_model;
            }
        }

        // 應用輸出格式
        if (preferences.output_format) {
            const formatSelect = document.getElementById('formatSelect');
            if (formatSelect) {
                formatSelect.value = preferences.output_format;
            }
        }

        // 應用輸出資料夾
        if (preferences.output_folder) {
            const outputFolder = document.getElementById('outputFolder');
            if (outputFolder) {
                outputFolder.value = preferences.output_folder;
            }
        }

        // 應用頁面選擇
        if (preferences.default_pages && Array.isArray(preferences.default_pages)) {
            // 這裡可以根據需要應用預設頁面選擇
            console.log('應用預設頁面選擇:', preferences.default_pages);
        }

        console.log(`工作流程 ${workId} 的偏好設定已應用到界面`);
    }

    async saveCurrentPreferences() {
        // 保存當前界面設定為工作流程偏好
        if (!this.currentWork) {
            console.warn('沒有選中的工作流程，無法保存偏好設定');
            return false;
        }

        const preferences = {
            ai_provider: document.getElementById('workflowAiProvider')?.value || '',
            ai_model: document.getElementById('workflowAiModel')?.value || '',
            output_format: document.getElementById('formatSelect')?.value || 'docx',
            output_folder: document.getElementById('outputFolder')?.value || 'output',
            auto_cost_estimate: true,
            page_selection_mode: 'manual',
            default_pages: Object.values(this.selectedPagesMap).flat(),
            cost_threshold: 1.0,
            context_window_warning: 80,
            auto_save_preferences: true,
            show_advanced_options: false,
            last_used: new Date().toISOString()
        };

        const success = await this.saveWorkflowPreferences(this.currentWork.id, preferences);
        
        if (success) {
            showNotification('偏好設定已保存', 'success');
        } else {
            showNotification('偏好設定保存失敗', 'error');
        }

        return success;
    }

    setupPreferenceAutoSave() {
        // 設置偏好設定自動保存
        // 監聽AI提供者變更
        const providerSelect = document.getElementById('workflowAiProvider');
        if (providerSelect) {
            providerSelect.addEventListener('change', () => {
                if (this.currentWork) {
                    this.updateWorkflowPreference(this.currentWork.id, 'ai_provider', providerSelect.value);
                }
            });
        }

        // 監聽AI模型變更
        const modelSelect = document.getElementById('workflowAiModel');
        if (modelSelect) {
            modelSelect.addEventListener('change', () => {
                if (this.currentWork) {
                    this.updateWorkflowPreference(this.currentWork.id, 'ai_model', modelSelect.value);
                }
            });
        }

        // 監聽輸出格式變更
        const formatSelect = document.getElementById('formatSelect');
        if (formatSelect) {
            formatSelect.addEventListener('change', () => {
                if (this.currentWork) {
                    this.updateWorkflowPreference(this.currentWork.id, 'output_format', formatSelect.value);
                }
            });
        }

        // 監聽輸出資料夾變更
        const outputFolder = document.getElementById('outputFolder');
        if (outputFolder) {
            outputFolder.addEventListener('change', () => {
                if (this.currentWork) {
                    this.updateWorkflowPreference(this.currentWork.id, 'output_folder', outputFolder.value);
                }
            });
        }

        console.log('偏好設定自動保存已設置');
    }
}

// 全域函數
function openFolder(folderType) {
    // 顯示載入狀態
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 開啟中...';
    button.disabled = true;
    
    fetch(`/api/open-folder/${folderType}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 成功開啟資料夾
                button.innerHTML = '<i class="fas fa-check"></i> 已開啟';
                button.style.backgroundColor = '#28a745';
                
                // 顯示成功訊息
                showNotification(`已開啟 ${folderType} 資料夾`, 'success');
                
                // 2秒後恢復按鈕狀態
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.style.backgroundColor = '';
                    button.disabled = false;
                }, 2000);
            } else {
                // 顯示錯誤訊息
                button.innerHTML = originalText;
                button.disabled = false;
                showNotification('開啟資料夾失敗: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('開啟資料夾錯誤:', error);
            button.innerHTML = originalText;
            button.disabled = false;
            showNotification('開啟資料夾失敗，請檢查資料夾是否存在', 'error');
        });
}

// 顯示通知訊息
function showNotification(message, type = 'info') {
    // 創建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // 添加樣式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1'};
        color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#0c5460'};
        border: 1px solid ${type === 'success' ? '#c3e6cb' : type === 'error' ? '#f5c6cb' : '#bee5eb'};
        border-radius: 8px;
        padding: 15px 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 14px;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
    `;
    
    // 添加動畫樣式
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    
    // 添加到頁面
    document.body.appendChild(notification);
    
    // 3秒後自動移除
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function showWorkspaceInfo() {
    // 顯示載入狀態
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 載入中...';
    button.disabled = true;
    
    fetch('/api/workspace-info')
        .then(response => response.json())
        .then(data => {
            button.innerHTML = originalText;
            button.disabled = false;
            
            if (data.success) {
                const info = data.workspace_info;
                showWorkspaceModal(info);
            } else {
                showNotification('獲取工作空間資訊失敗: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('獲取工作空間資訊錯誤:', error);
            button.innerHTML = originalText;
            button.disabled = false;
            showNotification('獲取工作空間資訊失敗', 'error');
        });
}

function showWorkspaceModal(info) {
    // 創建模態框
    const modal = document.createElement('div');
    modal.className = 'workspace-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="closeWorkspaceModal()"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="fas fa-info-circle"></i> 工作空間資訊</h3>
                <button class="close-btn" onclick="closeWorkspaceModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="info-section">
                    <h4><i class="fas fa-folder"></i> 基本資訊</h4>
                    <div class="info-item">
                        <label>工作目錄:</label>
                        <span class="path-value">${info.workspace_dir}</span>
                    </div>
                    <div class="info-item">
                        <label>桌面環境:</label>
                        <span class="status-badge ${info.is_desktop_environment ? 'success' : 'warning'}">
                            ${info.is_desktop_environment ? '是' : '否'}
                        </span>
                    </div>
                </div>
                
                <div class="info-section">
                    <h4><i class="fas fa-folder-open"></i> 資料夾路徑</h4>
                    <div class="folder-list">
                        <div class="folder-item">
                            <i class="fas fa-upload"></i>
                            <span class="folder-name">輸入資料夾</span>
                            <span class="folder-path">${info.directories.input}</span>
                        </div>
                        <div class="folder-item">
                            <i class="fas fa-download"></i>
                            <span class="folder-name">輸出資料夾</span>
                            <span class="folder-path">${info.directories.output}</span>
                        </div>
                        <div class="folder-item">
                            <i class="fas fa-file-alt"></i>
                            <span class="folder-name">模板資料夾</span>
                            <span class="folder-path">${info.directories.template}</span>
                        </div>
                        <div class="folder-item">
                            <i class="fas fa-archive"></i>
                            <span class="folder-name">快取資料夾</span>
                            <span class="folder-path">${info.directories.cache}</span>
                        </div>
                    </div>
                </div>
                
                <div class="info-section">
                    <h4><i class="fas fa-lightbulb"></i> 使用提示</h4>
                    <ul class="tips-list">
                        <li>您可以直接雙擊桌面上的快捷方式來開啟對應的資料夾</li>
                        <li>將要處理的檔案放入「輸入資料夾」</li>
                        <li>處理完成的檔案會出現在「輸出資料夾」</li>
                        <li>可以在「模板資料夾」中自定義輸出格式</li>
                    </ul>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-primary" onclick="closeWorkspaceModal()">關閉</button>
            </div>
        </div>
    `;
    
    // 添加樣式
    const style = document.createElement('style');
    style.textContent = `
        .workspace-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2000;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .modal-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(5px);
        }
        
        .modal-content {
            position: relative;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            animation: modalSlideIn 0.3s ease-out;
        }
        
        @keyframes modalSlideIn {
            from { transform: scale(0.8) translateY(-50px); opacity: 0; }
            to { transform: scale(1) translateY(0); opacity: 1; }
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 25px;
            border-bottom: 1px solid #e0e0e0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px 15px 0 0;
        }
        
        .modal-header h3 {
            margin: 0;
            font-size: 1.3rem;
        }
        
        .modal-header h3 i {
            margin-right: 10px;
        }
        
        .close-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.2rem;
            cursor: pointer;
            padding: 5px;
            border-radius: 50%;
            transition: background 0.3s ease;
        }
        
        .close-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .modal-body {
            padding: 25px;
        }
        
        .info-section {
            margin-bottom: 25px;
        }
        
        .info-section h4 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
        }
        
        .info-section h4 i {
            margin-right: 8px;
            color: #667eea;
        }
        
        .info-item {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .info-item label {
            font-weight: 600;
            min-width: 100px;
            color: #555;
        }
        
        .path-value {
            font-family: 'Courier New', monospace;
            background: #e9ecef;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.9rem;
            word-break: break-all;
        }
        
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .status-badge.success {
            background: #d4edda;
            color: #155724;
        }
        
        .status-badge.warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .folder-list {
            display: grid;
            gap: 10px;
        }
        
        .folder-item {
            display: flex;
            align-items: center;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .folder-item i {
            margin-right: 12px;
            color: #667eea;
            font-size: 1.1rem;
        }
        
        .folder-name {
            font-weight: 600;
            min-width: 100px;
            color: #333;
        }
        
        .folder-path {
            font-family: 'Courier New', monospace;
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
            word-break: break-all;
            margin-left: auto;
        }
        
        .tips-list {
            list-style: none;
            padding: 0;
        }
        
        .tips-list li {
            padding: 8px 0;
            padding-left: 20px;
            position: relative;
            color: #666;
            line-height: 1.5;
        }
        
        .tips-list li:before {
            content: "💡";
            position: absolute;
            left: 0;
        }
        
        .modal-footer {
            padding: 20px 25px;
            border-top: 1px solid #e0e0e0;
            text-align: right;
        }
    `;
    document.head.appendChild(style);
    
    // 添加到頁面
    document.body.appendChild(modal);
}

function closeWorkspaceModal() {
    const modal = document.querySelector('.workspace-modal');
    if (modal) {
        modal.style.animation = 'modalSlideOut 0.3s ease-in';
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    }
}

// 全域函數
// 學習功能暫時停用
/*
function closeLearnModal() {
    prodocux.closeLearnModal();
}

function submitLearning() {
    prodocux.submitLearning();
}
*/

// 頁面選擇相關全域函數

function closePageSelectionModal() {
    prodocux.closePageSelectionModal();
}

function confirmPageSelection() {
    prodocux.confirmPageSelection();
}

function showCreateWorkModal() {
    const modal = document.getElementById('createWorkModal');
    modal.style.display = 'flex';
    
    // 載入工作模板列表和提示詞列表
    loadWorkTemplates();
    loadWorkPrompts();
    loadWorkProfiles();
    
    console.log('工作創建模態框已打開，開始載入選項...');
}

// 載入工作模板列表
async function loadWorkTemplates() {
    try {
        const response = await fetch('/api/templates');
        const data = await response.json();
        
        if (data.success) {
            const workTemplateSelect = document.getElementById('workTemplateSelect');
            if (!workTemplateSelect) {
                console.warn('找不到 workTemplateSelect 元素，可能不在當前頁面');
                return;
            }
            workTemplateSelect.innerHTML = '<option value="">使用預設模板</option>';
            
            data.templates.forEach(template => {
                const option = document.createElement('option');
                option.value = template.filename;
                option.textContent = template.name || template.filename;
                workTemplateSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('載入工作模板列表失敗:', error);
    }
}

function closeCreateWorkModal() {
    const modal = document.getElementById('createWorkModal');
    modal.style.display = 'none';
    // 清空表單
    document.getElementById('workNameInput').value = '';
    document.getElementById('workDescriptionInput').value = '';
    document.getElementById('workTypeSelect').value = '';
    document.getElementById('brandInput').value = '';
    document.getElementById('workProfileSelect').innerHTML = '<option value="">使用預設配置</option>';
    document.getElementById('workTemplateSelect').innerHTML = '<option value="">使用預設模板</option>';
    document.getElementById('workPromptSelect').innerHTML = '<option value="">使用預設提示詞</option>';
}

// 已移除推薦配置下拉框，系統會自動處理配置推薦

async function createWorkOld() {
    const workName = document.getElementById('workNameInput').value.trim();
    const workDescription = document.getElementById('workDescriptionInput').value.trim();
    const workType = document.getElementById('workTypeSelect').value;
    const brand = document.getElementById('brandInput').value.trim();
    const workProfile = document.getElementById('workProfileSelect').value;
    const workTemplate = document.getElementById('workTemplateSelect').value;
    const workPrompt = document.getElementById('workPromptSelect').value;
    
    console.log('創建工作時的設定:', {
        workName, workDescription, workType, brand, 
        workProfile, workTemplate, workPrompt
    });
    
    if (!workName || !workType) {
        const message = currentLang === 'en' ? 'Please fill in work name and type' : '請填寫工作名稱和類型';
        alert(message);
        return;
    }
    
    try {
        const response = await fetch('/api/works', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: workName,
                description: workDescription,
                type: workType,
                brand: brand,
                profile: workProfile,
                template: workTemplate,
                prompt: workPrompt
            })
        });
        
        const data = await response.json();
        console.log('API 響應數據:', data);
        console.log('工作創建時的提示詞設定:', workPrompt);
        
        if (data.success) {
            console.log('工作創建成功，開始載入工作列表...');
            console.log('創建的工作數據:', data.work);
            
            // 重新載入工作列表
            await prodocux.loadWorks();
            console.log('工作列表載入完成');
            
            // 選擇新創建的工作
            console.log('選擇工作 ID:', data.work.id);
            prodocux.selectWork(data.work.id);
            console.log('工作選擇完成');
            
            // 關閉模態框
            closeCreateWorkModal();
            
            prodocux.showSuccess('工作創建成功！');
        } else {
            console.log('API 返回錯誤:', data.error);
            prodocux.showError(data.error || '工作創建失敗');
        }
    } catch (error) {
        console.error('創建工作錯誤:', error);
        prodocux.showError('工作創建失敗');
    }
}

function switchLearnTab(mode) {
    // 切換標籤按鈕狀態
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // 切換學習模式
    const jsonMode = document.getElementById('jsonLearnMode');
    const wordMode = document.getElementById('wordLearnMode');
    
    if (mode === 'json') {
        jsonMode.style.display = 'block';
        wordMode.style.display = 'none';
        prodocux.currentLearnMode = 'json';
    } else if (mode === 'word') {
        jsonMode.style.display = 'none';
        wordMode.style.display = 'block';
        prodocux.currentLearnMode = 'word';
    }
}

function removeWordFile() {
    const wordFileInput = document.getElementById('wordFileInput');
    const wordFileInfo = document.getElementById('wordFileInfo');
    const wordUploadArea = document.getElementById('wordUploadArea');
    
    wordFileInput.value = '';
    wordFileInfo.style.display = 'none';
    wordUploadArea.style.display = 'block';
}

// Word檔案上傳處理
document.addEventListener('DOMContentLoaded', function() {
    const wordFileInput = document.getElementById('wordFileInput');
    const wordUploadArea = document.getElementById('wordUploadArea');
    const wordFileInfo = document.getElementById('wordFileInfo');
    const wordFileName = document.getElementById('wordFileName');
    
    if (wordFileInput) {
        wordFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                wordFileName.textContent = file.name;
                wordFileInfo.style.display = 'flex';
                wordUploadArea.style.display = 'none';
            }
        });
    }
    
    // 初始化安全檢查監控
    setupProfileChangeMonitoring();
    setupPromptChangeMonitoring();
    
    // 初始化安全檢查模型選項
    initializeSafetyModelOptions();
    
    // 拖拽上傳
    if (wordUploadArea) {
        wordUploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.currentTarget.classList.add('dragover');
        });
        
        wordUploadArea.addEventListener('dragleave', function(e) {
            e.currentTarget.classList.remove('dragover');
        });
        
        wordUploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            e.currentTarget.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.name.toLowerCase().endsWith('.docx')) {
                    wordFileInput.files = files;
                    wordFileName.textContent = file.name;
                    wordFileInfo.style.display = 'flex';
                    wordUploadArea.style.display = 'none';
                } else {
                    const message = currentLang === 'en' ? 'Please select DOCX format Word document' : '請選擇DOCX格式的Word文檔';
                    alert(message);
                }
            }
        });
    }
});

// 初始化應用
// 輸出資料夾選擇功能
function selectOutputFolder() {
    // 創建隱藏的檔案輸入元素
    const input = document.createElement('input');
    input.type = 'file';
    input.webkitdirectory = true;
    input.style.display = 'none';
    
    input.addEventListener('change', function(e) {
        const files = e.target.files;
        if (files.length > 0) {
            // 獲取選擇的資料夾路徑
            const folderPath = files[0].webkitRelativePath.split('/')[0];
            document.getElementById('outputFolder').value = folderPath;
            
            // 更新 ProDocuX 實例的輸出資料夾設定
            if (prodocux) {
                prodocux.outputFolder = folderPath;
            }
        }
    });
    
    // 觸發檔案選擇對話框
    document.body.appendChild(input);
    input.click();
    document.body.removeChild(input);
}

// 初始化預設輸出資料夾和模板
document.addEventListener('DOMContentLoaded', function() {
    // 設定預設輸出資料夾
    const outputFolder = document.getElementById('outputFolder');
    if (outputFolder) {
        outputFolder.value = 'output'; // 預設使用工作空間的 output 資料夾
    }
    
    // 載入模板列表和提示詞列表
    loadTemplates();
    loadPrompts();
});

// 載入模板列表
async function loadTemplates() {
    try {
        console.log('開始載入模板列表...');
        const response = await fetch('/api/templates');
        console.log('模板API響應狀態:', response.status);
        
        const data = await response.json();
        console.log('模板API響應數據:', data);
        
        if (data.success) {
            // templateSelect 元素已經被移除，不再需要載入
            console.log(`已載入 ${data.templates ? data.templates.length : 0} 個模板（新界面不再需要下拉選單）`);
        } else {
            console.error('模板API返回錯誤:', data.error);
        }
    } catch (error) {
        console.error('載入模板列表失敗:', error);
    }
}

// 上傳模板檔案
function uploadTemplate() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.docx,.doc,.pdf';
    input.style.display = 'none';
    
    input.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('template', file);
            
            try {
                const response = await fetch('/api/templates/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showNotification('模板上傳成功', 'success');
                    
                    // 更新當前工作的模板設定
                    if (prodocux && prodocux.currentWork) {
                        // 使用服務器返回的原始文件名
                        const templateName = data.filename || file.name;
                        prodocux.currentWork.template = templateName;
                        
                        // 更新顯示
                        prodocux.updateCurrentSettings();
                        
                        // 如果編輯工作模態框是打開的，也要更新顯示
                        await loadCurrentTemplateDisplay();
                        
                        showNotification(`模板已設定為: ${templateName}`, 'success');
                    }
                    
                    loadTemplates(); // 重新載入模板列表
                } else {
                    showNotification('模板上傳失敗: ' + data.error, 'error');
                }
            } catch (error) {
                console.error('模板上傳錯誤:', error);
                showNotification('模板上傳失敗', 'error');
            }
        }
    });
    
    document.body.appendChild(input);
    input.click();
    document.body.removeChild(input);
}

// 選擇模板檔案
function selectTemplate() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.docx,.doc,.pdf';
    input.style.display = 'none';
    
    input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // 更新 ProDocuX 實例的模板設定
            if (prodocux && prodocux.currentWork) {
                prodocux.currentWork.template = file.name;
                // 更新當前設定顯示
                prodocux.updateCurrentSettings();
            }
            
            showNotification('模板上傳成功: ' + file.name, 'success');
        }
    });
    
    document.body.appendChild(input);
    input.click();
    document.body.removeChild(input);
}

// 工作模板上傳
function uploadWorkTemplate() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.docx,.doc,.pdf';
    input.style.display = 'none';
    
    input.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('template', file);
            
            try {
                const response = await fetch('/api/templates/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // 更新工作模板選擇器
                    const workTemplateSelect = document.getElementById('workTemplateSelect');
                    const option = document.createElement('option');
                    option.value = file.name;
                    option.textContent = file.name;
                    workTemplateSelect.appendChild(option);
                    workTemplateSelect.value = file.name;
                    
                    showNotification('工作模板上傳成功', 'success');
                } else {
                    showNotification('工作模板上傳失敗: ' + data.error, 'error');
                }
            } catch (error) {
                console.error('工作模板上傳錯誤:', error);
                showNotification('工作模板上傳失敗', 'error');
            }
        }
    });
    
    document.body.appendChild(input);
    input.click();
    document.body.removeChild(input);
}

// 載入提示詞列表
async function loadPrompts() {
    try {
        console.log('開始載入提示詞列表...');
        const response = await fetch('/api/prompts');
        console.log('提示詞API響應狀態:', response.status);
        
        const data = await response.json();
        console.log('提示詞API響應數據:', data);
        
        if (data.success) {
            // promptSelect 元素已經被移除，不再需要載入下拉選單
            console.log(`已載入 ${data.prompts ? data.prompts.length : 0} 個提示詞（新界面不再需要下拉選單）`);
        } else {
            console.error('提示詞API返回錯誤:', data.error);
        }
    } catch (error) {
        console.error('載入提示詞列表失敗:', error);
    }
}

// 編輯提示詞
function editPrompt() {
    // 提示詞編輯功能已移至編輯工作模態框中
    showNotification('提示詞編輯功能已移至"編輯工作"面板中', 'info');
}

// 創建新提示詞
function createPrompt() {
    // 清空表單
    document.getElementById('promptNameInput').value = '';
    document.getElementById('promptDescriptionInput').value = '';
    document.getElementById('promptContentInput').value = '';
    document.getElementById('promptFieldsInput').value = '';
    
    showPromptModal('創建新提示詞');
}

// 顯示提示詞模態框
function showPromptModal(title) {
    document.getElementById('promptModalTitle').textContent = title;
    document.getElementById('promptModal').style.display = 'flex';
}

// 關閉提示詞模態框
function closePromptModal() {
    document.getElementById('promptModal').style.display = 'none';
}

// 載入提示詞內容
async function loadPromptContent(filename) {
    try {
        const response = await fetch(`/api/prompts/${filename}`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('promptNameInput').value = data.prompt.name || '';
            document.getElementById('promptDescriptionInput').value = data.prompt.description || '';
            document.getElementById('promptContentInput').value = data.prompt.content || '';
            document.getElementById('promptFieldsInput').value = data.prompt.fields ? data.prompt.fields.join(', ') : '';
        }
    } catch (error) {
        console.error('載入提示詞內容失敗:', error);
        showNotification('載入提示詞內容失敗', 'error');
    }
}

// 保存提示詞
async function savePrompt() {
    const name = document.getElementById('promptNameInput').value.trim();
    const description = document.getElementById('promptDescriptionInput').value.trim();
    const content = document.getElementById('promptContentInput').value.trim();
    const fields = document.getElementById('promptFieldsInput').value.trim();
    
    if (!name || !content) {
        showNotification('請填寫提示詞名稱和內容', 'warning');
        return;
    }
    
    try {
        const promptData = {
            name: name,
            description: description,
            content: content,
            fields: fields ? fields.split(',').map(f => f.trim()) : []
        };
        
        const response = await fetch('/api/prompts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(promptData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('提示詞保存成功', 'success');
            closePromptModal();
            
            // 重新載入提示詞列表
            await loadPrompts();
            
            // promptSelect 元素已移除，不再需要自動選擇
            console.log('新提示詞創建成功:', data.filename);
            
            // 同時更新工作流程編輯頁面的提示詞選擇
            const editWorkPromptSelect = document.getElementById('editWorkPromptSelect');
            if (editWorkPromptSelect && data.filename) {
                editWorkPromptSelect.value = data.filename;
                console.log('已更新工作流程編輯頁面的提示詞選擇:', data.filename);
            }
            
            // 同時更新工作流程創建頁面的提示詞列表
            await loadWorkPrompts();
            
            // 更新工作流程編輯頁面的提示詞列表
            await loadEditWorkPrompts();
        } else {
            showNotification('提示詞保存失敗: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('保存提示詞錯誤:', error);
        showNotification('提示詞保存失敗', 'error');
    }
}

// 載入工作提示詞列表
async function loadWorkPrompts() {
    try {
        console.log('開始載入工作提示詞列表...');
        const response = await fetch('/api/prompts');
        const data = await response.json();
        
        if (data.success) {
            const workPromptSelect = document.getElementById('workPromptSelect');
            if (!workPromptSelect) {
                console.warn('找不到 workPromptSelect 元素，可能不在當前頁面');
                return;
            }
            workPromptSelect.innerHTML = '<option value="">使用預設提示詞</option>';
            
            if (data.prompts && data.prompts.length > 0) {
                data.prompts.forEach(prompt => {
                    const option = document.createElement('option');
                    option.value = prompt.filename;
                    option.textContent = prompt.name || prompt.filename;
                    workPromptSelect.appendChild(option);
                });
                console.log(`已載入 ${data.prompts.length} 個工作提示詞選項`);
            } else {
                console.log('沒有找到工作提示詞檔案');
            }
        } else {
            console.error('工作提示詞API返回錯誤:', data.error);
        }
    } catch (error) {
        console.error('載入工作提示詞列表失敗:', error);
    }
}

// 載入工作配置列表
async function loadWorkProfiles() {
    try {
        console.log('開始載入工作配置列表...');
        const response = await fetch('/api/profiles');
        console.log('API 響應狀態:', response.status);
        
        const data = await response.json();
        console.log('API 響應數據:', data);
        
        if (data.success) {
            const workProfileSelect = document.getElementById('workProfileSelect');
            if (!workProfileSelect) {
            console.warn('找不到 workProfileSelect 元素，可能不在當前頁面');
                return;
            }
            
            workProfileSelect.innerHTML = '<option value="">使用預設配置</option>';
            
            data.profiles.forEach(profile => {
                const option = document.createElement('option');
                option.value = profile.filename;
                option.textContent = profile.name || profile.filename;
                workProfileSelect.appendChild(option);
            });
            
            console.log(`成功載入 ${data.profiles.length} 個配置`);
        } else {
            console.error('API 返回錯誤:', data.error);
        }
    } catch (error) {
        console.error('載入工作配置列表失敗:', error);
    }
}

// 工作提示詞編輯
function editWorkPrompt() {
    const workPromptSelect = document.getElementById('workPromptSelect');
    const selectedPrompt = workPromptSelect.value;
    
    if (!selectedPrompt) {
        showNotification('請先選擇要編輯的提示詞', 'warning');
        return;
    }
    
    loadPromptContent(selectedPrompt);
    showPromptModal('編輯工作提示詞');
}

// 工作提示詞創建
function createWorkPrompt() {
    // 清空表單
    document.getElementById('promptNameInput').value = '';
    document.getElementById('promptDescriptionInput').value = '';
    document.getElementById('promptContentInput').value = '';
    document.getElementById('promptFieldsInput').value = '';
    
    showPromptModal('創建工作提示詞');
}

// 已移除工作提示詞載入功能，簡化創建工作流程

// 編輯工作功能
async function editWork() {
    if (!prodocux.currentWork) {
        showNotification('請先選擇一個工作', 'warning');
        return;
    }
    
    // 填充基本編輯表單
    document.getElementById('editWorkNameInput').value = prodocux.currentWork.name || '';
    document.getElementById('editWorkDescriptionInput').value = prodocux.currentWork.description || '';
    document.getElementById('editWorkTypeSelect').value = prodocux.currentWork.type || '';
    document.getElementById('editBrandInput').value = prodocux.currentWork.brand || '';
    
    // 載入當前設定顯示
    await loadCurrentSettings();
    
    // 顯示編輯模態框
    document.getElementById('editWorkModal').style.display = 'flex';
}

function closeEditWorkModal() {
    document.getElementById('editWorkModal').style.display = 'none';
}

// 載入當前設定顯示
async function loadCurrentSettings() {
    if (!prodocux.currentWork) return;
    
    // 載入當前配置顯示
    await loadCurrentProfileDisplay();
    
    // 載入當前模板顯示
    await loadCurrentTemplateDisplay();
    
    // 載入當前提示詞顯示
    await loadCurrentPromptDisplay();
}

// 載入當前配置顯示
async function loadCurrentProfileDisplay() {
    const profileValue = document.getElementById('currentProfileValue');
    if (!profileValue) {
        console.log('currentProfileValue 元素不存在，跳過載入');
        return;
    }
    
        if (typeof prodocux.currentWork.profile === 'object' && prodocux.currentWork.profile) {
            const currentLang = (prodocux && prodocux.currentLanguage) || 'zh_TW';
            const profileName = prodocux.currentWork.profile.name || (currentLang === 'en' ? 'Custom Configuration' : '自定義配置');
            const simplifiedName = profileName.replace('資料提取Profile', '').replace('Profile', '').trim();
            const createTime = prodocux.currentWork.profile.created_at || prodocux.currentWork.created_at || (currentLang === 'en' ? 'Unknown Time' : '未知時間');
            const displayTime = new Date(createTime).toLocaleString(currentLang === 'en' ? 'en-US' : 'zh-TW');
            const createLabel = currentLang === 'en' ? 'Created' : '創建';
            profileValue.textContent = `${simplifiedName || (currentLang === 'en' ? 'Custom Configuration' : '自定義配置')} (${createLabel}: ${displayTime})`;
            profileValue.className = 'current';
        } else if (typeof prodocux.currentWork.profile === 'string' && prodocux.currentWork.profile) {
            const currentLang = (prodocux && prodocux.currentLanguage) || 'zh_TW';
            const createTime = prodocux.currentWork.created_at || (currentLang === 'en' ? 'Unknown Time' : '未知時間');
            const displayTime = new Date(createTime).toLocaleString(currentLang === 'en' ? 'en-US' : 'zh-TW');
            const createLabel = currentLang === 'en' ? 'Created' : '創建';
            profileValue.textContent = `${prodocux.currentWork.profile} (${createLabel}: ${displayTime})`;
            profileValue.className = 'current';
        } else {
            const currentLang = (prodocux && prodocux.currentLanguage) || 'zh_TW';
            const emptyText = currentLang === 'en' ? 'No Configuration' : '無配置';
            profileValue.textContent = emptyText;
            profileValue.className = 'loading';
        }
}

// 載入當前模板顯示
async function loadCurrentTemplateDisplay() {
    const templateValue = document.getElementById('currentTemplateValue');
    if (!templateValue) {
        console.log('currentTemplateValue 元素不存在，跳過載入');
        return;
    }
    
    if (typeof prodocux.currentWork.template === 'string' && prodocux.currentWork.template) {
        const templateName = prodocux.currentWork.template;
        
        // 如果是完整路徑，提取文件名；否則直接使用
        let fileName = templateName;
        if (templateName.includes('\\') || templateName.includes('/')) {
            fileName = templateName.split(/[\\\/]/).pop();
        }
        
        // 移除文件擴展名用於顯示
        const displayName = fileName.replace(/\.(docx|doc|pdf)$/i, '');
        
        // 獲取創建時間
        const createTime = prodocux.currentWork.created_at || '未知時間';
        const displayTime = new Date(createTime).toLocaleString('zh-TW');
        
        templateValue.textContent = `${displayName} (上傳: ${displayTime})`;
        templateValue.className = 'current';
    } else {
        templateValue.textContent = '無模板';
        templateValue.className = 'loading';
    }
}

// 載入當前提示詞顯示
async function loadCurrentPromptDisplay() {
    const promptValue = document.getElementById('currentPromptValue');
    if (!promptValue) {
        console.log('currentPromptValue 元素不存在，跳過載入');
        return;
    }
    
    if (typeof prodocux.currentWork.prompt === 'string' && prodocux.currentWork.prompt) {
        const currentLang = (prodocux && prodocux.currentLanguage) || 'zh_TW';
        const prompt = prodocux.currentWork.prompt;
        const createTime = prodocux.currentWork.created_at || (currentLang === 'en' ? 'Unknown Time' : '未知時間');
        const displayTime = new Date(createTime).toLocaleString(currentLang === 'en' ? 'en-US' : 'zh-TW');
        const createLabel = currentLang === 'en' ? 'Created' : '創建';
        
        if (prompt.includes('.md')) {
            const fileName = prompt.replace('.md', '');
            promptValue.textContent = `${fileName} (${createLabel}: ${displayTime})`;
        } else {
            const promptLength = prompt.length;
            const customPromptLabel = currentLang === 'en' ? 'Custom Prompt' : '自定義提示詞';
            const wordLabel = currentLang === 'en' ? 'chars' : '字';
            promptValue.textContent = `${customPromptLabel} (${promptLength}${wordLabel}) (${createLabel}: ${displayTime})`;
        }
        promptValue.className = 'current';
    } else {
        promptValue.textContent = '無提示詞';
        promptValue.className = 'loading';
    }
}

// 版本選擇功能
let currentVersionType = null; // 'profile', 'template', 'prompt'
let selectedVersionIndex = null;

// 顯示配置版本選擇
async function showProfileVersions() {
    currentVersionType = 'profile';
    await showVersionSelection('配置版本');
}

// 顯示模板版本選擇
async function showTemplateVersions() {
    currentVersionType = 'template';
    await showVersionSelection('模板版本');
}

// 顯示提示詞版本選擇
async function showPromptVersions() {
    currentVersionType = 'prompt';
    await showVersionSelection('提示詞版本');
}

// 顯示版本選擇模態框
async function showVersionSelection(title) {
    if (!prodocux.currentWork) return;
    
    document.getElementById('versionModalTitle').textContent = title;
    
    try {
        const response = await fetch(`/api/works/${prodocux.currentWork.id}/versions`);
        const data = await response.json();
        
        if (data.success) {
            displayVersionSelection(data.versions);
            document.getElementById('versionSelectionModal').style.display = 'flex';
        }
    } catch (error) {
        console.error('載入版本歷史失敗:', error);
        showNotification('載入版本歷史失敗', 'error');
    }
}

// 顯示版本選擇列表
function displayVersionSelection(versions) {
    const versionList = document.getElementById('versionList');
    versionList.innerHTML = '';
    
    // 添加當前版本
    const currentVersionItem = document.createElement('div');
    currentVersionItem.className = 'version-item';
    currentVersionItem.onclick = () => selectVersion(-1);
    
    const currentVersionInfo = document.createElement('div');
    currentVersionInfo.className = 'version-info';
    
    const currentVersionName = document.createElement('div');
    currentVersionName.className = 'version-name';
    currentVersionName.textContent = '當前版本 (最新)';
    
    const currentVersionMeta = document.createElement('div');
    currentVersionMeta.className = 'version-meta';
    currentVersionMeta.textContent = '正在使用的版本';
    
    currentVersionInfo.appendChild(currentVersionName);
    currentVersionInfo.appendChild(currentVersionMeta);
    currentVersionItem.appendChild(currentVersionInfo);
    versionList.appendChild(currentVersionItem);
    
    // 添加歷史版本
    versions.reverse().forEach((version, index) => {
        if (version.changes[currentVersionType]) {
            const versionItem = document.createElement('div');
            versionItem.className = 'version-item';
            versionItem.onclick = () => selectVersion(index);
            
            const versionInfo = document.createElement('div');
            versionInfo.className = 'version-info';
            
            const versionName = document.createElement('div');
            versionName.className = 'version-name';
            
            const versionMeta = document.createElement('div');
            versionMeta.className = 'version-meta';
            versionMeta.textContent = new Date(version.timestamp).toLocaleString('zh-TW');
            
            // 根據類型設置版本名稱
            const changeData = version.changes[currentVersionType];
            if (currentVersionType === 'profile') {
                const profileName = changeData.new?.name || '配置';
                const simplifiedName = profileName.replace('資料提取Profile', '').replace('Profile', '').trim();
                versionName.textContent = simplifiedName || '配置';
            } else if (currentVersionType === 'template') {
                const templatePath = changeData.new || '';
                if (templatePath) {
                    const fileName = templatePath.split('\\').pop().replace('.docx', '');
                    // 顯示原始文件名，不要簡化
                    versionName.textContent = fileName;
                } else {
                    versionName.textContent = '無模板';
                }
            } else if (currentVersionType === 'prompt') {
                const prompt = changeData.new || '';
                if (prompt) {
                    if (prompt.includes('.md')) {
                        const fileName = prompt.replace('.md', '');
                        versionName.textContent = fileName;
                    } else {
                        const promptLength = prompt.length;
                        versionName.textContent = `自定義提示詞 (${promptLength}字)`;
                    }
                } else {
                    versionName.textContent = '無提示詞';
                }
            }
            
            versionInfo.appendChild(versionName);
            versionInfo.appendChild(versionMeta);
            versionItem.appendChild(versionInfo);
            versionList.appendChild(versionItem);
        }
    });
}

// 選擇版本
function selectVersion(index) {
    selectedVersionIndex = index;
    
    // 更新視覺選中狀態
    document.querySelectorAll('.version-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    event.currentTarget.classList.add('selected');
}

// 應用版本選擇
async function applyVersionSelection() {
    if (selectedVersionIndex === null) {
        showNotification('請選擇一個版本', 'warning');
        return;
    }
    
    if (selectedVersionIndex === -1) {
        // 選擇當前版本，不需要做任何操作
        closeVersionSelection();
        return;
    }
    
    // 回滾到選中的版本
    try {
        const response = await fetch(`/api/works/${prodocux.currentWork.id}/rollback/${selectedVersionIndex}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('版本切換成功！', 'success');
            
            // 重新載入工作數據
            await prodocux.loadWorks();
            
            // 更新當前工作
            const updatedWork = prodocux.works.find(w => w.id === prodocux.currentWork.id);
            if (updatedWork) {
                prodocux.currentWork = updatedWork;
                prodocux.showWorkInfo();
            }
            
            // 重新載入當前設定顯示
            await loadCurrentSettings();
            
            closeVersionSelection();
        } else {
            showNotification(data.error || '版本切換失敗', 'error');
        }
    } catch (error) {
        console.error('版本切換錯誤:', error);
        showNotification('版本切換失敗', 'error');
    }
}

// 關閉版本選擇
function closeVersionSelection() {
    document.getElementById('versionSelectionModal').style.display = 'none';
    selectedVersionIndex = null;
    currentVersionType = null;
}

// 操作按鈕函數
// 配置相關操作
function viewProfileDetails() {
    if (!prodocux.currentWork || !prodocux.currentWork.profile) {
        showNotification('沒有可查看的配置', 'warning');
        return;
    }
    
    const profile = prodocux.currentWork.profile;
    let details = '';
    
    if (typeof profile === 'object') {
        details = `配置名稱: ${profile.name || '未命名'}\n`;
        details += `描述: ${profile.description || '無描述'}\n`;
        details += `欄位數量: ${profile.fields ? profile.fields.length : 0}\n`;
        if (profile.fields) {
            details += '\n欄位列表:\n';
            profile.fields.forEach(field => {
                details += `- ${field.name} (${field.type})\n`;
            });
        }
    } else {
        details = `配置: ${profile}`;
    }
    
    alert(details);
}

function editCurrentProfile() {
    showNotification('配置編輯功能開發中，敬請期待...', 'info');
    // TODO: 實現配置編輯功能
}

function createNewProfile() {
    showNotification('新建配置功能開發中，敬請期待...', 'info');
    // TODO: 實現新建配置功能
}

// 模板相關操作
function viewTemplateDetails() {
    if (!prodocux.currentWork || !prodocux.currentWork.template) {
        showNotification('沒有可查看的模板', 'warning');
        return;
    }
    
    const template = prodocux.currentWork.template;
    const fileName = template.split('\\').pop().replace('.docx', '');
    
    let details = `模板路徑: ${template}\n`;
    details += `文件名: ${fileName}\n`;
    details += `類型: ${fileName.startsWith('template_') ? '自定義模板' : '預設模板'}`;
    
    alert(details);
}

function editCurrentTemplate() {
    showNotification('模板編輯功能開發中，敬請期待...', 'info');
    // TODO: 實現模板編輯功能
}

function uploadNewTemplate() {
    showNotification('模板上傳功能開發中，敬請期待...', 'info');
    // TODO: 實現模板上傳功能
}

// 提示詞相關操作
function viewPromptDetails() {
    if (!prodocux.currentWork || !prodocux.currentWork.prompt) {
        showNotification('沒有可查看的提示詞', 'warning');
        return;
    }
    
    const prompt = prodocux.currentWork.prompt;
    let details = '';
    
    if (prompt.includes('.md')) {
        details = `提示詞文件: ${prompt}\n`;
        details += `類型: 預設提示詞`;
    } else {
        details = `提示詞類型: 自定義\n`;
        details += `字數: ${prompt.length}\n`;
        details += `內容預覽:\n${prompt.substring(0, 200)}${prompt.length > 200 ? '...' : ''}`;
    }
    
    alert(details);
}

function editCurrentPrompt() {
    showNotification('提示詞編輯功能開發中，敬請期待...', 'info');
    // TODO: 實現提示詞編輯功能
}

function createNewPrompt() {
    showNotification('新建提示詞功能開發中，敬請期待...', 'info');
    // TODO: 實現新建提示詞功能
}

// 版本管理功能
async function loadWorkVersionHistory() {
    if (!prodocux.currentWork) return;
    
    try {
        const response = await fetch(`/api/works/${prodocux.currentWork.id}/versions`);
        const data = await response.json();
        
        if (data.success) {
            displayVersionHistory(data.versions);
        }
    } catch (error) {
        console.error('載入版本歷史失敗:', error);
    }
}

function displayVersionHistory(versions) {
    const versionManagement = document.querySelector('.version-management');
    const versionList = document.getElementById('versionList');
    
    if (!versions || versions.length === 0) {
        versionManagement.style.display = 'none';
        return;
    }
    
    // 顯示版本管理區域
    versionManagement.style.display = 'block';
    
    // 清空現有內容
    versionList.innerHTML = '';
    
    // 添加版本切換按鈕
    const toggleButton = document.createElement('button');
    toggleButton.className = 'btn btn-outline-secondary version-toggle';
    toggleButton.innerHTML = '<i class="fas fa-history"></i> 查看版本歷史';
    toggleButton.onclick = () => toggleVersionList();
    versionList.appendChild(toggleButton);
    
    // 創建版本列表容器
    const versionsContainer = document.createElement('div');
    versionsContainer.id = 'versionsContainer';
    versionsContainer.style.display = 'none';
    
    // 按時間倒序排列（最新的在前）
    const sortedVersions = versions.slice().reverse();
    
    sortedVersions.forEach((version, index) => {
        const versionItem = createVersionItem(version, sortedVersions.length - 1 - index);
        versionsContainer.appendChild(versionItem);
    });
    
    versionList.appendChild(versionsContainer);
}

function createVersionItem(version, versionIndex) {
    const versionItem = document.createElement('div');
    versionItem.className = 'version-item';
    
    // 版本信息
    const versionInfo = document.createElement('div');
    versionInfo.className = 'version-info';
    
    const timestamp = document.createElement('div');
    timestamp.className = 'version-timestamp';
    timestamp.textContent = new Date(version.timestamp).toLocaleString('zh-TW');
    
    const changes = document.createElement('div');
    changes.className = 'version-changes';
    
    const changeItems = Object.keys(version.changes).map(field => {
        const changeItem = document.createElement('span');
        changeItem.className = 'change-item';
        changeItem.textContent = field;
        return changeItem;
    });
    
    changes.append(...changeItems);
    versionInfo.appendChild(timestamp);
    versionInfo.appendChild(changes);
    
    // 版本操作
    const versionActions = document.createElement('div');
    versionActions.className = 'version-actions';
    
    const rollbackButton = document.createElement('button');
    rollbackButton.className = 'btn btn-warning btn-sm';
    rollbackButton.innerHTML = '<i class="fas fa-undo"></i> 回滾';
    rollbackButton.onclick = () => rollbackToVersion(versionIndex);
    
    versionActions.appendChild(rollbackButton);
    
    versionItem.appendChild(versionInfo);
    versionItem.appendChild(versionActions);
    
    return versionItem;
}

function toggleVersionList() {
    const container = document.getElementById('versionsContainer');
    const button = document.querySelector('.version-toggle');
    
    if (container.style.display === 'none') {
        container.style.display = 'block';
        button.innerHTML = '<i class="fas fa-eye-slash"></i> 隱藏版本歷史';
    } else {
        container.style.display = 'none';
        button.innerHTML = '<i class="fas fa-history"></i> 查看版本歷史';
    }
}

async function rollbackToVersion(versionIndex) {
    if (!prodocux.currentWork) return;
    
    if (!confirm('確定要回滾到這個版本嗎？這將覆蓋當前的配置。')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/works/${prodocux.currentWork.id}/rollback/${versionIndex}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('版本回滾成功！', 'success');
            
            // 重新載入工作數據
            await prodocux.loadWorks();
            
            // 更新當前工作
            const updatedWork = prodocux.works.find(w => w.id === prodocux.currentWork.id);
            if (updatedWork) {
                prodocux.currentWork = updatedWork;
                prodocux.showWorkInfo();
            }
            
            // 關閉編輯模態框
            closeEditWorkModal();
        } else {
            showNotification(data.error || '版本回滾失敗', 'error');
        }
    } catch (error) {
        console.error('版本回滾錯誤:', error);
        showNotification('版本回滾失敗', 'error');
    }
}

// 載入編輯工作的配置選項 - 只載入當前工作的版本歷史
async function loadEditWorkProfiles() {
    try {
            const editWorkProfileSelect = document.getElementById('editWorkProfileSelect');
        editWorkProfileSelect.innerHTML = '<option value="">選擇配置版本...</option>';
        
        if (!prodocux.currentWork) return;
        
        // 獲取版本歷史
        const response = await fetch(`/api/works/${prodocux.currentWork.id}/versions`);
        const data = await response.json();
        
        if (data.success && data.versions) {
            // 添加當前版本
            const currentOption = document.createElement('option');
            currentOption.value = 'current';
            currentOption.textContent = '當前版本 (最新)';
            currentOption.selected = true;
            editWorkProfileSelect.appendChild(currentOption);
            
            // 添加歷史版本
            data.versions.reverse().forEach((version, index) => {
                if (version.changes.profile) {
                const option = document.createElement('option');
                    option.value = `version_${index}`;
                    
                    const timestamp = new Date(version.timestamp).toLocaleString('zh-TW');
                    const profileName = version.changes.profile.new?.name || '配置';
                    const simplifiedName = profileName.replace('資料提取Profile', '').replace('Profile', '').trim();
                    
                    option.textContent = `${simplifiedName} (${timestamp})`;
                editWorkProfileSelect.appendChild(option);
                }
            });
        } else {
            // 如果沒有版本歷史，只顯示當前版本
            const currentOption = document.createElement('option');
            currentOption.value = 'current';
            currentOption.textContent = '當前版本';
            currentOption.selected = true;
            editWorkProfileSelect.appendChild(currentOption);
        }
    } catch (error) {
        console.error('載入編輯工作配置列表失敗:', error);
    }
}

async function loadEditWorkTemplates() {
    try {
        const editWorkTemplateSelect = document.getElementById('editWorkTemplateSelect');
        editWorkTemplateSelect.innerHTML = '<option value="">選擇模板版本...</option>';
        
        if (!prodocux.currentWork) return;
        
        // 獲取版本歷史
        const response = await fetch(`/api/works/${prodocux.currentWork.id}/versions`);
        const data = await response.json();
        
        if (data.success && data.versions) {
            // 添加當前版本
            const currentOption = document.createElement('option');
            currentOption.value = 'current';
            
            if (prodocux.currentWork.template) {
                const templatePath = prodocux.currentWork.template;
                const fileName = templatePath.split('\\').pop().replace('.docx', '');
                
                // 嘗試從文件名提取原始名稱
                let displayName = fileName;
                if (fileName.startsWith('template_') && fileName.length > 20) {
                    displayName = '自定義模板';
                }
                
                currentOption.textContent = `${displayName} (當前)`;
            } else {
                currentOption.textContent = '無模板 (當前)';
            }
            currentOption.selected = true;
            editWorkTemplateSelect.appendChild(currentOption);
            
            // 添加歷史版本
            data.versions.reverse().forEach((version, index) => {
                if (version.changes.template) {
                const option = document.createElement('option');
                    option.value = `version_${index}`;
                    
                    const timestamp = new Date(version.timestamp).toLocaleString('zh-TW');
                    const templatePath = version.changes.template.new || '';
                    
                    if (templatePath) {
                        const fileName = templatePath.split('\\').pop().replace('.docx', '');
                        let displayName = fileName;
                        if (fileName.startsWith('template_') && fileName.length > 20) {
                            displayName = '自定義模板';
                        }
                        option.textContent = `${displayName} (${timestamp})`;
                    } else {
                        option.textContent = `無模板 (${timestamp})`;
                    }
                    
                editWorkTemplateSelect.appendChild(option);
                }
            });
        } else {
            // 如果沒有版本歷史，只顯示當前版本
            const currentOption = document.createElement('option');
            currentOption.value = 'current';
            
            if (prodocux.currentWork.template) {
                const templatePath = prodocux.currentWork.template;
                const fileName = templatePath.split('\\').pop().replace('.docx', '');
                let displayName = fileName;
                if (fileName.startsWith('template_') && fileName.length > 20) {
                    displayName = '自定義模板';
                }
                currentOption.textContent = `${displayName} (當前)`;
            } else {
                currentOption.textContent = '無模板 (當前)';
            }
            currentOption.selected = true;
            editWorkTemplateSelect.appendChild(currentOption);
        }
    } catch (error) {
        console.error('載入編輯工作模板列表失敗:', error);
    }
}

async function loadEditWorkPrompts() {
    try {
        const editWorkPromptSelect = document.getElementById('editWorkPromptSelect');
        editWorkPromptSelect.innerHTML = '<option value="">選擇提示詞版本...</option>';
        
        if (!prodocux.currentWork) return;
        
        // 獲取版本歷史
        const response = await fetch(`/api/works/${prodocux.currentWork.id}/versions`);
        const data = await response.json();
        
        if (data.success && data.versions) {
            // 添加當前版本
            const currentOption = document.createElement('option');
            currentOption.value = 'current';
            
            if (prodocux.currentWork.prompt) {
                const prompt = prodocux.currentWork.prompt;
                if (prompt.includes('.md')) {
                    // 預設提示詞文件
                    const fileName = prompt.replace('.md', '');
                    currentOption.textContent = `${fileName} (當前)`;
                } else {
                    // 自定義提示詞
                    const promptLength = prompt.length;
                    currentOption.textContent = `自定義提示詞 (${promptLength}字) (當前)`;
                }
            } else {
                currentOption.textContent = '無提示詞 (當前)';
            }
            currentOption.selected = true;
            editWorkPromptSelect.appendChild(currentOption);
            
            // 添加歷史版本
            data.versions.reverse().forEach((version, index) => {
                if (version.changes.prompt) {
                const option = document.createElement('option');
                    option.value = `version_${index}`;
                    
                    const timestamp = new Date(version.timestamp).toLocaleString('zh-TW');
                    const prompt = version.changes.prompt.new || '';
                    
                    if (prompt) {
                        if (prompt.includes('.md')) {
                            const fileName = prompt.replace('.md', '');
                            option.textContent = `${fileName} (${timestamp})`;
                        } else {
                            const promptLength = prompt.length;
                            option.textContent = `自定義提示詞 (${promptLength}字) (${timestamp})`;
                        }
                    } else {
                        option.textContent = `無提示詞 (${timestamp})`;
                    }
                    
                editWorkPromptSelect.appendChild(option);
                }
            });
        } else {
            // 如果沒有版本歷史，只顯示當前版本
            const currentOption = document.createElement('option');
            currentOption.value = 'current';
            
            if (prodocux.currentWork.prompt) {
                const prompt = prodocux.currentWork.prompt;
                if (prompt.includes('.md')) {
                    const fileName = prompt.replace('.md', '');
                    currentOption.textContent = `${fileName} (當前)`;
                } else {
                    const promptLength = prompt.length;
                    currentOption.textContent = `自定義提示詞 (${promptLength}字) (當前)`;
                }
            } else {
                currentOption.textContent = '無提示詞 (當前)';
            }
            currentOption.selected = true;
            editWorkPromptSelect.appendChild(currentOption);
        }
    } catch (error) {
        console.error('載入編輯工作提示詞列表失敗:', error);
    }
}

// 更新工作
async function updateWork() {
    if (!prodocux.currentWork) {
        showNotification('請先選擇一個工作', 'warning');
        return;
    }
    
    const workName = document.getElementById('editWorkNameInput').value.trim();
    const workDescription = document.getElementById('editWorkDescriptionInput').value.trim();
    const workType = document.getElementById('editWorkTypeSelect').value;
    const brand = document.getElementById('editBrandInput').value.trim();
    const workProfile = document.getElementById('editWorkProfileSelect').value;
    const workTemplate = document.getElementById('editWorkTemplateSelect').value;
    const workPrompt = document.getElementById('editWorkPromptSelect').value;
    
    if (!workName) {
        showNotification('請輸入工作名稱', 'warning');
        return;
    }
    
    if (!workType) {
        showNotification('請選擇工作類型', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/api/works/${prodocux.currentWork.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: workName,
                description: workDescription,
                type: workType,
                brand: brand,
                profile: workProfile,
                template: workTemplate,
                prompt: workPrompt
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 重新載入工作列表
            await prodocux.loadWorks();
            
            // 更新當前工作數據
            if (prodocux.currentWork) {
                const updatedWork = prodocux.works.find(w => w.id === prodocux.currentWork.id);
                if (updatedWork) {
                    prodocux.currentWork = updatedWork;
                    prodocux.showWorkInfo(); // 重新顯示工作信息
                }
            }
            
            // 關閉模態框
            closeEditWorkModal();
            
            showNotification('工作更新成功！', 'success');
        } else {
            showNotification(data.error || '工作更新失敗', 'error');
        }
    } catch (error) {
        console.error('更新工作錯誤:', error);
        showNotification('工作更新失敗', 'error');
    }
}

// 刪除工作
async function deleteWork() {
    if (!prodocux.currentWork) {
        showNotification('請先選擇一個工作', 'warning');
        return;
    }
    
    const workName = prodocux.currentWork.name;
    
    if (!confirm(`確定要刪除工作「${workName}」嗎？\n\n此操作無法復原！`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/works/${prodocux.currentWork.id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 重新載入工作列表
            await prodocux.loadWorks();
            
            // 清空當前工作選擇
            prodocux.selectWork('');
            document.getElementById('workSelect').value = '';
            
            showNotification('工作刪除成功！', 'success');
        } else {
            showNotification(data.error || '工作刪除失敗', 'error');
        }
    } catch (error) {
        console.error('刪除工作錯誤:', error);
        showNotification('工作刪除失敗', 'error');
    }
}

// 編輯工作的模板和提示詞功能
function uploadEditWorkTemplate() {
    // 重用現有的模板上傳功能
    uploadTemplate();
}

function editEditWorkPrompt() {
    const workPromptSelect = document.getElementById('editWorkPromptSelect');
    const selectedPrompt = workPromptSelect.value;
    
    if (!selectedPrompt) {
        showNotification('請先選擇要編輯的提示詞', 'warning');
        return;
    }
    
    // 載入選中的提示詞內容
    loadPromptContent(selectedPrompt);
    showPromptModal('編輯提示詞');
}

function createEditWorkPrompt() {
    // 重用現有的提示詞創建功能
    createPrompt();
}

// 簡化的工作創建功能
let currentWork = {
    name: '',
    description: '',
    type: '',
    profile: null,
    prompt: null,
    template: null
};

// Profile生成
function generateProfilePrompt() {
    const description = document.getElementById('workDescription').value;
    const workType = document.getElementById('workType').value;
    const templateFile = document.getElementById('templateFile').files[0];
    
    if (!description.trim()) {
        const message = currentLang === 'en' ? '❌ Please fill in work description first, so AI can generate more accurate Profile' : '❌ 請先填寫工作描述，這樣AI可以生成更準確的Profile';
        alert(message);
        return;
    }
    
    if (!workType) {
        const message = currentLang === 'en' ? '❌ Please select document type' : '❌ 請選擇文檔類型';
        alert(message);
        return;
    }
    
    if (!templateFile) {
        const message = currentLang === 'en' ? '❌ Please upload template file first, so AI can generate more accurate Profile based on template structure' : '❌ 請先上傳模板檔案，這樣AI可以根據模板結構生成更準確的Profile';
        alert(message);
        return;
    }
    
    // 讀取模板檔案內容
    const reader = new FileReader();
    reader.onload = function(e) {
        const templateContent = e.target.result;
        generateProfilePromptWithTemplate(description, workType, templateFile.name, templateContent);
    };
    
    // 根據檔案類型選擇讀取方式
    if (templateFile.name.endsWith('.docx')) {
        reader.readAsArrayBuffer(templateFile);
    } else if (templateFile.name.endsWith('.xlsx')) {
        reader.readAsArrayBuffer(templateFile);
    } else if (templateFile.name.endsWith('.pptx')) {
        reader.readAsArrayBuffer(templateFile);
    } else {
        reader.readAsText(templateFile);
    }
}

function generateProfilePromptWithTemplate(description, workType, templateName, templateContent) {
    // 獲取當前語言
    const currentLang = (prodocux && prodocux.currentLanguage) || 'zh_TW';
    
    // 根據工作類型生成客製化指導
    const getWorkTypeProfileGuidance = (workType, lang) => {
        if (lang === 'en') {
            const guidance = {
                'pif': 'PIF Document (Product Information File): **Must include complete ingredient list with INCI names, CAS numbers, content percentages, and functions**. Focus on product basic information, safety assessment, manufacturer information, regulatory compliance, usage instructions, and other commercial technical fields. Ingredient list is the core field of PIF and must be completely extracted. Use standardized terminology, avoid sensitive descriptions.',
                'msds': 'MSDS Document (Material Safety Data Sheet): **Must include GHS hazard classification, safety precautions, and emergency procedures**. Focus on chemical information, safety classification, handling recommendations, physical and chemical properties, exposure controls, and other technical fields. Use GHS standard terminology.',
                'contract': 'Contract Document: **Must include party information, contract terms, performance deadlines, and dispute resolution**. Focus on party information, terms content, dates, amounts, signatures, breach of contract, and other commercial legal elements. Use standard contract terminology.',
                'invoice': 'Invoice Document: **Must include invoice number, issue date, item details, and tax calculations**. Focus on amounts, tax rates, dates, product information, buyer and seller, payment terms, and other financial elements. Use standard accounting terminology.',
                'report': 'Report Document: **Must include executive summary, data analysis, and conclusions with recommendations**. Focus on data, charts, conclusions, recommendations, methodology, references, appendices, and other technical elements. Use professional report terminology.',
                'certificate': 'Certificate Document: **Must include certificate type, issuing authority, validity period, and certification scope**. Focus on certificate type, issuing authority, validity period, certification scope, certificate number, issue date, and other certification elements. Use standard certification terminology.',
                'manual': 'Manual Document: **Must include operation steps, safety warnings, and troubleshooting procedures**. Focus on operation steps, technical specifications, troubleshooting, maintenance, technical specifications, diagrams, and other practical elements. Use technical manual terminology.',
                'specification': 'Specification Document: **Must include technical parameters, performance indicators, and acceptance standards**. Focus on technical parameters, performance indicators, testing methods, acceptance standards, material requirements, dimensional specifications, and other technical elements. Use standard specification terminology.',
                'policy': 'Policy Document: **Must include policy terms, scope of application, and violation handling procedures**. Focus on policy terms, scope of application, execution standards, violation handling, revision procedures, effective date, and other management elements. Use standard policy terminology.',
                'medical': 'Medical Document: **Must include product information, indications, contraindications, and adverse reactions**. Focus on product information, technical specifications, usage instructions, indications, contraindications, dosage, adverse reactions, storage conditions, and other technical elements. Avoid personal medical information, use product technical terminology.',
                'financial': 'Financial Document: **Must include financial data, accounting subjects, and audit opinions**. Focus on financial data, accounting subjects, budget allocation, cash flow, profit and loss analysis, audit opinions, and other financial elements. Use standard accounting terminology.',
                'legal': 'Legal Document: **Must include legal terms, rights and obligations, and dispute resolution procedures**. Focus on terms content, rights and obligations, scope of application, legal validity, revision procedures, dispute resolution, and other legal elements. Use standard legal terminology.',
                'technical': 'Technical Document: **Must include technical specifications, design parameters, and test results**. Focus on technical specifications, design parameters, test results, performance indicators, technical standards, implementation plans, and other technical elements. Use standard technical terminology.',
                'marketing': 'Marketing Document: **Must include product features, target market analysis, and competitive advantages**. Focus on product features, target market, competitive advantages, marketing strategies, customer analysis, market positioning, and other marketing elements. Use standard marketing terminology.',
                'custom': 'Custom Document: Identify key fields based on specific requirements, use professional and neutral business terminology.'
            };
            return guidance[workType] || 'Document Processing: Identify key fields based on template structure, ensure extraction completeness and accuracy';
        } else {
            const guidance = {
                'pif': 'PIF文檔（產品資訊檔案）：**必須包含完整成分表，含INCI名稱、CAS編號、含量百分比、功能描述**。專注於產品基本信息、安全評估、製造商信息、法規合規性、使用方法等商業技術欄位。成分表是PIF的核心欄位，必須完整提取。使用標準化術語，避免敏感描述。',
                'msds': 'MSDS文檔（材料安全數據表）：**必須包含GHS危險分類、安全防護措施、應急處理程序**。專注於化學品信息、安全分類、處理建議、物理化學性質、暴露控制等技術欄位。使用GHS標準術語。',
                'contract': '合約文檔：**必須包含當事方信息、合約條款、履行期限、爭議解決**。專注於當事方信息、條款內容、日期、金額、簽署、違約責任等商業法律要素。使用標準合約術語。',
                'invoice': '發票文檔：**必須包含發票號碼、開票日期、商品明細、稅額計算**。專注於金額、稅率、日期、商品信息、買賣雙方、付款條件等財務要素。使用標準會計術語。',
                'report': '報告文檔：**必須包含執行摘要、數據分析、結論建議**。專注於數據、圖表、結論、建議、方法論、參考資料、附錄等技術要素。使用專業報告術語。',
                'certificate': '證書文檔：**必須包含證書類型、頒發機構、有效期、認證範圍**。專注於證書類型、頒發機構、有效期、認證範圍、證書編號、簽發日期等認證要素。使用標準認證術語。',
                'manual': '手冊文檔：**必須包含操作步驟、安全警告、故障排除程序**。專注於操作步驟、技術規格、故障排除、維護保養、技術規格、圖表說明等實用要素。使用技術手冊術語。',
                'specification': '規格文檔：**必須包含技術參數、性能指標、驗收標準**。專注於技術參數、性能指標、測試方法、驗收標準、材料要求、尺寸規格等技術要素。使用標準規格術語。',
                'policy': '政策文檔：**必須包含政策條款、適用範圍、違規處理程序**。專注於政策條款、適用範圍、執行標準、違規處理、修訂程序、生效日期等管理要素。使用標準政策術語。',
                'medical': '醫療文檔：**必須包含產品信息、適應症、禁忌症、不良反應**。專注於產品信息、技術規格、使用說明、適應症、禁忌症、用法用量、不良反應、儲存條件等技術要素。避免個人醫療信息，使用產品技術術語。',
                'financial': '財務文檔：**必須包含財務數據、會計科目、審計意見**。專注於財務數據、會計科目、預算分配、現金流、損益分析、審計意見等財務要素。使用標準會計術語。',
                'legal': '法律文檔：**必須包含法律條款、權利義務、爭議解決程序**。專注於法律條款、權利義務、適用範圍、法律效力、修訂程序、爭議解決等法律要素。使用標準法律術語。',
                'technical': '技術文檔：**必須包含技術規格、設計參數、測試結果**。專注於技術規格、設計參數、測試結果、性能指標、技術標準、實施方案等技術要素。使用標準技術術語。',
                'marketing': '行銷文檔：**必須包含產品特點、目標市場分析、競爭優勢**。專注於產品特點、目標市場、競爭優勢、行銷策略、客戶分析、市場定位等行銷要素。使用標準行銷術語。',
                'custom': '自定義文檔：根據具體需求識別關鍵欄位，使用專業、中性的商業術語。'
            };
            return guidance[workType] || '文檔處理：根據模板結構識別關鍵欄位，確保提取的完整性和準確性';
        }
    };

    const workTypeGuidance = getWorkTypeProfileGuidance(workType, currentLang);
    
    let prompt;
    if (currentLang === 'en') {
        prompt = `You are a professional document analysis expert specializing in designing extraction configurations for business document processing systems.

Task: Generate a document extraction Profile (JSON format) based on the following requirements

Work Description: ${description}
Document Type: ${workType}
Template File: ${templateName} (only as output format reference)
Specialized Guidance: ${workTypeGuidance}

Please generate a JSON Profile with the following structure:
{
    "name": "Profile Name",
    "description": "Profile Description",
    "fields": [
        {
            "name": "Field Name",
            "type": "text|number|date|boolean",
            "required": true|false,
            "description": "Field Description",
            "template_reference": "Position or variable name in template"
        }
    ]
}

Professional Requirements:
1. Carefully analyze the template file to identify all fields that need to be filled
2. Determine fields based on variable markers in the template (such as {field_name}, [field_name], etc.)
3. Determine field types based on their purpose in the template (text, number, date, boolean)
4. Mark required fields (usually indicated as required or important in the template)
5. Provide clear field descriptions explaining the role of each field in the template
6. In template_reference, explain the position of the field in the template
7. Consider multilingual conversion needs to ensure field design can handle inputs in different languages

Safety and Compliance Requirements:
- Use professional, neutral business terminology, avoid sensitive vocabulary
- Focus on technical and commercial data extraction
- Avoid personal privacy, medical diagnosis, legal advice, and other sensitive content
- Use standardized industry terminology and classification

Technical Requirements:
- This Profile will be used to extract data from **input documents**
- Template file is only used as output format reference, no need to process template content
- Focus on designing Profiles that can extract corresponding fields from various input documents
- Return only JSON, no other text

Length Limits:
- Profile JSON total length controlled between 500-2000 characters (ideal 1500 characters)
- Each field's description controlled within 30-50 characters
- Recommended total fields: 15-25
- Prioritize the most important fields, maintain clear structure
- Use compressed JSON format (no extra spaces and line breaks)
- template_reference uses short format (e.g., "p.3" instead of "Basic Info p.3")

Please generate the Profile:`;
    } else {
        prompt = `你是一個專業的文檔分析專家，專門為商業文檔處理系統設計提取配置。

任務：根據以下需求生成一個文檔提取Profile（JSON格式）

工作描述：${description}
文檔類型：${workType}
模板檔案：${templateName}（僅作為輸出格式參考）
專項指導：${workTypeGuidance}

請生成一個包含以下結構的JSON Profile：
{
    "name": "Profile名稱",
    "description": "Profile描述",
    "fields": [
        {
            "name": "欄位名稱",
            "type": "text|number|date|boolean",
            "required": true|false,
            "description": "欄位描述",
            "template_reference": "在中文模板中的位置或變數名稱"
        }
    ]
}

專業要求：
1. 仔細分析模板檔案，識別所有需要填寫的欄位
2. 根據模板中的變數標記（如{欄位名稱}、[欄位名稱]等）確定欄位
3. 根據欄位在模板中的用途確定類型（文字、數字、日期、布林值）
4. 標記必填欄位（通常在模板中標示為必填或重要欄位）
5. 提供清晰的欄位描述，說明該欄位在模板中的作用
6. 在template_reference中說明該欄位在模板中的位置
7. 考慮多語言轉換需求，確保欄位設計能處理不同語言的輸入

安全與合規要求：
- 使用專業、中性的商業術語，避免敏感詞彙
- 專注於技術和商業層面的資料提取
- 避免涉及個人隱私、醫療診斷、法律建議等敏感內容
- 使用標準化的行業術語和分類

技術要求：
- 此Profile將用於從**輸入文檔**中提取資料
- 模板檔案僅作為輸出格式的參考，不需要處理模板內容
- 專注於設計能從各種輸入文檔中提取對應欄位的Profile
- 只返回JSON，不要其他文字

長度限制：
- Profile JSON總長度控制在500-2000字元之間（理想1500字元）
- 每個欄位的description控制在30-50字元
- 欄位總數建議15-25個
- 優先選擇最重要的欄位，保持結構清晰
- 使用壓縮JSON格式（無多餘空格和換行）
- template_reference使用簡短格式（如"p.3"而非"基本資料 p.3"）

請生成Profile：`;
    }

    const promptText = document.getElementById('profilePrompt');
    if (promptText) {
        promptText.value = prompt;
    }
}

// 提示詞模板生成
function generatePromptTemplate() {
    const description = document.getElementById('workDescription').value;
    const workType = document.getElementById('workType').value;
    const profile = currentWork.profile;
    const templateFile = document.getElementById('templateFile').files[0];
    
    // 獲取當前語言
    const currentLang = (prodocux && prodocux.currentLanguage) || 'zh_TW';
    
    if (!description.trim()) {
        alert(currentLang === 'en' ? '❌ Please fill in the work description first' : '❌ 請先填寫工作描述');
        return;
    }
    
    if (!workType) {
        alert(currentLang === 'en' ? '❌ Please select document type' : '❌ 請選擇文檔類型');
        return;
    }
    
    if (!profile) {
        alert(currentLang === 'en' ? '❌ Please generate and validate Profile first' : '❌ 請先生成並驗證Profile');
        return;
    }
    
    if (!templateFile) {
        alert(currentLang === 'en' ? '❌ Please upload template file first, so AI can generate more accurate prompts based on template structure' : '❌ 請先上傳模板檔案，這樣AI可以根據模板結構生成更準確的提示詞');
        return;
    }
    
    const fields = profile.fields.map(field => 
        currentLang === 'en' 
            ? `- ${field.name} (${field.type}): ${field.description}${field.template_reference ? ` [Template position: ${field.template_reference}]` : ''}`
            : `- ${field.name} (${field.type}): ${field.description}${field.template_reference ? ` [模板位置: ${field.template_reference}]` : ''}`
    ).join('\n');
    
    // 根據工作類型生成客製化提示詞
    const getWorkTypeGuidance = (workType, lang) => {
        if (lang === 'en') {
            const guidance = {
                'pif': 'PIF Document Conversion: **Ingredient list is core required field with INCI names, CAS numbers, content percentages, and functions**. Process cosmetic product information files, focus on INCI ingredient names, CAS numbers, regulatory compliance, safety assessment, manufacturer information, and other technical fields. Must completely extract all ingredient information. Use standardized terminology, avoid sensitive descriptions.',
                'msds': 'MSDS Document Conversion: **Must include GHS hazard classification, safety precautions, and emergency procedures**. Process material safety data sheets, focus on safety classification, handling recommendations, GHS labeling, physical and chemical properties, exposure controls, and other technical fields. Use GHS standard terminology.',
                'contract': 'Contract Document Conversion: **Must include party information, contract terms, performance deadlines, and dispute resolution**. Process legal documents, focus on terms content, dates, signatory information, breach of contract, and other commercial legal elements. Use standard contract terminology.',
                'invoice': 'Invoice Document Conversion: **Must include invoice number, issue date, item details, and tax calculations**. Process financial documents, focus on amounts, tax rates, date formats, product information, buyer and seller, payment terms, and other financial elements. Use standard accounting terminology.',
                'report': 'Report Document Conversion: **Must include executive summary, data analysis, and conclusions with recommendations**. Process technical reports, focus on data accuracy, chart descriptions, methodology, references, appendices, and other technical elements. Use professional report terminology.',
                'certificate': 'Certificate Document Conversion: **Must include certificate type, issuing authority, validity period, and certification scope**. Process certification documents, focus on certificate type, issuing authority, validity period, certification scope, certificate number, issue date, and other certification elements. Use standard certification terminology.',
                'manual': 'Manual Document Conversion: **Must include operation steps, safety warnings, and troubleshooting procedures**. Process operation manuals, focus on operation steps, technical specifications, troubleshooting, maintenance, diagrams, and other practical elements. Use technical manual terminology.',
                'specification': 'Specification Document Conversion: **Must include technical parameters, performance indicators, and acceptance standards**. Process technical specifications, focus on technical parameters, performance indicators, testing methods, acceptance standards, material requirements, dimensional specifications, and other technical elements. Use standard specification terminology.',
                'policy': 'Policy Document Conversion: **Must include policy terms, scope of application, and violation handling procedures**. Process policy documents, focus on policy terms, scope of application, execution standards, violation handling, revision procedures, effective date, and other management elements. Use standard policy terminology.',
                'medical': 'Medical Document Conversion: **Must include product information, indications, contraindications, and adverse reactions**. Process medical documents, focus on product information, technical specifications, usage instructions, indications, contraindications, dosage, adverse reactions, storage conditions, and other technical elements. Avoid personal medical information, use product technical terminology.',
                'financial': 'Financial Document Conversion: **Must include financial data, accounting subjects, and audit opinions**. Process financial documents, focus on financial data, accounting subjects, budget allocation, cash flow, profit and loss analysis, audit opinions, and other financial elements. Use standard accounting terminology.',
                'legal': 'Legal Document Conversion: **Must include legal terms, rights and obligations, and dispute resolution procedures**. Process legal documents, focus on legal terms, rights and obligations, scope of application, legal validity, revision procedures, dispute resolution, and other legal elements. Use standard legal terminology.',
                'technical': 'Technical Document Conversion: **Must include technical specifications, design parameters, and test results**. Process technical documents, focus on technical specifications, design parameters, test results, performance indicators, technical standards, implementation plans, and other technical elements. Use standard technical terminology.',
                'marketing': 'Marketing Document Conversion: **Must include product features, target market analysis, and competitive advantages**. Process marketing documents, focus on product features, target market, competitive advantages, marketing strategies, customer analysis, market positioning, and other marketing elements. Use standard marketing terminology.',
                'custom': 'Custom Document Conversion: Process documents based on specific requirements, use professional and neutral business terminology, ensure extraction accuracy and completeness.'
            };
            return guidance[workType] || 'Document Conversion: Extract and convert content according to template requirements, ensure accuracy and completeness';
        } else {
            const guidance = {
                'pif': 'PIF文檔轉換：**成分表是核心必填欄位**，處理化妝品產品信息檔案，專注於INCI成分名稱、CAS編號、含量百分比、功能描述、法規合規性、安全評估、製造商信息等技術欄位。必須完整提取所有成分信息，包括INCI名稱、CAS號碼、含量、功能。使用標準化術語，避免敏感描述。',
                'msds': 'MSDS文檔轉換：**必須包含GHS危險分類、安全防護措施、應急處理程序**。處理材料安全數據表，專注於安全分類、處理建議、GHS標示、物理化學性質、暴露控制等技術欄位。使用GHS標準術語。',
                'contract': '合約文檔轉換：**必須包含當事方信息、合約條款、履行期限、爭議解決**。處理法律文件，專注於條款內容、日期、簽署方信息、違約責任等商業法律要素。使用標準合約術語。',
                'invoice': '發票文檔轉換：**必須包含發票號碼、開票日期、商品明細、稅額計算**。處理財務文件，專注於金額、稅率、日期格式、商品信息、買賣雙方、付款條件等財務要素。使用標準會計術語。',
                'report': '報告文檔轉換：**必須包含執行摘要、數據分析、結論建議**。處理技術報告，專注於數據準確性、圖表說明、方法論、參考資料、附錄等技術要素。使用專業報告術語。',
                'certificate': '證書文檔轉換：**必須包含證書類型、頒發機構、有效期、認證範圍**。處理認證證書，專注於證書類型、頒發機構、有效期、認證範圍、證書編號、簽發日期等認證要素。使用標準認證術語。',
                'manual': '手冊文檔轉換：**必須包含操作步驟、安全警告、故障排除程序**。處理操作手冊，專注於操作步驟、技術規格、故障排除、維護保養、技術規格、圖表說明等實用要素。使用技術手冊術語。',
                'specification': '規格文檔轉換：**必須包含技術參數、性能指標、驗收標準**。處理技術規格，專注於技術參數、性能指標、測試方法、驗收標準、材料要求、尺寸規格等技術要素。使用標準規格術語。',
                'policy': '政策文檔轉換：**必須包含政策條款、適用範圍、違規處理程序**。處理政策文件，專注於政策條款、適用範圍、執行標準、違規處理、修訂程序、生效日期等管理要素。使用標準政策術語。',
                'medical': '醫療文檔轉換：**必須包含產品信息、適應症、禁忌症、不良反應**。處理醫療文件，專注於產品信息、技術規格、使用說明、適應症、禁忌症、用法用量、不良反應、儲存條件等技術要素。避免個人醫療信息，使用產品技術術語。',
                'financial': '財務文檔轉換：**必須包含財務數據、會計科目、審計意見**。處理財務文件，專注於財務數據、會計科目、預算分配、現金流、損益分析、審計意見等財務要素。使用標準會計術語。',
                'legal': '法律文檔轉換：**必須包含法律條款、權利義務、爭議解決程序**。處理法律文件，專注於法律條款、權利義務、適用範圍、法律效力、修訂程序、爭議解決等法律要素。使用標準法律術語。',
                'technical': '技術文檔轉換：**必須包含技術規格、設計參數、測試結果**。處理技術文件，專注於技術規格、設計參數、測試結果、性能指標、技術標準、實施方案等技術要素。使用標準技術術語。',
                'marketing': '行銷文檔轉換：**必須包含產品特點、目標市場分析、競爭優勢**。處理行銷文件，專注於產品特點、目標市場、競爭優勢、行銷策略、客戶分析、市場定位等行銷要素。使用標準行銷術語。',
                'custom': '自定義文檔轉換：根據具體需求處理文檔，使用專業、中性的商業術語，確保提取的準確性和完整性。'
            };
            return guidance[workType] || '文檔轉換：根據模板要求提取和轉換內容，確保準確性和完整性';
        }
    };

    const workTypeGuidance = getWorkTypeGuidance(workType, currentLang);
    
    let prompt;
    if (currentLang === 'en') {
        prompt = `You are a professional document analysis expert specializing in designing extraction instructions for business document processing systems.

Task: Generate an AI extraction prompt based on the following Profile

Work Description: ${description}
Document Type: ${workType}
Template File: ${templateFile.name}
Specialized Guidance: ${workTypeGuidance}

Profile Configuration:
${JSON.stringify(profile, null, 2)}

Fields to Extract:
${fields}

Please generate a detailed prompt that includes:
1. Task Description
2. Extraction Requirements
3. Output Format
4. Important Notes

Prompt Requirements:
- Clear and precise
- Easy to understand
- Include specific examples
- Suitable for AI model use
- Use professional terminology
- Focus on accuracy and completeness

Please generate the prompt:`;
    } else {
        prompt = `你是一個專業的文檔分析專家，專門為商業文檔處理系統設計提取指令。

任務：根據以下Profile生成一個AI提取提示詞

工作描述：${description}
文檔類型：${workType}
模板檔案：${templateFile.name}
專項指導：${workTypeGuidance}

Profile配置：
${JSON.stringify(profile, null, 2)}

需要提取的欄位：
${fields}

請生成一個詳細的提示詞，包含：
1. 任務描述
2. 提取要求
3. 輸出格式
4. 注意事項

提示詞要求：
- 清晰明確
- 易於理解
- 包含具體示例
- 適合AI模型使用
- 使用專業術語
- 專注於準確性和完整性

請生成提示詞：`;
    }

    const promptText = document.getElementById('promptTemplate');
    if (promptText) {
        promptText.value = prompt;
    }
}

// 安全檢查相關函數
let safetyCheckCache = {}; // 快取安全檢查結果
let contentHashes = {}; // 追蹤內容變更
let selectedSafetyModels = []; // 用戶選擇的安全檢查模型

// 執行安全檢查
async function performSafetyCheck(content, contentType, validationDiv) {
    try {
        // 檢查是否有選擇的模型
        if (selectedSafetyModels.length === 0) {
            const message = currentLang === 'en' ? '💡 Safety check is optional. You can skip it or select AI models to perform safety check.' : '💡 安全檢查是可選的。您可以跳過或選擇AI模型進行安全檢查。';
            showValidationResult(validationDiv, 'info', message);
            return true; // 允許跳過安全檢查
        }
        
        // 顯示檢查中狀態
        const checkingMessage = currentLang === 'en' 
            ? `Performing safety check using ${selectedSafetyModels.length} models...` 
            : `正在使用 ${selectedSafetyModels.length} 個模型執行安全檢查...`;
        showValidationResult(validationDiv, 'info', checkingMessage, true);
        
        // 計算內容雜湊值
        const contentHash = await calculateContentHash(content);
        
        // 檢查是否已快取
        if (safetyCheckCache[contentHash]) {
            displaySafetyResult(safetyCheckCache[contentHash], validationDiv);
            return safetyCheckCache[contentHash].is_safe;
        }
        
        // 執行安全檢查
        const response = await fetch('/api/safety/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                context: 'cosmetic_context',
                check_models: selectedSafetyModels
            })
        });
        
        if (!response.ok) {
            const errorMessage = currentLang === 'en' ? `Safety check failed: ${response.statusText}` : `安全檢查失敗: ${response.statusText}`;
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        
        if (result.success) {
            // 快取結果
            safetyCheckCache[contentHash] = result.result;
            contentHashes[contentType] = contentHash;
            
            // 顯示結果
            displaySafetyResult(result.result, validationDiv);
            return result.result.is_safe;
        } else {
            const errorMessage = currentLang === 'en' ? `Safety check failed: ${result.error}` : `安全檢查失敗: ${result.error}`;
            showValidationResult(validationDiv, 'error', errorMessage);
            return false;
        }
        
    } catch (error) {
        console.error('安全檢查錯誤:', error);
        const errorMessage = currentLang === 'en' ? `Safety check failed: ${error.message}` : `安全檢查失敗: ${error.message}`;
        showValidationResult(validationDiv, 'error', errorMessage);
        return false;
    }
}

// 顯示安全檢查結果
function displaySafetyResult(result, validationDiv) {
    const isSafe = result.is_safe;
    const riskLevel = result.local_check?.risk_level || 'unknown';
    const passedModels = result.passed_models || [];
    const failedModels = result.failed_models || [];
    const suggestions = result.suggestions || [];
    const aiChecks = result.ai_checks || {};
    
    let statusClass = 'success';
    let statusIcon = '✅';
    let statusText = currentLang === 'en' ? 'Safety check passed' : '安全檢查通過';
    
    if (!isSafe) {
        statusClass = 'warning';
        statusIcon = '⚠️';
        statusText = currentLang === 'en' ? 'Safety check found risks' : '安全檢查發現風險';
    }
    
    // 構建結果訊息
    let message = `${statusIcon} ${statusText}`;
    
    if (passedModels.length > 0) {
        const modelNames = passedModels.map(model => {
            const firstDashIndex = model.indexOf('-');
            const provider = model.substring(0, firstDashIndex);
            const modelName = model.substring(firstDashIndex + 1);
            return `${provider} ${modelName}`;
        });
        const passedText = currentLang === 'en' ? 'Passed models:' : '通過模型檢查：';
        message += `\n\n✅ ${passedText}${modelNames.join('、')}`;
    }
    
    if (failedModels.length > 0) {
        const modelNames = failedModels.map(model => {
            const firstDashIndex = model.indexOf('-');
            const provider = model.substring(0, firstDashIndex);
            const modelName = model.substring(firstDashIndex + 1);
            return `${provider} ${modelName}`;
        });
        const failedText = currentLang === 'en' ? 'Failed models:' : '未通過模型檢查：';
        message += `\n\n❌ ${failedText}${modelNames.join('、')}`;
    }
    
    if (suggestions.length > 0) {
        const suggestionsText = currentLang === 'en' ? 'Suggestions:' : '建議：';
        const translatedSuggestions = suggestions.map(s => {
            // 翻譯常見的建議內容
            if (currentLang === 'zh_TW') {
                if (s.includes('內容安全，可以正常處理')) return '• 內容安全，可以正常處理';
                if (s.includes('無法解析 AI 回應，預設為安全')) return '• 無法解析 AI 回應，預設為安全';
                if (s.includes('建議修改內容或使用其他模型')) return '• 建議修改內容或使用其他模型';
                if (s.includes('建議提供更詳細的欄位定義')) return '• 建議提供更詳細的欄位定義';
                if (s.includes('建議提供更詳細的提取要求')) return '• 建議提供更詳細的提取要求';
            } else {
                if (s.includes('內容安全，可以正常處理')) return '• Content is safe and can be processed normally';
                if (s.includes('無法解析 AI 回應，預設為安全')) return '• Unable to parse AI response, defaulting to safe';
                if (s.includes('建議修改內容或使用其他模型')) return '• Suggest modifying content or using other models';
                if (s.includes('建議提供更詳細的欄位定義')) return '• Suggest providing more detailed field definitions';
                if (s.includes('建議提供更詳細的提取要求')) return '• Suggest providing more detailed extraction requirements';
            }
            return `• ${s}`;
        });
        message += `\n\n💡 ${suggestionsText}\n${translatedSuggestions.join('\n')}`;
    }
    
    // 不再顯示獨立的安全檢查結果區塊，結果已顯示在驗證區域內
    
    showValidationResult(validationDiv, statusClass, message);
}

// 顯示詳細的安全檢查結果
function displayDetailedSafetyResults(result) {
    const safetyResultsDiv = document.getElementById('safetyResults');
    const safetyResultContent = document.getElementById('safetyResultContent');
    
    if (!safetyResultsDiv || !safetyResultContent) return;
    
    const passedModels = result.passed_models || [];
    const failedModels = result.failed_models || [];
    const aiChecks = result.ai_checks || {};
    
    let html = '';
    
    // 顯示通過的模型
    passedModels.forEach(model => {
        const [provider, modelName] = model.split('-', 2);
        const checkResult = aiChecks[model] || {};
        html += `
            <div class="safety-result-item">
                <div class="safety-result-icon success">✅</div>
                <div class="safety-result-text">
                    <div class="safety-result-model">${getModelDisplayName({provider, model: modelName})}</div>
                    <div class="safety-result-status">通過安全檢查</div>
                </div>
            </div>
        `;
    });
    
    // 顯示未通過的模型
    failedModels.forEach(model => {
        const [provider, modelName] = model.split('-', 2);
        const checkResult = aiChecks[model] || {};
        html += `
            <div class="safety-result-item">
                <div class="safety-result-icon error">❌</div>
                <div class="safety-result-text">
                    <div class="safety-result-model">${getModelDisplayName({provider, model: modelName})}</div>
                    <div class="safety-result-status">未通過安全檢查</div>
                </div>
            </div>
        `;
    });
    
    // 顯示本機檢查結果
    if (result.local_check) {
        const localResult = result.local_check;
        const localIcon = localResult.is_safe ? '✅' : '⚠️';
        const localClass = localResult.is_safe ? 'success' : 'warning';
        
        html += `
            <div class="safety-result-item">
                <div class="safety-result-icon ${localClass}">${localIcon}</div>
                <div class="safety-result-text">
                    <div class="safety-result-model">本機預檢查</div>
                    <div class="safety-result-status">風險等級: ${localResult.risk_level}</div>
                </div>
            </div>
        `;
    }
    
    safetyResultContent.innerHTML = html;
    safetyResultsDiv.style.display = 'block';
}

// 獲取可用的 AI 模型
async function getAvailableAIModels() {
    try {
        const response = await fetch('/api/settings');
        const data = await response.json();
        
        if (!data.success) {
            return [];
        }
        
        const settings = data.settings;
        const models = [];
        
        // 檢查 OpenAI
        if (settings.openai_api_key) {
            models.push(
                { provider: 'openai', model: 'gpt-4o' },
                { provider: 'openai', model: 'gpt-4o-mini' },
                { provider: 'openai', model: 'gpt-4-turbo' },
                { provider: 'openai', model: 'gpt-3.5-turbo' }
            );
        }
        
        // 檢查 Gemini
        if (settings.gemini_api_key) {
            models.push(
                { provider: 'gemini', model: 'gemini-2.5-pro' },
                { provider: 'gemini', model: 'gemini-2.5-flash' },
                { provider: 'gemini', model: 'gemini-2.0-flash' },
                { provider: 'gemini', model: 'gemini-2.0-flash-lite' },
                { provider: 'gemini', model: 'gemini-pro' }
            );
        }
        
        // 檢查 Claude
        if (settings.claude_api_key) {
            models.push(
                { provider: 'claude', model: 'claude-3-5-haiku-20241022' },
                { provider: 'claude', model: 'claude-3-5-sonnet-20241022' },
                { provider: 'claude', model: 'claude-3-opus-20240229' }
            );
        }
        
        // 檢查 Grok
        if (settings.grok_api_key) {
            models.push(
                { provider: 'grok', model: 'grok-beta' },
                { provider: 'grok', model: 'grok-2' }
            );
        }
        
        // 檢查 Copilot
        if (settings.copilot_api_key) {
            models.push(
                { provider: 'copilot', model: 'copilot-gpt-4' },
                { provider: 'copilot', model: 'copilot-gpt-4o' }
            );
        }
        
        return models;
        
    } catch (error) {
        console.error('獲取可用模型失敗:', error);
        return [];
    }
}

// 計算內容雜湊值
async function calculateContentHash(content) {
    const encoder = new TextEncoder();
    const data = encoder.encode(content);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// 檢查內容是否已變更
async function checkContentChanged(contentType, currentContent) {
    const currentHash = await calculateContentHash(currentContent);
    const storedHash = contentHashes[contentType];
    
    if (storedHash && currentHash !== storedHash) {
        // 內容已變更，清除快取
        delete safetyCheckCache[storedHash];
        delete contentHashes[contentType];
        return true;
    }
    
    return false;
}

// 監控 Profile 內容變更
function setupProfileChangeMonitoring() {
    const profileTextarea = document.getElementById('generatedProfile');
    if (!profileTextarea) return;
    
    let lastContent = '';
    
    profileTextarea.addEventListener('input', async function() {
        const currentContent = this.value;
        
        if (currentContent !== lastContent) {
            lastContent = currentContent;
            
            // 檢查內容是否已變更
            const hasChanged = await checkContentChanged('profile', currentContent);
            
            if (hasChanged) {
                // 顯示內容已變更警告
                const validationDiv = document.getElementById('profileValidation');
                if (validationDiv) {
                    showValidationResult(validationDiv, 'warning', '⚠️ 內容已變更，安全檢查結果可能不再適用，建議重新驗證');
                }
            }
        }
    });
}

// 監控提示詞內容變更
function setupPromptChangeMonitoring() {
    const promptTextarea = document.getElementById('generatedPrompt');
    if (!promptTextarea) return;
    
    let lastContent = '';
    
    promptTextarea.addEventListener('input', async function() {
        const currentContent = this.value;
        
        if (currentContent !== lastContent) {
            lastContent = currentContent;
            
            // 檢查內容是否已變更
            const hasChanged = await checkContentChanged('prompt', currentContent);
            
            if (hasChanged) {
                // 顯示內容已變更警告
                const validationDiv = document.getElementById('promptValidation');
                if (validationDiv) {
                    showValidationResult(validationDiv, 'warning', '⚠️ 內容已變更，安全檢查結果可能不再適用，建議重新驗證');
                }
            }
        }
    });
}

// 初始化安全檢查模型選項
async function initializeSafetyModelOptions() {
    try {
        const availableModels = await getAvailableAIModels();
        const modelProvidersContainer = document.getElementById('safetyModelProviders');
        
        if (!modelProvidersContainer) return;
        
        if (availableModels.length === 0) {
            modelProvidersContainer.innerHTML = '<p style="color: #666; text-align: center; padding: 20px;">沒有可用的 AI 模型進行安全檢查</p>';
            return;
        }
        
        // 按業者分組模型
        const modelsByProvider = {};
        availableModels.forEach(model => {
            if (!modelsByProvider[model.provider]) {
                modelsByProvider[model.provider] = [];
            }
            modelsByProvider[model.provider].push(model);
        });
        
        // 清空容器
        modelProvidersContainer.innerHTML = '';
        
        // 為每個業者創建選項
        Object.keys(modelsByProvider).forEach(provider => {
            const models = modelsByProvider[provider];
            const providerDiv = document.createElement('div');
            providerDiv.className = 'model-provider';
            
            const providerName = getProviderDisplayName(provider);
            const providerIcon = getProviderIcon(provider);
            
            providerDiv.innerHTML = `
                <div class="provider-header" data-provider="${provider}">
                    <div class="provider-name">
                        <span class="provider-icon">${providerIcon}</span>
                        ${providerName}
                    </div>
                    <span class="provider-toggle">▼</span>
                </div>
                <div class="provider-models" data-provider="${provider}">
                    ${models.map((model, index) => {
                        const modelId = `safety-model-${provider}-${index}`;
                        return `
                            <div class="model-option" data-model="${model.provider}-${model.model}">
                                <input type="checkbox" id="${modelId}" value="${model.provider}-${model.model}">
                                <div class="model-info">
                                    <div class="model-name">${model.model}</div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
            
            // 添加業者展開/收合事件
            const providerHeader = providerDiv.querySelector('.provider-header');
            const providerModels = providerDiv.querySelector('.provider-models');
            
            providerHeader.addEventListener('click', function() {
                const isExpanded = providerModels.classList.contains('expanded');
                if (isExpanded) {
                    providerModels.classList.remove('expanded');
                    providerHeader.classList.remove('expanded');
                } else {
                    providerModels.classList.add('expanded');
                    providerHeader.classList.add('expanded');
                }
            });
            
            // 添加模型選擇事件
            const modelOptions = providerDiv.querySelectorAll('.model-option');
            modelOptions.forEach(option => {
                option.addEventListener('click', function(e) {
                    if (e.target.type !== 'checkbox') {
                        const checkbox = option.querySelector('input[type="checkbox"]');
                        checkbox.checked = !checkbox.checked;
                        updateSelectedModels();
                        updatePricingInfo();
                    }
                });
                
                const checkbox = option.querySelector('input[type="checkbox"]');
                checkbox.addEventListener('change', function() {
                    updateSelectedModels();
                    updatePricingInfo();
                });
            });
            
            modelProvidersContainer.appendChild(providerDiv);
        });
        
        // 預設展開第一個業者
        const firstProvider = modelProvidersContainer.querySelector('.provider-header');
        if (firstProvider) {
            firstProvider.click();
        }
        
        // 初始化選中的模型
        updateSelectedModels();
        updatePricingInfo();
        
    } catch (error) {
        console.error('初始化安全檢查模型選項失敗:', error);
    }
}

// 獲取業者顯示名稱
function getProviderDisplayName(provider) {
    const providerNames = {
        'openai': 'OpenAI',
        'gemini': 'Google Gemini',
        'claude': 'Anthropic Claude',
        'grok': 'xAI Grok',
        'copilot': 'Microsoft Copilot'
    };
    
    return providerNames[provider] || provider;
}

// 獲取業者圖標
function getProviderIcon(provider) {
    const providerIcons = {
        'openai': '🤖',
        'gemini': '🔍',
        'claude': '🧠',
        'grok': '⚡',
        'copilot': '💼'
    };
    
    return providerIcons[provider] || '🤖';
}

// 獲取模型顯示名稱
function getModelDisplayName(model) {
    const providerName = getProviderDisplayName(model.provider);
    return `${providerName} ${model.model}`;
}

// 獲取模型定價信息
function getModelPricing(model) {
    const pricing = {
        'openai': { 
            'gpt-4o': '$0.005/$0.015', 
            'gpt-4o-mini': '$0.00015/$0.0006',
            'gpt-4-turbo': '$0.01/$0.03',
            'gpt-3.5-turbo': '$0.0005/$0.0015'
        },
        'gemini': { 
            'gemini-2.5-pro': '$0.00125/$0.01', 
            'gemini-2.5-flash': '$0.0003/$0.0025',
            'gemini-2.5-flash-lite': '$0.0001/$0.0004',
            'gemini-2.0-flash': '$0.0001/$0.0004',
            'gemini-2.0-flash-lite': '$0.000075/$0.0003',
            'gemini-pro': '$0.0005/$0.0015'
        },
        'claude': { 
            'claude-3-5-haiku-20241022': '$0.0008/$0.004',
            'claude-3-5-sonnet-20241022': '$0.003/$0.015',
            'claude-3-opus-20240229': '$0.015/$0.075'
        },
        'grok': { 
            'grok-2': '$0.0003/$0.001',
            'grok-beta': '$0.0002/$0.0015'
        },
        'copilot': { 
            'copilot-gpt-4': '$0.005/$0.015',
            'copilot-gpt-4-turbo': '$0.01/$0.03'
        }
    };
    
    const modelPricing = pricing[model.provider]?.[model.model] || (currentLang === 'en' ? 'Price Unknown' : '價格未知');
    return modelPricing;
}

// 更新選中的模型
function updateSelectedModels() {
    const checkboxes = document.querySelectorAll('#safetyModelProviders input[type="checkbox"]:checked');
    selectedSafetyModels = Array.from(checkboxes).map(cb => {
        const value = cb.value;
        const firstDashIndex = value.indexOf('-');
        const provider = value.substring(0, firstDashIndex);
        const model = value.substring(firstDashIndex + 1);
        return { provider, model };
    });
    
    console.log('選中的安全檢查模型:', selectedSafetyModels);
}

// 更新定價信息
function updatePricingInfo() {
    const pricingContent = document.getElementById('pricingContent');
    if (!pricingContent) return;
    
    if (selectedSafetyModels.length === 0) {
        const message = currentLang === 'en' ? 'Please select a model to view pricing information' : '請選擇模型查看定價信息';
        pricingContent.innerHTML = `<p style="color: #666; text-align: center; padding: 20px;">${message}</p>`;
        return;
    }
    
    let html = '';
    let totalInputCost = 0;
    let totalOutputCost = 0;
    
    selectedSafetyModels.forEach(model => {
        const pricing = getModelPricing(model);
        
        if (pricing === '價格未知') {
            const unknownPriceText = currentLang === 'en' ? 'Price Unknown' : '價格未知';
            html += `
                <div class="pricing-item">
                    <div class="pricing-model-name">${getModelDisplayName(model)}</div>
                    <div class="pricing-cost">${unknownPriceText}</div>
                </div>
            `;
            return;
        }
        
        const [inputCost, outputCost] = pricing.split('/');
        
        // 解析成本（移除 $ 符號並轉換為數字）
        const inputCostNum = parseFloat(inputCost.replace('$', '')) || 0;
        const outputCostNum = parseFloat(outputCost.replace('$', '')) || 0;
        
        totalInputCost += inputCostNum;
        totalOutputCost += outputCostNum;
        
        const inputText = currentLang === 'en' ? 'Input' : '輸入';
        const outputText = currentLang === 'en' ? 'Output' : '輸出';
        html += `
            <div class="pricing-item">
                <div class="pricing-model-name">${getModelDisplayName(model)}</div>
                <div class="pricing-cost">${inputText}: ${inputCost} / ${outputText}: ${outputCost} per 1K tokens</div>
            </div>
        `;
    });
    
    // 添加總計
    const totalText = currentLang === 'en' ? 'Total (Input/Output)' : '總計（輸入/輸出）';
    html += `
        <div class="pricing-total">
            <div>${totalText}</div>
            <div class="total-cost">$${totalInputCost.toFixed(6)} / $${totalOutputCost.toFixed(6)} per 1K tokens</div>
        </div>
    `;
    
    pricingContent.innerHTML = html;
}

// 驗證Profile
async function validateProfile() {
    const profileText = document.getElementById('generatedProfile').value;
    const validationDiv = document.getElementById('profileValidation');
    
    if (!profileText.trim()) {
        const message = currentLang === 'en' ? 'Please enter Profile JSON' : '請輸入Profile JSON';
        showValidationResult(validationDiv, 'error', message);
        return false;
    }
    
    try {
        const profile = JSON.parse(profileText);
        
        if (validateProfileStructure(profile)) {
            // 檢查欄位數量
            if (profile.fields && profile.fields.length > 25) {
                const message = currentLang === 'en' 
                    ? `Too many fields (${profile.fields.length}), recommend keeping under 25` 
                    : `欄位數量過多 (${profile.fields.length}個)，建議控制在25個以內`;
                showValidationResult(validationDiv, 'warning', message);
                return false;
            }
            
            // 檢查欄位描述長度
            const longDescriptions = profile.fields.filter(field => 
                field.description && field.description.length > 50
            );
            
            if (longDescriptions.length > 0) {
                const message = currentLang === 'en' 
                    ? `${longDescriptions.length} fields have descriptions that are too long, recommend keeping under 50 characters` 
                    : `有${longDescriptions.length}個欄位的描述過長，建議控制在50字元以內`;
                showValidationResult(validationDiv, 'warning', message);
                return false;
            }
            
            // 執行安全檢查（可選）
            const safetyCheckResult = await performSafetyCheck(profileText, 'profile', validationDiv);
            
            // 安全檢查失敗時，仍然允許繼續驗證，但會顯示警告
            if (safetyCheckResult === false) {
                const warningMessage = currentLang === 'en' 
                    ? '⚠️ Safety check failed, but you can still proceed. Please review the content carefully.' 
                    : '⚠️ 安全檢查失敗，但您仍可繼續。請仔細檢查內容。';
                showValidationResult(validationDiv, 'warning', warningMessage);
                // 不返回false，允許繼續驗證，但標記安全檢查失敗
                currentWork.safetyCheckFailed = true;
            } else {
                currentWork.safetyCheckFailed = false;
            }
            
            // 自動壓縮Profile
            let compressedProfile = compressProfile(profile);
            let compressedText = JSON.stringify(compressedProfile, null, 0);
            
            // 如果壓縮後仍然過長，進行更激進的壓縮
            if (compressedText.length > 2000) {
                compressedProfile = aggressiveCompressProfile(profile);
                compressedText = JSON.stringify(compressedProfile, null, 0);
                
                // 如果仍然過長，提供用戶選擇
                if (compressedText.length > 2000) {
                    const suggestions = generateOptimizationSuggestions(profile);
                    const message = currentLang === 'en' 
                        ? `Profile too long (${compressedText.length} characters), compressed but still exceeds 2000 character limit. Suggestions: ${suggestions.join('; ')}` 
                        : `Profile過長 (${compressedText.length}字元)，已進行壓縮但仍超過2000字元限制。建議：${suggestions.join('; ')}`;
                    showValidationResult(validationDiv, 'warning', message);
                    
                    // 仍然更新為壓縮版本，讓用戶決定是否使用
                    document.getElementById('generatedProfile').value = compressedText;
                    currentWork.profile = compressedProfile;
                    return false; // 返回false，但已更新內容
                }
            }
            
            if (compressedText.length < 500) {
                const message = currentLang === 'en' 
                    ? `Profile is short (${compressedText.length} characters), suggest providing more detailed field definitions` 
                    : `Profile較短 (${compressedText.length}字元)，建議提供更詳細的欄位定義`;
                showValidationResult(validationDiv, 'warning', message);
            }
            
            // 更新輸入框為壓縮後的JSON
            document.getElementById('generatedProfile').value = compressedText;
            
            currentWork.profile = compressedProfile;
            
            // 根據安全檢查結果顯示不同的成功訊息
            let successMessage;
            if (currentWork.safetyCheckFailed) {
                successMessage = currentLang === 'en' 
                    ? `Profile validated and compressed successfully (${compressedText.length} characters), but safety check failed` 
                    : `Profile驗證成功並已壓縮 (${compressedText.length}字元)，但安全檢查失敗`;
                showValidationResult(validationDiv, 'warning', successMessage);
            } else {
                successMessage = currentLang === 'en' 
                    ? `Profile validated and compressed successfully (${compressedText.length} characters)` 
                    : `Profile驗證成功並已壓縮 (${compressedText.length}字元)`;
                showValidationResult(validationDiv, 'success', successMessage);
            }
            return true;
        } else {
            const message = currentLang === 'en' ? 'Profile structure is incorrect' : 'Profile結構不正確';
            showValidationResult(validationDiv, 'error', message);
            return false;
        }
    } catch (error) {
        const message = currentLang === 'en' ? 'JSON format error: ' + error.message : 'JSON格式錯誤：' + error.message;
        showValidationResult(validationDiv, 'error', message);
        return false;
    }
}

function validateProfileStructure(profile) {
    return profile && 
           typeof profile.name === 'string' &&
           typeof profile.description === 'string' &&
           Array.isArray(profile.fields) &&
           profile.fields.every(field => 
               field.name && 
               field.type && 
               typeof field.required === 'boolean'
           );
}

// 壓縮Profile函數
function compressProfile(profile) {
    const compressed = {
        name: profile.name,
        description: profile.description,
        fields: profile.fields.map(field => {
            const compressedField = {
                name: field.name,
                type: field.type,
                required: field.required
            };
            
            // 簡化description（更激進的壓縮）
            if (field.description) {
                compressedField.desc = field.description.length > 30 
                    ? field.description.substring(0, 27) + '...'
                    : field.description;
            }
            
            // 簡化template_reference
            if (field.template_reference) {
                compressedField.ref = field.template_reference
                    .replace(/基本資料\s+/g, '')
                    .replace(/標籤\s+/g, '')
                    .replace(/成分\s+/g, '')
                    .replace(/品質\s+/g, '')
                    .replace(/安全評估\s+/g, '')
                    .replace(/封面\s+/g, '');
            }
            
            return compressedField;
        })
    };
    
    return compressed;
}

// 更激進的壓縮Profile函數（保持AI可讀性）
function aggressiveCompressProfile(profile) {
    const compressed = {
        name: profile.name,
        description: profile.description.length > 50 ? profile.description.substring(0, 47) + '...' : profile.description,
        fields: profile.fields.slice(0, 18).map(field => { // 限制最多18個欄位
            const compressedField = {
                name: field.name, // 保持完整欄位名稱，不截斷
                type: field.type,
                required: field.required
            };
            
            // 適度壓縮description，保持關鍵信息
            if (field.description) {
                if (field.description.length > 40) {
                    // 嘗試在句號或逗號處截斷，保持語意完整
                    const truncateAt = Math.max(
                        field.description.lastIndexOf('。', 40),
                        field.description.lastIndexOf('，', 40),
                        field.description.lastIndexOf('.', 40),
                        field.description.lastIndexOf(',', 40)
                    );
                    compressedField.desc = truncateAt > 20 
                        ? field.description.substring(0, truncateAt + 1)
                        : field.description.substring(0, 37) + '...';
                } else {
                    compressedField.desc = field.description;
                }
            }
            
            // 適度壓縮template_reference，保持可讀性
            if (field.template_reference) {
                compressedField.ref = field.template_reference
                    .replace(/基本資料\s+/g, '')
                    .replace(/標籤\s+/g, '')
                    .replace(/成分\s+/g, '')
                    .replace(/品質\s+/g, '')
                    .replace(/安全評估\s+/g, '')
                    .replace(/封面\s+/g, '')
                    .replace(/頁面\s+/g, 'p.')
                    .replace(/第\s*(\d+)\s*頁/g, 'p.$1')
                    .substring(0, 15); // 適度限制長度
            }
            
            return compressedField;
        })
    };
    
    return compressed;
}

// 生成優化建議
function generateOptimizationSuggestions(profile) {
    const suggestions = [];
    
    if (profile.fields.length > 25) {
        suggestions.push(`減少欄位數量至25個以下 (目前${profile.fields.length}個)`);
    }
    
    const longDescriptions = profile.fields.filter(field => 
        field.description && field.description.length > 50
    );
    
    if (longDescriptions.length > 0) {
        suggestions.push(`縮短${longDescriptions.length}個欄位描述至50字元以內`);
    }
    
    const longReferences = profile.fields.filter(field => 
        field.template_reference && field.template_reference.length > 20
    );
    
    if (longReferences.length > 0) {
        suggestions.push(`簡化${longReferences.length}個template_reference`);
    }
    
    if (suggestions.length === 0) {
        suggestions.push('考慮合併相似欄位或移除非必要欄位');
    }
    
    return suggestions.join('; ');
}

// 驗證提示詞
async function validatePrompt() {
    const promptText = document.getElementById('generatedPrompt').value;
    const validationDiv = document.getElementById('promptValidation');
    
    if (!promptText.trim()) {
        const message = currentLang === 'en' ? 'Please enter prompt' : '請輸入提示詞';
        showValidationResult(validationDiv, 'error', message);
        return false;
    }
    
    if (promptText.length < 50) {
        const message = currentLang === 'en' ? 'Prompt is too short, please provide more detailed instructions' : '提示詞太短，請提供更詳細的說明';
        showValidationResult(validationDiv, 'error', message);
        return false;
    }
    
    // 檢查長度限制
    if (promptText.length > 4000) {
        const message = currentLang === 'en' 
            ? `Prompt too long (${promptText.length} characters), please keep under 4000 characters` 
            : `提示詞過長 (${promptText.length}字元)，請控制在4000字元以內`;
        showValidationResult(validationDiv, 'error', message);
        return false;
    }
    
    if (promptText.length < 1500) {
        const message = currentLang === 'en' 
            ? `Prompt is short (${promptText.length} characters), suggest providing more detailed extraction requirements` 
            : `提示詞較短 (${promptText.length}字元)，建議提供更詳細的提取要求`;
        showValidationResult(validationDiv, 'warning', message);
    }
    
    // 執行安全檢查（可選）
    const safetyCheckResult = await performSafetyCheck(promptText, 'prompt', validationDiv);
    
    // 安全檢查失敗時，仍然允許繼續驗證，但會顯示警告
    if (safetyCheckResult === false) {
        const warningMessage = currentLang === 'en' 
            ? '⚠️ Safety check failed, but you can still proceed. Please review the content carefully.' 
            : '⚠️ 安全檢查失敗，但您仍可繼續。請仔細檢查內容。';
        showValidationResult(validationDiv, 'warning', warningMessage);
        // 不返回false，允許繼續驗證，但標記安全檢查失敗
        currentWork.safetyCheckFailed = true;
    } else {
        currentWork.safetyCheckFailed = false;
    }
    
    currentWork.prompt = promptText;
    return true;
}

// 處理模板上傳
function handleTemplateUpload(event) {
    const file = event.target.files[0];
    const previewDiv = document.getElementById('templatePreview');
    
    if (!file) {
        currentWork.template = null;
        const message = currentLang === 'en' ? 'Please select a template file' : '請選擇模板檔案';
        showTemplatePreview(previewDiv, 'error', message);
        return;
    }
    
    const allowedTypes = [
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
        'application/vnd.openxmlformats-officedocument.presentationml.presentation' // .pptx
    ];
    
    if (!allowedTypes.includes(file.type)) {
        const message = currentLang === 'en' ? 'Unsupported file format, please select Word, Excel or PowerPoint files' : '不支援的檔案格式，請選擇Word、Excel或PowerPoint檔案';
        showTemplatePreview(previewDiv, 'error', message);
        return;
    }
    
    // 檢查檔案大小並提醒用戶
    const fileSizeMB = file.size / (1024 * 1024);
    let sizeWarning = '';
    
    if (fileSizeMB > 10) {
        if (currentLang === 'en') {
            sizeWarning = `
        
⚠️ File Size Warning:
Your template file size is ${fileSizeMB.toFixed(1)}MB, which may exceed some AI tools' context length limits.

Recommended AI Tool Choices:
- Gemini 1.5 Pro (2M tokens) - Best for large files
- Gemini 1.5 Flash (1M tokens) - Second best choice
- Claude 3.5 (200K tokens) - Medium size files
- ChatGPT GPT-4 (128K tokens) - Smaller files`;
        } else {
            sizeWarning = `
        
⚠️ 檔案大小提醒：
您的模板檔案大小為 ${fileSizeMB.toFixed(1)}MB，這可能會超過某些AI工具的上下文長度限制。

建議的AI工具選擇：
- Gemini 1.5 Pro (2M tokens) - 最適合大檔案
- Gemini 1.5 Flash (1M tokens) - 次佳選擇
- Claude 3.5 (200K tokens) - 中等大小檔案
- ChatGPT GPT-4 (128K tokens) - 較小檔案`;
        }
    } else if (fileSizeMB > 5) {
        if (currentLang === 'en') {
            sizeWarning = `
        
💡 File Size Warning:
Your template file size is ${fileSizeMB.toFixed(1)}MB, recommend using AI tools that support longer context:
- Gemini 1.5 Pro/Flash
- Claude 3.5`;
        } else {
            sizeWarning = `
        
💡 檔案大小提醒：
您的模板檔案大小為 ${fileSizeMB.toFixed(1)}MB，建議使用支援較長上下文的AI工具：
- Gemini 1.5 Pro/Flash
- Claude 3.5`;
        }
    }
    
    currentWork.template = file;
    const successMessage = currentLang === 'en' ? `Template selected: ${file.name}` : `已選擇模板：${file.name}`;
    showTemplatePreview(previewDiv, 'success', `${successMessage}${sizeWarning}`);
}

// 創建工作
async function createWork() {
    console.log('開始創建工作...');
    console.log('currentWork狀態:', currentWork);
    
    // 收集基本資訊
    const nameElement = document.getElementById('workName');
    const descriptionElement = document.getElementById('workDescription');
    const typeElement = document.getElementById('workType');
    const brandElement = document.getElementById('workBrand');
    
    console.log('元素檢查:', { 
        nameElement: !!nameElement, 
        descriptionElement: !!descriptionElement, 
        typeElement: !!typeElement,
        brandElement: !!brandElement
    });
    
    if (!nameElement || !descriptionElement || !typeElement) {
        const message = currentLang === 'en' ? '❌ Form elements not found, please reload the page' : '❌ 表單元素未找到，請重新載入頁面';
        alert(message);
        console.error('缺少必要元素:', { nameElement, descriptionElement, typeElement });
        return;
    }
    
    const name = nameElement.value;
    const description = descriptionElement.value;
    const type = typeElement.value;
    const brand = brandElement ? brandElement.value.trim() : '';
    
    console.log('基本資訊:', { name, description, type, brand });
    
    if (!name.trim() || !description.trim()) {
        const message = currentLang === 'en' ? '❌ Please fill in work name and description' : '❌ 請填寫工作名稱和描述';
        alert(message);
        return;
    }
    
    // 驗證Profile
    if (!validateProfile()) {
        const message = currentLang === 'en' ? '❌ Please generate and validate Profile' : '❌ 請生成並驗證Profile';
        alert(message);
        console.log('Profile驗證失敗');
        return;
    }
    
    // 驗證提示詞
    if (!(await validatePrompt())) {
        const message = currentLang === 'en' ? '❌ Please generate and validate prompt' : '❌ 請生成並驗證提示詞';
        alert(message);
        console.log('提示詞驗證失敗');
        return;
    }
    
    // 檢查模板上傳
    const templateFile = document.getElementById('templateFile');
    if (!templateFile || !templateFile.files || !templateFile.files[0]) {
        const message = currentLang === 'en' ? '❌ Please upload output template' : '❌ 請上傳輸出模板';
        alert(message);
        console.log('模板上傳失敗');
        return;
    }
    
    // 設置模板
    currentWork.template = templateFile.files[0];
    
    console.log('所有驗證通過，準備發送請求...');
    console.log('currentWork.profile:', currentWork.profile);
    console.log('currentWork.prompt:', currentWork.prompt);
    console.log('currentWork.template:', currentWork.template);
    
    const formData = new FormData();
    formData.append('name', name);
    formData.append('description', description);
    formData.append('type', type);
    formData.append('brand', brand);
    formData.append('profile', JSON.stringify(currentWork.profile));
    formData.append('prompt', currentWork.prompt);
    formData.append('template', currentWork.template);
    
    console.log('FormData內容:');
    for (let [key, value] of formData.entries()) {
        console.log(`  ${key}:`, value);
    }
    
    fetch('/api/works', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const message = currentLang === 'en' ? '✅ Work created successfully!' : '✅ 工作創建成功！';
            alert(message);
            closeCreateWorkModal();
            // 重新載入工作列表
            if (typeof prodocux !== 'undefined' && prodocux.loadWorks) {
                prodocux.loadWorks().then(() => {
                    // 選擇新創建的工作
                    if (data.work && data.work.id) {
                        prodocux.selectWork(data.work.id);
                    }
                });
            } else {
                console.warn('prodocux 對象不存在，嘗試重新載入頁面');
                location.reload();
            }
        } else {
            const errorMsg = currentLang === 'en' ? 'Unknown error' : '未知錯誤';
            const message = currentLang === 'en' ? '❌ Creation failed: ' + (data.error || errorMsg) : '❌ 創建失敗：' + (data.error || '未知錯誤');
            alert(message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const message = currentLang === 'en' ? '❌ Creation failed: ' + error.message : '❌ 創建失敗：' + error.message;
        alert(message);
    });
}

// 工具函數
function showValidationResult(element, type, message) {
    if (element) {
        element.innerHTML = `<div class="${type}">${message}</div>`;
    }
}

function showTemplatePreview(element, type, message) {
    if (element) {
        element.innerHTML = `<div class="${type}">${message}</div>`;
    }
}

function closeCreateWorkModal() {
    const modal = document.getElementById('createWorkModal');
    if (modal) {
        modal.style.display = 'none';
    }
    resetForm();
}

function resetForm() {
    currentWork = {
        name: '',
        description: '',
        type: '',
        profile: null,
        prompt: null,
        template: null
    };
    
    // 清空表單
    const workName = document.getElementById('workName');
    const workDescription = document.getElementById('workDescription');
    const workType = document.getElementById('workType');
    const generatedProfile = document.getElementById('generatedProfile');
    const generatedPrompt = document.getElementById('generatedPrompt');
    const templateFile = document.getElementById('templateFile');
    const profilePrompt = document.getElementById('profilePrompt');
    const promptTemplate = document.getElementById('promptTemplate');
    
    if (workName) workName.value = '';
    if (workDescription) workDescription.value = '';
    if (workType) workType.selectedIndex = 0;
    if (generatedProfile) generatedProfile.value = '';
    if (generatedPrompt) generatedPrompt.value = '';
    if (templateFile) templateFile.value = '';
    if (profilePrompt) profilePrompt.value = '';
    if (promptTemplate) promptTemplate.value = '';
    
    // 清空驗證結果
    const profileValidation = document.getElementById('profileValidation');
    const promptValidation = document.getElementById('promptValidation');
    const templatePreview = document.getElementById('templatePreview');
    
    if (profileValidation) profileValidation.innerHTML = '';
    if (promptValidation) promptValidation.innerHTML = '';
    if (templatePreview) templatePreview.innerHTML = '';
}

// 舊的AIGuidanceSystem類（已廢棄）
class AIGuidanceSystem {
    constructor() {
        this.currentStep = 1;
        this.currentWork = {
            name: '',
            description: '',
            type: '',
            profile: null,
            prompt: null,
            template: null
        };
    }
    
    // 步驟導航
    nextStep(step) {
        console.log(`nextStep called: currentStep=${this.currentStep}, targetStep=${step}`);
        
        if (this.validateCurrentStep()) {
            console.log('Validation passed, proceeding to next step');
            this.hideStep(this.currentStep);
            this.showStep(step);
            this.currentStep = step;
            this.updateStepIndicator();
        } else {
            console.log('Validation failed, staying on current step');
        }
    }
    
    prevStep(step) {
        this.hideStep(this.currentStep);
        this.showStep(step);
        this.currentStep = step;
        this.updateStepIndicator();
    }
    
    showStep(step) {
        const stepElement = document.getElementById(`step${step}`);
        if (stepElement) {
            stepElement.style.display = 'block';
            stepElement.classList.add('active');
            console.log(`Showing step ${step}`);
        } else {
            console.error(`Step element not found: step${step}`);
        }
    }
    
    hideStep(step) {
        const stepElement = document.getElementById(`step${step}`);
        if (stepElement) {
            stepElement.style.display = 'none';
            stepElement.classList.remove('active');
            console.log(`Hiding step ${step}`);
        } else {
            console.error(`Step element not found: step${step}`);
        }
    }
    
    // Profile生成
    generateProfilePrompt() {
        const description = document.getElementById('workDescription').value;
        const workType = document.getElementById('workType').value;
        
        const prompt = `
請根據以下需求生成一個文檔提取Profile（JSON格式）：

工作描述：${description}
文檔類型：${workType}

請生成包含以下結構的Profile：
{
    "name": "Profile名稱",
    "description": "Profile描述",
    "fields": [
        {
            "name": "欄位名稱",
            "type": "text|number|date|list",
            "description": "欄位描述",
            "extraction_rules": ["規則1", "規則2"],
            "required": true
        }
    ],
    "output_format": "json|xml|csv|docx",
    "special_instructions": "特殊處理說明"
}

請確保：
1. 欄位定義要完整且準確
2. 提取規則要具體可操作
3. 輸出格式要符合需求
4. JSON格式要正確
        `;
        
        const promptElement = document.getElementById('profilePrompt');
        const promptArea = document.getElementById('profilePromptArea');
        
        if (promptElement) {
            promptElement.value = prompt;
        }
        if (promptArea) {
            promptArea.style.display = 'block';
        }
    }
    
    // 提示詞生成
    generatePromptTemplate() {
        const profile = this.currentWork.profile;
        if (!profile) {
            this.showError('請先生成Profile');
            return;
        }
        
        const prompt = `
請根據以下Profile生成一個AI提取提示詞：

Profile配置：${JSON.stringify(profile, null, 2)}

請生成一個詳細的提示詞，包含：
1. 任務描述
2. 提取要求
3. 輸出格式
4. 注意事項

提示詞要求：
- 清晰明確
- 易於理解
- 包含具體示例
- 適合AI模型使用
        `;
        
        const promptElement = document.getElementById('promptTemplate');
        const promptArea = document.getElementById('promptTemplateArea');
        
        if (promptElement) {
            promptElement.value = prompt;
        }
        if (promptArea) {
            promptArea.style.display = 'block';
        }
    }
    
    // Profile驗證
    validateProfile() {
        const profileJson = document.getElementById('generatedProfile').value;
        const validationDiv = document.getElementById('profileValidation');
        
        try {
            const profile = JSON.parse(profileJson);
            
            // 基本驗證
            if (!profile.name || !profile.fields) {
                throw new Error('Profile缺少必要欄位');
            }
            
            // 欄位驗證
            for (const field of profile.fields) {
                if (!field.name || !field.type) {
                    throw new Error('欄位定義不完整');
                }
            }
            
            this.currentWork.profile = profile;
            this.showValidationResult(validationDiv, 'success', '✅ Profile驗證成功！');
            document.getElementById('step2Next').disabled = false;
            
        } catch (error) {
            this.showValidationResult(validationDiv, 'error', `❌ Profile格式錯誤：${error.message}`);
            document.getElementById('step2Next').disabled = true;
        }
    }
    
    // 提示詞驗證
    validatePrompt() {
        const prompt = document.getElementById('generatedPrompt').value;
        const validationDiv = document.getElementById('promptValidation');
        
        if (!prompt.trim()) {
            this.showValidationResult(validationDiv, 'error', '❌ 請輸入提示詞');
            document.getElementById('step3Next').disabled = true;
            return;
        }
        
        this.currentWork.prompt = prompt;
        
        // 根據安全檢查結果顯示不同的成功訊息
        if (this.currentWork.safetyCheckFailed) {
            this.showValidationResult(validationDiv, 'warning', '✅ 提示詞驗證成功，但安全檢查失敗！');
        } else {
            this.showValidationResult(validationDiv, 'success', '✅ 提示詞驗證成功！');
        }
        document.getElementById('step3Next').disabled = false;
    }
    
    // Template上傳處理
    handleTemplateUpload(event) {
        const file = event.target.files[0];
        const previewDiv = document.getElementById('templatePreview');
        
        if (!file) return;
        
        // 驗證檔案格式
        const allowedTypes = ['.docx', '.xlsx', '.pptx'];
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExt)) {
            this.showTemplatePreview(previewDiv, 'error', '❌ 不支援的檔案格式，請上傳 .docx, .xlsx, .pptx 檔案');
            document.getElementById('step4Next').disabled = true;
            return;
        }
        
        this.currentWork.template = file;
        this.showTemplatePreview(previewDiv, 'success', `✅ 模板上傳成功：${file.name}`);
        document.getElementById('step4Next').disabled = false;
    }
    
    // 工作創建
    async createWork() {
        if (!this.validateWorkData()) {
            return;
        }
        
        try {
            const formData = new FormData();
            formData.append('name', this.currentWork.name);
            formData.append('description', this.currentWork.description);
            formData.append('type', this.currentWork.type);
            formData.append('profile', JSON.stringify(this.currentWork.profile));
            formData.append('prompt', this.currentWork.prompt);
            if (this.currentWork.template) {
                formData.append('template', this.currentWork.template);
            }
            
            const response = await fetch('/api/works', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('工作創建成功！');
                this.closeCreateWorkModal();
                // 重新載入工作列表
                if (typeof prodocux !== 'undefined') {
                    prodocux.loadWorks();
                }
            } else {
                this.showError('工作創建失敗：' + result.error);
            }
            
        } catch (error) {
            this.showError('創建失敗：' + error.message);
        }
    }
    
    // 工具函數
    copyPrompt(elementId) {
        const textarea = document.getElementById(elementId);
        if (textarea) {
            textarea.select();
            document.execCommand('copy');
            this.showSuccess('提示詞已複製到剪貼板');
        }
    }
    
    openAITool(type) {
        const tools = {
            'profile': 'https://chat.openai.com',
            'prompt': 'https://chat.openai.com'
        };
        window.open(tools[type], '_blank');
    }
    
    validateCurrentStep() {
        switch (this.currentStep) {
            case 1:
                return this.validateStep1();
            case 2:
                return this.validateStep2();
            case 3:
                return this.validateStep3();
            case 4:
                return this.validateStep4();
            default:
                return true;
        }
    }
    
    validateStep1() {
        const name = document.getElementById('workName').value;
        const description = document.getElementById('workDescription').value;
        
        if (!name.trim() || !description.trim()) {
            this.showError('請填寫工作名稱和描述');
            return false;
        }
        
        this.currentWork.name = name;
        this.currentWork.description = description;
        this.currentWork.type = document.getElementById('workType').value;
        
        return true;
    }
    
    validateStep2() {
        return this.currentWork.profile !== null;
    }
    
    validateStep3() {
        return this.currentWork.prompt !== null;
    }
    
    validateStep4() {
        return this.currentWork.template !== null;
    }
    
    validateWorkData() {
        return this.currentWork.name && 
               this.currentWork.description && 
               this.currentWork.profile && 
               this.currentWork.prompt && 
               this.currentWork.template;
    }
    
    updateStepIndicator() {
        // 更新步驟指示器
        const indicators = document.querySelectorAll('.step-indicator');
        indicators.forEach((indicator, index) => {
            const stepNumber = index + 1;
            indicator.classList.remove('active', 'completed');
            
            if (stepNumber < this.currentStep) {
                indicator.classList.add('completed');
            } else if (stepNumber === this.currentStep) {
                indicator.classList.add('active');
            }
        });
    }
    
    updateSummary() {
        const summaryName = document.getElementById('summaryName');
        const summaryDescription = document.getElementById('summaryDescription');
        const summaryType = document.getElementById('summaryType');
        
        if (summaryName) summaryName.textContent = this.currentWork.name;
        if (summaryDescription) summaryDescription.textContent = this.currentWork.description;
        if (summaryType) summaryType.textContent = this.currentWork.type;
    }
    
    showValidationResult(element, type, message) {
        if (element) {
            element.innerHTML = `<div class="${type}">${message}</div>`;
        }
    }
    
    showTemplatePreview(element, type, message) {
        if (element) {
            element.innerHTML = `<div class="${type}">${message}</div>`;
        }
    }
    
    showSuccess(message) {
        // 顯示成功訊息
        console.log('Success:', message);
        // 使用瀏覽器原生alert顯示訊息
        alert('✅ ' + message);
    }
    
    showError(message) {
        // 顯示錯誤訊息
        console.error('Error:', message);
        // 使用瀏覽器原生alert顯示錯誤
        alert('❌ ' + message);
    }
    
    closeCreateWorkModal() {
        const modal = document.getElementById('createWorkModal');
        if (modal) {
            modal.style.display = 'none';
        }
        // 重置表單
        this.resetForm();
    }
    
    resetForm() {
        this.currentStep = 1;
        this.currentWork = {
            name: '',
            description: '',
            type: '',
            profile: null,
            prompt: null,
            template: null
        };
        
        // 重置所有步驟
        for (let i = 1; i <= 5; i++) {
            this.hideStep(i);
        }
        this.showStep(1);
        this.updateStepIndicator();
        
        // 清空表單
        const workName = document.getElementById('workName');
        const workDescription = document.getElementById('workDescription');
        const workType = document.getElementById('workType');
        
        if (workName) workName.value = '';
        if (workDescription) workDescription.value = '';
        if (workType) workType.selectedIndex = 0;
    }
}

// 全局函數
function closeAIToolsModal() {
    const modal = document.getElementById('aiToolsModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function updateWorkflowModelOptions() {
    if (prodocux) {
        prodocux.updateWorkflowModelOptions();
    }
}

// 創建全局實例
const aiGuidance = new AIGuidanceSystem();

// 創建ProDocuX實例並暴露到全局
let prodocux;
window.ProDocuX = ProDocuX;

// 等待DOM載入完成後初始化
document.addEventListener('DOMContentLoaded', async function() {
    prodocux = new ProDocuX();
    window.prodocux = prodocux;
    console.log('ProDocuX initialized with language:', prodocux.currentLanguage);
});

// 導航到settings頁面並保持語言設置
window.navigateToSettings = function(event) {
    event.preventDefault();
    const currentLang = (prodocux && prodocux.currentLanguage) || 'zh_TW';
    const settingsUrl = `/settings?lang=${currentLang}`;
    window.location.href = settingsUrl;
    return false;
};
