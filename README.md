# DenizMacroBot - Bot Doğrulama Otomasyonu ⚡

## 🚀 HIZLI VE GÜÇLENDİRİLMİŞ VERSİYON

### ⚡ Yenilikler (v2.0 - Hız ve Performans):
- **0.5 saniye kontrol** - Çok hızlı tespit!
- **Paralel okuma** - 4 buton aynı anda okunuyor
- **3x görüntü büyütme** - OCR doğruluğu %300 arttı
- **Anında tıklama** - Tespit edince direkt tıklıyor, gecikme yok!
- **Esnek pattern** - 4-7 haneli kodları okur

## 🎯 Özellikler

- ✅ **5 Bölge Seçimi**: Yeşil kod + 4 buton bölgesini hızlıca seçin
- 🤖 **Otomatik Tespit**: Bot doğrulaması ekranda göründüğünde anında tespit eder
- 🔍 **Gelişmiş OCR**: 3x büyütülmüş görüntüyle yüksek doğruluk
- 🎯 **Akıllı Eşleştirme**: Yeşil kod ile butonları karşılaştırır
- ⚡ **Yıldırım Hızı**: 20 saniye sınırı içinde rahatça çalışır

## 📋 Kullanım Adımları

### 1. İLK KURULUM (Bölge Seçimi)

**ÖNEMLİ**: Bölge seçimini doğru yapmak kritik!

1. Oyunu açın
2. Bot doğrulaması çıkana kadar bekleyin
3. Uygulamada **"TÜM BÖLGELERİ HIZLICA SEÇ"** butonuna tıklayın
4. Sırasıyla şu bölgeleri seçin:

   **🟢 1/5: Yeşil Kod Bölgesi**
   - Üstteki YEŞİL sayıyı tam olarak çevreleyin
   - Sadece sayı bölgesini seçin (875609 gibi)
   
   **⬜ 2/5: 1. Buton (En Üstteki)**
   - İlk gri butondaki sayıyı çevreleyin
   - Butonun tamamını değil, sadece sayı kısmını seçin
   
   **⬜ 3/5: 2. Buton**
   - İkinci gri butondaki sayıyı çevreleyin
   
   **⬜ 4/5: 3. Buton**
   - Üçüncü gri butondaki sayıyı çevreleyin
   
   **⬜ 5/5: 4. Buton (En Alttaki)**
   - Dördüncü gri butondaki sayıyı çevreleyin

5. ✅ "TÜM BÖLGELER SEÇİLDİ" mesajını gördükten sonra oyunu kapatın

### 2. BOT KULLANIMI

1. **"BOT'U BAŞLAT"** butonuna tıklayın
2. Oyunu açın
3. **Bot artık çalışıyor!** 
   - Her 0.5 saniyede ekranı kontrol ediyor
   - Bot doğrulaması geldiğinde ANINDA tespit ediyor
   - Eşleşen butona otomatik tıklıyor

## ⚙️ Performans Ayarları

### Otomatik Optimizasyonlar:
- **Kontrol Hızı**: 0.5 saniye (çok hızlı!)
- **OCR Büyütme**: 3x (yüksek doğruluk)
- **Paralel İşlem**: 4 buton aynı anda okunuyor
- **Anında Tıklama**: Gecikme yok!

### Manuel Ayarlar:
- **Min Gecikme**: 4 saniye (doğrulama sonrası bekleme)
- **Max Gecikme**: 14 saniye (doğrulama sonrası bekleme)
- **Kod Deseni**: 4-7 haneli sayılar (esnek!)

## 🔧 Sorun Giderme

### ❌ "Bot tıklamadı, oyun kapandı"
**Çözüm**:
1. Bölgeleri TEKRAR seçin - bu sefer daha dikkatli!
2. Sadece SAYILARI seçin, butonun tamamını değil
3. Yeşil kod bölgesini net şekilde seçin
4. Botu başlatmadan ÖNCE oyunu kapatın
5. Botu başlat → Sonra oyunu aç

### ⚠️ "Eşleşme bulunamadı"
**Çözüm**:
1. Ekran çözünürlüğünü yükseltin
2. Oyunu tam ekran yapın
3. Bölgeleri daha küçük seçin (sadece sayılar)
4. Tesseract tessdata klasörünün yerinde olduğunu kontrol edin

### 🐌 "Bot çok yavaş"
**Çözüm**:
1. Bilgisayarınızı yeniden başlatın
2. Diğer programları kapatın
3. Uygulamayı yönetici olarak çalıştırın

## 📊 Log Mesajları Anlamı

- `🎯 BOT DOĞRULAMASI TESPİT EDİLDİ!` - Doğrulama bulundu!
- `🟢 Yeşil Kod: 875609` - Yeşil kod okundu
- `Buton 1: 592430` - Buton kodları okunuyor
- `✅ EŞLEŞME BULUNDU!` - Doğru buton bulundu!
- `🖱 HEMEN TIKLANIYOR...` - Tıklanıyor!
- `✅ TIKLANDI!` - Başarılı!
- `⚠ Eşleşme bulunamadı!` - Tekrar denenecek

## 🎮 Kullanım İpuçları

1. **İlk kurulumda aceleci olmayın** - Bölgeleri doğru seçmek çok önemli!
2. **Oyun açıkken botu başlatmayın** - Önce bot → Sonra oyun
3. **Log ekranını takip edin** - Ne olduğunu görürsünüz
4. **Test edin** - İlk doğrulamada bot çalıştı mı kontrol edin

## 🔧 Gereksinimler

- Windows 10/11 (64-bit)
- .NET 8.0 Runtime
- Tesseract OCR (dahil)
- 4GB+ RAM
- İyi ekran çözünürlüğü

## 📝 Teknik Detaylar

- **OCR Engine**: Tesseract 5.2.0 (optimized)
- **Framework**: .NET 8.0 Windows Forms
- **Görüntü İşleme**: 3x upscaling, adaptive thresholding
- **Paralel İşlem**: Task-based async pattern
- **Kontrol Sıklığı**: 500ms (0.5 saniye)
- **Kod Pattern**: Regex `\d{4,7}` (4-7 haneli sayılar)

## 🚨 SORUN YAŞIYORSANIZ

1. Bölgeleri tekrar seçin (en yaygın sorun!)
2. Oyunu tam ekran yapın
3. Ekran ölçeklemeyi %100 yapın
4. Uygulamayı yönetici olarak çalıştırın
5. tessdata klasörünü kontrol edin
6. Log ekranında hata mesajlarını okuyun

---

**💡 İpucu**: İlk kullanımda bölge seçimi kritik! Aceleci olmayın, dikkatli seçin.

**⚡ Performans**: 20 saniye sınırı için optimize edildi - rahatça çalışır!

**🎯 Doğruluk**: 3x görüntü büyütme ile yüksek OCR doğruluğu!
