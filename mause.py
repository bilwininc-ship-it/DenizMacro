import pyautogui
import time
import win32gui
import win32con

# Güvenlik özelliği: Fareyi ekranın sol üst köşesine hızlıca hareket ettirerek programı durdurabilirsin
pyautogui.FAILSAFE = False  # Otomasyon için devre dışı


def butona_gercek_tiklama(window_handle, button_region, button_number):
    """
    Belirlenen butona GERÇEK fare hareketi ile tıklama yapar
    
    Args:
        window_handle: Pencere handle'ı (win32gui)
        button_region: Buton bölgesi (x1, y1, x2, y2) - lokal koordinatlar
        button_number: Buton numarası (1-4)
    
    Returns:
        bool: Başarılı ise True, değilse False
    """
    try:
        x1, y1, x2, y2 = button_region
        
        # Butonun merkezini hesapla (LOKAL KOORDİNATLAR)
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        print(f"\n🖱️  MAUSE.PY - Buton {button_number}'e GERÇEKten tıklanacak!")
        print(f"   Buton bölgesi (lokal): ({x1}, {y1}, {x2}, {y2})")
        print(f"   Buton merkezi (lokal): ({center_x}, {center_y})")
        
        # Pencereyi aktif et
        try:
            win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)
            time.sleep(0.15)
            win32gui.SetForegroundWindow(window_handle)
            time.sleep(0.25)
            print("   ✓ Pencere aktif edildi")
        except Exception as focus_error:
            print(f"   ⚠️ Pencere odaklama hatası: {focus_error}")
        
        # CLIENT AREA koordinatlarını al (global koordinat için)
        try:
            client_to_screen = win32gui.ClientToScreen(window_handle, (0, 0))
            
            # Global koordinatlara çevir
            global_x = client_to_screen[0] + center_x
            global_y = client_to_screen[1] + center_y
            
            print(f"   Client area offset: {client_to_screen}")
            print(f"   Global koordinat: ({global_x}, {global_y})")
            
        except Exception as coord_error:
            print(f"   ⚠️ Koordinat hesaplama hatası: {coord_error}")
            # Yedek yöntem: GetWindowRect
            left, top, _, _ = win32gui.GetWindowRect(window_handle)
            global_x = left + center_x
            global_y = top + center_y
            print(f"   Yedek koordinat kullanılıyor: ({global_x}, {global_y})")
        
        # Eski fare pozisyonunu kaydet
        old_x, old_y = pyautogui.position()
        print(f"   Eski fare pozisyonu: ({old_x}, {old_y})")
        
        # GERÇEK FARE HAREKETİ - Yavaş ve insansı hareket
        print(f"\n   🐭 Fare hedefe hareket ediyor: ({global_x}, {global_y})")
        pyautogui.moveTo(global_x, global_y, duration=0.5, tween=pyautogui.easeInOutQuad)
        time.sleep(0.15)
        
        # Fare pozisyonunu doğrula
        actual_x, actual_y = pyautogui.position()
        print(f"   Gerçek fare pozisyonu: ({actual_x}, {actual_y})")
        
        if abs(actual_x - global_x) > 5 or abs(actual_y - global_y) > 5:
            print(f"   ⚠️ Fare hedeften uzakta! Tekrar deneniyor...")
            # Tekrar deneme
            pyautogui.moveTo(global_x, global_y, duration=0.2)
            time.sleep(0.1)
        
        # GERÇEK TIKLAMA - PyAutoGUI ile
        print(f"\n   👆 SOL TIKLAMA yapılıyor...")
        pyautogui.click(clicks=1, interval=0.1, button='left')
        time.sleep(0.2)
        
        print(f"\n✅ BAŞARILI! Buton {button_number}'e GERÇEKten tıklandı!")
        print(f"   Koordinat: ({global_x}, {global_y})")
        
        # Fareyi eski pozisyona yavaşça geri al (opsiyonel)
        time.sleep(0.25)
        pyautogui.moveTo(old_x, old_y, duration=0.4, tween=pyautogui.easeInOutQuad)
        print(f"   Fare eski pozisyona döndü: ({old_x}, {old_y})")
        
        return True
        
    except Exception as e:
        print(f"\n❌ MAUSE.PY HATA: {e}")
        import traceback
        traceback.print_exc()
        return False


def ana_ekranda_sag_tik():
    """
    Ana ekranın ortasında sağ tık yapar (TEST AMAÇLI)
    """
    # Ekran çözünürlüğünü al
    ekran_genislik, ekran_yukseklik = pyautogui.size()
    
    print(f"Ekran çözünürlüğü: {ekran_genislik}x{ekran_yukseklik}")
    
    # Ekranın ortasını hesapla
    orta_x = ekran_genislik // 2
    orta_y = ekran_yukseklik // 2
    
    print(f"Fare {orta_x}, {orta_y} konumuna gidecek...")
    
    # Fareyi ekranın ortasına getir
    pyautogui.moveTo(orta_x, orta_y, duration=1)
    
    # 1 saniye bekle
    time.sleep(1)
    
    # Sağ tık yap
    print("Sağ tık yapılıyor...")
    pyautogui.rightClick()
    
    print("İşlem tamamlandı!")


if __name__ == "__main__":
    print("Program 3 saniye içinde başlayacak...")
    print("İptal etmek için fareyi ekranın sol üst köşesine götür!")
    time.sleep(3)
    
    ana_ekranda_sag_tik()