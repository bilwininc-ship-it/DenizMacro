@echo off
chcp 65001 >nul
color 0A
title 📦 Paket Hazırlama Sistemi

echo.
echo ═══════════════════════════════════════════════════════════
echo                   📦 PAKET HAZIRLAMA SİSTEMİ
echo ═══════════════════════════════════════════════════════════
echo.
echo Bu script arkadaşlarınız için dağıtılabilir ZIP paketi oluşturur.
echo.
echo ═══════════════════════════════════════════════════════════
pause

echo.
echo [1/4] 🔨 EXE dosyası oluşturuluyor...
echo.
python build_exe_gelismis.py

if not exist "dist\OyunBotu.exe" (
    echo.
    echo ❌ HATA: EXE dosyası oluşturulamadı!
    echo Lütfen hataları kontrol edin.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════
echo [2/4] 📁 Paket klasörü hazırlanıyor...
echo ═══════════════════════════════════════════════════════════
echo.

if exist "OyunBotu_Paket" (
    echo Eski paket klasörü siliniyor...
    rmdir /s /q "OyunBotu_Paket"
)

mkdir "OyunBotu_Paket"

echo ✅ Paket klasörü oluşturuldu
echo.

echo ═══════════════════════════════════════════════════════════
echo [3/4] 📋 Dosyalar kopyalanıyor...
echo ═══════════════════════════════════════════════════════════
echo.

echo Kopyalanıyor: OyunBotu.exe
copy "dist\OyunBotu.exe" "OyunBotu_Paket\" >nul

if exist "TESSERACT_KUR.bat" (
    echo Kopyalanıyor: TESSERACT_KUR.bat
    copy "TESSERACT_KUR.bat" "OyunBotu_Paket\" >nul
)

if exist "KULLANICI_KILAVUZU.txt" (
    echo Kopyalanıyor: KULLANICI_KILAVUZU.txt
    copy "KULLANICI_KILAVUZU.txt" "OyunBotu_Paket\" >nul
)

if exist "icon.ico" (
    echo Kopyalanıyor: icon.ico
    copy "icon.ico" "OyunBotu_Paket\" >nul
)

echo Oluşturuluyor: BENIOKU.txt
echo ═══════════════════════════════════════════════════════════ > "OyunBotu_Paket\BENIOKU.txt"
echo            🎮 OYUN BOTU - KURULUM REHBERİ >> "OyunBotu_Paket\BENIOKU.txt"
echo ═══════════════════════════════════════════════════════════ >> "OyunBotu_Paket\BENIOKU.txt"
echo. >> "OyunBotu_Paket\BENIOKU.txt"
echo 🚀 KURULUM (İLK KULLANIM): >> "OyunBotu_Paket\BENIOKU.txt"
echo ────────────────────────────────────────────────────────── >> "OyunBotu_Paket\BENIOKU.txt"
echo 1. TESSERACT_KUR.bat dosyasına çift tıklayın >> "OyunBotu_Paket\BENIOKU.txt"
echo 2. Kurulum tamamlanana kadar bekleyin >> "OyunBotu_Paket\BENIOKU.txt"
echo 3. Kurulum bitince OyunBotu.exe'yi çalıştırın >> "OyunBotu_Paket\BENIOKU.txt"
echo. >> "OyunBotu_Paket\BENIOKU.txt"
echo ✅ KULLANIM: >> "OyunBotu_Paket\BENIOKU.txt"
echo ────────────────────────────────────────────────────────── >> "OyunBotu_Paket\BENIOKU.txt"
echo 1. OyunBotu.exe'yi çift tıklayın >> "OyunBotu_Paket\BENIOKU.txt"
echo 2. Başlat butonuna basın >> "OyunBotu_Paket\BENIOKU.txt"
echo 3. Bot otomatik çalışmaya başlayacak >> "OyunBotu_Paket\BENIOKU.txt"
echo. >> "OyunBotu_Paket\BENIOKU.txt"
echo ⚠️  ÖNEMLİ NOTLAR: >> "OyunBotu_Paket\BENIOKU.txt"
echo ────────────────────────────────────────────────────────── >> "OyunBotu_Paket\BENIOKU.txt"
echo • Tesseract OCR kurulumu sadece ilk kulanımda gereklidir >> "OyunBotu_Paket\BENIOKU.txt"
echo • Windows 10/11 gereklidir >> "OyunBotu_Paket\BENIOKU.txt"
echo • İnternet bağlantısı (ilk kurulum için) >> "OyunBotu_Paket\BENIOKU.txt"
echo. >> "OyunBotu_Paket\BENIOKU.txt"
echo 📧 SORUN OLURSA: >> "OyunBotu_Paket\BENIOKU.txt"
echo ────────────────────────────────────────────────────────── >> "OyunBotu_Paket\BENIOKU.txt"
echo KULLANICI_KILAVUZU.txt dosyasını okuyun >> "OyunBotu_Paket\BENIOKU.txt"
echo. >> "OyunBotu_Paket\BENIOKU.txt"
echo ═══════════════════════════════════════════════════════════ >> "OyunBotu_Paket\BENIOKU.txt"
echo           İYİ KULANIMLAR! 🎮 >> "OyunBotu_Paket\BENIOKU.txt"
echo ═══════════════════════════════════════════════════════════ >> "OyunBotu_Paket\BENIOKU.txt"

echo ✅ Tüm dosyalar kopyalandı
echo.

echo ═══════════════════════════════════════════════════════════
echo [4/4] 📦 ZIP dosyası oluşturuluyor...
echo ═══════════════════════════════════════════════════════════
echo.

if exist "OyunBotu_Paket.zip" (
    echo Eski ZIP siliniyor...
    del "OyunBotu_Paket.zip"
)

echo ZIP oluşturuluyor (PowerShell kullanılıyor)...
powershell -command "Compress-Archive -Path 'OyunBotu_Paket\*' -DestinationPath 'OyunBotu_Paket.zip' -Force"

if exist "OyunBotu_Paket.zip" (
    echo ✅ ZIP dosyası oluşturuldu!
) else (
    echo ⚠️  ZIP oluşturulamadı, manuel olarak sıkıştırın.
)

echo.
echo ═══════════════════════════════════════════════════════════
echo                   ✅ PAKET HAZIR!
echo ═══════════════════════════════════════════════════════════
echo.
echo 📦 Paket konumu: OyunBotu_Paket.zip
echo 📁 Klasör konumu: OyunBotu_Paket\
echo.
echo 🌐 Şimdi yapabilecekleriniz:
echo    • ZIP dosyasını arkadaşlarınıza gönderin
echo    • Google Drive, Discord, WhatsApp vb. kullanabilirsiniz
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
