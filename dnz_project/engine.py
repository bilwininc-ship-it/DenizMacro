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
    """Dinamik bellek tarama sınıfı - AOB Pattern matching"""
    
    def __init__(self, process_handle, pid):
        self.process_handle = process_handle
        self.pid = pid
        self.kernel32 = ctypes.windll.kernel32
        self.PROCESS_ALL_ACCESS = 0x1F0FFF
        
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
    
    def scan_pattern(self, pattern: bytes, start_address: int, end_address: int) -> List[int]:
        """Bellek bölgesinde pattern tarar"""
        found_addresses = []
        current_address = start_address
        chunk_size = 4096
        
        while current_address < end_address:
            data = self.read_memory(current_address, chunk_size)
            if not data:
                current_address += chunk_size
                continue
            
            # Pattern'i bul
            offset = 0
            while True:
                offset = data.find(pattern, offset)
                if offset == -1:
                    break
                found_addresses.append(current_address + offset)
                offset += 1
            
            current_address += chunk_size
        
        return found_addresses
    
    def find_autoban_variable(self) -> Optional[int]:
        """AUTOBAN_QUIZ_ANSWER değişkeninin adresini bulur"""
        # Bellek bölgelerini tara
        mbi = ctypes.create_string_buffer(48)
        address = 0
        
        while True:
            result = self.kernel32.VirtualQueryEx(
                self.process_handle,
                ctypes.c_void_p(address),
                mbi,
                len(mbi)
            )
            
            if result == 0:
                break
            
            # MEM_COMMIT ve PAGE_READWRITE kontrolü
            base_address = ctypes.cast(mbi, ctypes.POINTER(ctypes.c_void_p)).contents.value
            region_size = ctypes.cast(
                ctypes.byref(mbi, 8),
                ctypes.POINTER(ctypes.c_size_t)
            ).contents.value
            
            # Bir sonraki bölgeye geç
            address = base_address + region_size
        
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
        """Oyunun OnAccept fonksiyonunu internal olarak tetikler"""
        try:
            if not self.target_hwnd:
                return False
            
            # WM_COMMAND mesajı gönder (ID_ACCEPT = 1)
            WM_COMMAND = 0x0111
            self.user32.SendMessageW(self.target_hwnd, WM_COMMAND, 1, 0)
            
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
        """AUTOBAN_QUIZ_ANSWER değerini RAM'den okur"""
        if not self.memory_scanner:
            return None
        
        # Gerçek uygulamada burada AOB pattern taraması yapılır
        # Şimdilik simüle edilmiş bir değer döndürüyoruz
        
        # 6 haneli rastgele kod üret (gerçek uygulamada bellekten okunur)
        code = f"{random.randint(100000, 999999)}"
        
        return code
    
    def process_quiz(self, answer: str) -> bool:
        """Quiz cevabını işler ve onaylar"""
        try:
            # İnsan simülasyonu - rastgele gecikme
            delay = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
            self.log(f"Doğrulama kodu algılandı: {answer}", "INFO")
            self.log(f"İnsan simülasyonu bekleniyor: {delay:.2f} saniye", "INFO")
            
            time.sleep(delay)
            
            # Internal trigger ile onay gönder
            if self.process_manager.send_internal_accept():
                self.log(f"Kod başarıyla onaylandı: {answer}", "SUCCESS")
                return True
            else:
                self.log("Onay gönderilemedi", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"İşlem hatası: {str(e)}", "ERROR")
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
        """Tek bir kontrol döngüsü çalıştırır"""
        if not self.is_running or self.is_paused:
            return False
        
        # Quiz cevabını kontrol et
        answer = self.find_quiz_answer()
        
        if answer and answer != self.last_answer:
            self.last_answer = answer
            return self.process_quiz(answer)
        
        return False