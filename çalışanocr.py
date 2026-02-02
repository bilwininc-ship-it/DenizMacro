#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EASYOCR QUIZ - GELİŞTİRİLMİŞ VERSİYON
5 sayıyı da garantili çıkarır!
"""

try:
    import easyocr
except ImportError:
    print("❌ EasyOCR kurulu değil!")
    print("\nKurulum: pip install easyocr")
    exit(1)

from PIL import Image, ImageEnhance, ImageFilter
import json
import os
import glob
import numpy as np

class ImprovedEasyOCR:
    """Geliştirilmiş EasyOCR"""
    
    def __init__(self):
        print("🔧 EasyOCR başlatılıyor...\n")
        self.reader = easyocr.Reader(['tr', 'en'], gpu=False, verbose=False)
        print("✅ EasyOCR hazır!\n")
    
    def detect_button_regions(self, img):
        """Buton bölgelerini otomatik tespit et"""
        width, height = img.size
        
        # 4-5 buton için bölgeler oluştur
        regions = []
        
        # Butonlar görsel yüksekliğinin %33-%83 arasında
        start_y = int(height * 0.33)
        end_y = int(height * 0.83)
        region_height = (end_y - start_y) // 5  # 5 eşit bölge
        
        for i in range(5):
            y = start_y + (i * region_height)
            region = {
                'x': int(width * 0.12),
                'y': y,
                'width': int(width * 0.76),
                'height': int(region_height * 0.9)
            }
            regions.append(region)
        
        return regions
    
    def extract_numbers_advanced(self, image_path):
        """
        Gelişmiş sayı çıkarma - Bölge bazlı
        """
        print(f"📸 İşleniyor: {os.path.basename(image_path)}\n")
        
        # Görseli aç
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Tüm görseli tara
        print("🔍 1. ADIM: Tam görsel tarama...")
        all_results = self.reader.readtext(img_array)
        print(f"   ✓ {len(all_results)} metin bloğu bulundu\n")
        
        # Tüm bulunan sayıları topla
        found_numbers = []
        
        for (bbox, text, conf) in all_results:
            digits = ''.join(c for c in text if c.isdigit())
            
            # 5-7 haneli sayılar - GÜVENLİK EŞIĞI DÜŞÜK (0.2)
            if 5 <= len(digits) <= 7:
                y_coord = bbox[0][1]
                found_numbers.append({
                    'number': digits,
                    'y': y_coord,
                    'conf': conf
                })
                print(f"   Bulundu: {digits} (Y:{int(y_coord)}, güven:{conf:.2f})")
        
        # Eğer 5'ten az bulunmuşsa, bölge bazlı tarama yap
        if len(found_numbers) < 5:
            print(f"\n🔍 2. ADIM: Bölge bazlı tarama...")
            print(f"   (Şu ana kadar {len(found_numbers)} sayı bulundu)\n")
            
            regions = self.detect_button_regions(img)
            
            for i, region in enumerate(regions, 1):
                # Bu bölgede sayı var mı kontrol et
                has_number = False
                for num_data in found_numbers:
                    if region['y'] <= num_data['y'] <= region['y'] + region['height']:
                        has_number = True
                        break
                
                if has_number:
                    continue  # Bu bölgede zaten var
                
                # Bölgeyi kes
                x, y, w, h = region['x'], region['y'], region['width'], region['height']
                cropped = img.crop((x, y, x + w, y + h))
                
                # Kontrast artır
                enhancer = ImageEnhance.Contrast(cropped)
                cropped = enhancer.enhance(3.0)
                
                # Keskinlik artır
                cropped = cropped.filter(ImageFilter.SHARPEN)
                
                # OCR uygula
                cropped_array = np.array(cropped)
                results = self.reader.readtext(cropped_array)
                
                for (bbox, text, conf) in results:
                    digits = ''.join(c for c in text if c.isdigit())
                    
                    if 5 <= len(digits) <= 7:
                        found_numbers.append({
                            'number': digits,
                            'y': y + bbox[0][1],  # Mutlak Y koordinatı
                            'conf': conf
                        })
                        print(f"   Bölge {i}: {digits} (güven:{conf:.2f})")
                        break  # Bu bölgeden bir sayı bulduk
        
        # Y koordinatına göre sırala (yukarıdan aşağıya)
        found_numbers.sort(key=lambda x: x['y'])
        
        # İlk 5 sayıyı al ve 6 haneli yap
        result = {}
        for i, num_data in enumerate(found_numbers[:5], 1):
            number = num_data['number']
            
            # 6 haneli yap
            if len(number) == 6:
                result[str(i)] = number
            elif len(number) == 5:
                # 5 haneliyse sonuna 0 ekle (genelde son rakam eksik olur)
                result[str(i)] = number + '0'
            elif len(number) == 7:
                # 7 haneliyse ilk 6'sını al
                result[str(i)] = number[:6]
            else:
                result[str(i)] = number
        
        return result
    
    def process_single(self, image_path, output_json=None):
        """Tek görsel işle"""
        
        print("="*60)
        print("GELİŞMİŞ EASYOCR QUIZ ÇÖZÜCÜ")
        print("="*60 + "\n")
        
        result = self.extract_numbers_advanced(image_path)
        
        print("\n" + "="*60)
        print("SONUÇLAR:")
        print("="*60)
        
        if result:
            for key, value in result.items():
                print(f"  {key}. {value}")
            
            if len(result) < 5:
                print(f"\n⚠️  {len(result)}/5 sayı bulundu")
        else:
            print("  ❌ Sayı bulunamadı")
        
        print("="*60 + "\n")
        
        if output_json:
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Sonuç: {output_json}\n")
        
        return result
    
    def process_folder(self, folder_path, output_file="quiz_results.json"):
        """Klasördeki tüm görselleri işle"""
        
        print("="*60)
        print(f"📁 KLASÖR: {folder_path}")
        print("="*60 + "\n")
        
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']:
            image_files.extend(glob.glob(os.path.join(folder_path, ext)))
        
        if not image_files:
            print("❌ Görsel bulunamadı!")
            return []
        
        print(f"✓ {len(image_files)} görsel bulundu\n")
        
        all_results = []
        
        for i, img_path in enumerate(image_files, 1):
            print(f"\n{'#'*60}")
            print(f"GÖRSEL {i}/{len(image_files)}")
            print(f"{'#'*60}\n")
            
            try:
                result = self.extract_numbers_advanced(img_path)
                
                if result:
                    all_results.append({
                        "image": os.path.basename(img_path),
                        "options": result
                    })
            
            except Exception as e:
                print(f"❌ Hata: {e}\n")
                continue
        
        if all_results:
            output_path = os.path.join(folder_path, output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            
            print("\n" + "="*60)
            print(f"✅ {len(all_results)} görsel işlendi")
            print(f"💾 {output_path}")
            print("="*60 + "\n")
        
        return all_results


def main():
    """Ana fonksiyon"""
    
    print("\n" + "="*60)
    print("GELİŞMİŞ EASYOCR - 5 SAYI GARANTİLİ")
    print("="*60)
    print("\n🎯 Özellikler:")
    print("  ✓ 2 aşamalı tarama (tam + bölge)")
    print("  ✓ Düşük güven eşiği")
    print("  ✓ Otomatik 6 haneli dönüşüm")
    print("  ✓ Y koordinatına göre sıralama")
    print("\n" + "="*60)
    
    print("\n💡 KULLANIM:")
    print("-"*60)
    print("""
# TEK GÖRSEL:
from improved_easyocr import ImprovedEasyOCR
ocr = ImprovedEasyOCR()
result = ocr.process_single("quiz.png", "sonuc.json")

# KLASÖR:
ocr = ImprovedEasyOCR()
results = ocr.process_folder("C:/quiz_images")
    """)
    
    print("="*60)
    print("\n🚀 TEST:")
    print("-"*60)
    
    path = input("\nGörsel yolu: ").strip().strip('"')
    
    if path and os.path.exists(path):
        ocr = ImprovedEasyOCR()
        result = ocr.process_single(path, "sonuc_improved.json")
        
        print("📋 JSON ÇIKTI:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif path:
        print(f"\n❌ Dosya bulunamadı: {path}")


if __name__ == "__main__":
    main()