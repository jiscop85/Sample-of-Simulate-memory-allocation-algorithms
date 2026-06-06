@echo off
chcp 65001 >nul 2>&1
title نصب و اجرای برنامه
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    call "%~dp0setup.bat" --run
) else (
    call "%~dp0start.bat"
)
