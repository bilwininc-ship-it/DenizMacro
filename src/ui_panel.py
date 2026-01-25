import customtkinter as ctk
from typing import Callable

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class UIPanel:
    """Modern arayüz - Kritik Mod"""
    
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("denizv1 Bot - KRİTİK MOD")
        self.window.geometry("360x450")
        self.window.resizable(False, False)
        
        self.is_running = False
        self.success_count = 0
        self.fail_count = 0
        self._create_widgets()
        
    def _create_widgets(self):
        """Arayüz elemanlarını oluştur"""
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Başlık
        ctk.CTkLabel(
            main_frame, 
            text="🎮 denizv1 Bot", 
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            main_frame, 
            text="KRİTİK MOD - %100 Kesinlik", 
            font=ctk.CTkFont(size=11), 
            text_color="yellow"
        ).pack(pady=(0, 15))
        
        # Başlat/Durdur butonu
        self.start_button = ctk.CTkButton(
            main_frame,
            text="Sistemi Başlat",
            command=self._toggle_system,
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            corner_radius=10
        )
        self.start_button.pack(pady=10, padx=20, fill="x")
        
        # Durum etiketi
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Durum: Beklemede",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(pady=8)
        
        # İstatistik frame
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.pack(pady=10, padx=20, fill="x")
        
        # Başarı sayacı
        self.success_label = ctk.CTkLabel(
            stats_frame,
            text="✅ Başarı: 0",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4caf50"
        )
        self.success_label.pack(side="left", padx=10, pady=8)
        
        # Atlama sayacı
        self.fail_label = ctk.CTkLabel(
            stats_frame,
            text="❌ Atla: 0",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#ff9800"
        )
        self.fail_label.pack(side="right", padx=10, pady=8)
        
        # Bilgi etiketi
        self.info_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.info_label.pack(pady=5)
        
        # Log alanı
        self.log_text = ctk.CTkTextbox(main_frame, height=150, width=320)
        self.log_text.pack(pady=10, padx=10)
        self.log_text.configure(state="disabled")
        
    def _toggle_system(self):
        """Sistemi başlat/durdur"""
        self.is_running = not self.is_running
        
        if self.is_running:
            self.start_button.configure(text="Sistemi Durdur", fg_color="#d32f2f")
            self.update_status("Sistem Aktif", "green")
        else:
            self.start_button.configure(text="Sistemi Başlat", fg_color="#1f6aa5")
            self.update_status("Beklemede", "gray")
            
    def update_status(self, message: str, color: str = "white"):
        """Durum mesajını güncelle"""
        color_map = {
            "green": "#4caf50",
            "red": "#f44336",
            "yellow": "#ff9800",
            "gray": "#9e9e9e",
            "white": "white"
        }
        
        self.status_label.configure(
            text=f"Durum: {message}",
            text_color=color_map.get(color, "white")
        )
        
    def update_success_count(self):
        """Başarı sayacını artır"""
        self.success_count += 1
        self.success_label.configure(text=f"✅ Başarı: {self.success_count}")
    
    def update_fail_count(self):
        """Atlama sayacını artır"""
        self.fail_count += 1
        self.fail_label.configure(text=f"❌ Atla: {self.fail_count}")
        
    def update_info(self, message: str):
        """Bilgi mesajını güncelle"""
        self.info_label.configure(text=message)
    
    def add_log(self, message: str):
        """Log mesajı ekle"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        
    def set_start_callback(self, callback: Callable):
        """Başlat butonu callback'i ayarla"""
        self.start_button.configure(command=callback)
        
    def run(self):
        """Arayüzü başlat"""
        self.window.mainloop()
        
    def is_system_running(self) -> bool:
        """Sistem çalışıyor mu?"""
        return self.is_running