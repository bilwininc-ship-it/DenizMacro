import pyautogui
import time

# Güvenlik özelliği: Fareyi ekranın sol üst köşesine hızlıca hareket ettirerek programı durdurabilirsin
pyautogui.FAILSAFE = True

def ana_ekranda_sag_tik():
    """
    Ana ekranın ortasında sağ tık yapar
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