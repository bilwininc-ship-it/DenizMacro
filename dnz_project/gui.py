"""
DNZ (Dinamik Nesne Zamanlayıcı) - Grafik Arayüz Modülü
Modern ve profesyonel kullanıcı arayüzü
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from typing import Optional

import config
from engine import DNZEngine


class DNZInterface:
    """Ana GUI sınıfı"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(config.APP_NAME)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        
        # Motor örneği
        self.engine = DNZEngine(log_callback=self.add_log)
        self.worker_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        # Tema ayarları
        self.setup_theme()
        
        # Arayüz bileşenleri
        self.create_widgets()
        
        # Kapanış eventi
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_theme(self):
        """Tema ve stil ayarları"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Renkler
        bg_color = "#1e1e2e"
        fg_color = "#ffffff"
        accent_color = "#00aaff"
        
        self.root.configure(bg=bg_color)
        
        # Button stili
        style.configure(
            "DNZ.TButton",
            background=accent_color,
            foreground=fg_color,
            borderwidth=0,
            focuscolor='none',
            font=('Segoe UI', 10, 'bold')
        )
        
        style.map(
            "DNZ.TButton",
            background=[('active', '#0088cc')]
        )
        
        # Frame stili
        style.configure("DNZ.TFrame", background=bg_color)
        style.configure("DNZ.TLabel", background=bg_color, foreground=fg_color)
    
    def create_widgets(self):
        """Arayüz bileşenlerini oluşturur"""
        
        # Header Frame
        header_frame = ttk.Frame(self.root, style="DNZ.TFrame")
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_label = ttk.Label(
            header_frame,
            text=config.APP_NAME,
            style="DNZ.TLabel",
            font=('Segoe UI', 20, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(
            header_frame,
            text=f"v{config.APP_VERSION}",
            style="DNZ.TLabel",
            font=('Segoe UI', 10)
        )
        version_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Description
        desc_label = ttk.Label(
            self.root,
            text=config.APP_DESCRIPTION,
            style="DNZ.TLabel",
            font=('Segoe UI', 9)
        )
        desc_label.pack(pady=(0, 20))
        
        # Status Frame
        status_frame = ttk.Frame(self.root, style="DNZ.TFrame")
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        status_label = ttk.Label(
            status_frame,
            text="Durum:",
            style="DNZ.TLabel",
            font=('Segoe UI', 10, 'bold')
        )
        status_label.pack(side=tk.LEFT)
        
        self.status_text = tk.StringVar(value=config.STATUS_WAITING)
        self.status_value = ttk.Label(
            status_frame,
            textvariable=self.status_text,
            style="DNZ.TLabel",
            font=('Segoe UI', 10)
        )
        self.status_value.pack(side=tk.LEFT, padx=(10, 0))
        
        # Status indicator (LED)
        self.status_canvas = tk.Canvas(
            status_frame,
            width=20,
            height=20,
            bg="#1e1e2e",
            highlightthickness=0
        )
        self.status_canvas.pack(side=tk.LEFT, padx=(10, 0))
        self.status_indicator = self.status_canvas.create_oval(
            5, 5, 15, 15,
            fill="#666666",
            outline=""
        )
        
        # Control Buttons Frame
        button_frame = ttk.Frame(self.root, style="DNZ.TFrame")
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.start_button = ttk.Button(
            button_frame,
            text="Başlat",
            style="DNZ.TButton",
            command=self.start_engine,
            width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ttk.Button(
            button_frame,
            text="Duraklat",
            style="DNZ.TButton",
            command=self.pause_engine,
            width=15,
            state=tk.DISABLED
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="Durdur",
            style="DNZ.TButton",
            command=self.stop_engine,
            width=15,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Log Frame
        log_frame = ttk.Frame(self.root, style="DNZ.TFrame")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        log_label = ttk.Label(
            log_frame,
            text="İşlem Günlüğü:",
            style="DNZ.TLabel",
            font=('Segoe UI', 10, 'bold')
        )
        log_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Log text widget
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            bg="#2a2a3e",
            fg="#ffffff",
            font=('Consolas', 9),
            insertbackground="#ffffff",
            relief=tk.FLAT,
            borderwidth=2
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state=tk.DISABLED)
        
        # Footer Frame
        footer_frame = ttk.Frame(self.root, style="DNZ.TFrame")
        footer_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        footer_label = ttk.Label(
            footer_frame,
            text="© 2025 DNZ Assistant - Tüm hakları saklıdır",
            style="DNZ.TLabel",
            font=('Segoe UI', 8)
        )
        footer_label.pack()
    
    def add_log(self, message: str):
        """Log mesajı ekler"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
        # Renk kodlama
        if "[SUCCESS]" in message:
            start = self.log_text.index("end-2c linestart")
            end = self.log_text.index("end-1c")
            self.log_text.tag_add("success", start, end)
            self.log_text.tag_config("success", foreground=config.COLOR_SUCCESS)
        elif "[WARNING]" in message:
            start = self.log_text.index("end-2c linestart")
            end = self.log_text.index("end-1c")
            self.log_text.tag_add("warning", start, end)
            self.log_text.tag_config("warning", foreground=config.COLOR_WARNING)
        elif "[ERROR]" in message:
            start = self.log_text.index("end-2c linestart")
            end = self.log_text.index("end-1c")
            self.log_text.tag_add("error", start, end)
            self.log_text.tag_config("error", foreground=config.COLOR_ERROR)
    
    def update_status(self, status: str, color: str = "#666666"):
        """Durum göstergesini günceller"""
        self.status_text.set(status)
        self.status_canvas.itemconfig(self.status_indicator, fill=color)
    
    def start_engine(self):
        """Motoru başlatır"""
        if not self.is_running:
            # Hedef pencereye bağlan
            if not self.engine.auto_attach():
                messagebox.showwarning(
                    "Uyarı",
                    "Hedef pencere bulunamadı!\n\nLütfen oyunun çalıştığından emin olun."
                )
                return
            
            self.is_running = True
            self.engine.start()
            
            # Worker thread başlat
            self.worker_thread = threading.Thread(target=self.worker_loop, daemon=True)
            self.worker_thread.start()
            
            # UI güncellemeleri
            self.start_button.configure(state=tk.DISABLED)
            self.pause_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.NORMAL)
            self.update_status(config.STATUS_READY, config.COLOR_SUCCESS)
            
            # 2 saniye sonra aktif duruma geç
            self.root.after(2000, lambda: self.update_status(config.STATUS_ACTIVE, config.COLOR_SUCCESS))
    
    def pause_engine(self):
        """Motoru duraklatır/devam ettirir"""
        if self.engine.is_paused:
            self.engine.resume()
            self.pause_button.configure(text="Duraklat")
            self.update_status(config.STATUS_ACTIVE, config.COLOR_SUCCESS)
        else:
            self.engine.pause()
            self.pause_button.configure(text="Devam Et")
            self.update_status(config.STATUS_PAUSED, config.COLOR_WARNING)
    
    def stop_engine(self):
        """Motoru durdurur"""
        if self.is_running:
            self.is_running = False
            self.engine.stop()
            
            # UI güncellemeleri
            self.start_button.configure(state=tk.NORMAL)
            self.pause_button.configure(state=tk.DISABLED, text="Duraklat")
            self.stop_button.configure(state=tk.DISABLED)
            self.update_status(config.STATUS_WAITING, "#666666")
    
    def worker_loop(self):
        """Arka planda sürekli çalışan işçi döngüsü"""
        while self.is_running:
            try:
                self.engine.run_cycle()
                time.sleep(config.SCAN_INTERVAL)
            except Exception as e:
                self.add_log(f"[ERROR] Worker döngüsü hatası: {str(e)}")
                time.sleep(1)
    
    def on_closing(self):
        """Pencere kapatma eventi"""
        if self.is_running:
            if messagebox.askokcancel("Çıkış", "DNZ çalışıyor. Kapatmak istediğinizden emin misiniz?"):
                self.stop_engine()
                self.root.quit()
        else:
            self.root.quit()
    
    def run(self):
        """Arayüzü başlatır"""
        # Başlangıç log mesajı
        self.add_log(f"[INFO] {config.APP_NAME} v{config.APP_VERSION} başlatıldı")
        self.add_log(f"[INFO] {config.APP_DESCRIPTION}")
        self.add_log("[INFO] Başlamak için 'Başlat' butonuna tıklayın")
        
        self.root.mainloop()


def main():
    """Ana giriş noktası"""
    app = DNZInterface()
    app.run()


if __name__ == "__main__":
    main()