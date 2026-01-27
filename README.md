# DenizMacroBot - Bot Doğrulama Otomasyonu

## 🎯 Özellikler

Bu uygulama, oyun içi bot doğrulamalarını otomatik olarak çözer:

- ✅ **5 Bölge Seçimi**: Yeşil kod + 4 buton bölgesini hızlıca seçin
- 🤖 **Otomatik Tespit**: Bot doğrulaması ekranda göründüğünde anında tespit eder
- 🔍 **OCR Tabanlı**: Tesseract OCR ile sayıları okur
- 🎯 **Akıllı Eşleştirme**: Yeşil kod ile butonları karşılaştırır ve doğru butona tıklar
- ⚡ **Hızlı İşlem**: 20 saniye sınırı içinde güvenle çalışır (4-14 saniye arası)

## 📋 Kullanım Adımları

### 1. İlk Kurulum (Bölge Seçimi)

1. Oyunu açın
2. Bot doğrulaması çıkana kadar bekleyin
3. Uygulamada **"TÜM BÖLGELERİ HIZLICA SEÇ"** butonuna tıklayın
4. Sırasıyla şu bölgeleri seçin:
   - **1/5**: Yeşil kod bölgesi (üstteki yeşil sayı)
   - **2/5**: 1. Buton bölgesi (en üstteki gri buton)
   - **3/5**: 2. Buton bölgesi
   - **4/5**: 3. Buton bölgesi
   - **5/5**: 4. Buton bölgesi (en alttaki gri buton)
5. Tüm bölgeler seçildikten sonra oyunu kapatın

### 2. Bot Kullanımı

1. Uygulamada **"BOT'U BAŞLAT"** butonuna tıklayın
2. Oyunu açın
3. Artık bot doğrulaması her çıktığında **bot otomatik olarak halledecek**
4. Bot sürekli ekranı izler ve doğrulama tespit edildiğinde:
   - Yeşil kodu okur
   - 4 butonu okur
   - Eşleşeni bulur
   - Otomatik tıklar

## ⚙️ Ayarlar

- **Min Gecikme**: Bot doğrulaması çözüldükten sonra minimum bekleme süresi (varsayılan: 4 saniye)
- **Max Gecikme**: Bot doğrulaması çözüldükten sonra maksimum bekleme süresi (varsayılan: 14 saniye)
- **Kontrol Aralığı**: Bot doğrulaması yokken kontrol sıklığı (varsayılan: 1.5 saniye)

## 🔧 Gereksinimler

- Windows 10/11
- .NET 8.0 Runtime
- Tesseract OCR (tessdata klasörü uygulamayla birlikte gelir)

## 📝 Notlar

- Bot doğrulaması 20 saniye içinde çözülmezse oyun kapanır
- Uygulama 4-14 saniye içinde güvenle işlemi tamamlar
- Tüm bölgeleri doğru seçtiğinizden emin olun
- OCR doğruluğu için ekran çözünürlüğünü yüksek tutun

## 🛠️ Teknik Detaylar

- **OCR Engine**: Tesseract 5.2.0
- **Framework**: .NET 8.0 Windows Forms
- **Görüntü İşleme**: OpenCvSharp4
- **Sayı Deseni**: 6 haneli kodlar (\d{6})

## 📞 Destek

Sorun yaşarsanız:
1. Bölgeleri tekrar seçmeyi deneyin
2. Oyun çözünürlüğünü kontrol edin
3. tessdata klasörünün yerinde olduğunu kontrol edin
4. Uygulamayı yönetici olarak çalıştırın

---

**Önemli**: Bu araç sadece eğitim amaçlıdır. Kullanımdan doğabilecek sorumluluk kullanıcıya aittir.
