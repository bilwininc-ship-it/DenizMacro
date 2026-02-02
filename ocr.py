"""
CAPTCHA Sayı Okuyucu ve Kayıt Sistemi - GELİŞTİRİLMİŞ VERSİYON
Ana sayı ve buton sayılarını OCR ile okur, JSON'a kaydeder
ÇİFT MOTOR: EasyOCR + Pytesseract (Hibrit Sistem)
"""

import cv2
import numpy as np
import json
import os
from datetime import datetime
from pathlib import Path

# Pytesseract yolu
try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    TESSERACT_AVAILABLE = True
except:
    TESSERACT_AVAILABLE = False
    print("⚠️ Pytesseract kullanılamıyor")

# EasyOCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except:
    EASYOCR_AVAILABLE = False
    print("⚠️ EasyOCR kullanılamıyor")


class CaptchaNumberReader:
    """Geliştirilmiş CAPTCHA Okuyucu - Çift Motor (EasyOCR + Tesseract)"""
    
    def __init__(self):
        self.results = []
        self.output_folder = "captcha_results"
        
        # Çıktı klasörünü oluştur
        Path(self.output_folder).mkdir(exist_ok=True)
        
        # EasyOCR başlat
        self.easyocr_reader = None
        if EASYOCR_AVAILABLE:
            try:
                print("🔧 EasyOCR başlatılıyor...")
                self.easyocr_reader = easyocr.Reader(['tr', 'en'], gpu=False, verbose=False)
                print("✅ EasyOCR hazır!")
            except Exception as e:
                print(f"⚠️ EasyOCR başlatılamadı: {e}")
        
        print("=" * 60)
        print("CAPTCHA SAYI OKUYUCU v2.0 - HİBRİT MOTOR")
        print("=" * 60)
        if self.easyocr_reader:
            print("✓ EasyOCR: AKTİF")
        if TESSERACT_AVAILABLE:
            print("✓ Tesseract: AKTİF")
        print("=" * 60)
    
    
    def preprocess_image_advanced(self, img, method='standard'):
        """Gelişmiş görüntü ön işleme"""
        # Gri tonlama
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        if method == 'standard':
            # Kontrast artırma
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Gürültü azaltma
            denoised = cv2.fastNlMeansDenoising(enhanced, None, h=10, templateWindowSize=7, searchWindowSize=21)
            
            # Büyütme (3x) - OCR için daha iyi
            scale = 3
            denoised = cv2.resize(denoised, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            
            # Binary threshold (OTSU)
            _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return binary
        
        elif method == 'adaptive':
            # Adaptive threshold
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Büyütme
            scale = 3
            enhanced = cv2.resize(enhanced, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            
            binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
            return binary
        
        elif method == 'inverse':
            # Inverse OTSU
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            scale = 3
            enhanced = cv2.resize(enhanced, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            return binary
        
        return gray
    
    
    def extract_green_number_easyocr(self, img):
        """YEŞİL renkteki ana sayıyı bul - EasyOCR ile"""
        if not self.easyocr_reader:
            return None
        
        try:
            # HSV'ye çevir
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Yeşil renk maskesi (geniş aralık)
            lower_green1 = np.array([35, 50, 50])
            upper_green1 = np.array([85, 255, 255])
            mask1 = cv2.inRange(hsv, lower_green1, upper_green1)
            
            # Daha açık yeşiller
            lower_green2 = np.array([40, 40, 100])
            upper_green2 = np.array([80, 255, 255])
            mask2 = cv2.inRange(hsv, lower_green2, upper_green2)
            
            # Birleştir
            mask = cv2.bitwise_or(mask1, mask2)
            
            # Morfolojik işlemler
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Yeşil bölgeleri bul
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
            
            # Sayı gibi görünen bölgeleri filtrele
            valid_contours = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w > 50 and h > 15:
                    valid_contours.append(cnt)
            
            if not valid_contours:
                return None
            
            # En büyük bölgeyi al
            largest_contour = max(valid_contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Bölgeyi genişlet
            margin = 15
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(img.shape[1] - x, w + 2*margin)
            h = min(img.shape[0] - y, h + 2*margin)
            
            # Yeşil sayı bölgesini çıkar
            green_roi = img[y:y+h, x:x+w]
            
            # EasyOCR ile oku
            green_array = np.array(green_roi)
            results = self.easyocr_reader.readtext(green_array)
            
            for (bbox, text, conf) in results:
                digits = ''.join(c for c in text if c.isdigit())
                if len(digits) >= 4 and conf > 0.2:  # Düşük eşik
                    print(f"  ✅ YEŞİL ANA SAYI (EasyOCR): {digits} (güven:{conf:.2f})")
                    return digits, (x, y, w, h)
            
            return None
            
        except Exception as e:
            print(f"⚠️ Yeşil sayı tespit hatası (EasyOCR): {e}")
            return None
    
    
    def extract_number_hybrid(self, img, roi, label=""):
        """Hibrit OCR - EasyOCR + Tesseract"""
        x, y, w, h = roi
        roi_img = img[y:y+h, x:x+w]
        
        best_text = ""
        best_conf = 0.0
        
        # YÖNTEM 1: EasyOCR (Öncelikli)
        if self.easyocr_reader:
            try:
                roi_array = np.array(roi_img)
                results = self.easyocr_reader.readtext(roi_array)
                
                for (bbox, text, conf) in results:
                    digits = ''.join(c for c in text if c.isdigit())
                    # 5-7 haneli sayılar kabul et
                    if 5 <= len(digits) <= 7 and conf > 0.2:  # Düşük eşik
                        if len(digits) > len(best_text) or conf > best_conf:
                            best_text = digits
                            best_conf = conf
                            print(f"  {label}: {digits} (EasyOCR, güven:{conf:.2f})")
            except Exception as e:
                print(f"  ⚠️ EasyOCR hatası: {e}")
        
        # YÖNTEM 2: Tesseract (Yedek)
        if not best_text and TESSERACT_AVAILABLE:
            try:
                # 3 farklı ön işleme yöntemi dene
                for method in ['standard', 'adaptive', 'inverse']:
                    processed = self.preprocess_image_advanced(roi_img, method)
                    
                    custom_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
                    text = pytesseract.image_to_string(processed, config=custom_config).strip()
                    text = text.replace(' ', '').replace('\n', '').replace('O', '0').replace('o', '0')
                    
                    if text and text.isdigit() and len(text) >= 4:
                        if len(text) > len(best_text):
                            best_text = text
                            print(f"  {label}: {text} (Tesseract-{method})")
                            break
            except Exception as e:
                print(f"  ⚠️ Tesseract hatası: {e}")
        
        # Hiçbir yöntem çalışmadıysa
        if not best_text:
            print(f"  {label}: ❌ Okunamadı")
        
        return best_text
    
    
    def detect_button_regions_auto(self, img):
        """Butonları otomatik tespit et"""
        height, width = img.shape[:2]
        
        # EasyOCR ile tüm görseli tara
        if self.easyocr_reader:
            try:
                img_array = np.array(img)
                all_results = self.easyocr_reader.readtext(img_array)
                
                # Tüm bulunan sayıları topla
                found_numbers = []
                for (bbox, text, conf) in all_results:
                    digits = ''.join(c for c in text if c.isdigit())
                    
                    # 5-7 haneli sayılar
                    if 5 <= len(digits) <= 7 and conf > 0.2:
                        y_coord = bbox[0][1]
                        x_coord = bbox[0][0]
                        width_box = bbox[1][0] - bbox[0][0]
                        height_box = bbox[2][1] - bbox[0][1]
                        
                        found_numbers.append({
                            'roi': (int(x_coord), int(y_coord), int(width_box), int(height_box)),
                            'y': y_coord,
                            'digits': digits
                        })
                
                # Y koordinatına göre sırala
                found_numbers.sort(key=lambda x: x['y'])
                
                if len(found_numbers) >= 5:
                    # İlk biri ana sayı, sonraki 4'ü butonlar
                    main_roi = found_numbers[0]['roi']
                    button_rois = [num['roi'] for num in found_numbers[1:5]]
                    print(f"✓ EasyOCR otomatik tespit: Ana sayı + {len(button_rois)} buton")
                    return main_roi, button_rois
                elif len(found_numbers) == 4:
                    main_roi = found_numbers[0]['roi']
                    button_rois = [num['roi'] for num in found_numbers[0:4]]
                    print(f"✓ EasyOCR otomatik tespit: {len(found_numbers)} bölge")
                    return main_roi, button_rois
            except Exception as e:
                print(f"⚠️ EasyOCR otomatik tespit hatası: {e}")
        
        # Manuel bölgelere dön
        print(f"⚠️ Otomatik tespit başarısız, manuel bölgeler kullanılıyor")
        return self.detect_button_regions_manual(img)
    
    
    def detect_button_regions_manual(self, img):
        """Manuel bölge koordinatları - Optimize edilmiş"""
        height, width = img.shape[:2]
        
        # Ana sayı bölgesi - üstte, ortada (daha büyük alan)
        main_number_roi = (int(width * 0.10), int(height * 0.02), 
                          int(width * 0.80), int(height * 0.20))
        
        # 4 buton bölgesi (alt alta, ortada)
        button_height = int(height * 0.12)
        button_width = int(width * 0.75)
        button_x = int(width * 0.12)
        button_start_y = int(height * 0.22)
        button_spacing = int(height * 0.15)
        
        button_rois = []
        for i in range(4):
            y = button_start_y + (i * button_spacing)
            button_rois.append((button_x, y, button_width, button_height))
        
        print(f"ℹ️ Manuel bölgeler kullanılıyor")
        
        return main_number_roi, button_rois
    
    
    def process_captcha_image(self, image_path):
        """CAPTCHA görselini işle - GELİŞTİRİLMİŞ HİBRİT MOTOR"""
        print(f"\n📷 İşleniyor: {os.path.basename(image_path)}")
        print("-" * 60)
        
        # Görseli yükle
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ Görsel yüklenemedi: {image_path}")
            return None
        
        print(f"✓ Görsel boyutu: {img.shape[1]}x{img.shape[0]}")
        
        # TÜM GÖRSELİ TARA - Ana sayıyı bul (EasyOCR)
        main_number = None
        
        if self.easyocr_reader:
            print("\n🔍 Tüm görsel taranıyor (EasyOCR)...")
            try:
                img_array = np.array(img)
                all_results = self.easyocr_reader.readtext(img_array)
                
                # Y koordinatına göre sırala (en üstteki ana sayı olabilir)
                all_results.sort(key=lambda x: x[0][0][1])
                
                # Tüm bulunan sayıları göster
                found_numbers = []
                for idx, (bbox, text, conf) in enumerate(all_results):
                    digits = ''.join(c for c in text if c.isdigit())
                    if digits and len(digits) >= 4:
                        y_coord = bbox[0][1]
                        found_numbers.append({
                            'digits': digits,
                            'y': y_coord,
                            'conf': conf
                        })
                        print(f"  [{idx+1}] Y:{int(y_coord):3d} -> {digits} (güven:{conf:.2f})")
                
                # İLK (EN ÜSTTEKİ) SAYIYI ANA SAYI OLARAK AL
                if found_numbers:
                    main_number = found_numbers[0]['digits']
                    print(f"\n  ✅ ANA SAYI (En üstteki): {main_number}")
                
            except Exception as e:
                print(f"⚠️ EasyOCR tarama hatası: {e}")
        
        # Buton bölgelerini tespit et
        main_roi, button_rois = self.detect_button_regions_auto(img)
        
        # Ana sayı hala bulunamadıysa manuel bölgeden dene
        if not main_number:
            print("⚠️ Otomatik taramada ana sayı bulunamadı, manuel bölge deneniyor...")
            main_number = self.extract_number_hybrid(img, main_roi, "ANA SAYI (Manuel)")
        
        # Buton sayılarını oku (Hibrit)
        print("\n🔍 Buton sayıları okunuyor (Hibrit Motor)...")
        button_numbers = []
        for i, roi in enumerate(button_rois, 1):
            number = self.extract_number_hybrid(img, roi, f"BUTON {i}")
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
        
        # İLK 4 RAKAM İLE EŞLEŞTİR
        print(f"\n🔍 İLK 4 RAKAM eşleşmesi aranıyor...")
        print(f"   Ana sayı: {main_number}")
        
        if main_number and len(main_number) >= 4:
            main_first_4 = main_number[:4]
            print(f"   Ana sayının ilk 4 rakamı: {main_first_4}")
            
            for i, btn_num in enumerate(button_numbers, 1):
                if btn_num and len(btn_num) >= 4:
                    btn_first_4 = btn_num[:4]
                    print(f"   Buton {i} ilk 4 rakamı: {btn_first_4} {'✅' if btn_first_4 == main_first_4 else '❌'}")
                    
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
