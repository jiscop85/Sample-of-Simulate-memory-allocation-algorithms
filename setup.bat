@echo off
chcp 65001 >nul 2>&1
title نصب پروژه - Memory Allocation Simulator
cd /d "%~dp0"

echo.
echo  ============================================================
echo    نصب خودکار - شبیه‌سازی تخصیص حافظه
echo  ============================================================
echo.

REM --- Find Python ---
set "PY_CMD="
where python >nul 2>&1 && set "PY_CMD=python"
if not defined PY_CMD (
    where py >nul 2>&1 && set "PY_CMD=py -3"
)
if not defined PY_CMD (
    echo  [خطا] Python روی سیستم نصب نیست!
    echo.
    echo  1. از سایت python.org نسخه 3.8 یا بالاتر را نصب کنید
    echo  2. هنگام نصب گزینه "Add Python to PATH" را فعال کنید
    echo  3. دوباره این فایل را اجرا کنید
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

echo  [1/4] Python پیدا شد: %PY_CMD%
%PY_CMD% --version

REM --- Virtual environment ---
if not exist ".venv\Scripts\python.exe" (
    echo  [2/4] ساخت محیط مجازی (.venv)...
    %PY_CMD% -m venv .venv
    if errorlevel 1 (
        echo  [خطا] ساخت venv ناموفق بود.
        pause
        exit /b 1
    )
) else (
    echo  [2/4] محیط مجازی از قبل وجود دارد.
)

echo  [3/4] نصب کتابخانه‌ها...
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip -q
pip install -r requirements.txt
if errorlevel 1 (
    echo  [خطا] نصب وابستگی‌ها ناموفق بود.
    pause
    exit /b 1
)

echo  [4/4] اجرای تست‌ها...
python -m unittest tests.test_simulator -q
if errorlevel 1 (
    echo  [هشدار] برخی تست‌ها ناموفق بودند، ولی نصب ادامه می‌یابد.
) else (
    echo  همه تست‌ها OK
)

echo.
echo  ============================================================
echo    نصب با موفقیت انجام شد!
echo  ============================================================
echo.
echo  برای اجرا: دوبار کلیک روی  start.bat
echo.
if /I "%~1"=="--run" (
    python main.py --gui
) else (
    echo  Enter برای باز کردن GUI یا پنجره را ببندید...
    pause
    python main.py --gui
)
