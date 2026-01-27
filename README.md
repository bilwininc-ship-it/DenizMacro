# DenizMacroBot - Template Matching Edition

## 🎯 Özellikler (Features)

### ✅ Yeni Template Matching Sistemi
Bu versiyon, **OCR yerine OpenCvSharp4 Template Matching** kullanır:

- **Tek Bölge Seçimi**: Tüm doğrulama dialogunu bir kez seçin
- **Dinamik Kırpma**: Otomatik olarak:
  - Yeşil kod: %20-40 yükseklik
  - Butonlar: %40-90 yükseklik  
  - 4 buton: Otomatik 4 eşit parçaya bölünür
- **Görüntü İşleme**: 
  - Grayscale dönüşümü
  - Binary Threshold (ilk deneme)
  - Canny Edge Detection (fallback)
  - Renkleri görmezden gelir, sadece sayı şekillerine odaklanır
- **Template Matching**: 
  - OpenCV `MatchTemplate` (CCoeffNormed)
  - Ayarlanabilir eşik değeri (%85 varsayılan)
  - Her buton için benzerlik skoru
- **Akıllı Tıklama**:
  - ±5 piksel rastgele sapma
  - 4-14 saniye rastgele gecikme
  - 5 saniyede bir kontrol döngüsü
  - Eşik altındaki skorlarda tıklama YOK (ban koruması)

---

## 📋 Gereksinimler (Requirements)

- **Windows 10/11** (64-bit)
- **.NET 8.0 SDK** ([Download](https://dotnet.microsoft.com/download/dotnet/8.0))
- **Visual Studio 2022** (opsiyonel, önerilen)

### NuGet Paketleri (Otomatik yüklenecek):
- `OpenCvSharp4.Windows` 4.9.0 ✅
- `Newtonsoft.Json` 13.0.3 ✅
- ~~`Tesseract` 5.2.0~~ ❌ (Artık kullanılmıyor)

---

## 🔧 Kurulum ve Build (Installation & Build)

### Yöntem 1: Visual Studio ile
1. `DenizMacroBot.csproj` dosyasını Visual Studio 2022 ile açın
2. Solution Explorer'da projeye sağ tıklayın → **Restore NuGet Packages**
3. `Build` → `Build Solution` (veya `Ctrl+Shift+B`)
4. Çalıştır: `Debug` → `Start Debugging` (veya `F5`)

### Yöntem 2: Komut Satırı ile
```bash
cd /path/to/DenizMacroBot
dotnet restore
dotnet build --configuration Release
dotnet run
```

### Yayınlama (Publish - Tek EXE):
```bash
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
```
Çıktı: `bin/Release/net8.0-windows/win-x64/publish/DenizMacroBot.exe`

---

## 🚀 Kullanım Kılavuzu (Usage Guide)

### 1. Ana Pencereyi Seçin
- **"🎯 ANA PENCEREYİ SEÇ"** butonuna tıklayın
- Ekranda oyunun **tüm doğrulama dialogunu** çizin (yeşil kod + 4 buton dahil)
- ESC tuşu ile iptal edebilirsiniz

### 2. Ayarları Yapılandırın
- **Eşleşme Eşiği**: %50-%100 (varsayılan %85)
  - Yüksek değer = daha sıkı eşleşme (daha güvenli)
  - Düşük değer = daha esnek eşleşme (daha riskli)
- **Min/Max Gecikme**: Tıklama öncesi rastgele bekleme süresi (4-14 sn önerilen)

### 3. Bot'u Başlatın
- **"▶ BOT'U BAŞLAT"** butonuna tıklayın
- Bot her 5 saniyede bir kontrol yapar
- Eşleşme bulduğunda otomatik tıklar
- Eşik altındaki skorlarda **tıklama yapmaz** (yanlış tıklama koruması)

### 4. Debug Resimleri Kaydet (Opsiyonel)
- **"💾 Debug Resimleri Kaydet"** butonuna tıklayın
- Masaüstünde `DenizBot_Debug_YYYYMMDD_HHMMSS` klasörü oluşturulur
- İçerik:
  - Orijinal kırpılmış resimler
  - Binary Threshold işlenmiş resimler
  - Canny Edge Detection işlenmiş resimler
- Eşleşme sorunlarını analiz etmek için kullanılır

---

## 📁 Proje Yapısı (Project Structure)

```
DenizMacroBot/
├── Program.cs                      # Ana giriş noktası
├── Form1.cs                        # Ana UI (Template Matching versiyonu) ⭐ YENİ
├── Form1.Designer.cs               # Form designer
├── DenizMacroBot.csproj            # Proje dosyası
├── Models/
│   └── BotConfig.cs               # Konfigürasyon modeli ⭐ GÜNCELLENDİ
├── Services/
│   ├── TemplateMatchingService.cs  # OpenCV template matching ⭐ YENİ
│   ├── ScreenCaptureService.cs     # Ekran yakalama
│   └── OCRService.cs               # (Artık kullanılmıyor)
├── Utils/
│   ├── MouseHelper.cs              # Doğal fare hareketi
│   └── RegionSelector.cs           # Bölge seçimi UI
└── config.json                     # Bot ayarları
```

---

## 🔍 Nasıl Çalışır? (How It Works)

### Template Matching Akışı:

```
1. ANA PENCERE YAKALAMA
   └─ Screenshot (user tarafından seçilen bölge)

2. DİNAMİK KIRPMA
   ├─ Yeşil Kod: %20-40 yükseklik
   └─ Butonlar: %40-90 yükseklik
       └─ 4 eşit parçaya böl (her buton için)

3. GÖRÜNTÜ İŞLEME
   ├─ Grayscale dönüşümü
   ├─ Binary Threshold (ilk deneme)
   └─ Canny Edge Detection (düşük skor ise fallback)

4. TEMPLATE MATCHING
   ├─ Yeşil kod vs Buton 1: Skor = 0.72
   ├─ Yeşil kod vs Buton 2: Skor = 0.91 ✅
   ├─ Yeşil kod vs Buton 3: Skor = 0.65
   └─ Yeşil kod vs Buton 4: Skor = 0.58

5. KARAR VE TIKLA
   └─ Skor >= %85 ise → Tıkla (aksi halde bekle)
```

### OpenCV Metotları:
- `Cv2.CvtColor()` - Grayscale dönüşümü
- `Cv2.Threshold()` - Binary threshold
- `Cv2.Canny()` - Edge detection
- `Cv2.MatchTemplate()` - Template matching (CCoeffNormed)
- `Cv2.MinMaxLoc()` - En iyi eşleşme skorunu bul

---

## ⚙️ Konfigürasyon (config.json)

```json
{
  "mainWindowRegion": {
    "x": 100,
    "y": 100,
    "width": 800,
    "height": 600
  },
  "matchingThreshold": 0.85,
  "delayMin": 4000,
  "delayMax": 14000,
  "checkIntervalMs": 5000,
  "targetCodeTopPercent": 0.20,
  "targetCodeBottomPercent": 0.40,
  "buttonsAreaTopPercent": 0.40,
  "buttonsAreaBottomPercent": 0.90
}
```

### Parametreler:
- **mainWindowRegion**: Seçilen ana pencere koordinatları
- **matchingThreshold**: Eşleşme eşiği (0.0-1.0, 0.85 = %85)
- **delayMin/Max**: Tıklama öncesi gecikme aralığı (ms)
- **checkIntervalMs**: Kontrol döngüsü sıklığı (5000ms = 5 saniye)
- **targetCodeTopPercent**: Yeşil kod başlangıcı (0.20 = %20)
- **targetCodeBottomPercent**: Yeşil kod bitişi (0.40 = %40)
- **buttonsAreaTopPercent**: Butonlar başlangıcı (0.40 = %40)
- **buttonsAreaBottomPercent**: Butonlar bitişi (0.90 = %90)

---

## 🐛 Sorun Giderme (Troubleshooting)

### Problem: "Eşleşme bulunamadı"
**Çözüm**:
1. **Debug resimleri kaydet** butonuna tıklayın
2. `0_target_threshold.png` ve `X_buttonX_threshold.png` resimlerini inceleyin
3. Sayılar net görünüyorsa → Eşik değerini düşürün (%75-%80)
4. Sayılar bulanıksa → Ana pencere seçimini tekrarlayın (daha doğru çizin)
5. Arka plan gürültülüyse → Canny versiyonları kontrol edin

### Problem: "Yanlış butona tıklıyor"
**Çözüm**:
1. Eşik değerini yükseltin (%90-%95)
2. Ana pencere seçimini kontrol edin (tam doğrulama dialogu seçili mi?)
3. Oranları ayarlayın (`config.json`):
   - Yeşil kod daha yukarıdaysa: `targetCodeTopPercent = 0.15`
   - Butonlar daha aşağıdaysa: `buttonsAreaTopPercent = 0.45`

### Problem: OpenCV hatası
**Çözüm**:
1. NuGet paketlerini restore edin: `dotnet restore`
2. `OpenCvSharp4.Windows` versiyonu 4.9.0 olmalı
3. Native DLL'ler eksikse otomatik indirilir (ilk build sırasında)

---

## 📊 OCR vs Template Matching Karşılaştırması

| Özellik | OCR (Eski) | Template Matching (Yeni) |
|---------|------------|--------------------------|
| **Bölge Seçimi** | 5 ayrı bölge (yeşil + 4 buton) | 1 tek bölge (tüm dialog) ✅ |
| **Kırpma** | Manuel, sabit koordinatlar | Dinamik, orana dayalı ✅ |
| **Tanıma** | Tesseract OCR (metin okuma) | OpenCV (görüntü eşleştirme) ✅ |
| **Renk Bağımlılığı** | Yüksek (yeşil/gri fark eder) | Yok (sadece şekil) ✅ |
| **Hız** | Orta (OCR işleme) | Hızlı (piksel karşılaştırma) ✅ |
| **Doğruluk** | Orta (%70-85) | Yüksek (%85-99) ✅ |
| **Kurulum** | Tesseract + tessdata gerekli | Sadece OpenCV ✅ |

---

## 🎨 Ekran Görüntüleri (Screenshots)

### Ana Arayüz:
- 🎯 Tek buton ile bölge seçimi
- ⚙ Eşleşme eşiği ayarı (trackbar)
- 📋 Gerçek zamanlı log çıktısı
- 💾 Debug resim kaydetme

### Debug Resimleri Örneği:
```
Desktop/DenizBot_Debug_20250208_143022/
├── 0_target_original.png        # Yeşil kod (orijinal)
├── 0_target_threshold.png       # Yeşil kod (threshold işlenmiş)
├── 0_target_canny.png           # Yeşil kod (canny işlenmiş)
├── 1_button1_original.png       # Buton 1 (orijinal)
├── 1_button1_threshold.png      # Buton 1 (threshold)
├── 1_button1_canny.png          # Buton 1 (canny)
├── ... (2, 3, 4 için benzer)
```

---

## ⚠️ Önemli Notlar (Important Notes)

1. **Ban Koruması**: Eşik altındaki skorlarda tıklama yapmaz (yanlış tıklamayı önler)
2. **Rastgelelik**: Fare pozisyonu ve gecikme süresi her seferinde farklı (anti-bot)
3. **Performans**: 5 saniyede bir kontrol (sunucuya yük bindirmez)
4. **Dinamik**: Ekran çözünürlüğü değişirse otomatik adapte olur (orana dayalı)
5. **Thread-Safe**: Paralel işlemler için kilitleme mekanizması

---

## 📝 Değişiklik Günlüğü (Changelog)

### v2.0.0 - Template Matching Edition (2025-02-08)
- ✅ OCR tamamen kaldırıldı (Tesseract artık gerekli değil)
- ✅ OpenCvSharp4 Template Matching eklendi
- ✅ Dinamik kırpma sistemi (%20-40, %40-90)
- ✅ Tek bölge seçimi (5 bölge yerine 1)
- ✅ Binary Threshold + Canny fallback
- ✅ Ayarlanabilir eşleşme eşiği
- ✅ Debug resim kaydetme özelliği
- ✅ Geliştirilmiş log sistemi

### v1.0.0 - OCR Edition (Original)
- OCR tabanlı kod tanıma
- 5 ayrı bölge seçimi
- Tesseract bağımlılığı

---

## 📞 Destek ve Katkı (Support & Contribution)

Sorularınız veya önerileriniz için:
- GitHub Issues açın
- Pull request gönderin
- README'yi güncel tutun

---

## 📄 Lisans (License)

Bu proje eğitim amaçlıdır. Ticari kullanım öncesi lisans şartlarını kontrol edin.

---

**Keyifli kullanımlar! 🎮🤖**
