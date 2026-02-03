"""
BUTON TIKLAYICI MODÜL - WINDOWS API VERSİYONU
Direkt Windows API ile fare kontrolü (daha güvenilir)
"""

import time
import logging
import win32api
import win32con
import win32gui

logger = logging.getLogger('ButtonClicker')


class ButtonClicker:
    """Windows API ile fareyi kontrol ederek butona tıklayan sınıf"""
    
    def __init__(self):
        logger.info("ButtonClicker hazır (Windows API)")
    
    
    def click_button(self, button_region, window_handle=None):
        """
        Belirtilen bölgenin ortasına Windows API ile tıklar
        
        Args:
            button_region: (x1, y1, x2, y2) koordinatları
            window_handle: Pencere handle (opsiyonel)
        
        Returns:
            bool: Başarılı ise True
        """
        try:
            if not button_region:
                logger.error("❌ Buton bölgesi belirtilmedi!")
                return False
            
            x1, y1, x2, y2 = button_region
            
            # Butonun merkez noktasını hesapla
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            logger.info(f"🎯 Hedef konum (lokal): ({center_x}, {center_y})")
            logger.info(f"   Buton bölgesi: ({x1}, {y1}, {x2}, {y2})")
            
            # Ekran koordinatlarını hesapla
            if window_handle:
                try:
                    # Pencere aktif mi kontrol et
                    if not win32gui.IsWindow(window_handle):
                        logger.error("❌ Pencere handle geçersiz!")
                        return False
                    
                    # Pencereyi öne getir ve aktif et
                    logger.info("🪟 Pencere aktif ediliyor...")
                    try:
                        win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)
                        time.sleep(0.2)
                        win32gui.SetForegroundWindow(window_handle)
                        time.sleep(0.3)
                        win32gui.BringWindowToTop(window_handle)
                        time.sleep(0.2)
                        logger.info("   ✓ Pencere aktif edildi")
                    except Exception as fg_error:
                        logger.warning(f"   ⚠️ Pencere öne getirilemedi: {fg_error}")
                    
                    # CLIENT AREA koordinatlarını kullan
                    client_to_screen = win32gui.ClientToScreen(window_handle, (0, 0))
                    
                    # Ekran koordinatlarına çevir
                    screen_x = client_to_screen[0] + center_x
                    screen_y = client_to_screen[1] + center_y
                    
                    logger.info(f"📍 Client area offset: {client_to_screen}")
                    logger.info(f"🖥️  Ekran koordinatı: ({screen_x}, {screen_y})")
                    
                except Exception as e:
                    logger.error(f"❌ Koordinat hesaplama hatası: {e}", exc_info=True)
                    return False
            else:
                # Pencere handle yoksa direkt koordinat kullan
                screen_x, screen_y = center_x, center_y
                logger.info(f"🖥️  Direkt koordinat kullanılıyor: ({screen_x}, {screen_y})")
            
            # Eski fare pozisyonunu kaydet
            old_pos = win32api.GetCursorPos()
            logger.info(f"💾 Eski fare pozisyonu: {old_pos}")
            
            # YÖNTEM 1: Windows API ile fare hareketi
            logger.info(f"🖱️  Fare hareket ediyor ({screen_x}, {screen_y})...")
            
            try:
                # Fareyi hedefe taşı
                win32api.SetCursorPos((screen_x, screen_y))
                time.sleep(0.3)
                
                # Fare pozisyonunu doğrula
                current_pos = win32api.GetCursorPos()
                logger.info(f"✓ Fare pozisyonu: {current_pos}")
                
                if abs(current_pos[0] - screen_x) > 5 or abs(current_pos[1] - screen_y) > 5:
                    logger.warning(f"⚠️ Fare hedeften uzak! Hedef: ({screen_x}, {screen_y}), Gerçek: {current_pos}")
                    # Tekrar dene
                    win32api.SetCursorPos((screen_x, screen_y))
                    time.sleep(0.2)
                    current_pos = win32api.GetCursorPos()
                    logger.info(f"   2. deneme pozisyon: {current_pos}")
                
            except Exception as move_error:
                logger.error(f"❌ Fare hareket hatası: {move_error}")
                return False
            
            # TIKLAMA - 3 yöntem dene
            logger.info("👆 Tıklama yapılıyor...")
            
            try:
                # YÖNTEM 1: mouse_event (en güvenilir)
                logger.info("   Yöntem 1: mouse_event kullanılıyor")
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, screen_x, screen_y, 0, 0)
                time.sleep(0.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, screen_x, screen_y, 0, 0)
                time.sleep(0.1)
                logger.info("   ✓ mouse_event tamamlandı")
                
            except Exception as click_error:
                logger.error(f"❌ Tıklama hatası (mouse_event): {click_error}")
                
                # YÖNTEM 2: PyAutoGUI yedek
                try:
                    logger.info("   Yöntem 2: PyAutoGUI deneniyor")
                    import pyautogui
                    pyautogui.click(screen_x, screen_y)
                    time.sleep(0.1)
                    logger.info("   ✓ PyAutoGUI tamamlandı")
                except Exception as pag_error:
                    logger.error(f"❌ PyAutoGUI hatası: {pag_error}")
                    return False
            
            # Kısa bekle
            time.sleep(0.2)
            
            # Fareyi eski pozisyona döndür (opsiyonel)
            try:
                win32api.SetCursorPos(old_pos)
                logger.info(f"↩️  Fare eski pozisyona döndü: {old_pos}")
            except:
                pass
            
            logger.info("✅ Tıklama başarılı!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Genel tıklama hatası: {e}", exc_info=True)
            return False
    
    
    def click_correct_button(self, main_number, button_numbers, button_regions, window_handle=None):
        """
        Ana sayı ile eşleşen butonu bulup tıklar
        
        Args:
            main_number: Ana sayı (str)
            button_numbers: Buton sayıları listesi (list of str)
            button_regions: Buton koordinatları listesi (list of tuples)
            window_handle: Pencere handle (opsiyonel)
        
        Returns:
            tuple: (success: bool, button_index: int or None)
        """
        try:
            if not main_number:
                logger.error("❌ Ana sayı yok!")
                return False, None
            
            if not button_numbers or not button_regions:
                logger.error("❌ Buton bilgileri eksik!")
                return False, None
            
            if len(button_numbers) != len(button_regions):
                logger.error("❌ Buton sayı ve koordinat sayısı uyuşmuyor!")
                return False, None
            
            logger.info("=" * 70)
            logger.info(f"🔍 DOĞRU BUTON ARANYOR")
            logger.info(f"   Ana sayı: {main_number}")
            logger.info(f"   Butonlar: {button_numbers}")
            
            # Ana sayıdan sadece rakamları al
            main_digits = ''.join(c for c in str(main_number) if c.isdigit())
            
            # İLK 4 RAKAM İLE EŞLEŞTİR
            if len(main_digits) >= 4:
                main_first_4 = main_digits[:4]
                logger.info(f"   Ana sayının ilk 4 rakamı: {main_first_4}")
                
                for i, btn_num in enumerate(button_numbers):
                    if btn_num:
                        btn_digits = ''.join(c for c in str(btn_num) if c.isdigit())
                        if len(btn_digits) >= 4:
                            btn_first_4 = btn_digits[:4]
                            match = btn_first_4 == main_first_4
                            logger.info(f"   Buton {i+1}: {btn_first_4} {'✅ EŞLEŞTİ' if match else '❌'}")
                            
                            if match:
                                logger.info(f"\n✅ DOĞRU BUTON BULUNDU: Buton {i+1}")
                                logger.info(f"   Koordinat: {button_regions[i]}")
                                logger.info("=" * 70)
                                
                                # TIKLA
                                success = self.click_button(button_regions[i], window_handle)
                                
                                if success:
                                    logger.info("🎉 TIKLAMA BAŞARILI!")
                                    return True, i + 1
                                else:
                                    logger.error("❌ Tıklama başarısız!")
                                    return False, i + 1
            
            # Tam eşleşme dene (yedek)
            logger.info("\n   İlk 4 rakam eşleşmedi, tam sayı deneniyor...")
            main_clean = ''.join(c for c in str(main_number) if c.isdigit())
            
            for i, btn_num in enumerate(button_numbers):
                btn_clean = ''.join(c for c in str(btn_num) if c.isdigit())
                if btn_clean == main_clean:
                    logger.info(f"\n✅ TAM EŞLEŞME BULUNDU: Buton {i+1}")
                    logger.info(f"   Koordinat: {button_regions[i]}")
                    logger.info("=" * 70)
                    
                    # TIKLA
                    success = self.click_button(button_regions[i], window_handle)
                    
                    if success:
                        logger.info("🎉 TIKLAMA BAŞARILI!")
                        return True, i + 1
                    else:
                        logger.error("❌ Tıklama başarısız!")
                        return False, i + 1
            
            logger.warning("❌ Eşleşen buton bulunamadı!")
            logger.info("=" * 70)
            return False, None
            
        except Exception as e:
            logger.error(f"❌ Buton tıklama hatası: {e}", exc_info=True)
            return False, None


# Test fonksiyonu
if __name__ == "__main__":
    # Logging ayarla
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    print("\n" + "=" * 70)
    print("BUTON TIKLAYICI TEST - WINDOWS API")
    print("=" * 70)
    
    clicker = ButtonClicker()
    
    # 3 saniye içinde fareyi istediğin yere getir
    print("\n⏰ 3 saniye içinde fareyi test etmek istediğin yere getir...")
    time.sleep(3)
    
    # Şu anki fare pozisyonunu al
    test_pos = win32api.GetCursorPos()
    print(f"✓ Test pozisyonu: {test_pos}")
    
    # Test bölgesi oluştur (fare pozisyonunun etrafında)
    test_region = (
        test_pos[0] - 50,
        test_pos[1] - 20,
        test_pos[0] + 50,
        test_pos[1] + 20
    )
    
    print(f"✓ Test bölgesi: {test_region}")
    print("\n🖱️  2 saniye sonra tıklama testi başlayacak...")
    time.sleep(2)
    
    # Test et
    success = clicker.click_button(test_region)
    
    if success:
        print("\n✅ Test başarılı!")
    else:
        print("\n❌ Test başarısız!")
