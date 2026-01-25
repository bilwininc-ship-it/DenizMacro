@echo off
title denizv1 Bot - EXE Olusturucu
cd /d "%~dp0"

echo ========================================
echo   denizv1 Bot - EXE Olusturuluyor
echo ========================================
echo.

REM Sanal ortami aktif et
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Sanal ortam aktif
) else (
    echo [HATA] Sanal ortam bulunamadi!
    pause
    exit
)

echo.
echo PyInstaller kontrol ediliyor...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller bulunamadi, yukleniyor...
    pip install pyinstaller
)

echo.
echo ========================================
echo   EXE Derleniyor... (2-3 dakika)
echo ========================================
echo.

REM Eski build klasorunu temizle
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "denizv1_bot.spec" del "denizv1_bot.spec"

REM PyInstaller ile EXE olustur
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "denizv1_bot" ^
    --add-data "src;src" ^
    --hidden-import "customtkinter" ^
    --hidden-import "PIL._tkinter_finder" ^
    --collect-all "customtkinter" ^
    --icon "icon.ico" ^
    src/main.py

echo.
echo ========================================
if exist "dist\denizv1_bot.exe" (
    echo   BASARILI! EXE olusturuldu
    echo ========================================
    echo.
    echo Dosya konumu: dist\denizv1_bot.exe
    echo.
    echo ONEMLI NOTLAR:
    echo 1. Tesseract OCR yuklu olmali
    echo    Indirin: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo 2. EXE + Tesseract ile calisir
    echo.
    echo 3. Arkadaslariniza gonderin:
    echo    - dist\denizv1_bot.exe
    echo    - Tesseract kurulum linki
    echo.
) else (
    echo   HATA! EXE olusturulamadi
    echo ========================================
    echo.
)

pause