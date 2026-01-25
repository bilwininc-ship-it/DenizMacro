#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş EXE Oluşturma ve Masaüstüne Kopyalama
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

print("="*70)
print("🎮 OYUN BOTU - GELİŞMİŞ EXE OLUŞTURMA SİSTEMİ")
print("="*70)
print()

# Icon kontrolü
icon_path = "icon.ico"
if os.path.exists(icon_path):
    print("✅ Icon dosyası bulundu: icon.ico")
    icon_param = f'--icon={icon_path}'
else:
    print("⚠️  Icon dosyası bulunamadı! (icon.ico)")
    print("   Varsayılan icon kullanılacak.")
    icon_param = '--icon=NONE'

print()

# Eski dosyaları temizle
if os.path.exists('dist'):
    print("📁 Eski dist klasörü temizleniyor...")
    shutil.rmtree('dist')

if os.path.exists('build'):
    print("📁 Eski build klasörü temizleniyor...")
    shutil.rmtree('build')

print("✅ Temizlik tamamlandı\n")

# PyInstaller komutu
print("🔨 EXE dosyası oluşturuluyor...")
print("   (Bu işlem 1-3 dakika sürebilir)\n")

cmd = [
    'pyinstaller',
    '--onefile',                    # Tek dosya
    '--windowed',                   # Konsol penceresi açmasın
    '--name=OyunBotu',              # EXE adı
    icon_param,                     # Icon
    '--clean',                      # Önce temizle
    '--noconfirm',                  # Onay isteme
    'game_bot.py'
]

try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("✅ EXE dosyası başarıyla oluşturuldu!\n")
except subprocess.CalledProcessError as e:
    print("❌ Hata oluştu:")
    print(e.stderr)
    input("\nDevam etmek için ENTER'a basın...")
    sys.exit(1)

# EXE kontrolü
exe_path = 'dist/OyunBotu.exe'
if not os.path.exists(exe_path):
    print("❌ EXE dosyası oluşturulamadı!")
    input("\nDevam etmek için ENTER'a basın...")
    sys.exit(1)

file_size = os.path.getsize(exe_path) / (1024*1024)

print("="*70)
print("🎉 EXE OLUŞTURMA BAŞARILI!")
print("="*70)
print(f"📦 Dosya: {exe_path}")
print(f"📏 Boyut: {file_size:.1f} MB\n")

# Masaüstü yolu bul
try:
    if os.name == 'nt':  # Windows
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        desktop = winreg.QueryValueEx(key, 'Desktop')[0]
        winreg.CloseKey(key)
    else:
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    
    if os.path.exists(desktop):
        print("="*70)
        print("📋 MASAÜSTÜNE KOPYALANIYOR...")
        print("="*70)
        
        desktop_exe = os.path.join(desktop, 'OyunBotu.exe')
        shutil.copy2(exe_path, desktop_exe)
        
        print(f"✅ Başarıyla kopyalandı: {desktop_exe}\n")
    else:
        print("⚠️  Masaüstü bulunamadı, manuel kopyalama gerekli.\n")
except Exception as e:
    print(f"⚠️  Masaüstüne kopyalanamadı: {e}")
    print(f"   Manuel olarak kopyalayın: {exe_path} -> Masaüstü\n")

print("="*70)
print("✅ İŞLEM TAMAMLANDI!")
print("="*70)
print("\n📝 Kullanım:")
print("   1. Masaüstündeki OyunBotu.exe'yi çalıştırın")
print("   2. Veya dist/OyunBotu.exe'yi kullanın\n")

print("⚠️  ÖNEMLİ: Tesseract OCR kurulu olmalı!")
print("   İndirin: https://github.com/UB-Mannheim/tesseract/wiki\n")

print("="*70)
print("\n✅ Her şey hazır! İyi kullanımlar! 🎮\n")
print("="*70)

input("\nÇıkmak için ENTER'a basın...")
