@echo off
title denizv1 Bot - KRİTİK MOD
cd /d "%~dp0"

echo.
echo ========================================
echo   denizv1 Bot - KRİTİK MOD v2.0
echo ========================================
echo.

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Sanal ortam aktif
) else (
    echo [HATA] Sanal ortam bulunamadi!
    echo Lutfen once Python paketlerini yukleyin.
    pause
    exit
)

echo.
echo Bot baslatiliyor...
echo.
python src\main.py

pause