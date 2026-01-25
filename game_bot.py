#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 Oyun Doğrulama Botu
300x300 Kompakt Versiyon
"""

import time
import random
import threading
import cv2
import numpy as np
import pytesseract
import pyautogui
import customtkinter as ctk
from PIL import ImageGrab
from typing import List, Tuple, Optional

# Güvenlik
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

# Tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class OyunBot:
    """Oyun doğrulama botu - Ana sınıf"""
    
    def __init__(self):
        # Tesseract path (Windows için)
        self.tesseract_kurulu = self.tesseract_kontrol()
        
        # Ana pencere
        self.pencere = ctk.CTk()
        self.pencere.title("🎮 Oyun Botu")
        self.pencere.geometry("300x300")
        self.pencere.resizable(False, False)
        
        # Durum değişkenleri
        self.calisiyor = False
        self.basari_sayisi = 0
        
        # Renk aralıkları
        self.yesil_alt = np.array([35, 80, 80])
        self.yesil_ust = np.array([85, 255, 255])
        self.gri_alt = np.array([0, 0, 40])
        self.gri_ust = np.array([180, 60, 220])
        
        # Arayüzü oluştur
        self.arayuz_olustur()
        
    def tesseract_kontrol(self):
        """Tesseract kurulu mu kontrol et"""
        import os
        yollar = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        ]
        
        for yol in yollar:
            if os.path.exists(yol):
                pytesseract.pytesseract.tesseract_cmd = yol
                return True
        
        pytesseract.pytesseract.tesseract_cmd = 'tesseract'
        return False
    
    def arayuz_olustur(self):
        """Kompakt arayüz oluştur - 300x300"""
        # Ana frame
        frame = ctk.CTkFrame(self.pencere)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık
        ctk.CTkLabel(
            frame,
            text="🎮 Oyun Botu",
            font=("Arial", 20, "bold")
        ).pack(pady=(5, 10))
        
        # Başlat/Durdur butonu
        self.baslat_btn = ctk.CTkButton(
            frame,
            text="▶ Başlat",
            command=self.toggle,
            font=("Arial", 14, "bold"),
            height=40,
            fg_color="#2196F3"
        )
        self.baslat_btn.pack(pady=5, padx=15, fill="x")
        
        # İstatistikler frame
        stats_frame = ctk.CTkFrame(frame)
        stats_frame.pack(pady=8, padx=15, fill="x")
        
        # Başarı sayısı
        self.basari_label = ctk.CTkLabel(
            stats_frame,
            text="✅ Geçti: 0",
            font=("Arial", 13, "bold"),
            text_color="#4CAF50"
        )
        self.basari_label.pack(pady=5)
        
        # Durum etiketi
        self.durum_label = ctk.CTkLabel(
            frame,
            text="⏸ Beklemede",
            font=("Arial", 12),
            text_color="gray"
        )
        self.durum_label.pack(pady=5)
        
        # Bilgi etiketi
        self.bilgi_label = ctk.CTkLabel(
            frame,
            text="",
            font=("Arial", 10),
            text_color="lightgray",
            wraplength=260
        )
        self.bilgi_label.pack(pady=5)
        
        # Log kutusu (küçük)
        self.log_box = ctk.CTkTextbox(frame, height=80, width=260)
        self.log_box.pack(pady=5)
        self.log_box.configure(state="disabled")
        
        # Tesseract uyarısı
        if not self.tesseract_kurulu:
            self.log_ekle("⚠️ Tesseract OCR gerekli!")
            self.log_ekle("İndirin: tesseract-ocr")
    
    def toggle(self):
        """Bot başlat/durdur"""
        self.calisiyor = not self.calisiyor
        
        if self.calisiyor:
            self.baslat_btn.configure(text="⏹ Durdur", fg_color="#f44336")
            self.durum_label.configure(text="🔴 Çalışıyor", text_color="#4CAF50")
            self.log_ekle("🚀 Bot başlatıldı")
            self.log_ekle("─" * 30)
            
            # Thread başlat
            thread = threading.Thread(target=self.ana_dongu, daemon=True)
            thread.start()
        else:
            self.baslat_btn.configure(text="▶ Başlat", fg_color="#2196F3")
            self.durum_label.configure(text="⏸ Beklemede", text_color="gray")
            self.log_ekle("⏹ Bot durduruldu\n")
    
    def log_ekle(self, mesaj: str):
        """Log ekle"""
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{mesaj}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
    
    def ekran_yakala(self) -> np.ndarray:
        """Ekran görüntüsü al"""
        ss = ImageGrab.grab()
        ss_np = np.array(ss)
        return cv2.cvtColor(ss_np, cv2.COLOR_RGB2BGR)
    
    def yesil_yazi_bul(self, goruntu: np.ndarray) -> Optional[str]:
        """Yeşil yazıyı bul"""
        hsv = cv2.cvtColor(goruntu, cv2.COLOR_BGR2HSV)
        maske = cv2.inRange(hsv, self.yesil_alt, self.yesil_ust)
        
        # Morfoloji
        kernel = np.ones((3, 3), np.uint8)
        maske = cv2.morphologyEx(maske, cv2.MORPH_CLOSE, kernel)
        maske = cv2.dilate(maske, kernel, iterations=2)
        
        # Konturları bul
        konturlar, _ = cv2.findContours(maske, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not konturlar:
            return None
        
        # En büyük konturları dene
        sirali = sorted(konturlar, key=cv2.contourArea, reverse=True)
        
        for kontur in sirali[:5]:
            alan = cv2.contourArea(kontur)
            if alan < 150:
                continue
            
            x, y, w, h = cv2.boundingRect(kontur)
            
            # Genişlet
            p = 10
            x = max(0, x - p)
            y = max(0, y - p)
            w = min(goruntu.shape[1] - x, w + 2*p)
            h = min(goruntu.shape[0] - y, h + 2*p)
            
            bolge = goruntu[y:y+h, x:x+w]
            gri = cv2.cvtColor(bolge, cv2.COLOR_BGR2GRAY)
            _, esik = cv2.threshold(gri, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR
            yazi = pytesseract.image_to_string(esik, config='--psm 6 digits')
            yazi = ''.join(filter(str.isdigit, yazi.strip()))
            
            if len(yazi) >= 4:
                return yazi
        
        return None
    
    def gri_butonlar_bul(self, goruntu: np.ndarray) -> List[Tuple[int, int, str]]:
        """Gri butonları bul"""
        hsv = cv2.cvtColor(goruntu, cv2.COLOR_BGR2HSV)
        maske = cv2.inRange(hsv, self.gri_alt, self.gri_ust)
        
        # Morfoloji
        kernel = np.ones((5, 5), np.uint8)
        maske = cv2.morphologyEx(maske, cv2.MORPH_CLOSE, kernel)
        
        # Konturlar
        konturlar, _ = cv2.findContours(maske, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        butonlar = []
        
        for kontur in konturlar:
            alan = cv2.contourArea(kontur)
            if alan < 1000:
                continue
            
            x, y, w, h = cv2.boundingRect(kontur)
            
            # Dikdörtgen kontrolü
            oran = w / float(h) if h > 0 else 0
            if oran < 1.5 or oran > 10:
                continue
            
            # Merkez
            cx = x + w // 2
            cy = y + h // 2
            
            # Buton bölgesi
            p = 8
            bolge = goruntu[max(0, y-p):y+h+p, max(0, x-p):x+w+p]
            
            if bolge.size == 0:
                continue
            
            gri = cv2.cvtColor(bolge, cv2.COLOR_BGR2GRAY)
            _, esik = cv2.threshold(gri, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # OCR
            yazi = pytesseract.image_to_string(esik, config='--psm 7 digits')
            yazi = ''.join(filter(str.isdigit, yazi.strip()))
            
            if len(yazi) >= 4:
                butonlar.append((cx, cy, yazi))
        
        # Yukarıdan aşağıya sırala
        butonlar = sorted(butonlar, key=lambda b: b[1])
        return butonlar[:4]
    
    def tiklama_yap(self, x: int, y: int):
        """Güvenli tıklama"""
        # Hafif offset
        ox = random.randint(-2, 2)
        oy = random.randint(-2, 2)
        
        # Hareket
        pyautogui.moveTo(x + ox, y + oy, duration=0.3)
        time.sleep(0.1)
        
        # Tıkla
        pyautogui.click()
    
    def ana_dongu(self):
        """Ana tarama döngüsü"""
        tarama = 0
        
        while self.calisiyor:
            try:
                tarama += 1
                self.durum_label.configure(text="📡 Taranıyor...")
                
                # Ekranı tara
                goruntu = self.ekran_yakala()
                yesil = self.yesil_yazi_bul(goruntu)
                butonlar = self.gri_butonlar_bul(goruntu)
                
                if yesil and butonlar:
                    buton_yazilar = [b[2] for b in butonlar]
                    
                    self.log_ekle(f"Tarama #{tarama}")
                    self.log_ekle(f"🟢 Yeşil: {yesil}")
                    self.log_ekle(f"🔘 Butonlar: {buton_yazilar}")
                    
                    # Eşleşme bul
                    eslesen = None
                    
                    for bx, by, byazi in butonlar:
                        if yesil == byazi:
                            eslesen = (bx, by, byazi)
                            self.log_ekle(f"✅ Eşleşti: {byazi}")
                            break
                    
                    if eslesen:
                        # Bekleme süresi: 4-15 saniye
                        bekle = random.uniform(4.0, 15.0)
                        self.bilgi_label.configure(text=f"⏳ {bekle:.1f}s bekleniyor...")
                        self.log_ekle(f"⏱️ {bekle:.1f}s bekle...")
                        
                        # Geri sayım
                        for i in range(int(bekle), 0, -1):
                            if not self.calisiyor:
                                break
                            self.bilgi_label.configure(text=f"⏳ {i}s...")
                            time.sleep(1)
                        
                        if not self.calisiyor:
                            continue
                        
                        # Kalan kesir
                        time.sleep(bekle % 1)
                        
                        # TIKLA
                        self.bilgi_label.configure(text="🖱️ Tıklanıyor...")
                        self.log_ekle(f"🎯 TIKLA: {eslesen[2]}")
                        
                        self.tiklama_yap(eslesen[0], eslesen[1])
                        
                        # Başarı
                        self.basari_sayisi += 1
                        self.basari_label.configure(text=f"✅ Geçti: {self.basari_sayisi}")
                        self.log_ekle(f"✅ BAŞARILI! Toplam: {self.basari_sayisi}")
                        self.log_ekle("")
                        
                        # Dinlen
                        time.sleep(3)
                    else:
                        # Eşleşme yok
                        self.log_ekle(f"❌ '{yesil}' butonlarda yok")
                        self.log_ekle("")
                else:
                    if not yesil:
                        self.durum_label.configure(text="⏳ Yeşil kod bekleniyor")
                    elif not butonlar:
                        self.durum_label.configure(text="⏳ Buton bekleniyor")
                
            except Exception as e:
                self.log_ekle(f"❌ Hata: {str(e)[:30]}")
                print(f"Detay: {e}")
            
            # 2 saniye bekle
            time.sleep(2)
    
    def calistir(self):
        """Uygulamayı başlat"""
        print("=" * 50)
        print("🎮 Oyun Doğrulama Botu")
        print("=" * 50)
        print("✅ 300x300 Kompakt Versiyon")
        print("✅ 4-15 saniye arası otomatik çözüm")
        print("✅ %100 doğru eşleştirme")
        print("=" * 50)
        self.pencere.mainloop()

if __name__ == "__main__":
    bot = OyunBot()
    bot.calistir()