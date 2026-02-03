"""
BASIT BUTON TIKLAYICI - OCR Sonucu ile Çalışır
Mevcut captcha_detector.py ve ocr.py kodunuza dokunmadan kullanın
"""

import pyautogui
import time
import json
import os
from pathlib import Path

class SimpleCaptchaClicker:
    """OCR sonuçlarını okur ve doğru butona tıklar"""
    
    def __init__(self, config_file="captcha_config_pro.json"):
        # Güvenlik
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3
        
        # Config dosyasından buton koordinatlarını yükle
        self.button_regions = []
        self.window_offset = (0, 0)
        
        self.load_config(config_file)
        
        print("=" * 70)
        print("BASIT CAPTCHA TIKLAYICI HAZIR")
        print("=" * 70)
        if self.button_regions:
            print(f"✓ {len(self.button_regions)} buton koordinatı yüklendi")
        else:
            print("⚠️ Buton koordinatları bulunamadı!")
    
    
    def load_config(self, config_file):
        """Config dosyasını yükle"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if 'button_regions' in data and data['button_regions']:
                        self.button_regions = [tuple(btn) for btn in data['button_regions']]
                        print(f"✓ Config yüklendi: {len(self.button_regions)} buton")
                    else:
                        print("⚠️ Config'de buton bilgisi yok")
            else:
                print(f"⚠️ Config dosyası bulunamadı: {config_file}")
        except Exception as e:
            print(f"❌ Config yükleme hatası: {e}")
    
    
    def click_button_by_index(self, button_index):
        """
        Belirli index'teki butona tıkla (0-based)
        
        Args:
            button_index (int): Buton index'i (0,1,2,3)
        
        Returns:
            bool: Başarı durumu
        """
        try:
            if not self.button_regions:
                print("❌ Buton koordinatları tanımlı değil!")
                return False
            
            if button_index < 0 or button_index >= len(self.button_regions):
                print(f"❌ Geçersiz buton index'i: {button_index}")
                return False
            
            x1, y1, x2, y2 = self.button_regions[button_index]
            
            # Butonun merkezi
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            print(f"\n🎯 Buton {button_index + 1} tıklanıyor...")
            print(f"   Koordinat: ({center_x}, {center_y})")
            
            # Fareyi götür
            pyautogui.moveTo(center_x, center_y, duration=0.5)
            time.sleep(0.2)
            
            # Tıkla
            pyautogui.click()
            
            print(f"✅ Buton {button_index + 1} tıklandı!")
            return True
            
        except Exception as e:
            print(f"❌ Tıklama hatası: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    
    def find_and_click(self, main_number, button_numbers):
        """
        Ana sayı ile eşleşen butonu bul ve tıkla
        
        Args:
            main_number (str): Ana sayı
            button_numbers (list): Buton sayıları listesi [str, str, str, str]
        
        Returns:
            int or None: Tıklanan buton index'i (1-based) veya None
        """
        try:
            if not main_number:
                print("❌ Ana sayı boş!")
                return None
            
            if not button_numbers or len(button_numbers) < 4:
                print(f"❌ Geçersiz buton sayıları: {button_numbers}")
                return None
            
            # Sadece rakamları al
            main_digits = ''.join(c for c in main_number if c.isdigit())
            
            if len(main_digits) < 4:
                print(f"❌ Ana sayı çok kısa: {main_digits}")
                return None
            
            print("\n" + "=" * 70)
            print("🔍 DOĞRU BUTON ARANIYOR")
            print("=" * 70)
            print(f"Ana sayı: {main_digits}")
            print(f"İlk 4 rakam: {main_digits[:4]}")
            print()
            
            # İlk 4 rakam ile eşleştir
            main_first_4 = main_digits[:4]
            
            for i, btn_num in enumerate(button_numbers):
                if not btn_num:
                    print(f"Buton {i+1}: [boş] ❌")
                    continue
                
                btn_digits = ''.join(c for c in btn_num if c.isdigit())
                
                if len(btn_digits) < 4:
                    print(f"Buton {i+1}: {btn_digits} (çok kısa) ❌")
                    continue
                
                btn_first_4 = btn_digits[:4]
                match = btn_first_4 == main_first_4
                
                print(f"Buton {i+1}: {btn_digits[:4]}... {'✅ EŞLEŞTI!' if match else '❌'}")
                
                if match:
                    print(f"\n🎯 DOĞRU BUTON BULUNDU: Buton {i+1}")
                    print("=" * 70)
                    
                    # Tıkla
                    success = self.click_button_by_index(i)
                    
                    if success:
                        return i + 1
                    else:
                        return None
            
            print("\n⚠️ Eşleşen buton bulunamadı!")
            print("=" * 70)
            return None
            
        except Exception as e:
            print(f"\n❌ find_and_click hatası: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Test/Manuel kullanım"""
    print("\n" + "=" * 70)
    print("BASIT CAPTCHA TIKLAYICI - MANUEL TEST")
    print("=" * 70)
    
    clicker = SimpleCaptchaClicker()
    
    # Test verileri
    print("\n📝 Test verisi:")
    main_number = "123456"
    button_numbers = [
        "234567",  # Buton 1
        "123478",  # Buton 2 - İlk 4 rakam eşleşiyor!
        "345678",  # Buton 3
        "456789",  # Buton 4
    ]
    
    print(f"Ana sayı: {main_number}")
    for i, num in enumerate(button_numbers, 1):
        print(f"Buton {i}: {num}")
    
    # 3 saniye bekle
    print("\n⏳ 3 saniye sonra test başlayacak...")
    time.sleep(3)
    
    # Bul ve tıkla
    result = clicker.find_and_click(main_number, button_numbers)
    
    if result:
        print(f"\n✅ Başarılı! Buton {result} tıklandı.")
    else:
        print(f"\n❌ Başarısız!")


if __name__ == "__main__":
    main()