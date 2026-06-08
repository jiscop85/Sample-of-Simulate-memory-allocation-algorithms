@echo off
chcp 65001 >nul 2>&1
title Memory Allocation Simulator - CLI
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo  محیط مجازی یافت نشد. در حال نصب...
    call "%~dp0setup.bat"
    exit /b %ERRORLEVEL%
)

call ".venv\Scripts\activate.bat"
python main.py
