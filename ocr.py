"""
CAPTCHA Sayı Okuyucu ve Kayıt Sistemi
Ana sayı ve buton sayılarını OCR ile okur, JSON'a kaydeder
"""

import cv2
import numpy as np
import pytesseract
import json
import os
from datetime import datetime
from pathlib import Path

# Tesseract yolu
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class CaptchaNumberReader:
    def __init__(self):
        self.results = []
        self.output_folder = "captcha_results"
        
        # Çıktı klasörünü oluştur
        Path(self.output_folder).mkdir(exist_ok=True)
        
        print("=" * 60)
        print("CAPTCHA SAYI OKUYUCU v1.0")
        print("=" * 60)
    
    
    def preprocess_image(self, img):
        """Görüntüyü OCR için hazırla"""
        # Gri tonlama
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Kontrast artırma
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Gürültü azaltma
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        # Binary threshold
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    
    def extract_numbers_from_roi(self, img, roi, label=""):
        """Belirli bir bölgeden sayıları çıkar"""
        x, y, w, h = roi
        
        # ROI'yi çıkar
        roi_img = img[y:y+h, x:x+w]
        
        # Ön işleme
        processed = self.preprocess_image(roi_img)
        
        # OCR - sadece rakamlar
        custom_config = '--psm 7 -c tessedit_char_whitelist=0123456789'
        text = pytesseract.image_to_string(processed, config=custom_config).strip()
        
        # Boşlukları temizle
        text = text.replace(' ', '').replace('\n', '')
        
        print(f"  {label}: {text}")
        
        return text, processed
    
    
    def detect_button_regions_auto(self, img):
        """Butonları otomatik olarak tespit et - Gelişmiş"""
        height, width = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Kenarları bul
        edges = cv2.Canny(gray, 50, 150)
        
        # Contour bul
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Dikdörtgen bölgeleri bul
        rectangles = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Buton boyutlarına uygun mu?
            if (50 < w < width * 0.8 and 20 < h < height * 0.15):
                rectangles.append((x, y, w, h))
        
        # Y koordinatına göre sırala (yukarıdan aşağıya)
        rectangles.sort(key=lambda r: r[1])
        
        if len(rectangles) >= 5:
            # İlk biri ana sayı, sonraki 4'ü butonlar
            main_roi = rectangles[0]
            button_rois = rectangles[1:5]
            print(f"✓ Otomatik tespit: {len(button_rois)} buton bulundu")
            return main_roi, button_rois
        
        # Otomatik tespit başarısız, manuel bölgelere dön
        print("⚠️  Otomatik tespit başarısız, manuel bölgeler kullanılıyor")
        return self.detect_button_regions_manual(img)
    
    
    def detect_button_regions_manual(self, img):
        """Manuel bölge koordinatları"""
        height, width = img.shape[:2]
        
        # Ana sayı bölgesi - görsel üstte ortada
        main_number_roi = (int(width * 0.2), int(height * 0.12), 
                          int(width * 0.6), int(height * 0.10))
        
        # 4 buton bölgesi (alt alta, ortada)
        button_height = int(height * 0.08)
        button_width = int(width * 0.6)
        button_x = int(width * 0.2)
        button_start_y = int(height * 0.30)
        button_spacing = int(height * 0.11)
        
        button_rois = []
        for i in range(4):
            y = button_start_y + (i * button_spacing)
            button_rois.append((button_x, y, button_width, button_height))
        
        return main_number_roi, button_rois
    
    
    def process_captcha_image(self, image_path):
        """CAPTCHA görselini işle"""
        print(f"\n📷 İşleniyor: {os.path.basename(image_path)}")
        print("-" * 60)
        
        # Görseli yükle
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ Görsel yüklenemedi: {image_path}")
            return None
        
        print(f"✓ Görsel boyutu: {img.shape[1]}x{img.shape[0]}")
        
        # Bölgeleri tespit et (önce otomatik dene)
        main_roi, button_rois = self.detect_button_regions_auto(img)
        
        # Ana sayıyı oku
        print("\n🔍 Sayılar okunuyor...")
        main_number, main_processed = self.extract_numbers_from_roi(
            img, main_roi, "ANA SAYI"
        )
        
        # Buton sayılarını oku
        button_numbers = []
        for i, roi in enumerate(button_rois, 1):
            number, _ = self.extract_numbers_from_roi(
                img, roi, f"BUTON {i}"
            )
            button_numbers.append(number)
        
        # Sonuç objesi oluştur
        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "image_file": os.path.basename(image_path),
            "main_number": main_number,
            "buttons": button_numbers,
            "correct_button": None  # Hangi buton doğru - kullanıcı belirtebilir
        }
        
        # Doğru butonu bul (ana sayı ile eşleşen)
        for i, btn_num in enumerate(button_numbers, 1):
            if btn_num == main_number:
                result["correct_button"] = i
                print(f"\n✅ EŞLEŞME BULUNDU! Buton {i}: {btn_num}")
                break
        
        if result["correct_button"] is None:
            print(f"\n⚠️  Eşleşme bulunamadı!")
        
        self.results.append(result)
        return result
    
    
    def save_results_to_json(self, filename="captcha_results.json"):
        """Sonuçları JSON'a kaydet"""
        output_path = os.path.join(self.output_folder, filename)
        
        # Mevcut dosya varsa yükle
        existing_data = []
        if os.path.exists(output_path):
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                existing_data = []
        
        # Yeni sonuçları ekle
        all_data = existing_data + self.results
        
        # Kaydet
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Sonuçlar kaydedildi: {output_path}")
        print(f"   Toplam kayıt: {len(all_data)}")
        
        return output_path
    
    
    def process_folder(self, folder_path):
        """Klasördeki tüm görselleri işle"""
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
        image_files = []
        
        # Görselleri bul
        for ext in image_extensions:
            image_files.extend(Path(folder_path).glob(f'*{ext}'))
        
        if not image_files:
            print(f"❌ '{folder_path}' klasöründe görsel bulunamadı!")
            return
        
        print(f"\n📁 {len(image_files)} görsel bulundu\n")
        
        # Her görseli işle
        for img_file in image_files:
            self.process_captcha_image(str(img_file))
        
        # Sonuçları kaydet
        if self.results:
            self.save_results_to_json()
            self.print_summary()
    
    
    def print_summary(self):
        """Özet rapor yazdır"""
        print("\n" + "=" * 60)
        print("📊 ÖZET RAPOR")
        print("=" * 60)
        
        total = len(self.results)
        matched = sum(1 for r in self.results if r['correct_button'] is not None)
        
        print(f"Toplam İşlenen: {total}")
        print(f"Eşleşme Bulunan: {matched}")
        print(f"Başarı Oranı: {(matched/total*100):.1f}%")
        
        print("\n🔢 Bulunan Sayılar:")
        for i, result in enumerate(self.results, 1):
            status = "✅" if result['correct_button'] else "❌"
            print(f"  {status} {result['main_number']} → Butonlar: {', '.join(result['buttons'])}")


def main():
    """Ana program"""
    reader = CaptchaNumberReader()
    
    # Seçenekler
    print("\n📋 Seçenekler:")
    print("1. Tek görsel işle")
    print("2. Klasör içindeki tüm görselleri işle")
    print("3. Çıkış")
    
    choice = input("\nSeçiminiz (1-3): ").strip()
    
    if choice == "1":
        # Tek görsel
        image_path = input("\nGörsel yolu: ").strip().strip('"')
        if os.path.exists(image_path):
            reader.process_captcha_image(image_path)
            reader.save_results_to_json()
            reader.print_summary()
        else:
            print(f"❌ Dosya bulunamadı: {image_path}")
    
    elif choice == "2":
        # Klasör
        folder_path = input("\nKlasör yolu: ").strip().strip('"')
        if os.path.exists(folder_path):
            reader.process_folder(folder_path)
        else:
            print(f"❌ Klasör bulunamadı: {folder_path}")
    
    elif choice == "3":
        print("\n👋 Görüşürüz!")
        return
    
    else:
        print("❌ Geçersiz seçim!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program kullanıcı tarafından durduruldu!")
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()