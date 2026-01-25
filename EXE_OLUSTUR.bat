@echo off
chcp 65001 >nul
echo ========================================
echo    🔨 EXE DOSYASI OLUŞTURULUYOR
echo ========================================
echo.
echo Lütfen bekleyin, bu işlem 1-2 dakika sürebilir...
echo.

python build_exe.py

echo.
echo ========================================
echo Tamamlandı! dist klasörüne bakın.
echo ========================================
pause
