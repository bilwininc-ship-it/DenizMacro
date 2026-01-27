# 🔧 Template Matching - Kod Detayları (Code Details)

Bu dokümant, **kırpma (cropping)** ve **eşleştirme (matching)** fonksiyonlarının detaylı açıklamalarını içerir.

---

## 📐 1. DİNAMİK KIRPMA FONKSİYONLARI (Dynamic Cropping Functions)

### `CropRegion()` - Yüzde Bazlı Kırpma

```csharp
/// <summary>
/// Ana pencereden orana dayalı bölge kırpar
/// </summary>
/// <param name="mainWindow">Ana pencere bitmap'i</param>
/// <param name="topPercent">Başlangıç yüzdesi (0.20 = %20)</param>
/// <param name="bottomPercent">Bitiş yüzdesi (0.40 = %40)</param>
/// <returns>Kırpılmış bitmap</returns>
public Bitmap CropRegion(Bitmap mainWindow, double topPercent, double bottomPercent)
{
    // Piksel koordinatlarını hesapla
    int startY = (int)(mainWindow.Height * topPercent);
    int endY = (int)(mainWindow.Height * bottomPercent);
    int height = endY - startY;

    // Geçersiz değerleri kontrol et
    if (height <= 0 || startY < 0 || endY > mainWindow.Height)
    {
        throw new ArgumentException($"Invalid crop percentages: {topPercent}-{bottomPercent}");
    }

    // Kırpma dikdörtgenini tanımla (X=0, tam genişlik)
    Rectangle cropRect = new Rectangle(0, startY, mainWindow.Width, height);
    
    // Yeni bitmap oluştur
    Bitmap croppedBitmap = new Bitmap(cropRect.Width, cropRect.Height, PixelFormat.Format24bppRgb);
    
    // Graphics ile kopyala
    using (Graphics g = Graphics.FromImage(croppedBitmap))
    {
        g.DrawImage(mainWindow, 
            new Rectangle(0, 0, cropRect.Width, cropRect.Height),  // Hedef
            cropRect,                                               // Kaynak
            GraphicsUnit.Pixel);
    }

    return croppedBitmap;
}
```

**Kullanım Örneği:**
```csharp
// Ana pencereden yeşil kod alanını kırp (%20-%40)
Bitmap targetCode = templateMatchingService.CropRegion(
    mainWindow, 
    topPercent: 0.20,      // %20'den başla
    bottomPercent: 0.40    // %40'ta bitir
);

// Ana pencereden butonlar alanını kırp (%40-%90)
Bitmap buttonsArea = templateMatchingService.CropRegion(
    mainWindow,
    topPercent: 0.40,      // %40'tan başla
    bottomPercent: 0.90    // %90'da bitir
);
```

**Görselleştirme:**
```
Ana Pencere (800x600):
┌──────────────────────────┐ 0%    (Y=0)
│   Üst kısım (başlık)     │
├──────────────────────────┤ 20%   (Y=120)  ← targetCodeTopPercent
│ ┌──────────────────────┐ │
│ │   YEŞİL KOD (875609) │ │  <- TARGET CODE
│ └──────────────────────┘ │
├──────────────────────────┤ 40%   (Y=240)  ← buttonsAreaTopPercent
│ ┌──────────────────────┐ │
│ │   Buton 1: 592430    │ │
│ ├──────────────────────┤ │
│ │   Buton 2: 875609    │ │  <- BUTTONS AREA
│ ├──────────────────────┤ │
│ │   Buton 3: 714685    │ │
│ ├──────────────────────┤ │
│ │   Buton 4: 305387    │ │
│ └──────────────────────┘ │
├──────────────────────────┤ 90%   (Y=540)  ← buttonsAreaBottomPercent
│   Alt kısım              │
└──────────────────────────┘ 100%  (Y=600)
```

---

### `SplitButtonsArea()` - 4 Eşit Parçaya Böl

```csharp
/// <summary>
/// Butonlar alanını dikey olarak 4 eşit parçaya böler
/// </summary>
/// <param name="buttonsArea">Butonlar alan bitmap'i</param>
/// <returns>4 buton bitmap dizisi</returns>
public Bitmap[] SplitButtonsArea(Bitmap buttonsArea)
{
    // Her butonun yüksekliğini hesapla
    int buttonHeight = buttonsArea.Height / 4;
    Bitmap[] buttons = new Bitmap[4];

    // Her buton için döngü
    for (int i = 0; i < 4; i++)
    {
        // Her butonun başlangıç Y koordinatı
        int startY = i * buttonHeight;
        
        // Buton dikdörtgeni (X=0, tam genişlik)
        Rectangle buttonRect = new Rectangle(0, startY, buttonsArea.Width, buttonHeight);
        
        // Yeni bitmap oluştur
        buttons[i] = new Bitmap(buttonRect.Width, buttonRect.Height, PixelFormat.Format24bppRgb);
        
        // Graphics ile kopyala
        using (Graphics g = Graphics.FromImage(buttons[i]))
        {
            g.DrawImage(buttonsArea,
                new Rectangle(0, 0, buttonRect.Width, buttonRect.Height),  // Hedef
                buttonRect,                                                 // Kaynak
                GraphicsUnit.Pixel);
        }
    }

    return buttons;
}
```

**Kullanım Örneği:**
```csharp
Bitmap[] buttons = templateMatchingService.SplitButtonsArea(buttonsAreaBitmap);

// buttons[0] = Buton 1
// buttons[1] = Buton 2
// buttons[2] = Buton 3
// buttons[3] = Buton 4
```

**Görselleştirme:**
```
Butonlar Alanı (800x300):
┌──────────────────────────┐
│   Buton 1: 592430        │  <- buttons[0]  (Y=0-75)
├──────────────────────────┤
│   Buton 2: 875609        │  <- buttons[1]  (Y=75-150)
├──────────────────────────┤
│   Buton 3: 714685        │  <- buttons[2]  (Y=150-225)
├──────────────────────────┤
│   Buton 4: 305387        │  <- buttons[3]  (Y=225-300)
└──────────────────────────┘

Her buton: 800x75 piksel (genişlik x yükseklik)
```

---

## 🎨 2. GÖRÜNTÜ İŞLEME FONKSİYONLARI (Preprocessing Functions)

### `ConvertToGrayscale()` - Gri Tonlamaya Dönüştür

```csharp
/// <summary>
/// Bitmap'i OpenCV Mat formatında gri tonlamaya dönüştürür
/// </summary>
public Mat ConvertToGrayscale(Bitmap bitmap)
{
    // Bitmap'i OpenCV Mat'e dönüştür
    using (Mat colorMat = BitmapConverter.ToMat(bitmap))
    {
        Mat grayMat = new Mat();
        
        // Renk uzayını değiştir: BGR → Grayscale
        Cv2.CvtColor(colorMat, grayMat, ColorConversionCodes.BGR2GRAY);
        
        return grayMat;
    }
}
```

**Görsel Örnek:**
```
Orijinal (Renkli):           Grayscale:
┌─────────────┐              ┌─────────────┐
│ YEŞİL 875609│  →  Cv2.     │ GRİ  875609 │
│ (RGB değeri)│     CvtColor  │ (0-255)     │
└─────────────┘              └─────────────┘
```

---

### `ApplyBinaryThreshold()` - İkili Eşikleme

```csharp
/// <summary>
/// Sayı şekillerini netleştirmek için ikili eşikleme uygular
/// Renkleri görmezden gelir, sadece siyah/beyaz
/// </summary>
/// <param name="grayMat">Gri tonlama Mat</param>
/// <param name="thresholdValue">Eşik değeri (0-255, varsayılan 128)</param>
public Mat ApplyBinaryThreshold(Mat grayMat, double thresholdValue = 128)
{
    Mat thresholdMat = new Mat();
    
    // Eşik uygulaması:
    // Piksel > 128 ise → 255 (beyaz)
    // Piksel <= 128 ise → 0 (siyah)
    Cv2.Threshold(grayMat, thresholdMat, thresholdValue, 255, ThresholdTypes.Binary);
    
    return thresholdMat;
}
```

**Görsel Örnek:**
```
Grayscale (0-255):           Binary Threshold:
┌─────────────┐              ┌─────────────┐
│ 120 180 190 │  Threshold   │   0 255 255 │
│ 100 200 210 │  →  128  →   │   0 255 255 │
│  80 170 190 │              │   0 255 255 │
└─────────────┘              └─────────────┘
   (Gri)                        (Siyah/Beyaz)

Sonuç: Sadece sayı şekilleri kalır, arka plan temiz!
```

---

### `ApplyCannyEdgeDetection()` - Kenar Tespiti (Fallback)

```csharp
/// <summary>
/// Canny edge detection - kenar çizgilerini bulur
/// Binary threshold yetersiz kalırsa kullanılır
/// </summary>
/// <param name="grayMat">Gri tonlama Mat</param>
/// <param name="threshold1">Düşük eşik (varsayılan 50)</param>
/// <param name="threshold2">Yüksek eşik (varsayılan 150)</param>
public Mat ApplyCannyEdgeDetection(Mat grayMat, double threshold1 = 50, double threshold2 = 150)
{
    Mat cannyMat = new Mat();
    
    // Canny algoritması: Gradyan bazlı kenar tespiti
    Cv2.Canny(grayMat, cannyMat, threshold1, threshold2);
    
    return cannyMat;
}
```

**Görsel Örnek:**
```
Grayscale:                   Canny Edges:
┌─────────────┐              ┌─────────────┐
│   █████     │              │   █   █     │
│   █   █     │  Canny   →   │   █   █     │
│   █████     │  Edge        │   █   █     │
│       █     │  Detection   │       █     │
│   █████     │              │   █   █     │
└─────────────┘              └─────────────┘
  (Dolu sayı)                 (Sadece kenarlar)

Avantaj: Arka plan dokusunu tamamen yok sayar!
```

---

### `PreprocessImage()` - Tek Çağrı ile İşleme

```csharp
/// <summary>
/// Bitmap'i template matching için hazırlar
/// </summary>
/// <param name="bitmap">İşlenecek bitmap</param>
/// <param name="useCanny">true = Canny, false = Threshold</param>
public Mat PreprocessImage(Bitmap bitmap, bool useCanny = false)
{
    // 1. Grayscale'e dönüştür
    using (Mat grayMat = ConvertToGrayscale(bitmap))
    {
        // 2. İşleme yöntemini seç
        if (useCanny)
        {
            return ApplyCannyEdgeDetection(grayMat);
        }
        else
        {
            return ApplyBinaryThreshold(grayMat);
        }
    }
}
```

**Kullanım:**
```csharp
// İlk deneme: Binary Threshold
Mat targetProcessed = PreprocessImage(targetCodeBitmap, useCanny: false);

// Fallback: Canny Edge Detection
Mat targetCannyProcessed = PreprocessImage(targetCodeBitmap, useCanny: true);
```

---

## 🔍 3. TEMPLATE MATCHING FONKSİYONLARI (Matching Functions)

### `MatchTemplate()` - Görüntü Eşleştirme

```csharp
/// <summary>
/// İki OpenCV Mat'i karşılaştırır ve benzerlik skoru döner
/// </summary>
/// <param name="target">Hedef görüntü (yeşil kod)</param>
/// <param name="template">Şablon görüntü (buton)</param>
/// <returns>Benzerlik skoru (0.0 - 1.0, 1.0 = mükemmel eşleşme)</returns>
public double MatchTemplate(Mat target, Mat template)
{
    lock (_matchLock)  // Thread-safe
    {
        // Boyut kontrolü: Eşit değilse resize et
        if (target.Width != template.Width || target.Height != template.Height)
        {
            using (Mat resizedTemplate = new Mat())
            {
                Cv2.Resize(template, resizedTemplate, 
                    new OpenCvSharp.Size(target.Width, target.Height));
                return PerformMatching(target, resizedTemplate);
            }
        }
        else
        {
            return PerformMatching(target, template);
        }
    }
}

/// <summary>
/// Gerçek eşleştirme işlemini yapar
/// </summary>
private double PerformMatching(Mat target, Mat template)
{
    try
    {
        using (Mat result = new Mat())
        {
            // OpenCV Template Matching (CCoeffNormed metodu)
            Cv2.MatchTemplate(target, template, result, TemplateMatchModes.CCoeffNormed);
            
            // En düşük ve en yüksek değerleri bul
            Cv2.MinMaxLoc(result, out double minVal, out double maxVal, out _, out _);
            
            // CCoeffNormed: -1 ile 1 arasında değer döner
            // 1.0 = Mükemmel eşleşme
            // 0.0 = Hiç benzerlik yok
            // -1.0 = Tam tersi
            return maxVal;
        }
    }
    catch (Exception ex)
    {
        throw new InvalidOperationException($"Template matching failed: {ex.Message}", ex);
    }
}
```

**CCoeffNormed Nedir?**
- **Correlation Coefficient Normalized** (Normalleştirilmiş Korelasyon Katsayısı)
- Parlaklık ve kontrast değişikliklerine karşı dayanıklı
- Sonuç: -1.0 (tam ters) ile 1.0 (mükemmel eşleşme) arası
- Daha yüksek skor = daha iyi eşleşme

**Görsel Örnek:**
```
Target (Yeşil Kod):        Template (Buton 2):        Sonuç:
┌─────────────┐            ┌─────────────┐
│  █████ ███  │            │  █████ ███  │          CCoeffNormed
│      █ █  █ │   vs.      │      █ █  █ │    →    Skor: 0.91
│  █████ ███  │            │  █████ ███  │          (Yüksek benzerlik!)
│  █   █   █  │            │  █   █   █  │
│  █████ ███  │            │  █████ ███  │
└─────────────┘            └─────────────┘
  875609                     875609

Target (Yeşil Kod):        Template (Buton 1):        Sonuç:
┌─────────────┐            ┌─────────────┐
│  █████ ███  │            │  █████ ███  │          CCoeffNormed
│      █ █  █ │   vs.      │  █   █ █  █ │    →    Skor: 0.72
│  █████ ███  │            │  █████  ████│          (Orta benzerlik)
│  █   █   █  │            │  █   █    █ │
│  █████ ███  │            │  █████  ████│
└─────────────┘            └─────────────┘
  875609                     592430
```

---

### `FindBestMatch()` - En İyi Eşleşmeyi Bul

```csharp
/// <summary>
/// Yeşil kodu 4 buton ile karşılaştırır ve en iyisini bulur
/// İki aşamalı: 1) Binary Threshold, 2) Canny (fallback)
/// </summary>
/// <param name="targetCodeBitmap">Yeşil kod bitmap'i</param>
/// <param name="buttonBitmaps">4 buton bitmap dizisi</param>
/// <param name="minimumThreshold">Minimum eşik değeri (0.85 = %85)</param>
/// <returns>(buttonIndex, similarity, usedCanny)</returns>
public (int buttonIndex, double similarity, bool usedCanny) FindBestMatch(
    Bitmap targetCodeBitmap, 
    Bitmap[] buttonBitmaps, 
    double minimumThreshold)
{
    Mat targetProcessed = null;
    Mat targetCannyProcessed = null;
    Mat[] buttonsProcessed = new Mat[4];
    Mat[] buttonsCannyProcessed = new Mat[4];

    try
    {
        // ========== PHASE 1: BINARY THRESHOLD ==========
        
        // Yeşil kodu işle
        targetProcessed = PreprocessImage(targetCodeBitmap, useCanny: false);
        
        // Her butonu işle ve skorları hesapla
        double[] scores = new double[4];
        for (int i = 0; i < 4; i++)
        {
            buttonsProcessed[i] = PreprocessImage(buttonBitmaps[i], useCanny: false);
            scores[i] = MatchTemplate(targetProcessed, buttonsProcessed[i]);
        }

        // En yüksek skoru bul
        int bestIndex = Array.IndexOf(scores, scores.Max());
        double bestScore = scores[bestIndex];

        // Eşik değeri kontrol et
        if (bestScore >= minimumThreshold)
        {
            // Başarılı! Binary threshold yeterli oldu
            return (bestIndex, bestScore, usedCanny: false);
        }

        // ========== PHASE 2: CANNY EDGE DETECTION (FALLBACK) ==========
        
        // Yeşil kodu Canny ile işle
        targetCannyProcessed = PreprocessImage(targetCodeBitmap, useCanny: true);
        
        // Her butonu Canny ile işle ve skorları hesapla
        double[] cannyScores = new double[4];
        for (int i = 0; i < 4; i++)
        {
            buttonsCannyProcessed[i] = PreprocessImage(buttonBitmaps[i], useCanny: true);
            cannyScores[i] = MatchTemplate(targetCannyProcessed, buttonsCannyProcessed[i]);
        }

        // En yüksek Canny skorunu bul
        int bestCannyIndex = Array.IndexOf(cannyScores, cannyScores.Max());
        double bestCannyScore = cannyScores[bestCannyIndex];

        // Canny sonucunu döndür (eşik kontrolü ana döngüde yapılır)
        return (bestCannyIndex, bestCannyScore, usedCanny: true);
    }
    finally
    {
        // Tüm Mat'leri dispose et (bellek sızıntısı önleme)
        targetProcessed?.Dispose();
        targetCannyProcessed?.Dispose();
        
        foreach (var mat in buttonsProcessed)
        {
            mat?.Dispose();
        }
        
        foreach (var mat in buttonsCannyProcessed)
        {
            mat?.Dispose();
        }
    }
}
```

**İki Aşamalı Eşleştirme Akışı:**
```
1. BINARY THRESHOLD DENEMESİ:
   ┌──────────────────────────────────────┐
   │ Target: 875609 (Threshold işlenmiş) │
   └──────────────────────────────────────┘
                    ↓
   ┌──────────────────────────────────────┐
   │ Button 1: 592430 → Skor: 0.72        │
   │ Button 2: 875609 → Skor: 0.91 ✅     │ ← Eşik: 0.85
   │ Button 3: 714685 → Skor: 0.65        │
   │ Button 4: 305387 → Skor: 0.58        │
   └──────────────────────────────────────┘
                    ↓
   0.91 >= 0.85 → BAŞARILI! (Canny gerekmez)

2. CANNY FALLBACK (Düşük skor durumu):
   ┌──────────────────────────────────────┐
   │ Target: 875609 (Canny işlenmiş)     │
   └──────────────────────────────────────┘
                    ↓
   ┌──────────────────────────────────────┐
   │ Button 1: 592430 → Skor: 0.78        │
   │ Button 2: 875609 → Skor: 0.89 ✅     │ ← Eşik: 0.85
   │ Button 3: 714685 → Skor: 0.70        │
   │ Button 4: 305387 → Skor: 0.62        │
   └──────────────────────────────────────┘
                    ↓
   0.89 >= 0.85 → BAŞARILI! (Canny ile)
```

---

## 🖱️ 4. TIKLA VE GÜVENLİK (Click & Security)

### Tıklama Pozisyonu Hesaplama

```csharp
// Dinamik buton pozisyonu hesaplama
int buttonsAreaStartY = (int)(_config.MainWindowRegion.Rectangle.Height * _config.ButtonsAreaTopPercent);
int buttonsAreaHeight = (int)(_config.MainWindowRegion.Rectangle.Height * 
                               (_config.ButtonsAreaBottomPercent - _config.ButtonsAreaTopPercent));
int buttonHeight = buttonsAreaHeight / 4;

// Butonun merkezi
int clickX = _config.MainWindowRegion.Rectangle.X + _config.MainWindowRegion.Rectangle.Width / 2;
int clickY = _config.MainWindowRegion.Rectangle.Y + buttonsAreaStartY + 
             (buttonIndex * buttonHeight) + (buttonHeight / 2);

// ±5 piksel rastgele sapma ekle (anti-bot)
Point clickPoint = MouseHelper.AddJitter(new Point(clickX, clickY), 5);
```

**Görselleştirme:**
```
Ana Pencere (X=100, Y=100, W=800, H=600):
┌────────────────────────────────────┐ Y=100
│                                    │
├────────────────────────────────────┤ Y=340 (100 + 600*0.40)
│ ┌────────────────────────────────┐ │
│ │ Buton 1                        │ │ Height = 300/4 = 75
│ ├────────────────────────────────┤ │ Y = 340 + (0*75) + 37.5 = 377.5
│ │ Buton 2 ← EŞLEŞTİ! [buttonIndex=1]
│ ├────────────────────────────────┤ │ Y = 340 + (1*75) + 37.5 = 452.5 ✅
│ │ Buton 3                        │ │
│ ├────────────────────────────────┤ │
│ │ Buton 4                        │ │
│ └────────────────────────────────┘ │
├────────────────────────────────────┤ Y=640 (100 + 600*0.90)
│                                    │
└────────────────────────────────────┘

Tıklama Noktası:
X = 100 + 800/2 = 500 (±5 piksel jitter)
Y = 452.5 (±5 piksel jitter)
Sonuç: (495-505, 447.5-457.5) arasında rastgele nokta
```

### Güvenlik ve Anti-Bot Mekanizmaları

```csharp
// 1. EŞİK KONTROLÜ (Yanlış tıklama önleme)
if (similarity >= _config.MatchingThreshold)
{
    // Sadece yüksek benzerlikte tıkla
    await ClickButton();
}
else
{
    // Düşük benzerlikte BEKLEBekleme ve loglama
    Log($"⚠ Eşleşme eşiği karşılanmadı (Skor: {similarity:P2} < Eşik: {_config.MatchingThreshold:P0})");
    // Yanlış butona tıklamayı önle!
}

// 2. RASTGELE GECİKME (4-14 saniye)
Random random = new Random();
int preClickDelay = random.Next(_config.DelayMin, _config.DelayMax);
await Task.Delay(preClickDelay, cancellationToken);

// 3. RASTGELE POZİSYON SAPMASI (±5 piksel)
Point clickPoint = MouseHelper.AddJitter(new Point(clickX, clickY), 5);

// 4. DOĞAL FARE HAREKETİ (Bezier eğrisi)
await MouseHelper.MoveAndClickAsync(clickPoint, cancellationToken);
// → Fare doğrusal değil, eğrisel hareket eder (insan gibi)

// 5. KONTROL ARALIKLARI (5 saniye)
await Task.Delay(_config.CheckIntervalMs, cancellationToken);
// → Sunucuya aşırı yük bindirmez
```

---

## 📊 5. PERFORMANS ve OPTİMİZASYON

### Bellek Yönetimi (Memory Management)

```csharp
// DOĞRU: using ve try-finally ile dispose
Bitmap? mainWindowCapture = null;
Bitmap? targetCodeBitmap = null;
Bitmap[]? buttonBitmaps = null;

try
{
    mainWindowCapture = _captureService.CaptureRegion(...);
    targetCodeBitmap = _templateMatchingService.CropRegion(...);
    buttonBitmaps = _templateMatchingService.SplitButtonsArea(...);
    
    // İşlemleri yap...
}
finally
{
    // Belleği serbest bırak
    mainWindowCapture?.Dispose();
    targetCodeBitmap?.Dispose();
    
    if (buttonBitmaps != null)
    {
        foreach (var bitmap in buttonBitmaps)
        {
            bitmap?.Dispose();
        }
    }
}
```

### Thread Safety (İş Parçacığı Güvenliği)

```csharp
// TemplateMatchingService içinde
private readonly object _matchLock = new object();

public double MatchTemplate(Mat target, Mat template)
{
    lock (_matchLock)  // ← Aynı anda tek thread erişir
    {
        // OpenCV işlemleri thread-safe değildir
        // Lock ile korunması gerekir
        return PerformMatching(target, template);
    }
}
```

---

## 🎯 6. SONUÇ ve ÖZET

### Tüm Akış (End-to-End Flow):

```csharp
// 1. Ana pencereyi yakala
Bitmap mainWindow = _captureService.CaptureRegion(_config.MainWindowRegion.Rectangle);

// 2. Dinamik kırpma
Bitmap targetCode = _templateMatchingService.CropRegion(mainWindow, 0.20, 0.40);
Bitmap buttonsArea = _templateMatchingService.CropRegion(mainWindow, 0.40, 0.90);

// 3. Butonları böl
Bitmap[] buttons = _templateMatchingService.SplitButtonsArea(buttonsArea);

// 4. Template matching
var (buttonIndex, similarity, usedCanny) = _templateMatchingService.FindBestMatch(
    targetCode, buttons, _config.MatchingThreshold);

// 5. Eşik kontrolü ve tıklama
if (similarity >= _config.MatchingThreshold)
{
    // Pozisyon hesapla
    Point clickPoint = CalculateButtonCenter(buttonIndex);
    
    // Rastgele gecikme
    await Task.Delay(random.Next(4000, 14000));
    
    // Tıkla
    await MouseHelper.MoveAndClickAsync(clickPoint);
    
    Log($"✅ Buton {buttonIndex + 1} tıklandı! Skor: {similarity:P2}");
}
else
{
    Log($"⚠ Eşik karşılanmadı, tıklama yapılmadı.");
}

// 6. Belleği temizle
Dispose(mainWindow, targetCode, buttonsArea, buttons);
```

---

Bu dokümantasyon, Template Matching sisteminin **tüm kırpma ve eşleştirme fonksiyonlarını** detaylı olarak açıklamaktadır. Kod örnekleri doğrudan projeden alınmıştır ve çalışır durumdadır.

**Keyifli kodlamalar! 🚀**
