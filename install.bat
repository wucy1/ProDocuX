@echo off
echo ========================================
echo ProDocuX 從原始碼安裝程式
echo ========================================
echo.

echo 正在檢查Python環境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 未找到Python環境
    echo 請先安裝Python 3.8或更高版本
    echo.
    echo 建議: 使用可執行檔版本 ProDocuX.exe
    echo 下載地址: https://github.com/wucy1/ProDocuX/releases
    pause
    exit /b 1
)

echo 正在安裝依賴套件...
pip install -r requirements.txt
if errorlevel 1 (
    echo 錯誤: 依賴套件安裝失敗
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安裝完成！
echo ========================================
echo.
echo 使用說明:
echo 1. 執行 run.py 啟動ProDocuX
echo 2. 在瀏覽器中完成初始設置
echo 3. 創建工作流程後開始處理文檔
echo.
echo 注意: 建議使用可執行檔版本 ProDocuX.exe
echo 下載地址: https://github.com/wucy1/ProDocuX/releases
echo.
pause
