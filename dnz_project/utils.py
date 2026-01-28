"""
DNZ (Dinamik Nesne Zamanlayıcı) - Yardımcı Araçlar Modülü
Bellek işlemleri, pattern matching ve utility fonksiyonları
"""

import ctypes
import struct
from typing import List, Optional, Tuple


class AdvancedMemoryScanner:
    """Gelişmiş bellek tarama özellikleri"""
    
    def __init__(self, process_handle):
        self.process_handle = process_handle
        self.kernel32 = ctypes.windll.kernel32
        
        # Memory protection flags
        self.PAGE_EXECUTE_READWRITE = 0x40
        self.PAGE_EXECUTE_WRITECOPY = 0x80
        self.PAGE_READWRITE = 0x04
        self.PAGE_WRITECOPY = 0x08
        
        # Memory state
        self.MEM_COMMIT = 0x1000
        self.MEM_FREE = 0x10000
        self.MEM_RESERVE = 0x2000
    
    def get_memory_regions(self) -> List[Tuple[int, int, int]]:
        """
        Bellek bölgelerini listeler
        Returns: [(base_address, size, protection), ...]
        """
        regions = []
        address = 0
        max_address = 0x7FFFFFFF  # 32-bit için maksimum user-space adresi
        
        mbi = ctypes.create_string_buffer(48)  # MEMORY_BASIC_INFORMATION boyutu
        
        while address < max_address:
            result = self.kernel32.VirtualQueryEx(
                self.process_handle,
                ctypes.c_void_p(address),
                mbi,
                len(mbi)
            )
            
            if result == 0:
                break
            
            # Struct'tan değerleri çıkar
            base_address = struct.unpack('P', mbi[0:ctypes.sizeof(ctypes.c_void_p)])[0]
            region_size = struct.unpack('P', mbi[8:8+ctypes.sizeof(ctypes.c_size_t)])[0]
            state = struct.unpack('I', mbi[16:20])[0]
            protect = struct.unpack('I', mbi[20:24])[0]
            
            # Sadece committed ve readable bölgeleri al
            if state == self.MEM_COMMIT and (
                protect == self.PAGE_READWRITE or 
                protect == self.PAGE_EXECUTE_READWRITE
            ):
                regions.append((base_address, region_size, protect))
            
            # Bir sonraki bölgeye geç
            address = base_address + region_size
        
        return regions
    
    def find_pattern_in_region(
        self,
        base_address: int,
        size: int,
        pattern: bytes,
        wildcard: bytes = b'?'
    ) -> List[int]:
        """
        Belirli bir bölgede pattern arar (wildcard desteği ile)
        
        Args:
            base_address: Başlangıç adresi
            size: Taranacak alan boyutu
            pattern: Aranacak pattern (wildcard için '?' kullan)
            wildcard: Wildcard karakteri
            
        Returns:
            Bulunan adreslerin listesi
        """
        found_addresses = []
        
        # Belleği oku
        buffer = ctypes.create_string_buffer(size)
        bytes_read = ctypes.c_size_t()
        
        success = self.kernel32.ReadProcessMemory(
            self.process_handle,
            ctypes.c_void_p(base_address),
            buffer,
            size,
            ctypes.byref(bytes_read)
        )
        
        if not success or bytes_read.value == 0:
            return found_addresses
        
        data = buffer.raw[:bytes_read.value]
        
        # Pattern matching (wildcard desteği ile)
        pattern_bytes = []
        pattern_mask = []
        
        for byte in pattern:
            if byte == ord(wildcard):
                pattern_bytes.append(0)
                pattern_mask.append(False)
            else:
                pattern_bytes.append(byte)
                pattern_mask.append(True)
        
        # Tarama yap
        for i in range(len(data) - len(pattern_bytes) + 1):
            match = True
            for j, (byte, mask) in enumerate(zip(pattern_bytes, pattern_mask)):
                if mask and data[i + j] != byte:
                    match = False
                    break
            
            if match:
                found_addresses.append(base_address + i)
        
        return found_addresses
    
    def scan_for_patterns(
        self,
        patterns: List[bytes],
        max_results: int = 10
    ) -> dict:
        """
        Tüm bellek bölgelerinde birden fazla pattern arar
        
        Args:
            patterns: Aranacak pattern listesi
            max_results: Pattern başına maksimum sonuç sayısı
            
        Returns:
            {pattern_index: [addresses]}
        """
        results = {i: [] for i in range(len(patterns))}
        regions = self.get_memory_regions()
        
        for base_address, size, _ in regions:
            # Her pattern için tara
            for pattern_idx, pattern in enumerate(patterns):
                if len(results[pattern_idx]) >= max_results:
                    continue
                
                addresses = self.find_pattern_in_region(base_address, size, pattern)
                results[pattern_idx].extend(addresses[:max_results - len(results[pattern_idx])])
        
        return results
    
    def read_int(self, address: int) -> Optional[int]:
        """Adresten 4-byte integer okur"""
        try:
            buffer = ctypes.c_int()
            bytes_read = ctypes.c_size_t()
            
            success = self.kernel32.ReadProcessMemory(
                self.process_handle,
                ctypes.c_void_p(address),
                ctypes.byref(buffer),
                4,
                ctypes.byref(bytes_read)
            )
            
            if success and bytes_read.value == 4:
                return buffer.value
            return None
        except Exception:
            return None
    
    def read_string(self, address: int, max_length: int = 256) -> Optional[str]:
        """Adresten string okur (null-terminated)"""
        try:
            buffer = ctypes.create_string_buffer(max_length)
            bytes_read = ctypes.c_size_t()
            
            success = self.kernel32.ReadProcessMemory(
                self.process_handle,
                ctypes.c_void_p(address),
                buffer,
                max_length,
                ctypes.byref(bytes_read)
            )
            
            if success:
                # Null terminator'a kadar oku
                result = buffer.value.decode('utf-8', errors='ignore')
                return result
            return None
        except Exception:
            return None
    
    def write_int(self, address: int, value: int) -> bool:
        """Adrese 4-byte integer yazar"""
        try:
            buffer = ctypes.c_int(value)
            bytes_written = ctypes.c_size_t()
            
            success = self.kernel32.WriteProcessMemory(
                self.process_handle,
                ctypes.c_void_p(address),
                ctypes.byref(buffer),
                4,
                ctypes.byref(bytes_written)
            )
            
            return success and bytes_written.value == 4
        except Exception:
            return False


class PatternGenerator:
    """AOB pattern oluşturucu yardımcı sınıf"""
    
    @staticmethod
    def from_hex_string(hex_string: str) -> bytes:
        """
        Hex string'den byte array oluşturur
        Örnek: "48 8B 05 ?? ?? ?? ??" -> b"\x48\x8B\x05????"
        """
        parts = hex_string.split()
        result = bytearray()
        
        for part in parts:
            if part == "??":
                result.append(ord('?'))
            else:
                result.append(int(part, 16))
        
        return bytes(result)
    
    @staticmethod
    def to_hex_string(byte_array: bytes) -> str:
        """
        Byte array'i hex string'e çevirir
        Örnek: b"\x48\x8B\x05" -> "48 8B 05"
        """
        return " ".join(f"{b:02X}" for b in byte_array)
    
    @staticmethod
    def create_int_pattern(value: int) -> bytes:
        """Integer değerden pattern oluşturur"""
        return struct.pack('<I', value)  # Little-endian 32-bit integer
    
    @staticmethod
    def create_string_pattern(text: str) -> bytes:
        """String'den pattern oluşturur"""
        return text.encode('utf-8')


class WindowHelper:
    """Pencere işlemleri için yardımcı fonksiyonlar"""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
    
    def get_window_rect(self, hwnd: int) -> Optional[Tuple[int, int, int, int]]:
        """Pencere koordinatlarını döndürür (left, top, right, bottom)"""
        rect = ctypes.wintypes.RECT()
        success = self.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        
        if success:
            return (rect.left, rect.top, rect.right, rect.bottom)
        return None
    
    def is_window_visible(self, hwnd: int) -> bool:
        """Pencerenin görünür olup olmadığını kontrol eder"""
        return self.user32.IsWindowVisible(hwnd) != 0
    
    def bring_window_to_front(self, hwnd: int) -> bool:
        """Pencereyi öne getirir"""
        return self.user32.SetForegroundWindow(hwnd) != 0
    
    def get_window_title(self, hwnd: int) -> Optional[str]:
        """Pencere başlığını döndürür"""
        length = self.user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return None
        
        buffer = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value


def format_address(address: int) -> str:
    """Bellek adresini formatlar (0x00000000)"""
    return f"0x{address:08X}"


def format_bytes(byte_array: bytes, max_length: int = 16) -> str:
    """Byte array'i okunabilir formata çevirir"""
    if len(byte_array) > max_length:
        visible = byte_array[:max_length]
        return " ".join(f"{b:02X}" for b in visible) + "..."
    return " ".join(f"{b:02X}" for b in byte_array)


def calculate_checksum(data: bytes) -> int:
    """Basit checksum hesaplar"""
    return sum(data) & 0xFF


def is_valid_address(address: int) -> bool:
    """Adresin geçerli olup olmadığını kontrol eder"""
    # 32-bit user-space için geçerli aralık
    return 0x00010000 <= address <= 0x7FFFFFFF


# Test fonksiyonu
def test_utilities():
    """Utility fonksiyonlarını test eder"""
    print("=== DNZ Utilities Test ===\n")
    
    # Pattern Generator test
    print("1. Pattern Generator Test:")
    hex_string = "48 8B 05 ?? ?? ?? ??"
    pattern = PatternGenerator.from_hex_string(hex_string)
    print(f"   Input:  {hex_string}")
    print(f"   Output: {format_bytes(pattern)}")
    print(f"   Back:   {PatternGenerator.to_hex_string(pattern[:3])}\n")
    
    # Address formatting test
    print("2. Address Formatting Test:")
    addr = 0x12345678
    print(f"   Address: {format_address(addr)}")
    print(f"   Valid: {is_valid_address(addr)}\n")
    
    print("Test tamamlandı!")


if __name__ == "__main__":
    test_utilities()