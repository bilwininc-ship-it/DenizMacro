import cv2
import numpy as np
import pytesseract
from PIL import ImageGrab
from typing import List, Tuple, Optional

# Tesseract path - otomatik bul
import os
import sys

def find_tesseract():
    """Tesseract'ı otomatik bul"""
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Tesseract-OCR\tesseract.exe',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return 'tesseract'  # PATH'te varsa

pytesseract.pytesseract.tesseract_cmd = find_tesseract()

class OCREngine:
    """Ekran okuma ve OCR motoru - Kritik Mod"""
    
    def __init__(self):
        # Yeşil renk aralığı (HSV) - oyuna göre optimize
        self.green_lower = np.array([35, 80, 80])
        self.green_upper = np.array([85, 255, 255])
        
        # Gri buton aralığı (HSV)
        self.gray_lower = np.array([0, 0, 40])
        self.gray_upper = np.array([180, 60, 220])
        
    def capture_screen(self) -> np.ndarray:
        """Ekran görüntüsü al"""
        screenshot = ImageGrab.grab()
        screenshot_np = np.array(screenshot)
        return cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    def detect_green_text(self, image: np.ndarray) -> Optional[str]:
        """Ekrandaki yeşil metni tespit et - HER YERDE ARA"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv, self.green_lower, self.green_upper)
        
        # Morfolojik işlemler
        kernel = np.ones((3, 3), np.uint8)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
        green_mask = cv2.dilate(green_mask, kernel, iterations=2)
        
        # Konturları bul
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # En büyükten küçüğe sırala, ilk 5'ini dene
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        for contour in sorted_contours[:5]:
            area = cv2.contourArea(contour)
            if area < 150:  # Çok küçük alanları atla
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            
            # Bölgeyi genişlet
            padding = 10
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2*padding)
            h = min(image.shape[0] - y, h + 2*padding)
            
            green_region = image[y:y+h, x:x+w]
            gray = cv2.cvtColor(green_region, cv2.COLOR_BGR2GRAY)
            
            # OTSU threshold
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR - sadece rakamlar
            text = pytesseract.image_to_string(thresh, config='--psm 6 digits -c tessedit_char_whitelist=0123456789')
            text = ''.join(filter(str.isdigit, text.strip()))
            
            # En az 4 haneli sayı
            if len(text) >= 4:
                return text
        
        return None
    
    def detect_gray_buttons(self, image: np.ndarray) -> List[Tuple[int, int, str]]:
        """Ekrandaki gri butonları tespit et"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        gray_mask = cv2.inRange(hsv, self.gray_lower, self.gray_upper)
        
        # Morfolojik işlemler
        kernel = np.ones((5, 5), np.uint8)
        gray_mask = cv2.morphologyEx(gray_mask, cv2.MORPH_CLOSE, kernel)
        
        # Konturları bul
        contours, _ = cv2.findContours(gray_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        buttons = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 1000:  # Minimum buton boyutu
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # Dikdörtgen kontrolü
            aspect_ratio = w / float(h) if h > 0 else 0
            if aspect_ratio < 1.5 or aspect_ratio > 10:
                continue
            
            # Merkez koordinat
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Buton bölgesini kırp
            padding = 8
            btn_region = image[max(0, y-padding):y+h+padding, max(0, x-padding):x+w+padding]
            
            if btn_region.size == 0:
                continue
            
            btn_gray = cv2.cvtColor(btn_region, cv2.COLOR_BGR2GRAY)
            _, btn_thresh = cv2.threshold(btn_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # OCR
            text = pytesseract.image_to_string(btn_thresh, config='--psm 7 digits -c tessedit_char_whitelist=0123456789')
            text = ''.join(filter(str.isdigit, text.strip()))
            
            # En az 4 haneli
            if len(text) >= 4:
                buttons.append((center_x, center_y, text))
        
        # Y koordinatına göre sırala (yukarıdan aşağıya)
        buttons = sorted(buttons, key=lambda b: b[1])
        
        # İlk 4 butonu döndür
        return buttons[:4]
    
    def scan_screen(self) -> Tuple[Optional[str], List[Tuple[int, int, str]]]:
        """Ekranı tara ve sonuçları döndür"""
        screenshot = self.capture_screen()
        green_text = self.detect_green_text(screenshot)
        gray_buttons = self.detect_gray_buttons(screenshot)
        return green_text, gray_buttons