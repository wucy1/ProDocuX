@echo off
echo ========================================
echo ProDocuX 安裝程式
echo ========================================
echo.

echo 正在檢查Python環境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 未找到Python環境
    echo 請先安裝Python 3.8或更高版本
    pause
    exit /b 1
)

echo 正在安裝依賴套件...
pip install -r requirements.txt

echo 正在創建必要目錄...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "cache" mkdir cache
if not exist "logs" mkdir logs

echo 正在創建環境變數檔案...
if not exist ".env" (
    echo # ProDocuX 環境變數設定 > .env
    echo OPENAI_API_KEY=your_openai_api_key_here >> .env
    echo IOPENAI_API_KEY=your_iopenai_api_key_here >> .env
)

echo.
echo ========================================
echo 安裝完成！
echo ========================================
echo.
echo 請編輯 .env 檔案，填入您的OpenAI API金鑰
echo 然後執行 run.py 啟動ProDocuX
echo.
pause
