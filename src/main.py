import time
import random
import threading
import pyautogui

from src.ocr_engine import OCREngine
from src.ui_panel import UIPanel

# Güvenlik ayarları
pyautogui.FAILSAFE = True  # Sol üst köşe = acil durdur
pyautogui.PAUSE = 0.1

class DenizBot:
    """denizv1 Bot - KRİTİK MOD
    
    Sadece %100 tam eşleşme ile tıklar.
    Yanlış tıklama = 0%
    """
    
    def __init__(self):
        self.ocr = OCREngine()
        self.ui = UIPanel()
        self.is_running = False
        self.ui.set_start_callback(self.toggle_bot)
        
    def toggle_bot(self):
        """Botu başlat/durdur"""
        self.is_running = not self.is_running
        
        if self.is_running:
            self.ui.start_button.configure(text="Sistemi Durdur", fg_color="#d32f2f")
            self.ui.update_status("Sistem Aktif", "green")
            self.ui.add_log("🚀 Bot başlatıldı - KRİTİK MOD")
            self.ui.add_log("⚠️  SADECE %100 eşleşme ile tıklanır")
            self.ui.add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            # Tarama thread'i başlat
            scan_thread = threading.Thread(target=self.scan_loop, daemon=True)
            scan_thread.start()
        else:
            self.ui.start_button.configure(text="Sistemi Başlat", fg_color="#1f6aa5")
            self.ui.update_status("Beklemede", "gray")
            self.ui.add_log("⏸️  Bot durduruldu")
            self.ui.add_log("")
    
    def human_mouse_move(self, target_x: int, target_y: int):
        """İnsansı fare hareketi - Bezier eğrisi"""
        start_x, start_y = pyautogui.position()
        
        # Bezier kontrol noktaları
        cp1_x = start_x + random.randint(-80, 80)
        cp1_y = start_y + random.randint(-80, 80)
        cp2_x = target_x + random.randint(-80, 80)
        cp2_y = target_y + random.randint(-80, 80)
        
        steps = 25
        
        for i in range(steps):
            t = i / (steps - 1)
            
            # Cubic Bezier formülü
            x = ((1-t)**3 * start_x + 
                 3*(1-t)**2*t * cp1_x + 
                 3*(1-t)*t**2 * cp2_x + 
                 t**3 * target_x)
            
            y = ((1-t)**3 * start_y + 
                 3*(1-t)**2*t * cp1_y + 
                 3*(1-t)*t**2 * cp2_y + 
                 t**3 * target_y)
            
            pyautogui.moveTo(int(x), int(y))
            time.sleep(0.003)
        
        # Son pozisyona kesin git
        pyautogui.moveTo(target_x, target_y)
    
    def safe_click(self, x: int, y: int):
        """Güvenli tıklama"""
        # Küçük offset ekle (daha doğal)
        offset_x = random.randint(-2, 2)
        offset_y = random.randint(-2, 2)
        
        # İnsansı hareket
        self.human_mouse_move(x + offset_x, y + offset_y)
        
        # Tıklama öncesi bekleme
        time.sleep(random.uniform(0.1, 0.2))
        
        # Tıkla
        pyautogui.click()
        
    def scan_loop(self):
        """Ana tarama döngüsü - KRİTİK MOD"""
        scan_count = 0
        
        while self.is_running:
            try:
                scan_count += 1
                self.ui.update_status("📡 Taranıyor...", "yellow")
                
                # Ekranı pasif oku
                green_text, gray_buttons = self.ocr.scan_screen()
                
                # Yeşil kod VE butonlar var mı?
                if green_text and gray_buttons:
                    button_texts = [btn[2] for btn in gray_buttons]
                    
                    self.ui.add_log(f"━━━ Tarama #{scan_count} ━━━")
                    self.ui.add_log(f"🟢 Yeşil: {green_text}")
                    self.ui.add_log(f"🔘 Butonlar: {button_texts}")
                    
                    # KRİTİK: SADECE TAM EŞLEŞMe
                    match = None
                    
                    for btn_x, btn_y, btn_text in gray_buttons:
                        if green_text == btn_text:
                            # TAM EŞLEŞMe BULUNDU!
                            match = (btn_x, btn_y, btn_text)
                            self.ui.add_log(f"✅ TAM EŞLEŞMe: {btn_text}")
                            break
                        else:
                            self.ui.add_log(f"❌ Uyuşmuyor: {btn_text} ≠ {green_text}")
                    
                    if match:
                        # EŞLEŞMe VAR - TIKLANABİLİR
                        self.ui.update_status("✅ %100 Eşleşme!", "green")
                        
                        # Rastgele bekleme süresi
                        wait_time = random.uniform(4, 14)
                        self.ui.add_log(f"⏱️  {wait_time:.1f}s bekleniyor...")
                        
                        # Geri sayım
                        for remaining in range(int(wait_time), 0, -1):
                            if not self.is_running:
                                self.ui.add_log("⚠️  Bot durduruldu, tıklama iptal")
                                break
                            
                            self.ui.update_info(f"⏳ {remaining}s...")
                            time.sleep(1)
                        
                        # Bot hala çalışıyor mu?
                        if not self.is_running:
                            continue
                        
                        # Kalan saniye kesiri
                        time.sleep(wait_time % 1)
                        
                        # TIKLAMA YAPILIYOR
                        self.ui.update_status("🖱️  Tıklanıyor...", "green")
                        self.ui.add_log(f"🎯 TIKLA: {match[2]} → ({match[0]}, {match[1]})")
                        
                        self.safe_click(match[0], match[1])
                        
                        # Başarı
                        self.ui.update_success_count()
                        self.ui.add_log(f"✅ BAŞARILI! Toplam: {self.ui.success_count}")
                        self.ui.add_log("")
                        
                        # Başarıdan sonra 3 saniye dinlen
                        time.sleep(3)
                        
                    else:
                        # EŞLEŞMe YOK - GÜVENLİ ATLA
                        self.ui.update_status("⚠️  Eşleşme yok, atlanıyor", "yellow")
                        self.ui.add_log(f"⚠️  '{green_text}' butonlarda yok")
                        self.ui.add_log(f"🛡️  GÜVENLİ ATLANDI (oyun kapanmadı)")
                        self.ui.add_log("")
                        self.ui.update_fail_count()
                        
                else:
                    # Eksik veri
                    if not green_text:
                        self.ui.update_status("Yeşil kod bekleniyor", "gray")
                    elif not gray_buttons:
                        self.ui.update_status("Buton bekleniyor", "gray")
                
            except Exception as e:
                self.ui.update_status("❌ Hata", "red")
                self.ui.add_log(f"❌ Hata: {str(e)[:50]}")
                print(f"Detaylı hata: {e}")
                
            # 2 saniye bekle, sonra tekrar tara
            time.sleep(2)
    
    def run(self):
        """Botu başlat"""
        print("=" * 60)
        print("denizv1 Bot - KRİTİK MOD v2.0")
        print("=" * 60)
        print("✅ Sadece %100 eşleşme → Yanlış tıklama YOK")
        print("✅ Eşleşme yoksa → Güvenli atla")
        print("✅ Oyun kapanma riski → %0")
        print("=" * 60)
        self.ui.run()

if __name__ == "__main__":
    bot = DenizBot()
    bot.run()