@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title بسته‌بندی پروژه برای انتقال

set "OUT=MemoryAllocatorSim_Portable"
set "ZIP=MemoryAllocatorSim_Portable.zip"

echo.
echo  در حال ساخت بسته قابل انتقال...
echo.

if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%OUT%"

xcopy /E /I /Y "memory_allocator" "%OUT%\memory_allocator\" >nul
xcopy /E /I /Y "samples" "%OUT%\samples\" >nul
xcopy /E /I /Y "tests" "%OUT%\tests\" >nul
mkdir "%OUT%\output" 2>nul

for %%F in (
    main.py
    requirements.txt
    README.md
    راهنمای_سریع.txt
    setup.bat
    start.bat
    start_cli.bat
    INSTALL_AND_RUN.bat
    run_gui.bat
    setup.sh
    start.sh
    setup_project.py
    pyproject.toml
    .gitignore
) do if exist "%%F" copy /Y "%%F" "%OUT%\" >nul

if exist "%ZIP%" del /f /q "%ZIP%"
powershell -NoProfile -Command "Compress-Archive -LiteralPath '%CD%\%OUT%' -DestinationPath '%CD%\%ZIP%' -Force"

echo.
echo  ============================================================
echo    بسته آماده شد!
echo  ============================================================
echo.
echo  پوشه: %CD%\%OUT%
echo  فایل ZIP: %CD%\%ZIP%
echo.
echo  این ZIP را به سیستم دیگر منتقل کنید و INSTALL_AND_RUN.bat را اجرا کنید.
echo.
