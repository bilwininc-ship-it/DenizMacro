"""
CAPTCHA OTOMATİK ÇÖZÜCÜ - WRAPPER
Mevcut OCR ve Captcha Detector kodlarınızla birlikte çalışır
"""

import time
import json
import os
from pathlib import Path
from simple_clicker import SimpleCaptchaClicker

class CaptchaAutoSolver:
    """OCR sonuçlarını izler ve otomatik tıklar"""
    
    def __init__(self, 
                 results_folder="captcha_results",
                 results_file="captcha_results.json"):
        
        self.results_folder = results_folder
        self.results_file = os.path.join(results_folder, results_file)
        self.clicker = SimpleCaptchaClicker()
        self.last_processed_count = 0
        
        print("=" * 70)
        print("CAPTCHA OTOMATİK ÇÖZÜCÜ BAŞLATILDI")
        print("=" * 70)
        print(f"İzlenen dosya: {self.results_file}")
        print(f"Clicker durumu: {'✓ Hazır' if self.clicker.button_regions else '✗ Butonlar tanımsız'}")
        print("=" * 70)
    
    
    def read_latest_result(self):
        """En son OCR sonucunu oku"""
        try:
            if not os.path.exists(self.results_file):
                return None
            
            with open(self.results_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data or len(data) == 0:
                return None
            
            # Son kaydı al
            latest = data[-1]
            return latest
            
        except Exception as e:
            print(f"⚠️ Dosya okuma hatası: {e}")
            return None
    
    
    def process_result(self, result):
        """Bir OCR sonucunu işle ve butona tıkla"""
        try:
            main_number = result.get('main_number')
            buttons = result.get('buttons', [])
            
            if not main_number:
                print("⚠️ Ana sayı bulunamadı")
                return False
            
            if not buttons or len(buttons) < 4:
                print(f"⚠️ Yetersiz buton sayısı: {len(buttons)}")
                return False
            
            print(f"\n📊 Yeni sonuç işleniyor:")
            print(f"   Ana sayı: {main_number}")
            print(f"   Butonlar: {buttons}")
            
            # Tıkla
            clicked = self.clicker.find_and_click(main_number, buttons)
            
            if clicked:
                print(f"✅ İŞLEM TAMAMLANDI - Buton {clicked} tıklandı!\n")
                return True
            else:
                print(f"⚠️ Tıklama yapılamadı\n")
                return False
            
        except Exception as e:
            print(f"❌ İşleme hatası: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    
    def monitor_and_click(self, check_interval=2):
        """
        OCR sonuç dosyasını sürekli izle ve yeni kayıt geldiğinde tıkla
        
        Args:
            check_interval (float): Kontrol sıklığı (saniye)
        """
        print(f"\n▶️  İZLEME BAŞLATILDI (Her {check_interval}s kontrol)")
        print("   Durdurmak için CTRL+C basın\n")
        
        try:
            while True:
                # Son sonucu oku
                latest = self.read_latest_result()
                
                if latest:
                    # Kaç kayıt var?
                    try:
                        with open(self.results_file, 'r', encoding='utf-8') as f:
                            all_data = json.load(f)
                        current_count = len(all_data)
                    except:
                        current_count = 0
                    
                    # Yeni kayıt var mı?
                    if current_count > self.last_processed_count:
                        print(f"\n🆕 YENİ KAYIT TESPİT EDİLDİ ({current_count}. kayıt)")
                        print("-" * 70)
                        
                        # İşle
                        self.process_result(latest)
                        
                        # Sayacı güncelle
                        self.last_processed_count = current_count
                        
                        print("-" * 70)
                
                # Bekle
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹  İzleme durduruldu (Kullanıcı)")
        except Exception as e:
            print(f"\n❌ İzleme hatası: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Ana program"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    CAPTCHA OTOMATİK ÇÖZÜCÜ v1.0                      ║
╚══════════════════════════════════════════════════════════════════════╝

NASIL ÇALIŞIR:
1. OCR scriptiniz (ocr.py) çalışır → captcha_results.json'a yazar
2. Bu script JSON dosyasını izler
3. Yeni kayıt geldiğinde:
   ✓ Ana sayıyı okur
   ✓ Eşleşen butonu bulur
   ✓ Otomatik tıklar

KULLANIM:
1. captcha_detector.py ile buton koordinatlarını ayarla
2. ocr.py'yi başlat (captcha'ları okuyor)
3. Bu scripti başlat (otomatik tıklıyor)
""")
    
    # Modu seç
    print("MODLAR:")
    print("1. Otomatik İzleme (Sürekli çalışır)")
    print("2. Tek Test (Son kaydı işle ve çık)")
    print("3. Çıkış")
    
    choice = input("\nSeçiminiz (1-3): ").strip()
    
    solver = CaptchaAutoSolver()
    
    if choice == "1":
        # Otomatik mod
        interval = input("Kontrol sıklığı (saniye, varsayılan 2): ").strip()
        interval = float(interval) if interval else 2.0
        
        solver.monitor_and_click(check_interval=interval)
        
    elif choice == "2":
        # Tek test
        print("\n📋 Son kayıt işleniyor...")
        latest = solver.read_latest_result()
        
        if latest:
            solver.process_result(latest)
        else:
            print("❌ Kayıt bulunamadı!")
    
    elif choice == "3":
        print("\n👋 Görüşürüz!")
        return
    
    else:
        print("❌ Geçersiz seçim!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()