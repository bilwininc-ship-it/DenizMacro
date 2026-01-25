@echo off
chcp 65001 >nul
color 0B
title 🔨 EXE Oluştur ve Masaüstüne Kopyala

echo.
echo ═══════════════════════════════════════════════════════════
echo          🔨 EXE OLUŞTURMA VE MASAÜSTÜNE KOPYALAMA
echo ═══════════════════════════════════════════════════════════
echo.
echo Bu script:
echo   1. OyunBotu.exe dosyasını oluşturur
echo   2. Otomatik olarak masaüstünüze kopyalar
echo   3. Kullanıma hazır hale getirir
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause

echo.
echo 🔨 EXE oluşturuluyor...
echo Lütfen bekleyin, bu işlem 1-3 dakika sürebilir...
echo.

python build_exe_gelismis.py

echo.
echo ═══════════════════════════════════════════════════════════
echo                    ✅ İŞLEM TAMAMLANDI!
echo ═══════════════════════════════════════════════════════════
echo.
echo Masaüstünüzdeki OyunBotu.exe'yi çalıştırabilirsiniz!
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
