# engine.py'ye EKLENECEK - run_cycle metodunu değiştir

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
            self.log(f"🎯 YENİ CAPTCHA ALGILANDI!", "SUCCESS")
            return self.process_quiz(answer)
        
        # Captcha yoksa sessizce devam et (spam logları önlemek için)
        # Her 10 saniyede bir "Sistem aktif" logu
        import time
        current_time = time.time()
        if not hasattr(self, '_last_active_log'):
            self._last_active_log = current_time
        
        if current_time - self._last_active_log > 10:
            self.log("⏳ Sistem aktif, captcha bekleniyor...", "INFO")
            self._last_active_log = current_time
        
    except Exception as e:
        self.log(f"Döngü hatası: {str(e)}", "ERROR")
    
    return False


# EKSTRA: find_quiz_answer metodunu da güncelleyelim
def find_quiz_answer(self) -> Optional[str]:
    """
    AUTOBAN_QUIZ_ANSWER değerini RAM'den okur
    Captcha gösterilene kadar None döner, gösterildiğinde kodu yakalar
    """
    if not self.memory_scanner:
        return None
    
    try:
        # Eğer daha önce adres bulunmuşsa direkt oradan oku
        if self.quiz_answer_address:
            # Bellekten 6 haneli kodu oku
            data = self.memory_scanner.read_memory(
                self.quiz_answer_address + self.memory_scanner.PY27_STRING_HEADER_SIZE,
                6
            )
            if data and len(data) == 6:
                try:
                    code = data.decode('utf-8', errors='ignore')
                    if code.isdigit():
                        return code
                except:
                    pass
            
            # Adres geçersiz olmuş, yeniden tara
            self.quiz_answer_address = None
        
        # İlk kez veya adres geçersizse, bellek taraması yap
        # ANCAK çok sık tarama yapma (performans için)
        import time
        current_time = time.time()
        
        if not hasattr(self, '_last_scan_time'):
            self._last_scan_time = 0
        
        # Her 5 saniyede bir tara
        if current_time - self._last_scan_time < 5:
            return None
        
        self._last_scan_time = current_time
        
        # Sessiz tarama (her seferinde log basma)
        if not hasattr(self, '_scan_logged'):
            self.log("🔍 AUTOBAN_QUIZ_ANSWER değişkeni aranıyor...", "INFO")
            self._scan_logged = True
        
        found_address = self.memory_scanner.find_autoban_variable()
        
        if found_address:
            self.quiz_answer_address = found_address
            self.log(f"✓ AUTOBAN değişkeni bulundu: 0x{found_address:08X}", "SUCCESS")
            
            # Bulunan adresten kodu oku
            data = self.memory_scanner.read_memory(
                found_address + self.memory_scanner.PY27_STRING_HEADER_SIZE,
                6
            )
            if data and len(data) == 6:
                try:
                    code = data.decode('utf-8', errors='ignore')
                    if code.isdigit():
                        return code
                except:
                    pass
        
        return None
        
    except Exception as e:
        self.log(f"Bellek okuma hatası: {str(e)}", "ERROR")
        return None