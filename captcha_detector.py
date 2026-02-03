import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import time
import os
import json
from datetime import datetime
import win32gui
import win32ui
import win32con
import win32api
from ctypes import windll
import logging
import pyautogui  # Gerçek fare hareketi için

# OCR kütüphaneleri
try:
    import pytesseract
    # Tesseract yolunu ayarla
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    OCR_AVAILABLE = True
    print("✅ Tesseract OCR yüklendi!")
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ pytesseract yüklü değil. OCR çalışmayacak.")
except Exception as e:
    OCR_AVAILABLE = False
    print(f"⚠️ Tesseract OCR hatası: {e}")


# Logger Kurulumu
def setup_logger():
    """Detaylı log sistemi"""
    logger = logging.getLogger('CaptchaDetector')
    logger.setLevel(logging.DEBUG)
    
    # Dosya handler
    log_file = os.path.join(os.getcwd(), 'captcha_detector_logs.txt')
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
    file_handler.setLevel(logging.DEBUG)
    
    # Konsol handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()
logger.info("="*70)
logger.info("CAPTCHA DEDEKTÖR PRO v6.1 BAŞLATILDI (DÜZELTİLMİŞ)")
logger.info("="*70)


class CaptchaDetectorPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Captcha Dedektör Pro v6.1")
        self.root.geometry("520x750")
        self.root.resizable(False, False)
        
        logger.info("Uygulama başlatılıyor...")
        
        # DPI Awareness
        try:
            windll.shcore.SetProcessDpiAwareness(1)
            logger.debug("DPI Awareness aktif edildi")
        except:
            logger.warning("DPI Awareness ayarlanamadı")
        
        # Değişkenler
        self.is_running = False
        self.window_handle = None
        self.window_name = None
        self.capture_count = 0
        self.check_interval = 1.0
        self.save_folder = os.path.join(os.getcwd(), "captcha_captures")
        
        logger.info(f"Kayıt klasörü: {self.save_folder}")
        
        # Captcha bölgesi ve şablon
        self.captcha_region = None
        self.template_image = None
        self.last_detection_time = 0
        self.detection_cooldown = 300  # 5 dakika = 300 saniye
        self.last_saved_image_path = None  # Son kaydedilen resmin yolu
        
        # 4 BUTON KOORDİNATLARI (YENİ)
        self.button_regions = []  # [(x1, y1, x2, y2), ...] 4 buton
        
        # Benzerlik eşiği
        self.similarity_threshold = 0.50  # %50'ye düşürüldü
        
        # Kalıcı ayar dosyası
        self.config_file = os.path.join(os.getcwd(), "captcha_config_pro.json")
        logger.info(f"Config dosyası: {self.config_file}")
        
        # Pencere kapatılma kontrolü için
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5  # 5 hatadan sonra durdur
        
        # Klasör oluştur (GÜVENLİ YÖNTEM)
        try:
            os.makedirs(self.save_folder, exist_ok=True)
            logger.info(f"✓ Kayıt klasörü hazır: {self.save_folder}")
        except Exception as e:
            logger.error(f"✗ Klasör oluşturma hatası: {e}")
            messagebox.showerror("Hata", f"Kayıt klasörü oluşturulamadı:\n{e}")
        
        # Ayarları yükle
        self.load_config()
        
        # UI Oluştur
        self.setup_ui()
        
        # Yüklenen ayarlara göre UI'ı güncelle
        self.update_ui_on_load()
    
    
    def load_config(self):
        """Kaydedilmiş ayarları yükle"""
        logger.info("Ayarlar yükleniyor...")
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if 'captcha_region' in data and data['captcha_region']:
                        self.captcha_region = tuple(data['captcha_region'])
                        logger.info(f"✓ Captcha bölgesi yüklendi: {self.captcha_region}")
                    
                    if 'capture_count' in data:
                        self.capture_count = data['capture_count']
                        logger.info(f"✓ Yakalama sayacı: {self.capture_count}")
                    
                    if 'check_interval' in data:
                        self.check_interval = data['check_interval']
                        logger.info(f"✓ Kontrol sıklığı: {self.check_interval}s")
                    
                    if 'similarity_threshold' in data:
                        self.similarity_threshold = data['similarity_threshold']
                        logger.info(f"✓ Benzerlik eşiği: {self.similarity_threshold:.0%}")
                    
                    # BUTON KOORDİNATLARINI YÜKLE (YENİ)
                    if 'button_regions' in data and data['button_regions']:
                        self.button_regions = [tuple(btn) for btn in data['button_regions']]
                        logger.info(f"✓ {len(self.button_regions)} buton koordinatı yüklendi")
                        for i, btn in enumerate(self.button_regions, 1):
                            logger.debug(f"  Buton {i}: {btn}")
                    
                    # Şablon görüntüsünü yükle
                    if 'template_path' in data and data['template_path']:
                        if os.path.exists(data['template_path']):
                            self.template_image = cv2.imread(data['template_path'])
                            if self.template_image is not None:
                                logger.info(f"✓ Şablon görüntü yüklendi: {data['template_path']}")
                                logger.debug(f"  Şablon boyutu: {self.template_image.shape}")
                            else:
                                logger.error(f"✗ Şablon görüntü okunamadı: {data['template_path']}")
                        else:
                            logger.warning(f"⚠ Şablon dosyası bulunamadı: {data['template_path']}")
                    
                    logger.info("✓ Tüm ayarlar başarıyla yüklendi!")
            else:
                logger.info("Config dosyası bulunamadı - ilk kullanım")
                    
        except Exception as e:
            logger.error(f"✗ Ayar yükleme hatası: {e}", exc_info=True)
    
    
    def save_config(self):
        """Ayarları kaydet"""
        logger.info("Ayarlar kaydediliyor...")
        try:
            # Klasörün varlığını garantile
            os.makedirs(self.save_folder, exist_ok=True)
            
            # Şablon görüntüsünü kaydet
            template_path = None
            if self.template_image is not None:
                template_path = os.path.join(self.save_folder, "captcha_template.png")
                cv2.imwrite(template_path, self.template_image)
                logger.debug(f"Şablon görüntü kaydedildi: {template_path}")
            
            data = {
                'captcha_region': list(self.captcha_region) if self.captcha_region else None,
                'template_path': template_path,
                'capture_count': self.capture_count,
                'check_interval': self.check_interval,
                'similarity_threshold': self.similarity_threshold,
                'button_regions': [list(btn) for btn in self.button_regions] if self.button_regions else [],
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Ayarlar kaydedildi: {self.config_file}")
            
        except Exception as e:
            logger.error(f"✗ Ayar kaydetme hatası: {e}", exc_info=True)
    
    
    def setup_ui(self):
        """UI Bileşenlerini Oluştur"""
        
        # Başlık
        header = tk.Frame(self.root, bg="#2196F3", height=50)
        header.pack(fill="x")
        
        title = tk.Label(header, text="🎯 CAPTCHA DEDEKTÖR PRO", 
                        bg="#2196F3", fg="white", 
                        font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Durum Paneli
        status_frame = tk.LabelFrame(self.root, text="📊 Durum", 
                                     padx=10, pady=8, font=("Arial", 9, "bold"))
        status_frame.pack(fill="x", padx=10, pady=8)
        
        self.status_label = tk.Label(status_frame, text="⏸ Hazır", 
                                     font=("Arial", 10, "bold"), fg="#2196F3")
        self.status_label.pack(anchor="w")
        
        self.window_label = tk.Label(status_frame, text="🪟 Oyun Penceresi: ❌ Seçilmedi",
                                     font=("Arial", 9))
        self.window_label.pack(anchor="w")
        
        self.region_label = tk.Label(status_frame, text="📍 Captcha Bölgesi: ❌ Belirtilmedi",
                                     font=("Arial", 9))
        self.region_label.pack(anchor="w")
        
        self.button_label = tk.Label(status_frame, text="🎯 Butonlar: ❌ Seçilmedi (0/4)",
                                     font=("Arial", 9))
        self.button_label.pack(anchor="w")
        
        self.count_label = tk.Label(status_frame, text=f"📸 Yakalanan: {self.capture_count}",
                                   font=("Arial", 9, "bold"))
        self.count_label.pack(anchor="w")
        
        # Ayarlar Paneli
        settings_frame = tk.LabelFrame(self.root, text="⚙️ Ayarlar",
                                       padx=10, pady=8, font=("Arial", 9, "bold"))
        settings_frame.pack(fill="x", padx=10, pady=8)
        
        # Kontrol sıklığı
        interval_frame = tk.Frame(settings_frame)
        interval_frame.pack(fill="x", pady=3)
        
        tk.Label(interval_frame, text="⏱️ Kontrol Sıklığı:",
                font=("Arial", 9)).pack(side="left")
        
        self.interval_var = tk.DoubleVar(value=self.check_interval)
        interval_slider = ttk.Scale(interval_frame, from_=0.5, to=5.0,
                                   variable=self.interval_var,
                                   orient="horizontal", length=200,
                                   command=self.update_interval)
        interval_slider.pack(side="left", padx=10)
        
        self.interval_label = tk.Label(interval_frame, text=f"{self.check_interval}s",
                                      font=("Arial", 9, "bold"))
        self.interval_label.pack(side="left")
        
        # Benzerlik eşiği
        similarity_frame = tk.Frame(settings_frame)
        similarity_frame.pack(fill="x", pady=3)
        
        tk.Label(similarity_frame, text="🎯 Benzerlik Eşiği:",
                font=("Arial", 9)).pack(side="left")
        
        self.similarity_var = tk.DoubleVar(value=self.similarity_threshold)
        similarity_slider = ttk.Scale(similarity_frame, from_=0.3, to=0.95,
                                     variable=self.similarity_var,
                                     orient="horizontal", length=200,
                                     command=self.update_similarity)
        similarity_slider.pack(side="left", padx=10)
        
        self.similarity_label = tk.Label(similarity_frame, text=f"{self.similarity_threshold:.0%}",
                                        font=("Arial", 9, "bold"))
        self.similarity_label.pack(side="left")
        
        # Butonlar
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        # Pencere seç
        self.btn_window = tk.Button(btn_frame, text="🪟 Oyun Penceresi Seç",
                                    command=self.select_window,
                                    bg="#4CAF50", fg="white",
                                    font=("Arial", 10, "bold"),
                                    padx=10, pady=8)
        self.btn_window.pack(fill="x", pady=3)
        
        # Captcha bölgesi seç
        self.btn_region = tk.Button(btn_frame, text="📍 Captcha Bölgesi Seç",
                                    command=self.select_captcha_region,
                                    bg="#2196F3", fg="white",
                                    font=("Arial", 10, "bold"),
                                    padx=10, pady=8,
                                    state="disabled")
        self.btn_region.pack(fill="x", pady=3)
        
        # Buton bölgelerini seç (YENİ)
        self.btn_buttons = tk.Button(btn_frame, text="🎯 4 Buton Bölgesi Seç",
                                     command=self.select_button_regions,
                                     bg="#9C27B0", fg="white",
                                     font=("Arial", 10, "bold"),
                                     padx=10, pady=8,
                                     state="disabled")
        self.btn_buttons.pack(fill="x", pady=3)
        
        # Test butonu
        self.btn_test = tk.Button(btn_frame, text="🧪 Test Et",
                                 command=self.test_detection,
                                 bg="#FF9800", fg="white",
                                 font=("Arial", 10, "bold"),
                                 padx=10, pady=8,
                                 state="disabled")
        self.btn_test.pack(fill="x", pady=3)
        
        # Başlat/Durdur
        self.btn_toggle = tk.Button(btn_frame, text="▶️ BAŞLAT",
                                    command=self.toggle_monitoring,
                                    bg="#4CAF50", fg="white",
                                    font=("Arial", 11, "bold"),
                                    padx=15, pady=12,
                                    state="disabled")
        self.btn_toggle.pack(fill="x", pady=5)
        
        # Sıfırla butonu
        self.btn_reset = tk.Button(btn_frame, text="🔄 Sıfırla",
                                   command=self.reset_region,
                                   bg="#F44336", fg="white",
                                   font=("Arial", 9),
                                   padx=10, pady=5)
        self.btn_reset.pack(fill="x", pady=3)
        
        # Önizleme
        preview_frame = tk.LabelFrame(self.root, text="👁️ Önizleme",
                                      padx=5, pady=5, font=("Arial", 9, "bold"))
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.preview_label = tk.Label(preview_frame, text="Henüz görüntü yok",
                                      bg="#f0f0f0", width=60, height=12)
        self.preview_label.pack(fill="both", expand=True)
        
        logger.info("UI başarıyla oluşturuldu")
    
    
    def update_ui_on_load(self):
        """Yüklenen ayarlara göre UI'ı güncelle"""
        # Captcha bölgesi kontrolü
        if self.captcha_region:
            x1, y1, x2, y2 = self.captcha_region
            self.region_label.config(text=f"📍 Captcha Bölgesi: ✓ ({x2-x1}x{y2-y1})")
            
            # Şablon varsa önizleme göster
            if self.template_image is not None:
                self.show_preview(self.template_image, "Yüklenen Şablon")
        
        # Buton kontrolü
        if self.button_regions and len(self.button_regions) == 4:
            self.button_label.config(text=f"🎯 Butonlar: ✅ Seçildi (4/4)")
            logger.info("✓ Buton koordinatları yüklendi ve UI güncellendi")
        
        # Test ve başlat butonlarını aktif et
        if self.captcha_region and self.template_image is not None:
            self.btn_test.config(state="normal")
            if len(self.button_regions) == 4:
                self.btn_toggle.config(state="normal")
    
    
    def update_interval(self, value):
        """Kontrol sıklığını güncelle"""
        self.check_interval = float(value)
        self.interval_label.config(text=f"{self.check_interval:.1f}s")
    
    
    def update_similarity(self, value):
        """Benzerlik eşiğini güncelle"""
        self.similarity_threshold = float(value)
        self.similarity_label.config(text=f"{self.similarity_threshold:.0%}")
    
    
    def select_window(self):
        """Oyun penceresini seç"""
        logger.info("Oyun penceresi seçimi başlatıldı")
        
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows.append((hwnd, title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if not windows:
            messagebox.showerror("Hata", "Hiç pencere bulunamadı!")
            return
        
        # Pencere seçim dialogu
        dialog = tk.Toplevel(self.root)
        dialog.title("Pencere Seç")
        dialog.geometry("450x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="🪟 Bir pencere seçin:",
                font=("Arial", 11, "bold")).pack(pady=10)
        
        listbox = tk.Listbox(dialog, font=("Arial", 9), height=15)
        listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(listbox)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        
        for hwnd, title in windows:
            listbox.insert(tk.END, f"{title}")
        
        selected_window = [None]
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                selected_window[0] = windows[idx]
                dialog.destroy()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(btn_frame, text="✓ Seç", command=on_select,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                 padx=20, pady=5).pack(side="left", expand=True, fill="x", padx=5)
        
        tk.Button(btn_frame, text="✗ İptal", command=dialog.destroy,
                 bg="#F44336", fg="white", font=("Arial", 10, "bold"),
                 padx=20, pady=5).pack(side="left", expand=True, fill="x", padx=5)
        
        listbox.bind('<Double-Button-1>', lambda e: on_select())
        
        dialog.wait_window()
        
        if selected_window[0]:
            self.window_handle, self.window_name = selected_window[0]
            self.window_label.config(text=f"🪟 Oyun Penceresi: ✓ {self.window_name}")
            self.btn_region.config(state="normal")
            self.btn_buttons.config(state="normal")
            logger.info(f"✓ Oyun penceresi seçildi: {self.window_name}")
    
    
    def capture_window(self, hwnd):
        """Pencereyi yakala - İyileştirilmiş Versiyon (Siyah Ekran Düzeltmesi)"""
        try:
            # Önce pencere geçerliliğini kontrol et
            if not win32gui.IsWindow(hwnd):
                logger.error("Pencere artık geçerli değil")
                return None
            
            # Pencere minimize mi kontrol et
            try:
                if win32gui.IsIconic(hwnd):
                    logger.info("Pencere minimize, geri yükleniyor...")
                    win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
                    time.sleep(0.5)
            except:
                pass
            
            # Pencereyi öne getir ve aktif et - GÜÇLENDİRİLMİŞ
            try:
                win32gui.ShowWindow(hwnd, 5)  # SW_SHOW
                time.sleep(0.2)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.3)  # Daha uzun bekleme
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.2)
                logger.debug("Pencere aktif edildi")
            except Exception as fg_error:
                logger.warning(f"Pencere öne getirilemedi: {fg_error}")
            
            # Pencere rect
            try:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            except Exception as rect_error:
                logger.error(f"GetWindowRect hatası: {rect_error}")
                return None
                
            width = right - left
            height = bottom - top
            
            logger.debug(f"Pencere boyutu: {width}x{height}")
            
            if width <= 0 or height <= 0:
                logger.error(f"Geçersiz pencere boyutu: {width}x{height}")
                return None
            
            # YÖNTEM 1: PrintWindow (Ana yöntem) - GELİŞTİRİLMİŞ
            try:
                # DC oluştur
                hwndDC = win32gui.GetWindowDC(hwnd)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                
                # Bitmap
                saveBitMap = win32ui.CreateBitmap()
                saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
                saveDC.SelectObject(saveBitMap)
                
                # Render için ekstra bekleme
                time.sleep(0.1)
                
                # PrintWindow - Tüm bayrakları sırayla dene
                # 0x00000002 = PW_RENDERFULLCONTENT
                # 0x00000000 = PW_CLIENTONLY
                # 0x00000003 = Her ikisi
                flags_to_try = [0x00000002, 0x00000003, 0x00000000, 0x00000001]
                result = 0
                
                for flag in flags_to_try:
                    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), flag)
                    if result != 0:
                        logger.debug(f"PrintWindow başarılı (bayrak: {flag})")
                        break
                    time.sleep(0.05)
                
                # Numpy array'e çevir
                bmpstr = saveBitMap.GetBitmapBits(True)
                img = np.frombuffer(bmpstr, dtype=np.uint8)
                
                if len(img) != width * height * 4:
                    logger.error(f"Boyut uyumsuzluğu: beklenen={width*height*4}, alınan={len(img)}")
                    raise Exception("Bitmap boyutu uyumsuz")
                
                img.shape = (height, width, 4)
                
                # Temizlik
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                
                # BGR'ye çevir
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Siyah ekran kontrolü - ESNEK
                mean_brightness = np.mean(img)
                logger.debug(f"Görüntü parlaklık ortalaması: {mean_brightness:.2f}")
                
                if mean_brightness < 1:
                    logger.warning("Görüntü tamamen siyah, alternatif yöntem deneniyor...")
                    raise Exception("Siyah ekran")
                
                logger.debug("✓ PrintWindow ile yakalama başarılı")
                self.consecutive_errors = 0
                return img
                
            except Exception as e1:
                logger.warning(f"PrintWindow hatası: {e1}, BitBlt deneniyor...")
                
                # YÖNTEM 2: BitBlt (Alternatif) - GELİŞTİRİLMİŞ
                try:
                    # DC'leri yeniden oluştur
                    hwndDC = win32gui.GetWindowDC(hwnd)
                    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                    saveDC = mfcDC.CreateCompatibleDC()
                    
                    saveBitMap = win32ui.CreateBitmap()
                    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
                    saveDC.SelectObject(saveBitMap)
                    
                    # Pencereyi tekrar aktif et
                    try:
                        win32gui.SetForegroundWindow(hwnd)
                        time.sleep(0.2)
                    except:
                        pass
                    
                    # BitBlt
                    result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
                    
                    if result == 0:
                        logger.warning("BitBlt başarısız")
                    
                    # Numpy array'e çevir
                    bmpstr = saveBitMap.GetBitmapBits(True)
                    img = np.frombuffer(bmpstr, dtype=np.uint8)
                    img.shape = (height, width, 4)
                    
                    # Temizlik
                    win32gui.DeleteObject(saveBitMap.GetHandle())
                    saveDC.DeleteDC()
                    mfcDC.DeleteDC()
                    win32gui.ReleaseDC(hwnd, hwndDC)
                    
                    # BGR'ye çevir
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    
                    # Siyah ekran kontrolü
                    mean_brightness = np.mean(img)
                    logger.debug(f"BitBlt - Parlaklık ortalaması: {mean_brightness:.2f}")
                    
                    if mean_brightness < 1:
                        logger.error("BitBlt de siyah ekran verdi")
                        raise Exception("Siyah ekran - BitBlt")
                    
                    logger.debug("✓ BitBlt ile yakalama başarılı")
                    self.consecutive_errors = 0
                    return img
                    
                except Exception as e2:
                    logger.error(f"BitBlt da başarısız: {e2}")
                    raise e2
            
        except Exception as e:
            logger.error(f"Tüm yakalama yöntemleri başarısız: {e}")
            self.consecutive_errors += 1
            return None    
    def select_captcha_region(self):
        """Captcha bölgesini seç"""
        if not self.window_handle:
            messagebox.showerror("Hata", "Önce oyun penceresini seçin!")
            return
        
        logger.info("Captcha bölgesi seçimi başlatıldı")
        
        # Pencere hala geçerli mi kontrol et
        try:
            if not win32gui.IsWindow(self.window_handle):
                logger.error("Seçili pencere artık mevcut değil")
                messagebox.showerror("Hata", 
                    "Seçili pencere artık mevcut değil!\n"
                    "Lütfen oyun penceresini yeniden seçin.")
                self.window_handle = None
                self.window_name = None
                self.window_label.config(text="🪟 Oyun Penceresi: ❌ Seçilmedi")
                return
        except Exception as e:
            logger.error(f"Pencere kontrolü hatası: {e}")
            messagebox.showerror("Hata", 
                "Pencere kontrol edilemedi!\n"
                "Lütfen oyun penceresini yeniden seçin.")
            return
        
        # Pencereyi öne getir
        try:
            win32gui.ShowWindow(self.window_handle, 9)  # SW_RESTORE
            time.sleep(0.2)
            win32gui.SetForegroundWindow(self.window_handle)
            logger.info("Pencere öne getirildi")
            time.sleep(0.5)  # Render için bekle
        except Exception as fg_error:
            logger.warning(f"Pencere öne getirilemedi: {fg_error}")
        
        # Pencere görüntüsünü al
        logger.info("Pencere görüntüsü alınıyor...")
        img = self.capture_window(self.window_handle)
        
        if img is None:
            logger.error("Pencere görüntüsü alınamadı")
            messagebox.showerror("Hata", 
                "❌ Pencere görüntüsü alınamadı!\n\n"
                "Çözümler:\n"
                "1. Oyunu NORMAL pencere modunda açın (tam ekran değil)\n"
                "2. Oyunu ve bu programı yönetici olarak çalıştırın\n"
                "3. Oyun penceresinin görünür olduğundan emin olun\n"
                "4. Pencereyi yeniden seçmeyi deneyin")
            return
        
        logger.info(f"✓ Görüntü başarıyla alındı: {img.shape}")
        
        # Bölge seç
        selector = RegionSelector(img, "Captcha bölgesini fare ile seçin")
        self.root.wait_window(selector.top)
        
        if selector.region:
            x1, y1, x2, y2 = selector.region
            
            # Captcha şablonunu kaydet
            self.captcha_region = selector.region
            self.template_image = img[y1:y2, x1:x2].copy()
            
            logger.info(f"✓ Captcha bölgesi seçildi: ({x1}, {y1}) → ({x2}, {y2})")
            logger.debug(f"  Şablon boyutu: {self.template_image.shape}")
            
            # Ayarları kaydet
            self.save_config()
            
            # UI güncelle
            self.region_label.config(text=f"📍 Captcha Bölgesi: ✓ ({x2-x1}x{y2-y1})")
            self.btn_test.config(state="normal")
            self.btn_toggle.config(state="normal")
            
            # Önizleme göster
            self.show_preview(self.template_image, "Şablon Görüntü")
            
            messagebox.showinfo("Başarılı", "✓ Captcha bölgesi başarıyla kaydedildi!")
            logger.info("✓ Captcha bölgesi başarıyla kaydedildi!")
        else:
            logger.warning("Bölge seçimi iptal edildi")
    
    
    def select_button_regions(self):
        """4 Buton bölgesini seç - SAĞ FARE İLE"""
        if not self.window_handle:
            messagebox.showerror("Hata", "Önce oyun penceresini seçin!")
            return
        
        logger.info("4 Buton bölgesi seçimi başlatıldı")
        
        # Pencere kontrolü
        try:
            if not win32gui.IsWindow(self.window_handle):
                logger.error("Seçili pencere artık mevcut değil")
                messagebox.showerror("Hata", "Seçili pencere artık mevcut değil!\nLütfen oyun penceresini yeniden seçin.")
                return
        except Exception as e:
            logger.error(f"Pencere kontrolü hatası: {e}")
            return
        
        # Pencereyi öne getir
        try:
            win32gui.ShowWindow(self.window_handle, 9)
            time.sleep(0.2)
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(0.5)
        except Exception as fg_error:
            logger.warning(f"Pencere öne getirilemedi: {fg_error}")
        
        # Pencere görüntüsünü al
        img = self.capture_window(self.window_handle)
        
        if img is None:
            logger.error("Pencere görüntüsü alınamadı")
            messagebox.showerror("Hata", "Pencere görüntüsü alınamadı!")
            return
        
        logger.info(f"✓ Görüntü alındı: {img.shape}")
        
        # 4 Butonu sırayla seç
        self.button_regions = []
        
        for i in range(1, 5):
            messagebox.showinfo("Buton Seçimi", 
                              f"🎯 {i}. BUTONU seçin\n\n"
                              f"Yukarıdan aşağıya sırayla:\n"
                              f"{'→ ' if i == 1 else '  '} 1. Buton\n"
                              f"{'→ ' if i == 2 else '  '} 2. Buton\n"
                              f"{'→ ' if i == 3 else '  '} 3. Buton\n"
                              f"{'→ ' if i == 4 else '  '} 4. Buton\n\n"
                              f"SAĞ FARE TUŞU ile buton üzerine tıklayın!")
            
            # Bölge seçiciyi aç (sağ tıklama modunda)
            selector = ButtonRegionSelector(img, f"{i}. Buton - SAĞ TIKLAMA ile seç")
            self.root.wait_window(selector.top)
            
            if selector.region:
                self.button_regions.append(selector.region)
                logger.info(f"✓ {i}. Buton seçildi: {selector.region}")
            else:
                logger.warning(f"{i}. Buton seçimi iptal edildi")
                messagebox.showwarning("İptal", "Buton seçimi iptal edildi.\nBaştan başlayın.")
                self.button_regions = []
                return
        
        # Tüm butonlar seçildi
        if len(self.button_regions) == 4:
            logger.info("✅ 4 buton başarıyla seçildi!")
            
            # Kaydet
            self.save_config()
            
            # UI güncelle
            self.button_label.config(text=f"🎯 Butonlar: ✅ Seçildi (4/4)")
            
            # Test ve başlat butonlarını aktif et
            if self.captcha_region:
                self.btn_test.config(state="normal")
                self.btn_toggle.config(state="normal")
            
            messagebox.showinfo("Başarılı", 
                              "✅ 4 buton başarıyla kaydedildi!\n\n"
                              "Artık otomatik tıklama hazır!")
            logger.info("✅ Buton koordinatları kaydedildi!")
        else:
            logger.error("Buton seçimi tamamlanamadı")
    
    
    def test_detection(self):
        """Algılamayı test et"""
        if not self.window_handle or not self.captcha_region or self.template_image is None:
            messagebox.showerror("Hata", "Önce pencere ve captcha bölgesi seçin!")
            return
        
        logger.info("=== TEST BAŞLATILDI ===")
        
        try:
            # Pencere durumunu kontrol et
            if not win32gui.IsWindow(self.window_handle):
                logger.error("✗ Pencere artık mevcut değil")
                messagebox.showerror("Hata", "Seçilen pencere artık mevcut değil!\nLütfen pencereyi yeniden seçin.")
                return
            
            window_title = win32gui.GetWindowText(self.window_handle)
            logger.info(f"Hedef pencere: {window_title}")
            
            # Pencereyi öne getirmeyi dene
            try:
                win32gui.SetForegroundWindow(self.window_handle)
                logger.info("Pencere öne getirildi")
                time.sleep(0.3)  # Pencere render olması için bekle
            except Exception as fg_error:
                logger.warning(f"Pencere öne getirilemedi: {fg_error}")
            
            # Pencere görüntüsünü al
            logger.info("Pencere görüntüsü alınıyor...")
            img = self.capture_window(self.window_handle)
            
            if img is None:
                logger.error("✗ Görüntü alınamadı")
                error_msg = (
                    "❌ Pencere görüntüsü alınamadı!\n\n"
                    "Çözüm önerileri:\n"
                    "1. Oyun penceresini NORMAL boyutta açın (tam ekran değil)\n"
                    "2. Pencereyi görünür bir yere taşıyın\n"
                    "3. Oyunu yönetici olarak çalıştırın\n"
                    "4. Bu programı da yönetici olarak çalıştırın\n"
                    "5. Pencereyi yeniden seçmeyi deneyin"
                )
                messagebox.showerror("Hata", error_msg)
                return
            
            logger.info(f"✓ Görüntü alındı: {img.shape}")
            
            # Captcha ara
            logger.info("Captcha aranıyor...")
            captcha_found, similarity, location, captcha_img = self.find_captcha(img)
            
            if captcha_found:
                # OCR
                logger.info("OCR işlemi başlatılıyor...")
                ocr_text = self.extract_text(captcha_img)
                logger.info(f"✓ OCR sonucu: '{ocr_text}'")
                
                # Sonuç
                result_msg = f"✅ CAPTCHA BULUNDU!\n\n"
                result_msg += f"📍 Konum: {location}\n"
                result_msg += f"🎯 Benzerlik: {similarity:.2%}\n"
                result_msg += f"📝 OCR: {ocr_text}"
                
                messagebox.showinfo("Test Sonucu", result_msg)
                logger.info("=== TEST TAMAMLANDI - BAŞARILI ===")
                
                # Önizleme göster
                self.show_preview(captcha_img, f"Test - {similarity:.0%} - {ocr_text}")
            else:
                messagebox.showwarning("Test Sonucu", 
                                      f"❌ Captcha bulunamadı\n\n"
                                      f"Benzerlik: {similarity:.2%}\n"
                                      f"Eşik: {self.similarity_threshold:.2%}\n\n"
                                      f"💡 Benzerlik eşiğini düşürmeyi deneyin.")
                logger.warning(f"=== TEST TAMAMLANDI - BULUNAMADI (Benzerlik: {similarity:.2%}) ===")
                
        except Exception as e:
            logger.error(f"✗ Test hatası: {e}", exc_info=True)
            messagebox.showerror("Hata", f"Test sırasında hata:\n{e}")
    
    
    def find_captcha(self, window_img):
        """Captcha'yı bul - OpenCV Template Matching ile"""
        try:
            if self.captcha_region is None or self.template_image is None:
                return False, 0.0, None, None
            
            x1, y1, x2, y2 = self.captcha_region
            
            # Bölgeyi çıkar
            region_img = window_img[y1:y2, x1:x2]
            
            # Boyut kontrolü
            if region_img.shape != self.template_image.shape:
                logger.warning(f"Boyut uyuşmazlığı: region={region_img.shape}, template={self.template_image.shape}")
                return False, 0.0, None, None
            
            # Gri tonlamaya çevir
            template_gray = cv2.cvtColor(self.template_image, cv2.COLOR_BGR2GRAY)
            region_gray = cv2.cvtColor(region_img, cv2.COLOR_BGR2GRAY)
            
            # Histogram karşılaştırma (daha hızlı ve NumPy 2.x uyumlu)
            template_hist = cv2.calcHist([template_gray], [0], None, [256], [0, 256])
            region_hist = cv2.calcHist([region_gray], [0], None, [256], [0, 256])
            
            # Normalize et
            cv2.normalize(template_hist, template_hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            cv2.normalize(region_hist, region_hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            
            # Karşılaştır (0-1 arası, 1=tamamen aynı)
            similarity = cv2.compareHist(template_hist, region_hist, cv2.HISTCMP_CORREL)
            
            # Negatif değerleri düzelt
            similarity = max(0.0, similarity)
            
            logger.debug(f"Benzerlik oranı: {similarity:.2%}")
            
            # Eşik kontrolü
            if similarity >= self.similarity_threshold:
                logger.info(f"✅ CAPTCHA BULUNDU! Konum: ({x1}, {y1})")
                return True, similarity, (x1, y1), region_img
            else:
                logger.debug(f"Benzerlik düşük: {similarity:.2%} < {self.similarity_threshold:.2%}")
                return False, similarity, None, None
                
        except Exception as e:
            logger.error(f"Captcha arama hatası: {e}", exc_info=True)
            return False, 0.0, None, None
    
    
    def extract_text(self, img):
        """OCR ile metin çıkar"""
        if not OCR_AVAILABLE:
            logger.warning("OCR mevcut değil")
            return "OCR Yok"
        
        try:
            # Ön işleme
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Tesseract
            config = '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789:'
            text = pytesseract.image_to_string(gray, config=config).strip()
            
            if text:
                logger.debug(f"OCR başarılı: '{text}'")
                return text
            else:
                logger.warning("⚠ OCR metin algılayamadı")
                return "Algılanamadı"
                
        except Exception as e:
            logger.error(f"OCR hatası: {e}")
            return f"Hata: {str(e)[:20]}"
    
    
    def click_button(self, button_number):
        """Belirtilen butona GERÇEK fare hareketi ile otomatik tıkla (1-4)"""
        if not self.button_regions or button_number < 1 or button_number > 4:
            logger.error(f"Geçersiz buton numarası: {button_number}")
            return False
        
        try:
            # Buton koordinatlarını al
            btn_index = button_number - 1
            x1, y1, x2, y2 = self.button_regions[btn_index]
            
            # Butonun merkezini hesapla (LOKAL KOORDİNATLAR)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            logger.info(f"🖱️ Buton {button_number}'e GERÇEK fare ile tıklanıyor...")
            logger.debug(f"  Buton bölgesi: ({x1}, {y1}, {x2}, {y2})")
            logger.debug(f"  Buton merkezi (lokal): ({center_x}, {center_y})")
            
            # Pencereyi aktif et
            try:
                win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
                time.sleep(0.15)
                win32gui.SetForegroundWindow(self.window_handle)
                time.sleep(0.25)
            except Exception as focus_error:
                logger.warning(f"Pencere odaklama hatası: {focus_error}")
            
            # CLIENT AREA koordinatlarını al (global koordinat için)
            try:
                client_to_screen = win32gui.ClientToScreen(self.window_handle, (0, 0))
                
                # Global koordinatlara çevir
                global_x = client_to_screen[0] + center_x
                global_y = client_to_screen[1] + center_y
                
                logger.debug(f"  Client area offset: {client_to_screen}")
                logger.debug(f"  Global koordinat: ({global_x}, {global_y})")
                
            except Exception as coord_error:
                logger.error(f"Koordinat hesaplama hatası: {coord_error}")
                # Yedek yöntem: GetWindowRect
                left, top, _, _ = win32gui.GetWindowRect(self.window_handle)
                global_x = left + center_x
                global_y = top + center_y
                logger.warning(f"  Yedek koordinat kullanılıyor: ({global_x}, {global_y})")
            
            # Eski fare pozisyonunu kaydet
            old_x, old_y = pyautogui.position()
            logger.debug(f"  Eski fare pozisyonu: ({old_x}, {old_y})")
            
            # PyAutoGUI güvenlik ayarı (failsafe devre dışı - isteğe bağlı)
            pyautogui.FAILSAFE = False
            
            # GERÇEK FARE HAREKETİ - Yavaş ve insansı hareket
            logger.info(f"  🐭 Fare hedefe hareket ediyor: ({global_x}, {global_y})")
            pyautogui.moveTo(global_x, global_y, duration=0.5, tween=pyautogui.easeInOutQuad)
            time.sleep(0.1)
            
            # Fare pozisyonunu doğrula
            actual_x, actual_y = pyautogui.position()
            logger.debug(f"  Gerçek fare pozisyonu: ({actual_x}, {actual_y})")
            
            if abs(actual_x - global_x) > 5 or abs(actual_y - global_y) > 5:
                logger.warning(f"  ⚠️ Fare hedeften uzakta! Hedef: ({global_x}, {global_y}), Gerçek: ({actual_x}, {actual_y})")
                # Tekrar deneme
                pyautogui.moveTo(global_x, global_y, duration=0.2)
                time.sleep(0.1)
            
            # GERÇEK TIKLAMA - PyAutoGUI ile
            logger.info(f"  👆 TIKLAMA yapılıyor...")
            pyautogui.click(clicks=1, interval=0.1, button='left')
            time.sleep(0.15)
            
            logger.info(f"✅ Buton {button_number}'e GERÇEK fare ile başarıyla tıklandı!")
            logger.debug(f"  Koordinat: ({global_x}, {global_y})")
            
            # Fareyi eski pozisyona yavaşça geri al (opsiyonel)
            time.sleep(0.2)
            pyautogui.moveTo(old_x, old_y, duration=0.4, tween=pyautogui.easeInOutQuad)
            logger.debug(f"  Fare eski pozisyona döndü: ({old_x}, {old_y})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Tıklama hatası: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            return False
    
    
    def toggle_monitoring(self):
        """İzlemeyi başlat/durdur"""
        if self.is_running:
            # Durdur
            self.is_running = False
            self.btn_toggle.config(text="▶️ BAŞLAT", bg="#4CAF50")
            self.status_label.config(text="⏸ Durduruldu", fg="#FF9800")
            logger.info("⏸ İzleme DURDURULDU")
        else:
            # Başlat
            if not self.window_handle or not self.captcha_region or self.template_image is None:
                messagebox.showerror("Hata", "Önce pencere ve captcha bölgesi seçin!")
                return
            
            self.is_running = True
            self.consecutive_errors = 0  # Hata sayacını sıfırla
            self.btn_toggle.config(text="⏸ DURDUR", bg="#F44336")
            self.status_label.config(text="▶️ Çalışıyor...", fg="#4CAF50")
            
            logger.info("="*70)
            logger.info("İZLEME BAŞLATILDI")
            logger.info(f"Kontrol Sıklığı: {self.check_interval}s")
            logger.info(f"Benzerlik Eşiği: {self.similarity_threshold:.0%}")
            logger.info(f"Cooldown: {self.detection_cooldown}s")
            logger.info("="*70)
            
            # Thread başlat
            thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            thread.start()
    
    
    def monitoring_loop(self):
        """İzleme döngüsü"""
        logger.info("🔍 İzleme döngüsü başladı...")
        
        while self.is_running:
            try:
                # Pencereyi kontrol et
                if not win32gui.IsWindow(self.window_handle):
                    logger.error("Pencere artık mevcut değil")
                    self.consecutive_errors += 1
                    
                    # Çok fazla hata varsa durdur
                    if self.consecutive_errors >= self.max_consecutive_errors:
                        logger.error(f"⛔ {self.max_consecutive_errors} ardışık hata! İzleme durduruluyor...")
                        self.root.after(0, self.stop_monitoring_due_to_error)
                        break
                    
                    logger.warning("⚠ Görüntü alınamadı, bekleniyor...")
                    time.sleep(self.check_interval)
                    continue
                
                # Görüntü al
                img = self.capture_window(self.window_handle)
                
                if img is None:
                    logger.warning("⚠️ Görüntü alınamadı, bekleniyor...")
                    self.root.after(0, lambda: self.status_label.config(
                        text="⚠️ Görüntü Alınamıyor - Bekleniyor...", fg="#FF9800"))
                    time.sleep(5)
                    continue
                
                # Hata sayacını sıfırla (başarılı görüntü alındı)
                self.consecutive_errors = 0
                self.root.after(0, lambda: self.status_label.config(
                    text="▶️ Çalışıyor...", fg="#4CAF50"))
                
                # Captcha ara
                captcha_found, similarity, location, captcha_img = self.find_captcha(img)
                
                if captcha_found:
                    logger.info(f"✅ CAPTCHA ALGILANDI! Benzerlik: {similarity:.0%}")
                    
                    # Cooldown kontrol
                    current_time = time.time()
                    if current_time - self.last_detection_time >= self.detection_cooldown:
                        
                        # OCR
                        ocr_text = self.extract_text(captcha_img)
                        
                        # Kaydet
                        self.save_captcha(captcha_img, similarity, ocr_text)
                        
                        self.last_detection_time = current_time
                        
                        # 5 DAKİKA BEKLE
                        logger.info(f"⏳ 5 dakika bekleniyor... (300 saniye)")
                        self.root.after(0, lambda: self.status_label.config(
                            text="⏳ 5 Dakika Bekleniyor...", fg="#2196F3"))
                        
                        # 300 saniye (5 dakika) bekle
                        for i in range(300):
                            if not self.is_running:  # Durduruldu mu kontrol et
                                break
                            time.sleep(1)
                            
                            # Her 30 saniyede bir kalan süreyi göster
                            if i % 30 == 0:
                                remaining = 300 - i
                                logger.debug(f"⏳ Kalan süre: {remaining} saniye")
                        
                        logger.info("✓ 5 dakika bekleme tamamlandı, taramaya devam ediliyor...")
                        self.root.after(0, lambda: self.status_label.config(
                            text="▶️ Çalışıyor...", fg="#4CAF50"))
                    else:
                        remaining = self.detection_cooldown - (current_time - self.last_detection_time)
                        logger.debug(f"⏳ Cooldown aktif (Kalan: {remaining:.1f}s)")
                else:
                    logger.debug(f"❌ Captcha bulunamadı (Benzerlik: {similarity:.0%})")
                
            except Exception as e:
                logger.error(f"✗ Döngü hatası: {e}", exc_info=True)
                self.consecutive_errors += 1
                
                if self.consecutive_errors >= self.max_consecutive_errors:
                    logger.error(f"⛔ {self.max_consecutive_errors} ardışık hata! İzleme durduruluyor...")
                    self.root.after(0, self.stop_monitoring_due_to_error)
                    break
            
            time.sleep(self.check_interval)
        
        logger.info("⏹ İzleme döngüsü sonlandırıldı")
    
    
    def stop_monitoring_due_to_error(self):
        """Hata nedeniyle izlemeyi durdur"""
        self.is_running = False
        self.btn_toggle.config(text="▶️ BAŞLAT", bg="#4CAF50")
        self.status_label.config(text="⛔ Hata - Durduruldu", fg="#F44336")
        messagebox.showerror("Hata", 
                            "Oyun penceresi kapandı veya erişilemez!\n\n"
                            "Lütfen pencereyi yeniden seçin.")
    
    
    def save_captcha(self, img, similarity, ocr_text):
        """Captcha'yı kaydet - ÖNCEKİ RESİMLERİ SİL (ŞABLON HARİÇ)"""
        try:
            # ÖNCEKİ RESMİ SİL (ŞABLON GÖRSEL DEĞİLSE)
            if self.last_saved_image_path and os.path.exists(self.last_saved_image_path):
                # Şablon görsel kontrolü
                template_path = os.path.join(self.save_folder, "captcha_template.png")
                if self.last_saved_image_path != template_path:
                    try:
                        # Resim ve metin dosyasını sil
                        os.remove(self.last_saved_image_path)
                        txt_path = self.last_saved_image_path.replace('.png', '.txt')
                        if os.path.exists(txt_path):
                            os.remove(txt_path)
                        logger.info(f"🗑️ Önceki resim silindi: {os.path.basename(self.last_saved_image_path)}")
                    except Exception as del_error:
                        logger.error(f"⚠️ Önceki resim silinemedi: {del_error}")
                else:
                    logger.debug("ℹ️ Şablon görsel korundu (silinmedi)")
            
            self.capture_count += 1
            
            # Klasörün varlığını garantile
            os.makedirs(self.save_folder, exist_ok=True)
            
            # Dosya adı
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Dogrulama{self.capture_count}_{timestamp}.png"
            filepath = os.path.join(self.save_folder, filename)
            
            logger.info(f"💾 Kayıt başlatıldı: {filename}")
            
            # Görüntüyü kaydet
            success = cv2.imwrite(filepath, img)
            if success:
                logger.debug(f"  ✓ Görüntü kaydedildi: {filepath}")
                self.last_saved_image_path = filepath  # Yolu kaydet
            else:
                logger.error(f"  ✗ Görüntü kaydedilemedi: {filepath}")
                return
            
            # Metin dosyası
            txt_filename = filename.replace('.png', '.txt')
            txt_filepath = os.path.join(self.save_folder, txt_filename)
            
            try:
                with open(txt_filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Yakalanma Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Benzerlik: {similarity:.2%}\n")
                    f.write(f"OCR Metni: {ocr_text}\n")
                
                logger.debug(f"  ✓ Metin dosyası kaydedildi: {txt_filepath}")
            except Exception as txt_error:
                logger.error(f"  ✗ Metin dosyası kaydedilemedi: {txt_error}")
            
            # Config kaydet
            try:
                self.save_config()
            except Exception as config_error:
                logger.error(f"  ✗ Config kaydedilemedi: {config_error}")
            
            # OCR İLE DETAYLI ANALİZ YAP
            try:
                logger.info("🔍 OCR ile detaylı analiz başlatılıyor...")
                from ocr import CaptchaNumberReader
                
                reader = CaptchaNumberReader()
                result = reader.process_captcha_image(filepath)
                
                if result and result.get('correct_button'):
                    logger.info(f"✅ OCR SONUCU: Ana sayı: {result['main_number']}, "
                              f"Doğru buton: {result['correct_button']}")
                    
                    # OCR sonucunu metin dosyasına ekle
                    with open(txt_filepath, 'a', encoding='utf-8') as f:
                        f.write(f"\n--- OCR ANALİZİ ---\n")
                        f.write(f"Ana Sayı: {result['main_number']}\n")
                        f.write(f"Butonlar: {', '.join(result['buttons'])}\n")
                        f.write(f"Doğru Buton: {result['correct_button']}\n")
                    
                    # Sonucu JSON'a kaydet
                    reader.save_results_to_json()
                    
                    # OTOMATIK TIKLAMA (YENİ)
                    if self.button_regions and len(self.button_regions) == 4:
                        logger.info(f"🎯 Otomatik tıklama başlatılıyor - Buton {result['correct_button']}")
                        
                        # Kısa bekleme
                        time.sleep(0.3)
                        
                        # Butona tıkla
                        click_success = self.click_button(result['correct_button'])
                        
                        if click_success:
                            logger.info("✅ Otomatik tıklama BAŞARILI!")
                            
                            # BAŞARILI TIKLAMA SONRASI RESMİ SİL (ŞABLON HARİÇ)
                            try:
                                time.sleep(0.5)  # Tıklamanın işlenmesi için kısa bekle
                                
                                # Şablon görsel kontrolü
                                template_path = os.path.join(self.save_folder, "captcha_template.png")
                                
                                if os.path.exists(filepath) and filepath != template_path:
                                    os.remove(filepath)
                                    logger.info(f"🗑️ Başarılı tıklama sonrası resim silindi: {filename}")
                                
                                # Metin dosyasını da sil
                                if os.path.exists(txt_filepath):
                                    os.remove(txt_filepath)
                                    logger.info(f"🗑️ İlgili metin dosyası silindi: {txt_filename}")
                                
                                # last_saved_image_path'i None yap (çünkü sildik)
                                self.last_saved_image_path = None
                                
                            except Exception as del_error:
                                logger.error(f"⚠️ Başarılı tıklama sonrası resim silinemedi: {del_error}")
                        else:
                            logger.error("❌ Otomatik tıklama BAŞARISIZ!")
                    else:
                        logger.warning("⚠️ Buton koordinatları eksik, otomatik tıklama yapılamadı")
                        
                else:
                    logger.warning("⚠️ OCR ile eşleşme bulunamadı")
                    
            except Exception as ocr_error:
                logger.error(f"⚠️ OCR analizi başarısız: {ocr_error}")
            
            # UI Güncelle
            self.root.after(0, self.update_ui, img, similarity, ocr_text)
            
            logger.info(f"✅ KAYIT BAŞARILI! Toplam: {self.capture_count}")
            logger.info(f"   Dosya: {filename}")
            logger.info(f"   Benzerlik: {similarity:.2%}")
            logger.info(f"   OCR: {ocr_text}")
            
        except Exception as e:
            logger.error(f"✗ Kaydetme hatası: {e}", exc_info=True)
    
    
    def update_ui(self, img, similarity, ocr_text):
        """UI'ı güncelle"""
        self.count_label.config(text=f"📸 Yakalanan: {self.capture_count}")
        self.show_preview(img, f"#{self.capture_count} - {similarity:.0%} - {ocr_text[:20]}")
    
    
    def show_preview(self, cv_img, title=""):
        """Önizleme göster"""
        try:
            # OpenCV BGR → RGB
            img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            
            # Boyutlandır
            pil_img.thumbnail((480, 300), Image.Resampling.LANCZOS)
            
            # PhotoImage
            photo = ImageTk.PhotoImage(pil_img)
            
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo
            
        except Exception as e:
            logger.error(f"Önizleme hatası: {e}")
    
    
    def reset_region(self):
        """Captcha bölgesini sıfırla"""
        if messagebox.askyesno("Sıfırla",
                              "⚠️ Captcha bölgesi ve şablon SİLİNECEK!\n"
                              "Emin misiniz?"):
            
            self.captcha_region = None
            self.template_image = None
            self.capture_count = 0
            self.button_regions = []  # Butonları da sıfırla
            
            # Config sil
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            
            # UI güncelle
            self.region_label.config(text="📍 Captcha Bölgesi: ❌ Belirtilmedi")
            self.button_label.config(text="🎯 Butonlar: ❌ Seçilmedi (0/4)")
            self.count_label.config(text="📸 Yakalanan: 0")
            self.preview_label.config(image="", text="Henüz görüntü yok")
            self.btn_test.config(state="disabled")
            self.btn_toggle.config(state="disabled")
            
            messagebox.showinfo("Sıfırlandı", "✓ Tüm ayarlar sıfırlandı!")
            logger.info("✓ Ayarlar sıfırlandı")


class RegionSelector:
    """Ekran bölgesi seçici"""
    
    def __init__(self, cv_image, instruction):
        self.top = tk.Toplevel()
        self.top.title("Bölge Seç")
        self.top.attributes('-topmost', True)
        
        # OpenCV → PIL
        img_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        self.original_image = Image.fromarray(img_rgb)
        
        # Ekran boyutuna sığdır
        screen_w = self.top.winfo_screenwidth()
        screen_h = self.top.winfo_screenheight()
        
        scale = min((screen_w * 0.9) / self.original_image.width,
                   (screen_h * 0.9) / self.original_image.height)
        
        if scale < 1:
            new_w = int(self.original_image.width * scale)
            new_h = int(self.original_image.height * scale)
            self.display_image = self.original_image.resize((new_w, new_h), 
                                                            Image.Resampling.LANCZOS)
            self.scale_factor = scale
        else:
            self.display_image = self.original_image
            self.scale_factor = 1.0
        
        # Canvas
        self.canvas = tk.Canvas(self.top, 
                               width=self.display_image.width,
                               height=self.display_image.height,
                               cursor="crosshair")
        self.canvas.pack()
        
        self.photo = ImageTk.PhotoImage(self.display_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        
        # Talimat
        info_label = tk.Label(self.top, text=instruction,
                             font=("Arial", 11, "bold"),
                             fg="white", bg="#FF5722",
                             padx=10, pady=5)
        info_label.pack(fill="x")
        
        # Değişkenler
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.region = None
        
        # Event binding
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.top.bind("<Escape>", lambda e: self.top.destroy())
    
    def on_press(self, event):
        """Fare basıldı"""
        self.start_x = event.x
        self.start_y = event.y
        
        if self.rect:
            self.canvas.delete(self.rect)
        
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.start_x, self.start_y,
            outline='red', width=3
        )
    
    def on_drag(self, event):
        """Fare sürüklendi"""
        self.canvas.coords(self.rect,
                          self.start_x, self.start_y,
                          event.x, event.y)
    
    def on_release(self, event):
        """Fare bırakıldı"""
        # Koordinatları orijinal boyuta çevir
        x1 = int(min(self.start_x, event.x) / self.scale_factor)
        y1 = int(min(self.start_y, event.y) / self.scale_factor)
        x2 = int(max(self.start_x, event.x) / self.scale_factor)
        y2 = int(max(self.start_y, event.y) / self.scale_factor)
        
        self.region = (x1, y1, x2, y2)
        self.top.destroy()


class ButtonRegionSelector:
    """Buton bölgesi seçici - SAĞ FARE İLE"""
    
    def __init__(self, cv_image, instruction):
        self.top = tk.Toplevel()
        self.top.title("Buton Seç - SAĞ TIKLAMA")
        self.top.attributes('-topmost', True)
        
        # OpenCV → PIL
        img_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        self.original_image = Image.fromarray(img_rgb)
        
        # Ekran boyutuna sığdır
        screen_w = self.top.winfo_screenwidth()
        screen_h = self.top.winfo_screenheight()
        
        scale = min((screen_w * 0.9) / self.original_image.width,
                   (screen_h * 0.9) / self.original_image.height)
        
        if scale < 1:
            new_w = int(self.original_image.width * scale)
            new_h = int(self.original_image.height * scale)
            self.display_image = self.original_image.resize((new_w, new_h), 
                                                            Image.Resampling.LANCZOS)
            self.scale_factor = scale
        else:
            self.display_image = self.original_image
            self.scale_factor = 1.0
        
        # Canvas
        self.canvas = tk.Canvas(self.top, 
                               width=self.display_image.width,
                               height=self.display_image.height,
                               cursor="crosshair")
        self.canvas.pack()
        
        self.photo = ImageTk.PhotoImage(self.display_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        
        # Talimat
        info_label = tk.Label(self.top, text=instruction,
                             font=("Arial", 11, "bold"),
                             fg="white", bg="#9C27B0",
                             padx=10, pady=5)
        info_label.pack(fill="x")
        
        # Değişkenler
        self.click_x = None
        self.click_y = None
        self.region = None
        self.marker = None
        
        # Event binding - SAĞ TIKLAMA
        self.canvas.bind("<Button-3>", self.on_right_click)  # Sağ tıklama
        self.top.bind("<Escape>", lambda e: self.top.destroy())
    
    def on_right_click(self, event):
        """Sağ tıklama - Butonu işaretle"""
        self.click_x = event.x
        self.click_y = event.y
        
        # İşaretleyici çiz
        if self.marker:
            self.canvas.delete(self.marker)
        
        # Kırmızı çarpı işareti
        size = 20
        self.marker = self.canvas.create_line(
            self.click_x - size, self.click_y - size,
            self.click_x + size, self.click_y + size,
            fill='red', width=3
        )
        self.canvas.create_line(
            self.click_x - size, self.click_y + size,
            self.click_x + size, self.click_y - size,
            fill='red', width=3
        )
        
        # Buton bölgesi oluştur (tıklanan noktanın etrafında)
        # Ortalama buton boyutu: 200x40 pixel
        btn_width = 200
        btn_height = 40
        
        # Orijinal koordinatlara çevir
        orig_x = int(self.click_x / self.scale_factor)
        orig_y = int(self.click_y / self.scale_factor)
        
        # Buton bölgesi (tıklanan nokta merkezde)
        x1 = max(0, orig_x - btn_width // 2)
        y1 = max(0, orig_y - btn_height // 2)
        x2 = min(self.original_image.width, orig_x + btn_width // 2)
        y2 = min(self.original_image.height, orig_y + btn_height // 2)
        
        self.region = (x1, y1, x2, y2)
        
        # Kısa bekleme sonra kapat
        self.top.after(500, self.top.destroy)


def main():
    root = tk.Tk()
    app = CaptchaDetectorPro(root)
    root.mainloop()


if __name__ == "__main__":
    main()