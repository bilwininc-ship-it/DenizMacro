#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXE Oluşturma Scripti
"""

import os
import sys
import shutil
import subprocess

print("="*60)
print("🎮 OYUN BOTU - EXE OLUŞTURULUYOR")
print("="*60)
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
print("   (Bu işlem 1-2 dakika sürebilir)\n")

cmd = [
    'pyinstaller',
    '--onefile',                    # Tek dosya
    '--windowed',                   # Konsol penceresi açmasın
    '--name=OyunBotu',              # EXE adı
    '--icon=NONE',                  # İkon yok
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
    sys.exit(1)

# Sonuç
if os.path.exists('dist/OyunBotu.exe'):
    file_size = os.path.getsize('dist/OyunBotu.exe') / (1024*1024)
    print("="*60)
    print("🎉 BAŞARILI!")
    print("="*60)
    print(f"📦 Dosya: dist/OyunBotu.exe")
    print(f"📏 Boyut: {file_size:.1f} MB")
    print()
    print("📋 Kullanım:")
    print("   1. dist/OyunBotu.exe dosyasını masaüstüne kopyalayın")
    print("   2. Çift tıklayın ve kullanın!")
    print()
    print("⚠️  ÖNEMLİ: Tesseract OCR kurulu olmalı!")
    print("   İndirin: https://github.com/UB-Mannheim/tesseract/wiki")
    print("="*60)
else:
    print("❌ EXE dosyası oluşturulamadı!")
    sys.exit(1)
