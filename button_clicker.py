"""
BUTON TIKLAYICI MODÜL
OCR sonucuna göre doğru butona fareyle tıklar
"""

import pyautogui
import time
import logging

logger = logging.getLogger('ButtonClicker')


class ButtonClicker:
    """Fareyi kontrol ederek butona tıklayan sınıf"""
    
    def __init__(self):
        # Güvenlik
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3
        
        logger.info("ButtonClicker hazır")
    
    
    def click_button(self, button_region, window_handle=None):
        """
        Belirtilen bölgenin ortasına fareyle tıklar
        
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
            
            logger.info(f"🎯 Hedef konum: ({center_x}, {center_y})")
            
            # Pencere handle varsa, pencere koordinatlarını ekran koordinatlarına çevir
            if window_handle:
                try:
                    import win32gui
                    # Pencere pozisyonunu al
                    rect = win32gui.GetWindowRect(window_handle)
                    window_x, window_y = rect[0], rect[1]
                    
                    # Ekran koordinatlarına çevir
                    screen_x = window_x + center_x
                    screen_y = window_y + center_y
                    
                    logger.info(f"📍 Pencere offset: ({window_x}, {window_y})")
                    logger.info(f"🖥️  Ekran koordinatı: ({screen_x}, {screen_y})")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Pencere koordinatları alınamadı: {e}")
                    # Pencere koordinatı alınamazsa direkt bölge koordinatını kullan
                    screen_x, screen_y = center_x, center_y
            else:
                # Pencere handle yoksa direkt koordinat kullan
                screen_x, screen_y = center_x, center_y
            
            # Fareyi yavaşça hedefe götür
            logger.info("🖱️  Fare hareket ediyor...")
            pyautogui.moveTo(screen_x, screen_y, duration=0.5)
            
            # Kısa bekle
            time.sleep(0.2)
            
            # Tıkla
            logger.info("👆 Tıklama yapılıyor...")
            pyautogui.click()
            
            logger.info("✅ Tıklama başarılı!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Tıklama hatası: {e}", exc_info=True)
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
            
            logger.info("=" * 60)
            logger.info(f"🔍 DOĞRU BUTON ARANYOR")
            logger.info(f"   Ana sayı: {main_number}")
            logger.info(f"   Butonlar: {button_numbers}")
            
            # İLK 4 RAKAM İLE EŞLEŞTİR
            if len(main_number) >= 4:
                main_first_4 = main_number[:4]
                logger.info(f"   Ana sayının ilk 4 rakamı: {main_first_4}")
                
                for i, btn_num in enumerate(button_numbers):
                    if btn_num and len(btn_num) >= 4:
                        btn_first_4 = btn_num[:4]
                        logger.info(f"   Buton {i+1}: {btn_num[:4]} {'✅ EŞLEŞTİ' if btn_first_4 == main_first_4 else '❌'}")
                        
                        if btn_first_4 == main_first_4:
                            logger.info(f"\n✅ DOĞRU BUTON BULUNDU: Buton {i+1}")
                            logger.info(f"   Koordinat: {button_regions[i]}")
                            
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
            for i, btn_num in enumerate(button_numbers):
                if btn_num == main_number:
                    logger.info(f"\n✅ TAM EŞLEŞME BULUNDU: Buton {i+1}")
                    logger.info(f"   Koordinat: {button_regions[i]}")
                    
                    # TIKLA
                    success = self.click_button(button_regions[i], window_handle)
                    
                    if success:
                        logger.info("🎉 TIKLAMA BAŞARILI!")
                        return True, i + 1
                    else:
                        logger.error("❌ Tıklama başarısız!")
                        return False, i + 1
            
            logger.warning("❌ Eşleşen buton bulunamadı!")
            logger.info("=" * 60)
            return False, None
            
        except Exception as e:
            logger.error(f"❌ Buton tıklama hatası: {e}", exc_info=True)
            return False, None


def test_clicker():
    """Test fonksiyonu"""
    print("\n" + "=" * 60)
    print("BUTON TIKLAYICI TEST")
    print("=" * 60)
    
    clicker = ButtonClicker()
    
    # Test verileri
    main_number = "123456"
    button_numbers = ["234567", "123456", "345678", "456789"]
    button_regions = [
        (100, 200, 300, 240),  # Buton 1
        (100, 260, 300, 300),  # Buton 2 - DOĞRU
        (100, 320, 300, 360),  # Buton 3
        (100, 380, 300, 420),  # Buton 4
    ]
    
    success, button_idx = clicker.click_correct_button(
        main_number, 
        button_numbers, 
        button_regions
    )
    
    if success:
        print(f"\n✅ Test başarılı! Buton {button_idx} tıklandı.")
    else:
        print(f"\n❌ Test başarısız!")


if __name__ == "__main__":
    # Logging ayarla
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    test_clicker()