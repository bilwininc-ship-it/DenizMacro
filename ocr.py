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
    
    
    def extract_green_number(self, img):
        """YEŞİL renkteki ana sayıyı bul (üstte) - İYİLEŞTİRİLMİŞ"""
        try:
            # HSV'ye çevir
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Yeşil renk maskesi (çok geniş aralık - farklı yeşil tonları için)
            lower_green1 = np.array([35, 50, 50])
            upper_green1 = np.array([85, 255, 255])
            mask1 = cv2.inRange(hsv, lower_green1, upper_green1)
            
            # Daha açık yeşiller için ikinci maske
            lower_green2 = np.array([40, 40, 100])
            upper_green2 = np.array([80, 255, 255])
            mask2 = cv2.inRange(hsv, lower_green2, upper_green2)
            
            # İki maskeyi birleştir
            mask = cv2.bitwise_or(mask1, mask2)
            
            # Morfolojik işlemler - gürültüyü azalt
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Yeşil bölgeleri bul
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                print("⚠️ Yeşil bölge bulunamadı, genel tarama yapılıyor...")
                return None
            
            # Sayı gibi görünen bölgeleri filtrele (en az 50x20 boyut)
            valid_contours = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w > 50 and h > 15:  # Sayı boyutu kontrolü
                    valid_contours.append(cnt)
            
            if not valid_contours:
                print("⚠️ Uygun boyutta yeşil bölge bulunamadı")
                return None
            
            # En büyük geçerli bölgeyi al
            largest_contour = max(valid_contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Bölgeyi genişlet (sayının tamamını almak için)
            margin = 15
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(img.shape[1] - x, w + 2*margin)
            h = min(img.shape[0] - y, h + 2*margin)
            
            # Yeşil sayı bölgesini çıkar
            green_roi = img[y:y+h, x:x+w]
            
            # GELİŞMİŞ ÖN İŞLEME
            gray = cv2.cvtColor(green_roi, cv2.COLOR_BGR2GRAY)
            
            # Kontrast artır
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            
            # Gürültü azalt
            gray = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
            
            # Resize (büyüt) - OCR için daha iyi
            scale = 3
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            
            # Binary threshold (birden fazla yöntem dene)
            methods = []
            
            # Yöntem 1: OTSU
            _, binary1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            methods.append(binary1)
            
            # Yöntem 2: Adaptive threshold
            binary2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                           cv2.THRESH_BINARY, 11, 2)
            methods.append(binary2)
            
            # Yöntem 3: Inverse OTSU
            _, binary3 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            methods.append(binary3)
            
            # Her yöntemle OCR dene
            best_text = ""
            
            custom_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
            
            for idx, method_img in enumerate(methods):
                try:
                    text = pytesseract.image_to_string(method_img, config=custom_config).strip()
                    text = text.replace(' ', '').replace('\n', '').replace('O', '0').replace('o', '0')
                    
                    if text and len(text) >= 4:  # En az 4 rakam
                        # Sadece rakam içeriyor mu kontrol et
                        if text.isdigit():
                            if len(text) > len(best_text):
                                best_text = text
                                print(f"    Yöntem {idx+1}: {text} ✓")
                except Exception:
                    pass
            
            if best_text:
                print(f"  ✅ YEŞİL ANA SAYI: {best_text}")
                return best_text, (x, y, w, h)
            
            print("⚠️ OCR yeşil sayıyı okuyamadı")
            return None
            
        except Exception as e:
            print(f"⚠️ Yeşil sayı tespit hatası: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    
    def extract_numbers_from_roi(self, img, roi, label=""):
        """Belirli bir bölgeden sayıları çıkar - İYİLEŞTİRİLMİŞ"""
        x, y, w, h = roi
        
        # ROI'yi çıkar
        roi_img = img[y:y+h, x:x+w]
        
        # GELİŞMİŞ ÖN İŞLEME
        gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
        
        # Kontrast artır
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Gürültü azalt
        gray = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        
        # Büyüt (3x) - OCR için daha iyi
        scale = 3
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Birden fazla threshold yöntemi dene
        methods = []
        
        # Yöntem 1: OTSU
        _, binary1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        methods.append(binary1)
        
        # Yöntem 2: Adaptive
        binary2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        methods.append(binary2)
        
        # Yöntem 3: Inverse OTSU
        _, binary3 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        methods.append(binary3)
        
        # Her yöntemle OCR dene
        best_text = ""
        best_processed = binary1
        
        custom_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
        
        for method_img in methods:
            try:
                text = pytesseract.image_to_string(method_img, config=custom_config).strip()
                text = text.replace(' ', '').replace('\n', '').replace('O', '0').replace('o', '0')
                
                if text and text.isdigit() and len(text) >= 4:
                    if len(text) > len(best_text):
                        best_text = text
                        best_processed = method_img
            except:
                pass
        
        print(f"  {label}: {best_text if best_text else '❌ Okunamadı'}")
        
        return best_text, best_processed
    
    
    def detect_button_regions_auto(self, img):
        """Butonları otomatik olarak tespit et - GELİŞTİRİLMİŞ"""
        height, width = img.shape[:2]
        
        # Görseli gri tonlamaya çevir
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Gaussian blur ile gürültüyü azalt
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Kenarları bul - daha hassas
        edges = cv2.Canny(blurred, 30, 100)
        
        # Morfolojik işlemler - kenarları güçlendir
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Contour bul
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Dikdörtgen bölgeleri bul ve filtrele
        rectangles = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Buton boyutlarına uygun mu?
            # Minimum genişlik: görsel genişliğinin %20'si
            # Maksimum genişlik: görsel genişliğinin %90'ı
            # Yükseklik: 15-100 piksel arası
            min_width = int(width * 0.20)
            max_width = int(width * 0.90)
            
            if (min_width < w < max_width and 15 < h < 100):
                # Aspect ratio kontrolü (çok uzun veya çok kısa olmasın)
                aspect_ratio = w / h
                if 2 < aspect_ratio < 15:  # Butonlar genellikle yatay
                    rectangles.append((x, y, w, h))
        
        # Y koordinatına göre sırala (yukarıdan aşağıya)
        rectangles.sort(key=lambda r: r[1])
        
        # Ana sayı + 4 buton = 5 bölge bekliyoruz
        if len(rectangles) >= 5:
            # İlk biri ana sayı, sonraki 4'ü butonlar
            main_roi = rectangles[0]
            button_rois = rectangles[1:5]
            print(f"✓ Otomatik tespit: Ana sayı + {len(button_rois)} buton bulundu")
            return main_roi, button_rois
        elif len(rectangles) == 4:
            # Sadece 4 buton varsa, en üsttekini ana sayı kabul et
            print(f"✓ Otomatik tespit: {len(rectangles)} bölge bulundu")
            main_roi = rectangles[0]
            button_rois = rectangles[0:4]  # 4 butonu döndür
            return main_roi, button_rois
        
        # Otomatik tespit başarısız, manuel bölgelere dön
        print(f"⚠️ Otomatik tespit başarısız ({len(rectangles)} bölge bulundu), manuel bölgeler kullanılıyor")
        return self.detect_button_regions_manual(img)
    
    
    def detect_button_regions_manual(self, img):
        """Manuel bölge koordinatları - İYİLEŞTİRİLMİŞ"""
        height, width = img.shape[:2]
        
        # Ana sayı bölgesi - üstte, ortada (yeşil sayı)
        # Görselin üst %15-30 kısmında
        main_number_roi = (int(width * 0.15), int(height * 0.05), 
                          int(width * 0.70), int(height * 0.15))
        
        # 4 buton bölgesi (alt alta, ortada)
        button_height = int(height * 0.10)  # Buton yüksekliği
        button_width = int(width * 0.70)    # Buton genişliği
        button_x = int(width * 0.15)        # Sol kenar
        button_start_y = int(height * 0.25) # İlk butonun Y pozisyonu
        button_spacing = int(height * 0.13) # Butonlar arası boşluk
        
        button_rois = []
        for i in range(4):
            y = button_start_y + (i * button_spacing)
            button_rois.append((button_x, y, button_width, button_height))
        
        print(f"ℹ️ Manuel bölgeler kullanılıyor:")
        print(f"   Ana sayı: {main_number_roi}")
        for i, btn in enumerate(button_rois, 1):
            print(f"   Buton {i}: {btn}")
        
        return main_number_roi, button_rois
    
    
    def process_captcha_image(self, image_path):
        """CAPTCHA görselini işle - GELİŞTİRİLMİŞ İLK 4 RAKAM EŞLEŞTİRME"""
        print(f"\n📷 İşleniyor: {os.path.basename(image_path)}")
        print("-" * 60)
        
        # Görseli yükle
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ Görsel yüklenemedi: {image_path}")
            return None
        
        print(f"✓ Görsel boyutu: {img.shape[1]}x{img.shape[0]}")
        
        # ÖNCE YEŞİL ANA SAYIYI BUL
        print("\n🔍 Yeşil ana sayı aranıyor...")
        green_result = self.extract_green_number(img)
        
        main_number = None
        if green_result:
            main_number = green_result[0]
        
        # Yeşil bulunamadıysa manuel bölgeden dene
        if not main_number:
            print("⚠️ Yeşil sayı bulunamadı, manuel bölge kullanılıyor...")
            main_roi, _ = self.detect_button_regions_manual(img)
            main_number, _ = self.extract_numbers_from_roi(img, main_roi, "ANA SAYI (Manuel)")
        
        # Buton bölgelerini tespit et
        _, button_rois = self.detect_button_regions_auto(img)
        
        # Buton sayılarını oku
        print("\n🔍 Buton sayıları okunuyor...")
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
            "correct_button": None,
            "correct_button_value": None
        }
        
        # İLK 4 RAKAM İLE EŞLEŞTİR (KULLANICININ İSTEĞİ)
        print(f"\n🔍 İLK 4 RAKAM eşleşmesi aranıyor...")
        print(f"   Ana sayı: {main_number}")
        
        if main_number and len(main_number) >= 4:
            main_first_4 = main_number[:4]
            print(f"   Ana sayının ilk 4 rakamı: {main_first_4}")
            
            for i, btn_num in enumerate(button_numbers, 1):
                if btn_num and len(btn_num) >= 4:
                    btn_first_4 = btn_num[:4]
                    print(f"   Buton {i} ilk 4 rakamı: {btn_first_4} {'✓' if btn_first_4 == main_first_4 else '✗'}")
                    
                    if btn_first_4 == main_first_4:
                        result["correct_button"] = i
                        result["correct_button_value"] = btn_num
                        print(f"\n✅ İLK 4 RAKAM EŞLEŞMESİ BULUNDU!")
                        print(f"   Ana sayı: {main_number} → İlk 4: {main_first_4}")
                        print(f"   Buton {i}: {btn_num} → İlk 4: {btn_first_4}")
                        break
        
        # Tam eşleşme de dene (yedek)
        if result["correct_button"] is None:
            print(f"\n🔍 Tam sayı eşleşmesi deneniyor...")
            for i, btn_num in enumerate(button_numbers, 1):
                if btn_num == main_number:
                    result["correct_button"] = i
                    result["correct_button_value"] = btn_num
                    print(f"\n✅ TAM EŞLEŞME BULUNDU! Buton {i}: {btn_num}")
                    break
        
        if result["correct_button"] is None:
            print(f"\n⚠️ Eşleşme bulunamadı!")
            print(f"   Ana sayı: {main_number}")
            print(f"   Butonlar: {', '.join(button_numbers)}")
        
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
        if total > 0:
            print(f"Başarı Oranı: {(matched/total*100):.1f}%")
        
        print("\n🔢 Bulunan Sayılar:")
        for i, result in enumerate(self.results, 1):
            status = "✅" if result['correct_button'] else "❌"
            correct_info = f"→ Buton {result['correct_button']}" if result['correct_button'] else "→ Eşleşme yok"
            print(f"  {status} {result['main_number']} {correct_info}")
            print(f"      Butonlar: {', '.join(result['buttons'])}")


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