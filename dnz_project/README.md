# DNZ (Dinamik Nesne Zamanlayıcı)

<div align="center">

**Profesyonel Otomasyon Asistanı**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

</div>

---

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Sistem Gereksinimleri](#-sistem-gereksinimleri)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Teknik Detaylar](#-teknik-detaylar)
- [Build (EXE Oluşturma)](#-build-exe-oluşturma)
- [SSS](#-sss)
- [Güvenlik](#-güvenlik)

---

## ✨ Özellikler

### 🎯 Çekirdek Özellikler

- **Dinamik Bellek Taraması (AOB)**: Sabit adreslere bağımlı kalmadan Array of Bytes pattern matching ile hedef değişkenleri bulur
- **Otomatik Süreç Algılama**: Hedef pencereyi otomatik bulur, manuel seçim gereksinimi yoktur
- **İnsan Simülasyonu**: 4-14 saniye arası rastgele gecikme ile doğal davranış sergiler
- **Internal Trigger**: Fiziksel fare hareketi kullanmadan Windows API üzerinden doğrudan onay gönderir
- **Gelişmiş Loglama**: Tüm işlemleri zaman damgalı olarak kaydeder

### 🎨 Kullanıcı Arayüzü

- Modern ve profesyonel tasarım
- Gerçek zamanlı durum göstergesi
- Renklendirilmiş log sistemi
- Kolay kontrol paneli (Başlat/Duraklat/Durdur)

### 🔒 Güvenlik ve Uyumluluk

- Yönetici yetkisi kontrolü
- Platform doğrulama
- Hata yönetimi ve kurtarma
- Temiz kod mimarisi

---

## 💻 Sistem Gereksinimleri

### Minimum Gereksinimler

- **İşletim Sistemi**: Windows 10 veya üzeri (64-bit)
- **Python**: 3.7 veya üzeri (kaynak kod için)
- **RAM**: 256 MB
- **Disk Alanı**: 50 MB

### Önerilen Gereksinimler

- **İşletim Sistemi**: Windows 11
- **Python**: 3.11+
- **RAM**: 512 MB
- **Yönetici Yetkileri**: Evet (önerilir)

---

## 🚀 Kurulum

### Yöntem 1: Kaynak Koddan Çalıştırma

1. **Repository'yi indirin:**
   ```bash
   git clone https://github.com/your-repo/dnz-assistant.git
   cd dnz-assistant
   ```

2. **Python bağımlılıklarını yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Programı çalıştırın:**
   ```bash
   python main.py
   ```

### Yöntem 2: EXE Dosyasından (Derleme Sonrası)

1. `DNZ_Assistant.exe` dosyasını indirin
2. Yönetici olarak çalıştırın (sağ tık → "Yönetici olarak çalıştır")
3. Arayüz otomatik olarak açılacaktır

---

## 📖 Kullanım

### Temel Kullanım

1. **Başlatma:**
   - DNZ Assistant'ı açın
   - Hedef uygulama çalışır durumda olmalıdır
   - "Başlat" butonuna tıklayın

2. **İzleme:**
   - Durum göstergesi yeşil yanıyorsa sistem aktiftir
   - Log ekranından işlemleri takip edebilirsiniz

3. **Durdurma:**
   - "Durdur" butonu ile sistemi durdurun
   - Veya pencereyi kapatın

### Gelişmiş Özellikler

#### Duraklat/Devam Et

Geçici olarak duraklatmak için "Duraklat" butonunu kullanın:
```
[Aktif] → [Duraklat] → [Duraklatıldı]
[Duraklatıldı] → [Devam Et] → [Aktif]
```

#### Log Kayıtları

Tüm işlemler `dnz_logs.txt` dosyasına kaydedilir:
```
[2025-01-28 14:23:45] [INFO] DNZ motoru başlatıldı
[2025-01-28 14:23:50] [SUCCESS] Hedef pencereye bağlanıldı
[2025-01-28 14:24:10] [INFO] Doğrulama kodu algılandı: 123456
```

---

## 🔧 Teknik Detaylar

### Proje Yapısı

```
dnz_project/
│
├── main.py              # Ana giriş noktası
├── config.py            # Yapılandırma ayarları
├── engine.py            # Çekirdek motor (AOB, Process Manager)
├── gui.py               # Grafik arayüz
├── build.py             # Build scripti
├── requirements.txt     # Python bağımlılıkları
└── README.md           # Bu dosya
```

### Mimari Bileşenler

#### 1. MemoryScanner
```python
# Bellek tarama ve AOB pattern matching
scanner = MemoryScanner(process_handle, pid)
address = scanner.find_autoban_variable()
```

#### 2. ProcessManager
```python
# Süreç yönetimi ve pencere kontrolü
manager = ProcessManager()
manager.auto_attach()
manager.send_internal_accept()
```

#### 3. DNZEngine
```python
# Ana koordinasyon motoru
engine = DNZEngine(log_callback=callback)
engine.start()
engine.run_cycle()
```

### Konfigürasyon

`config.py` dosyasından ayarları değiştirebilirsiniz:

```python
# Zamanlama ayarları
MIN_DELAY = 4   # Minimum gecikme (saniye)
MAX_DELAY = 14  # Maksimum gecikme (saniye)

# Tarama ayarları
SCAN_INTERVAL = 0.5  # Tarama sıklığı
```

---

## 🏗️ Build (EXE Oluşturma)

### PyInstaller ile Build

```bash
# Otomatik build
python build.py pyinstaller

# Manuel build
pyinstaller --onefile --windowed --name DNZ_Assistant main.py
```

### Nuitka ile Build (Optimize)

```bash
# Otomatik build
python build.py nuitka

# Manuel build
python -m nuitka --standalone --onefile --windows-disable-console main.py
```

### Build Çıktıları

- PyInstaller: `dist/DNZ_Assistant.exe` (~15-20 MB)
- Nuitka: `DNZ_Assistant.exe` (~10-15 MB, daha hızlı)

---

## ❓ SSS

### Soru: Yönetici yetkisi gerekli mi?

**Cevap:** Önerilir ancak zorunlu değildir. Bazı gelişmiş özellikler yönetici yetkisi gerektirebilir.

### Soru: Hedef pencere bulunamıyor hatası alıyorum?

**Cevap:** Hedef uygulamanın çalıştığından ve pencere başlığının doğru olduğundan emin olun. `config.py` dosyasındaki `TARGET_WINDOW_NAMES` listesini kontrol edin.

### Soru: Log dosyası nerede saklanır?

**Cevap:** Varsayılan olarak programın çalıştığı dizinde `dnz_logs.txt` olarak saklanır.

### Soru: Gecikme sürelerini değiştirebilir miyim?

**Cevap:** Evet, `config.py` dosyasından `MIN_DELAY` ve `MAX_DELAY` değerlerini düzenleyebilirsiniz.

---

## 🔒 Güvenlik

### Önemli Notlar

- Bu yazılım **sadece kişisel kullanım** içindir
- Yazılım hiçbir kötü amaçla kullanılmamalıdır
- Tüm sorumluluk kullanıcıya aittir

### Gizlilik

- DNZ hiçbir veriyi dışarı göndermez
- Tüm işlemler lokal bilgisayarda gerçekleşir
- Log dosyaları sadece local'de tutulur

---

## 📝 Lisans

Bu yazılım özel mülkiyettir. Ticari kullanım yasaktır.

Copyright © 2025 DNZ Assistant. Tüm hakları saklıdır.

---

## 🤝 Destek

Sorularınız için:
- GitHub Issues
- E-posta: support@dnz-assistant.com

---

## 📚 Değişiklik Geçmişi

### v1.0.0 (2025-01-28)
- ✨ İlk stabil sürüm
- 🎯 Dinamik bellek tarama
- 🖥️ Modern GUI arayüzü
- 📝 Gelişmiş loglama sistemi
- 🔧 EXE build desteği

---

<div align="center">

**DNZ Assistant ile profesyonel deneyimin tadını çıkarın!**

Made with ❤️ by DNZ Team

</div>