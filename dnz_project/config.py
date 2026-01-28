"""
DNZ (Dinamik Nesne Zamanlayıcı) - Yapılandırma Modülü
Tüm sabitler ve ayarlar bu dosyada tanımlanır.
"""

# Uygulama Bilgileri
APP_NAME = "DNZ Assistant"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Dinamik Nesne Zamanlayıcı - Profesyonel Otomasyon Asistanı"

# Zamanlama Ayarları (saniye)
MIN_DELAY = 4
MAX_DELAY = 14

# Bellek Tarama Ayarları
SCAN_INTERVAL = 0.5  # Saniye cinsinden tarama sıklığı
MAX_SCAN_ATTEMPTS = 100

# AOB İmzaları (Array of Bytes)
# Bu imzalar AUTOBAN_QUIZ_ANSWER değişkenini bulmak için kullanılır
AOB_PATTERNS = [
    b"\x00\x00\x00\x00\x00\x00\x00\x00",  # 8 byte sıfır pattern
    b"\xFF\xFF\xFF\xFF",  # Varsayılan pattern
]

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

# Hedef Oyun Pencere İsimleri
TARGET_WINDOW_NAMES = [
    "valen2client",
    "Valen2",
    "VALEN2"
]