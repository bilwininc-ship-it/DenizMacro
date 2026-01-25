@echo off
title denizv1 Bot - Portable Paket Olusturucu
cd /d "%~dp0"

echo ========================================
echo   PORTABLE PAKET OLUSTURULUYOR
echo ========================================
echo.

REM Paket klasoru olustur
set PACKAGE_DIR=denizv1_bot_portable
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"

echo [1/4] EXE kopyalaniyor...
if exist "dist\denizv1_bot.exe" (
    copy "dist\denizv1_bot.exe" "%PACKAGE_DIR%\"
    echo   OK denizv1_bot.exe
) else (
    echo   HATA! Once build_exe.bat calistirin
    pause
    exit
)

echo.
echo [2/4] Tesseract indiriliyor...
echo   (Bu birkaç dakika surebilir)
powershell -Command "& {Invoke-WebRequest -Uri 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe' -OutFile '%PACKAGE_DIR%\tesseract-installer.exe'}"
if exist "%PACKAGE_DIR%\tesseract-installer.exe" (
    echo   OK tesseract-installer.exe
) else (
    echo   UYARI: Tesseract indirilemedi
    echo   Manuel olarak ekleyin: https://github.com/UB-Mannheim/tesseract/wiki
)

echo.
echo [3/4] Kullanim kilavuzu olusturuluyor...
(
echo # denizv1 Bot - KURULUM
echo.
echo ## 1. Tesseract OCR Yukleyin
echo    - tesseract-installer.exe dosyasina cift tiklayin
echo    - Tum varsayilan ayarlari kabul edin
echo.
echo ## 2. denizv1_bot.exe Calistirin
echo    - denizv1_bot.exe dosyasina cift tiklayin
echo    - "Sistemi Baslat" butonuna tiklayin
echo.
echo ## NOTLAR:
echo    - Oyun pencere modunda olmali
echo    - Yesil kod ve butonlar gorunur olmali
echo    - Bot SADECE %%100 eslesme ile tiklar
echo.
echo Sorun yasarsaniz NASIL_KULLANILIR.txt dosyasini okuyun.
) > "%PACKAGE_DIR%\BASLANGIC_OKUYUN.txt"
echo   OK BASLANGIC_OKUYUN.txt

REM Detayli kilavuz kopyala
if exist "NASIL_KULLANILIR.txt" (
    copy "NASIL_KULLANILIR.txt" "%PACKAGE_DIR%\"
)

echo.
echo [4/4] ZIP arsivi olusturuluyor...
powershell -Command "& {Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath 'denizv1_bot_v2.0.zip' -Force}"
if exist "denizv1_bot_v2.0.zip" (
    echo   OK denizv1_bot_v2.0.zip
) else (
    echo   UYARI: ZIP olusturulamadi
)

echo.
echo ========================================
echo   PAKET HAZIR!
echo ========================================
echo.
echo Arkadaslariniza gonderin:
echo   1. denizv1_bot_v2.0.zip ^(hepsi bir arada^)
echo   VEYA
echo   2. %PACKAGE_DIR% klasorunu ^(acik halde^)
echo.
echo Icindekiler:
echo   - denizv1_bot.exe
echo   - tesseract-installer.exe
echo   - BASLANGIC_OKUYUN.txt
echo   - NASIL_KULLANILIR.txt
echo.
pause