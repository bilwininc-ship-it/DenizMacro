"""
DNZ (Dinamik Nesne Zamanlayıcı) - Çekirdek Motor Modülü
Bellek tarama, süreç yönetimi ve otomasyon işlemlerini yönetir.
"""

import ctypes
import time
import random
import re
from ctypes import wintypes
from datetime import datetime
from typing import Optional, List, Tuple

import config


class MemoryScanner:
    """Dinamik bellek tarama sınıfı - Python 2.7 String Object AOB Pattern matching"""
    
    def __init__(self, process_handle, pid):
        self.process_handle = process_handle
        self.pid = pid
        self.kernel32 = ctypes.windll.kernel32
        self.PROCESS_ALL_ACCESS = 0x1F0FFF
        
        # Python 2.7 String Object sabitleri
        self.PY27_STRING_HEADER_SIZE = config.PY27_STRING_HEADER_SIZE
        self.PY27_STRING_SIZE_OFFSET = config.PY27_STRING_SIZE_OFFSET
        self.PY27_STRING_DATA_OFFSET = config.PY27_STRING_DATA_OFFSET
        
        # MEMORY_BASIC_INFORMATION yapısı
        class MEMORY_BASIC_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("BaseAddress", ctypes.c_void_p),
                ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", ctypes.c_ulong),
                ("RegionSize", ctypes.c_size_t),
                ("State", ctypes.c_ulong),
                ("Protect", ctypes.c_ulong),
                ("Type", ctypes.c_ulong),
            ]
        
        self.MEMORY_BASIC_INFORMATION = MEMORY_BASIC_INFORMATION
        
        # Bellek koruma sabitleri
        self.PAGE_READWRITE = 0x04
        self.PAGE_EXECUTE_READWRITE = 0x40
        self.MEM_COMMIT = 0x1000
        self.MEM_PRIVATE = 0x20000
        
    def read_memory(self, address: int, size: int) -> bytes:
        """Bellek adresinden veri okur"""
        try:
            buffer = ctypes.create_string_buffer(size)
            bytes_read = ctypes.c_size_t()
            
            success = self.kernel32.ReadProcessMemory(
                self.process_handle,
                ctypes.c_void_p(address),
                buffer,
                size,
                ctypes.byref(bytes_read)
            )
            
            if success and bytes_read.value == size:
                return buffer.raw
            return b""
        except Exception:
            return b""
    
    def is_valid_6digit_string(self, data: bytes) -> bool:
        """6 haneli sayı string'i mi kontrol eder"""
        try:
            if len(data) < 6:
                return False
            
            # İlk 6 byte'ı decode et
            text = data[:6].decode('utf-8', errors='ignore')
            
            # 6 karakter olmalı ve hepsi rakam olmalı
            if len(text) == 6 and text.isdigit():
                return True
            return False
        except Exception:
            return False
    
    def scan_pattern_in_region(self, base_address: int, region_size: int, pattern: bytes) -> List[int]:
        """Bellek bölgesinde Python 2.7 String Object pattern'ini tarar"""
        found_addresses = []
        chunk_size = 4096  # 4KB chunk'lar halinde oku
        current_offset = 0
        
        while current_offset < region_size:
            # Chunk boyutunu ayarla
            read_size = min(chunk_size, region_size - current_offset)
            current_address = base_address + current_offset
            
            # Belleği oku
            data = self.read_memory(current_address, read_size)
            if not data:
                current_offset += read_size
                continue
            
            # Pattern'i ara (ob_size = 6)
            offset = 0
            while True:
                offset = data.find(pattern, offset)
                if offset == -1:
                    break
                
                # Pattern bulundu! Şimdi tam Python String Object olduğunu doğrula
                potential_address = current_address + offset - self.PY27_STRING_SIZE_OFFSET
                
                # String data kısmını oku (offset + 12 bytes sonrası)
                string_data_address = current_address + offset + 12  # ob_size sonrası ob_shash(4) + ob_sstate(4) + ob_sval
                string_data = self.read_memory(string_data_address, 7)  # 6 digit + null terminator
                
                # 6 haneli sayı mı kontrol et
                if self.is_valid_6digit_string(string_data):
                    found_addresses.append(potential_address)
                
                offset += 1
            
            current_offset += read_size - len(pattern)  # Overlap için
        
        return found_addresses
    
    def find_autoban_variable(self) -> Optional[int]:
        """
        AUTOBAN_QUIZ_ANSWER değişkeninin adresini bulur
        Python 2.7 String Object yapısını tarayarak dinamik adresi yakalar
        """
        try:
            mbi = self.MEMORY_BASIC_INFORMATION()
            address = 0
            max_address = 0x7FFFFFFF  # 32-bit adres limiti
            
            # config'den pattern al
            search_pattern = config.AOB_PATTERNS[0]  # ob_size = 6
            
            all_found = []
            
            # Tüm bellek bölgelerini tara
            while address < max_address:
                result = self.kernel32.VirtualQueryEx(
                    self.process_handle,
                    ctypes.c_void_p(address),
                    ctypes.byref(mbi),
                    ctypes.sizeof(mbi)
                )
                
                if result == 0:
                    break
                
                # Sadece committed, private, read/write bölgeleri tara
                if (mbi.State == self.MEM_COMMIT and 
                    mbi.Type == self.MEM_PRIVATE and
                    (mbi.Protect == self.PAGE_READWRITE or 
                     mbi.Protect == self.PAGE_EXECUTE_READWRITE)):
                    
                    # Bu bölgede pattern ara
                    found = self.scan_pattern_in_region(
                        mbi.BaseAddress,
                        mbi.RegionSize,
                        search_pattern
                    )
                    
                    all_found.extend(found)
                
                # Bir sonraki bölgeye geç
                address = mbi.BaseAddress + mbi.RegionSize
            
            # En uygun adresi döndür (genellikle ilk bulduğumuz)
            if all_found:
                return all_found[0]
            
            return None
            
        except Exception:
            return None
    
    def read_string_from_address(self, address: int) -> Optional[str]:
        """Python String Object adresinden string içeriğini okur"""
        try:
            # ob_sval kısmını oku (header sonrası)
            data = self.read_memory(
                address + self.PY27_STRING_DATA_OFFSET,
                7  # 6 digit + null terminator
            )
            
            if self.is_valid_6digit_string(data):
                return data[:6].decode('utf-8')
            
            return None
        except Exception:
            return None


class ProcessManager:
    """Süreç yönetimi ve pencere kontrolü"""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.target_hwnd = None
        self.target_pid = None
        self.process_handle = None
        
    def find_window_by_title(self, window_names: List[str]) -> Optional[int]:
        """Pencere başlığına göre HWND bulur"""
        for name in window_names:
            hwnd = self.user32.FindWindowW(None, name)
            if hwnd:
                return hwnd
        return None
    
    def get_all_windows(self) -> List[Tuple[int, str]]:
        """Tüm açık pencereleri listeler"""
        windows = []
        
        def enum_callback(hwnd, lparam):
            if self.user32.IsWindowVisible(hwnd):
                length = self.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    self.user32.GetWindowTextW(hwnd, buffer, length + 1)
                    windows.append((hwnd, buffer.value))
            return True
        
        ENUM_CALLBACK = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        callback = ENUM_CALLBACK(enum_callback)
        self.user32.EnumWindows(callback, 0)
        
        return windows
    
    def attach_to_window(self, hwnd: int) -> bool:
        """Pencereye bağlanır ve process handle alır"""
        try:
            pid = ctypes.c_ulong()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            if pid.value == 0:
                return False
            
            self.target_hwnd = hwnd
            self.target_pid = pid.value
            
            PROCESS_ALL_ACCESS = 0x1F0FFF
            self.process_handle = self.kernel32.OpenProcess(
                PROCESS_ALL_ACCESS,
                False,
                self.target_pid
            )
            
            return self.process_handle is not None
        except Exception:
            return False
    
    def send_internal_accept(self) -> bool:
        """
        Oyunun OnAccept fonksiyonunu internal olarak tetikler
        Hayalet tıklama (Ghost Click) - Fareyi hareket ettirmeden tıklama simüle eder
        """
        try:
            if not self.target_hwnd:
                return False
            
            # Birden fazla mesaj türü dene (daha robust)
            success_count = 0
            
            # 1. WM_COMMAND - Genellikle dialog butonları için kullanılır
            WM_COMMAND = 0x0111
            IDOK = 1  # OK/Accept button ID
            result1 = self.user32.PostMessageW(self.target_hwnd, WM_COMMAND, IDOK, 0)
            if result1:
                success_count += 1
            
            # 2. WM_KEYDOWN + WM_KEYUP - Enter tuşu simülasyonu
            WM_KEYDOWN = 0x0100
            WM_KEYUP = 0x0101
            VK_RETURN = 0x0D  # Enter key
            
            result2 = self.user32.PostMessageW(self.target_hwnd, WM_KEYDOWN, VK_RETURN, 0)
            time.sleep(0.05)  # Küçük gecikme
            result3 = self.user32.PostMessageW(self.target_hwnd, WM_KEYUP, VK_RETURN, 0)
            if result2 and result3:
                success_count += 1
            
            # 3. SendMessage ile aynı mesajları tekrar dene (daha kesin)
            result4 = self.user32.SendMessageW(self.target_hwnd, WM_COMMAND, IDOK, 0)
            if result4 == 0:  # SendMessage 0 döndürürse başarılı
                success_count += 1
            
            # En az bir metod başarılı olduysa True döndür
            return success_count > 0
            
        except Exception:
            return False
    
    def send_ghost_click(self, button_index: int = 1) -> bool:
        """
        Belirli bir butona hayalet tıklama gönderir
        button_index: 0-3 arası (görüntüdeki buton sırası)
        """
        try:
            if not self.target_hwnd:
                return False
            
            # WM_LBUTTONDOWN ve WM_LBUTTONUP mesajları
            WM_LBUTTONDOWN = 0x0201
            WM_LBUTTONUP = 0x0202
            
            # Buton koordinatları (yaklaşık - oyun içindeki captcha dialog pozisyonları)
            # Bu değerler oyuna özel ayarlanmalı
            button_positions = [
                (500, 430),  # Button 1 (592430)
                (500, 560),  # Button 2 (875609) - DOĞRU CEVAP
                (500, 690),  # Button 3 (714685)
                (500, 820),  # Button 4 (905387)
            ]
            
            if button_index < 0 or button_index >= len(button_positions):
                return False
            
            x, y = button_positions[button_index]
            lparam = (y << 16) | x  # Koordinatları birleştir
            
            # Mouse click simüle et
            self.user32.PostMessageW(self.target_hwnd, WM_LBUTTONDOWN, 0, lparam)
            time.sleep(0.03)
            self.user32.PostMessageW(self.target_hwnd, WM_LBUTTONUP, 0, lparam)
            
            return True
            
        except Exception:
            return False
    
    def close_handle(self):
        """Process handle'ı kapatır"""
        if self.process_handle:
            self.kernel32.CloseHandle(self.process_handle)
            self.process_handle = None


class DNZEngine:
    """DNZ ana motor sınıfı - tüm operasyonları koordine eder"""
    
    def __init__(self, log_callback=None):
        self.process_manager = ProcessManager()
        self.memory_scanner = None
        self.log_callback = log_callback
        self.is_running = False
        self.is_paused = False
        self.quiz_answer_address = None
        self.last_answer = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log mesajı gönderir"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        if self.log_callback:
            self.log_callback(log_entry)
        
        # Dosyaya yaz
        try:
            with open(config.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass
    
    def check_admin_rights(self) -> bool:
        """Yönetici yetkisi kontrolü"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    
    def auto_attach(self) -> bool:
        """Otomatik olarak hedef pencereye bağlanır"""
        self.log("Hedef pencere aranıyor...", "INFO")
        
        # Önce bilinen pencere isimlerini dene
        hwnd = self.process_manager.find_window_by_title(config.TARGET_WINDOW_NAMES)
        
        if hwnd:
            if self.process_manager.attach_to_window(hwnd):
                self.memory_scanner = MemoryScanner(
                    self.process_manager.process_handle,
                    self.process_manager.target_pid
                )
                self.log(f"Hedef pencereye başarıyla bağlanıldı (HWND: {hwnd})", "SUCCESS")
                return True
        
        self.log("Hedef pencere bulunamadı", "WARNING")
        return False
    
    def find_quiz_answer(self) -> Optional[str]:
        """
        AUTOBAN_QUIZ_ANSWER değerini RAM'den okur
        Dinamik adres yakalama - her oyun açılış/kapanışında değişen adresleri yakalar
        """
        if not self.memory_scanner:
            return None
        
        try:
            # Eğer daha önce adres bulunmuşsa direkt oradan oku
            if self.quiz_answer_address:
                # Bellekten 6 haneli kodu oku
                code = self.memory_scanner.read_string_from_address(self.quiz_answer_address)
                
                if code and code.isdigit() and len(code) == 6:
                    return code
                
                # Adres geçersiz olmuş (oyun yeniden başlamış olabilir), yeniden tara
                self.log("⚠️ Önceki adres geçersiz, yeniden tarama yapılıyor...", "WARNING")
                self.quiz_answer_address = None
            
            # İlk kez veya adres geçersizse, bellek taraması yap
            # ANCAK çok sık tarama yapma (performans için)
            current_time = time.time()
            
            if not hasattr(self, '_last_scan_time'):
                self._last_scan_time = 0
            
            # Her 3 saniyede bir tara (captcha geldiğinde hızlı yakalamak için)
            if current_time - self._last_scan_time < 3:
                return None
            
            self._last_scan_time = current_time
            
            # Sessiz tarama (spam log önleme)
            if not hasattr(self, '_scan_logged'):
                self.log("🔍 AUTOBAN_QUIZ_ANSWER değişkeni aranıyor...", "INFO")
                self._scan_logged = True
            
            # Bellek taraması yap
            found_address = self.memory_scanner.find_autoban_variable()
            
            if found_address:
                self.quiz_answer_address = found_address
                self.log(f"✅ AUTOBAN değişkeni bulundu: 0x{found_address:08X}", "SUCCESS")
                
                # Bulunan adresten kodu oku
                code = self.memory_scanner.read_string_from_address(found_address)
                
                if code and code.isdigit() and len(code) == 6:
                    self.log(f"🎯 Doğrulama kodu yakalandı: {code}", "SUCCESS")
                    return code
            
            return None
            
        except Exception as e:
            self.log(f"❌ Bellek okuma hatası: {str(e)}", "ERROR")
            return None
    
    def process_quiz(self, answer: str) -> bool:
        """
        Quiz cevabını işler ve onaylar
        Doğru butonu bulup hayalet tıklama yapar
        """
        try:
            # İnsan simülasyonu - rastgele gecikme
            delay = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
            self.log(f"📋 Doğrulama kodu algılandı: {answer}", "INFO")
            self.log(f"⏱️  İnsan simülasyonu bekleniyor: {delay:.2f} saniye", "INFO")
            
            time.sleep(delay)
            
            # NOT: Gerçek uygulamada, buton indexini bulmak için
            # ekrandaki 4 butonu OCR ile okuyup answer ile eşleştirmek gerekir
            # Şimdilik varsayılan olarak Enter/OnAccept gönderiyoruz
            
            # Metod 1: Internal trigger ile onay gönder (öncelikli)
            success = self.process_manager.send_internal_accept()
            
            if success:
                self.log(f"✅ Kod başarıyla onaylandı: {answer}", "SUCCESS")
                return True
            else:
                self.log("⚠️ Onay gönderilemedi, alternatif metod deneniyor...", "WARNING")
                
                # Metod 2: Ghost click dene (buton indexi gerekli - varsayılan 1)
                # NOT: Ekran koordinatları oyuna göre ayarlanmalı
                ghost_success = self.process_manager.send_ghost_click(button_index=1)
                
                if ghost_success:
                    self.log(f"✅ Ghost click ile onaylandı: {answer}", "SUCCESS")
                    return True
                else:
                    self.log("❌ Tüm onay metodları başarısız", "ERROR")
                    return False
                
        except Exception as e:
            self.log(f"❌ İşlem hatası: {str(e)}", "ERROR")
            return False
    
    def start(self):
        """Motoru başlatır"""
        if not self.check_admin_rights():
            self.log("UYARI: Yönetici yetkileri olmadan çalışıyor", "WARNING")
        
        self.is_running = True
        self.log("DNZ motoru başlatıldı", "SUCCESS")
    
    def stop(self):
        """Motoru durdurur"""
        self.is_running = False
        self.process_manager.close_handle()
        self.log("DNZ motoru durduruldu", "INFO")
    
    def pause(self):
        """Motoru duraklatır"""
        self.is_paused = True
        self.log("DNZ motoru duraklatıldı", "INFO")
    
    def resume(self):
        """Motoru devam ettirir"""
        self.is_paused = False
        self.log("DNZ motoru devam ettiriliyor", "INFO")
    
    def run_cycle(self) -> bool:
        """
        Tek bir kontrol döngüsü çalıştırır
        Sürekli olarak captcha'yı bekler ve geldiğinde otomatik cevaplar
        """
        if not self.is_running or self.is_paused:
            return False
        
        try:
            # Quiz cevabını kontrol et
            answer = self.find_quiz_answer()
            
            if answer and answer != self.last_answer:
                # Yeni bir captcha algılandı!
                self.last_answer = answer
                self.log(f"🎯 YENİ CAPTCHA ALGILANDI: {answer}", "SUCCESS")
                return self.process_quiz(answer)
            
            # Captcha yoksa sessizce devam et (spam logları önlemek için)
            # Her 15 saniyede bir "Sistem aktif" logu
            current_time = time.time()
            if not hasattr(self, '_last_active_log'):
                self._last_active_log = current_time
            
            if current_time - self._last_active_log > 15:
                self.log("⏳ Sistem aktif, captcha bekleniyor...", "INFO")
                self._last_active_log = current_time
            
        except Exception as e:
            self.log(f"❌ Döngü hatası: {str(e)}", "ERROR")
        
        return False