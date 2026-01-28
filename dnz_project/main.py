"""
DNZ (Dinamik Nesne Zamanlayıcı) - Ana Program
Profesyonel Otomasyon Asistanı

Kullanım:
    python main.py

Gereksinimler:
    - Python 3.7+
    - Windows işletim sistemi
    - Yönetici yetkileri (önerilir)
"""

import sys
import os
import ctypes

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from gui import DNZInterface


def check_platform():
    """Platform kontrolü - sadece Windows desteklenir"""
    if sys.platform != "win32":
        print("HATA: DNZ sadece Windows işletim sisteminde çalışır!")
        sys.exit(1)


def check_admin():
    """Yönetici yetkisi kontrolü"""
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        return is_admin != 0
    except Exception:
        return False


def request_admin():
    """Yönetici yetkisi ister"""
    if not check_admin():
        print("UYARI: Yönetici yetkileri olmadan çalışıyor!")
        print("Daha iyi performans için uygulamayı yönetici olarak çalıştırın.\n")
        return False
    return True


def main():
    """Ana giriş fonksiyonu"""
    
    # Banner
    print("=" * 60)
    print(f"  {config.APP_NAME} v{config.APP_VERSION}")
    print(f"  {config.APP_DESCRIPTION}")
    print("=" * 60)
    print()
    
    # Platform kontrolü
    check_platform()
    
    # Yönetici kontrolü
    is_admin = request_admin()
    if is_admin:
        print("✓ Yönetici yetkileriyle çalışıyor")
    
    print("✓ Sistem kontrolleri tamamlandı")
    print(f"✓ Log dosyası: {config.LOG_FILE}")
    print()
    print("Arayüz başlatılıyor...")
    print("=" * 60)
    print()
    
    # GUI'yi başlat
    try:
        app = DNZInterface()
        app.run()
    except KeyboardInterrupt:
        print("\n\nProgram kullanıcı tarafından sonlandırıldı.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nKRİTİK HATA: {str(e)}")
        input("\nDevam etmek için Enter tuşuna basın...")
        sys.exit(1)


if __name__ == "__main__":
    main()