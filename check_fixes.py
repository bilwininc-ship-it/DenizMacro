"""
DÜZELTMELERİ KONTROL ET
Bu script düzeltmelerin başarıyla uygulandığını kontrol eder
"""

import os

print("=" * 70)
print("🔍 CAPTCHA DETECTOR DÜZELTME KONTROLÜ")
print("=" * 70)

# 1. Dosya varlığı kontrolü
print("\n📁 Dosya Kontrolü:")
files_to_check = [
    ("captcha_detector.py", "Ana program (düzeltilmiş)"),
    ("captcha_detector_backup.py", "Yedek dosya"),
    ("ocr.py", "OCR modülü"),
    ("DUZELTMELER_README.md", "Düzeltmeler dokümantasyonu")
]

all_files_exist = True
for filename, description in files_to_check:
    if os.path.exists(filename):
        print(f"  ✅ {filename} - {description}")
    else:
        print(f"  ❌ {filename} - BULUNAMADI!")
        all_files_exist = False

# 2. Kod kontrolü
print("\n🔍 Kod Değişiklik Kontrolü:")

with open('captcha_detector.py', 'r', encoding='utf-8') as f:
    content = f.read()

checks = [
    ("captcha_region offset", "captcha_x1, captcha_y1, _, _ = self.captcha_region" in content),
    ("client_x hesaplama", "client_x = captcha_x1 + center_x" in content),
    ("BringWindowToTop eklendi", "win32gui.BringWindowToTop" in content),
    ("Doğru sayı yoksa log", "OCR ile eşleşme bulunamadı - TIKLAMA YAPILMAYACAK" in content),
    ("Beklemeye devam log", "Doğru sayı ekranda yok, beklemeye devam ediliyor" in content),
]

all_checks_passed = True
for check_name, check_result in checks:
    if check_result:
        print(f"  ✅ {check_name}")
    else:
        print(f"  ❌ {check_name} - BULUNAMADI!")
        all_checks_passed = False

# 3. Sonuç
print("\n" + "=" * 70)
if all_files_exist and all_checks_passed:
    print("✅ TÜM DÜZELTMELER BAŞARIYLA UYGULANMIŞ!")
    print("\n📋 Sonraki Adımlar:")
    print("  1. python captcha_detector.py → Programı başlat")
    print("  2. Oyun penceresini seç")
    print("  3. CAPTCHA bölgesini seç (eğer yoksa)")
    print("  4. 4 Buton bölgesini seç (eğer yoksa)")
    print("  5. BAŞLAT butonuna tıkla")
    print("\n📄 Detaylı bilgi için: DUZELTMELER_README.md")
else:
    print("⚠️ BAZI SORUNLAR VAR!")
    print("\n💡 Çözüm:")
    print("  1. python apply_fixes.py → Düzeltmeleri tekrar uygula")
    print("  2. Bu scripti tekrar çalıştır")

print("=" * 70)

# 4. Backup karşılaştırma
print("\n📊 Değişiklik İstatistikleri:")
try:
    with open('captcha_detector_backup.py', 'r', encoding='utf-8') as f:
        backup_content = f.read()
    
    with open('captcha_detector.py', 'r', encoding='utf-8') as f:
        new_content = f.read()
    
    backup_lines = backup_content.count('\n')
    new_lines = new_content.count('\n')
    line_diff = new_lines - backup_lines
    
    print(f"  📄 Eski dosya: {backup_lines} satır")
    print(f"  📄 Yeni dosya: {new_lines} satır")
    print(f"  {'➕' if line_diff > 0 else '➖'} Fark: {abs(line_diff)} satır")
    
except Exception as e:
    print(f"  ⚠️ Karşılaştırma yapılamadı: {e}")

print("\n✅ Kontrol tamamlandı!")
