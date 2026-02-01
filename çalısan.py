import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import time
import os
from datetime import datetime
import win32gui
import win32ui
import win32con

class CaptchaDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot Doğrulama Yakalayıcı v5.0 - Şablon Öğrenme")
        self.root.geometry("750x700")
        self.root.resizable(False, False)
        
        # Değişkenler
        self.is_running = False
        self.window_handle = None
        self.window_name = None
        self.capture_count = 0
        self.check_interval = 1.0
        self.save_folder = os.path.join(os.getcwd(), "captures")
        self.last_capture_path = None
        
        # Şablon bilgileri
        self.template_region = None  # (x1, y1, x2, y2)
        self.template_features = None  # Kaydedilen özellikler
        self.last_capture_time = 0
        self.cooldown = 4
        
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Bilgi Paneli
        info_frame = tk.LabelFrame(self.root, text="Durum Bilgisi", padx=10, pady=10)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = tk.Label(info_frame, text="Durum: Hazır", 
                                     font=("Arial", 11, "bold"), fg="blue")
        self.status_label.pack(anchor="w")
        
        self.window_label = tk.Label(info_frame, text="Oyun: Seçilmedi", 
                                     font=("Arial", 10))
        self.window_label.pack(anchor="w")
        
        self.template_label = tk.Label(info_frame, text="Captcha Şablonu: Yok", 
                                       font=("Arial", 10))
        self.template_label.pack(anchor="w")
        
        self.count_label = tk.Label(info_frame, text="Yakalanan: 0", 
                                    font=("Arial", 10))
        self.count_label.pack(anchor="w")
        
        self.match_label = tk.Label(info_frame, text="Son Kontrol: -", 
                                    font=("Arial", 9), fg="gray")
        self.match_label.pack(anchor="w")
        
        # Adım Paneli
        steps_frame = tk.LabelFrame(self.root, text="KULLANIM ADIMLARI", padx=10, pady=10)
        steps_frame.pack(fill="x", padx=10, pady=5)
        
        steps_text = tk.Label(steps_frame, 
                             text="1️⃣ Valen2 oyununu seç\n"
                                  "2️⃣ Oyunda captcha açık olmalı!\n"
                                  "3️⃣ 'Captcha Penceresini Seç' ile captcha'yı çerçevele\n"
                                  "4️⃣ 'İzlemeyi Başlat' - Program aynı pencereyi arar",
                             font=("Arial", 9), justify="left", fg="green")
        steps_text.pack(pady=5)
        
        # Kontrol Paneli
        control_frame = tk.LabelFrame(self.root, text="Kontroller", padx=10, pady=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Oyun seçimi
        btn_row1 = tk.Frame(control_frame)
        btn_row1.pack(fill="x", pady=5)
        
        self.select_window_btn = tk.Button(btn_row1, text="🎮 Valen2'yi Seç", 
                                          command=self.select_window,
                                          bg="#9C27B0", fg="white", 
                                          font=("Arial", 11, "bold"),
                                          width=25, height=2)
        self.select_window_btn.pack(side="left", padx=5)
        
        self.select_captcha_btn = tk.Button(btn_row1, text="📐 Captcha Penceresini Seç",
                                           command=self.select_captcha_region,
                                           bg="#FF5722", fg="white",
                                           font=("Arial", 11, "bold"),
                                           width=25, height=2,
                                           state="disabled")
        self.select_captcha_btn.pack(side="left", padx=5)
        
        # Test ve başlat
        btn_row2 = tk.Frame(control_frame)
        btn_row2.pack(fill="x", pady=5)
        
        self.test_btn = tk.Button(btn_row2, text="📸 Test Tespiti",
                                 command=self.test_detection,
                                 font=("Arial", 10, "bold"),
                                 width=25, height=2,
                                 state="disabled")
        self.test_btn.pack(side="left", padx=5)
        
        self.start_btn = tk.Button(btn_row2, text="▶ İZLEMEYİ BAŞLAT", 
                                   command=self.toggle_detection,
                                   bg="#4CAF50", fg="white",
                                   font=("Arial", 11, "bold"),
                                   width=25, height=2, 
                                   state="disabled")
        self.start_btn.pack(side="left", padx=5)
        
        # Ayarlar
        settings_frame = tk.LabelFrame(self.root, text="Ayarlar", padx=10, pady=10)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        settings_grid = tk.Frame(settings_frame)
        settings_grid.pack()
        
        tk.Label(settings_grid, text="Kontrol Sıklığı (sn):").grid(row=0, column=0, padx=5)
        self.interval_var = tk.DoubleVar(value=1.0)
        tk.Spinbox(settings_grid, from_=0.5, to=3.0, increment=0.5,
                  textvariable=self.interval_var, width=8).grid(row=0, column=1, padx=5)
        
        tk.Label(settings_grid, text="Eşleşme Hassasiyeti:").grid(row=0, column=2, padx=5)
        self.similarity_var = tk.DoubleVar(value=0.75)
        tk.Scale(settings_grid, from_=0.6, to=0.95, resolution=0.05,
                orient="horizontal", variable=self.similarity_var, 
                length=150).grid(row=0, column=3, padx=5)
        
        tk.Button(settings_grid, text="📁 Klasör", 
                 command=self.select_folder, width=10).grid(row=0, column=4, padx=5)
        tk.Button(settings_grid, text="🗑️ Temizle",
                 command=self.clear_data, width=10).grid(row=0, column=5, padx=5)
        
        # Önizleme
        preview_frame = tk.LabelFrame(self.root, text="Önizleme", padx=10, pady=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.preview_label = tk.Label(preview_frame, text="Henüz görüntü yok", 
                                     bg="gray", fg="white", font=("Arial", 11))
        self.preview_label.pack(fill="both", expand=True)
    
    def get_window_list(self):
        """Görünür pencereleri listele"""
        windows = []
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows.append((hwnd, title))
        win32gui.EnumWindows(callback, None)
        return windows
    
    def select_window(self):
        """Oyun penceresi seç"""
        windows = self.get_window_list()
        
        if not windows:
            messagebox.showerror("Hata", "Pencere bulunamadı!")
            return
        
        select_win = tk.Toplevel(self.root)
        select_win.title("Valen2'yi Seç")
        select_win.geometry("550x450")
        select_win.transient(self.root)
        select_win.grab_set()
        
        tk.Label(select_win, text="Valen2 oyun penceresini seç:", 
                font=("Arial", 11, "bold")).pack(pady=10)
        
        frame = tk.Frame(select_win)
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, 
                            font=("Arial", 10), height=15)
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        
        for idx, (hwnd, title) in enumerate(windows):
            listbox.insert(tk.END, title)
            if "valen" in title.lower():
                listbox.itemconfig(idx, bg="lightgreen")
                listbox.selection_set(idx)
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                self.window_handle, self.window_name = windows[idx]
                self.window_label.config(text=f"Oyun: {self.window_name}")
                self.select_captcha_btn.config(state="normal")
                messagebox.showinfo("Başarılı ✅", 
                                   f"Oyun seçildi:\n{self.window_name}\n\n"
                                   "Şimdi:\n"
                                   "1. Oyunda captcha'yı aç\n"
                                   "2. '📐 Captcha Penceresini Seç' butonuna bas")
                select_win.destroy()
        
        tk.Button(select_win, text="✓ Seç", command=on_select, 
                 bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                 width=15, height=2).pack(pady=10)
    
    def capture_window(self):
        """Pencere görüntüsü al"""
        try:
            left, top, right, bottom = win32gui.GetWindowRect(self.window_handle)
            width = right - left
            height = bottom - top
            
            hwndDC = win32gui.GetWindowDC(self.window_handle)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
            
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype=np.uint8)
            img.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)
            
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.window_handle, hwndDC)
            
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return img
            
        except Exception as e:
            print(f"Yakalama hatası: {e}")
            return None
    
    def select_captcha_region(self):
        """Captcha bölgesini seç"""
        messagebox.showinfo("Captcha Seçimi",
                          "ŞİMDİ:\n\n"
                          "1. Oyunda captcha AÇIK olmalı!\n"
                          "2. 'Tamam'a bas\n"
                          "3. Mouse ile CAPTCHA PENCERESİNİ çerçevele\n"
                          "   (Tüm captcha penceresi: başlık + sayılar + butonlar)\n"
                          "4. Program bu pencereyi öğrenecek!")
        
        # Pencere görüntüsünü al
        full_img = self.capture_window()
        if full_img is None:
            messagebox.showerror("Hata", "Oyun penceresi yakalanamadı!")
            return
        
        # Seçim penceresi
        selector = RegionSelector(full_img, "CAPTCHA PENCERESİNİ çerçevele")
        self.root.wait_window(selector.top)
        
        if selector.region:
            x1, y1, x2, y2 = selector.region
            self.template_region = (x1, y1, x2, y2)
            
            # Şablon bölgesini al
            template_img = full_img[y1:y2, x1:x2]
            
            # Şablon özelliklerini çıkar ve kaydet
            self.template_features = self.extract_features(template_img)
            
            # Kaydet
            template_path = os.path.join(self.save_folder, "template_captcha.png")
            cv2.imwrite(template_path, template_img)
            
            width = x2 - x1
            height = y2 - y1
            
            self.template_label.config(
                text=f"Captcha Şablonu: {width}x{height} piksel - Konum: ({x1},{y1})")
            
            self.test_btn.config(state="normal")
            self.start_btn.config(state="normal")
            
            # Önizleme göster
            self.show_preview(template_img, "Captcha Şablonu Kaydedildi")
            
            messagebox.showinfo("Başarılı ✅",
                              f"Captcha şablonu öğrenildi!\n\n"
                              f"Boyut: {width}x{height} piksel\n"
                              f"Konum: ({x1}, {y1})\n\n"
                              f"Özellikler:\n"
                              f"- Yeşil oran: {self.template_features['green_ratio']:.1f}%\n"
                              f"- Koyu oran: {self.template_features['dark_ratio']:.1f}%\n\n"
                              "'📸 Test Tespiti' ile kontrol et!")
    
    def extract_features(self, image):
        """Görüntüden ayırt edici özellikler çıkar"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Yeşil renk oranı
        lower_green = np.array([35, 80, 80])
        upper_green = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        green_ratio = (np.sum(green_mask > 0) / image.size) * 100
        
        # Koyu renk oranı (captcha arkaplanı)
        lower_dark = np.array([0, 0, 0])
        upper_dark = np.array([180, 255, 80])
        dark_mask = cv2.inRange(hsv, lower_dark, upper_dark)
        dark_ratio = (np.sum(dark_mask > 0) / image.size) * 100
        
        # Histogram (renk dağılımı)
        hist = cv2.calcHist([hsv], [0, 1], None, [30, 32], [0, 180, 0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        
        return {
            'green_ratio': green_ratio,
            'dark_ratio': dark_ratio,
            'histogram': hist,
            'size': (image.shape[1], image.shape[0])
        }
    
    def find_captcha_in_image(self, image):
        """Görüntüde captcha penceresini ara"""
        if self.template_region is None or self.template_features is None:
            return None, 0
        
        x1, y1, x2, y2 = self.template_region
        width = x2 - x1
        height = y2 - y1
        
        # Aynı bölgeyi kontrol et (konum değişmemiş olabilir)
        if y2 <= image.shape[0] and x2 <= image.shape[1]:
            region = image[y1:y2, x1:x2]
            features = self.extract_features(region)
            similarity = self.calculate_similarity(features, self.template_features)
            
            if similarity >= self.similarity_var.get():
                return self.template_region, similarity
        
        # Sliding window ile ara (konum değişmişse)
        best_match = None
        best_similarity = 0
        
        step = 30  # Her 30 pikselde bir kontrol et (daha hızlı)
        
        for y in range(0, image.shape[0] - height, step):
            for x in range(0, image.shape[1] - width, step):
                region = image[y:y+height, x:x+width]
                features = self.extract_features(region)
                similarity = self.calculate_similarity(features, self.template_features)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = (x, y, x+width, y+height)
                
                # Yeterince iyi bulundu, devam etme
                if similarity >= 0.9:
                    return best_match, similarity
        
        if best_similarity >= self.similarity_var.get():
            return best_match, best_similarity
        
        return None, best_similarity
    
    def calculate_similarity(self, features1, features2):
        """İki özellik seti arasındaki benzerliği hesapla"""
        # Boyut kontrolü
        size_diff = abs(features1['size'][0] - features2['size'][0]) + \
                   abs(features1['size'][1] - features2['size'][1])
        if size_diff > 50:  # Boyut çok farklı
            return 0
        
        # Yeşil oran benzerliği
        green_sim = 1 - abs(features1['green_ratio'] - features2['green_ratio']) / 100
        
        # Koyu oran benzerliği
        dark_sim = 1 - abs(features1['dark_ratio'] - features2['dark_ratio']) / 100
        
        # Histogram benzerliği (renk dağılımı)
        hist_sim = cv2.compareHist(features1['histogram'], features2['histogram'], 
                                   cv2.HISTCMP_CORREL)
        
        # Ağırlıklı ortalama
        similarity = (green_sim * 0.3 + dark_sim * 0.3 + hist_sim * 0.4)
        
        return max(0, min(1, similarity))
    
    def test_detection(self):
        """Test tespiti"""
        img = self.capture_window()
        if img is None:
            messagebox.showerror("Hata", "Pencere yakalanamadı!")
            return
        
        # Captcha'yı ara
        region, similarity = self.find_captcha_in_image(img)
        
        if region:
            x1, y1, x2, y2 = region
            captcha_img = img[y1:y2, x1:x2]
            
            # İşaretle
            test_img = img.copy()
            cv2.rectangle(test_img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(test_img, f"Benzerlik: {similarity:.0%}", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Kaydet
            test_path = os.path.join(self.save_folder, "test_detected.png")
            cv2.imwrite(test_path, test_img)
            
            # Önizleme
            self.show_preview(captcha_img, f"Test ✅ - Benzerlik: {similarity:.0%}")
            
            messagebox.showinfo("Test Başarılı ✅",
                              f"CAPTCHA BULUNDU!\n\n"
                              f"Benzerlik: {similarity:.0%}\n"
                              f"Konum: ({x1}, {y1})\n"
                              f"Boyut: {x2-x1}x{y2-y1}\n\n"
                              f"Eşik: {self.similarity_var.get():.0%}\n\n"
                              f"✅ Program captcha'yı tanıyor!\n"
                              f"'İzlemeyi Başlat' butonuna basabilirsin.\n\n"
                              f"Test dosyası: test_detected.png")
        else:
            self.show_preview(img, f"Test ❌ - En İyi: {similarity:.0%}")
            messagebox.showwarning("Test Başarısız ❌",
                                 f"Captcha bulunamadı!\n\n"
                                 f"En yüksek benzerlik: {similarity:.0%}\n"
                                 f"Eşik: {self.similarity_var.get():.0%}\n\n"
                                 f"Çözümler:\n"
                                 f"1. Oyunda captcha açık mı kontrol et\n"
                                 f"2. Eşleşme hassasiyetini düşür (0.65-0.70)\n"
                                 f"3. Captcha seçimini tekrarla\n"
                                 f"4. Captcha penceresi hareket etmişse yeniden seç")
    
    def toggle_detection(self):
        """İzlemeyi başlat/durdur"""
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(text="⏸ DURDUR", bg="#f44336")
            self.status_label.config(text="Durum: Aktif İzleniyor... 🔍", fg="green")
            
            self.check_interval = self.interval_var.get()
            
            thread = threading.Thread(target=self.detection_loop, daemon=True)
            thread.start()
        else:
            self.is_running = False
            self.start_btn.config(text="▶ İZLEMEYİ BAŞLAT", bg="#4CAF50")
            self.status_label.config(text="Durum: Durduruldu", fg="orange")
    
    def detection_loop(self):
        """Ana kontrol döngüsü"""
        while self.is_running:
            try:
                # Cooldown kontrolü
                if time.time() - self.last_capture_time < self.cooldown:
                    time.sleep(0.5)
                    continue
                
                # Görüntü al
                img = self.capture_window()
                if img is None:
                    time.sleep(self.check_interval)
                    continue
                
                # Captcha ara
                region, similarity = self.find_captcha_in_image(img)
                
                # UI güncelle
                status_text = f"Son Kontrol: {datetime.now().strftime('%H:%M:%S')} - "
                if region:
                    x1, y1, x2, y2 = region
                    status_text += f"✅ BULUNDU! ({x1},{y1}) - {similarity:.0%}"
                    status_color = "green"
                else:
                    status_text += f"❌ Bulunamadı (En iyi: {similarity:.0%})"
                    status_color = "gray"
                
                self.root.after(0, self.match_label.config,
                               {"text": status_text, "fg": status_color})
                
                # Bulunduysa kaydet
                if region:
                    x1, y1, x2, y2 = region
                    captcha_img = img[y1:y2, x1:x2]
                    self.save_captcha(captcha_img, similarity)
                    self.last_capture_time = time.time()
                
            except Exception as e:
                print(f"Döngü hatası: {e}")
            
            time.sleep(self.check_interval)
    
    def save_captcha(self, captcha_img, similarity):
        """Captcha'yı kaydet"""
        try:
            # Eski sil
            if self.last_capture_path and os.path.exists(self.last_capture_path):
                os.remove(self.last_capture_path)
            
            # Yeni kaydet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captcha_{timestamp}.png"
            filepath = os.path.join(self.save_folder, filename)
            cv2.imwrite(filepath, captcha_img)
            
            self.last_capture_path = filepath
            self.capture_count += 1
            
            self.root.after(0, self.update_ui, captcha_img, similarity)
            
        except Exception as e:
            print(f"Kayıt hatası: {e}")
    
    def update_ui(self, img, similarity):
        """UI güncelle"""
        self.count_label.config(text=f"Yakalanan: {self.capture_count}")
        self.show_preview(img, f"Captcha #{self.capture_count} - {similarity:.0%}")
    
    def show_preview(self, cv_img, title=""):
        """Önizleme göster"""
        try:
            img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_pil.thumbnail((500, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img_pil)
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo
        except Exception as e:
            print(f"Önizleme hatası: {e}")
    
    def select_folder(self):
        folder = filedialog.askdirectory(title="Kayıt Klasörü")
        if folder:
            self.save_folder = folder
            messagebox.showinfo("Klasör", f"✓ {folder}")
    
    def clear_data(self):
        if messagebox.askyesno("Temizle", "Şablon ve sayaç silinecek. Emin misin?"):
            self.template_region = None
            self.template_features = None
            self.capture_count = 0
            
            self.template_label.config(text="Captcha Şablonu: Yok")
            self.count_label.config(text="Yakalanan: 0")
            self.preview_label.config(image="", text="Henüz görüntü yok")
            
            self.select_captcha_btn.config(state="normal")
            self.test_btn.config(state="disabled")
            self.start_btn.config(state="disabled")
            
            messagebox.showinfo("Temizlendi", "Şablon silindi!")


class RegionSelector:
    """Görüntü üzerinde bölge seçimi"""
    def __init__(self, cv_image, instruction):
        self.top = tk.Toplevel()
        self.top.title("Bölge Seç")
        
        # OpenCV görüntüsünü PIL'e çevir
        img_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        self.pil_image = Image.fromarray(img_rgb)
        
        # Ekrana sığdır
        screen_w = self.top.winfo_screenwidth()
        screen_h = self.top.winfo_screenheight()
        
        scale = min(screen_w / self.pil_image.width * 0.9, 
                   screen_h / self.pil_image.height * 0.9)
        
        if scale < 1:
            new_w = int(self.pil_image.width * scale)
            new_h = int(self.pil_image.height * scale)
            self.display_image = self.pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
            self.scale_factor = scale
        else:
            self.display_image = self.pil_image
            self.scale_factor = 1.0
        
        self.photo = ImageTk.PhotoImage(self.display_image)
        
        # Canvas
        self.canvas = tk.Canvas(self.top, width=self.display_image.width, 
                               height=self.display_image.height, cursor="cross")
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        
        tk.Label(self.top, text=instruction, 
                font=("Arial", 11, "bold"), fg="red", bg="yellow").pack(pady=5)
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.region = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.top.bind("<Escape>", lambda e: self.top.destroy())
    
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=3
        )
    
    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
    
    def on_release(self, event):
        # Koordinatları orijinal boyuta çevir
        x1 = int(min(self.start_x, event.x) / self.scale_factor)
        y1 = int(min(self.start_y, event.y) / self.scale_factor)
        x2 = int(max(self.start_x, event.x) / self.scale_factor)
        y2 = int(max(self.start_y, event.y) / self.scale_factor)
        
        self.region = (x1, y1, x2, y2)
        self.top.destroy()


def main():
    root = tk.Tk()
    app = CaptchaDetector(root)
    root.mainloop()


if __name__ == "__main__":
    main()