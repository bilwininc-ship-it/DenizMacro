"""
DNZ (Dinamik Nesne Zamanlayıcı) - Yapılandırma Modülü
Tüm teknik sabitler ve oyun-spesifik ayarlar burada tanımlanır.
"""

# Uygulama Bilgileri
APP_NAME = "DNZ Assistant"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Dinamik Nesne Zamanlayıcı - Profesyonel Otomasyon Asistanı"

# Zamanlama Ayarları (saniye) - İnsan simülasyonu için kritik
MIN_DELAY = 4
MAX_DELAY = 14

# Bellek Tarama Ayarları
SCAN_INTERVAL = 0.5  # Saniye cinsinden tarama sıklığı
MAX_SCAN_ATTEMPTS = 500 # Daha uzun süre denemesi için artırıldı

# --- KRİTİK OYUN ANALİZ AYARLARI ---
# Valen2 Python 2.7.3 yapısı (L:\work\Python-2.7.3)

# Bellekteki AUTOBAN_QUIZ_ANSWER değişkenini bulmak için imza (Array of Bytes)
# Bu imza, Python 2.7 string objelerinin RAM'deki yerleşimini yakalar.
AOB_PATTERNS = [
    b"\x06\x00\x00\x00.{16}\x00\x00\x00\x00", # 6 haneli string objesi pattern'i
]

# Python 2.7 string objesi başlık boyutu
PY27_STRING_HEADER_SIZE = 16 

# String objesi içinde uzunluk bilgisinin bulunduğu yer (offset)
PY27_STRING_SIZE_OFFSET = 12

# Hedef Oyun Pencere İsimleri
TARGET_WINDOW_NAMES = [
    "Valen2 | www.valen2.com",
    "valen2client",
    "Valen2",
    "VALEN2"
]
# ----------------------------------

# GUI Ayarları
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
THEME = "dark-blue"

# Log Ayarları
LOG_FILE = "dnz_logs.txt"
MAX_LOG_LINES = 1000

# Renk Kodları
COLOR_SUCCESS = "#00ff00"
COLOR_WARNING = "#ffaa00"
COLOR_ERROR = "#ff0000"
COLOR_INFO = "#00aaff"

# Durum Mesajları
STATUS_WAITING = "Bekleniyor..."
STATUS_ACTIVE = "Aktif - Sistem Çalışıyor"
STATUS_PROCESSING = "İşlem Yapılıyor..."
STATUS_PAUSED = "Duraklatıldı"