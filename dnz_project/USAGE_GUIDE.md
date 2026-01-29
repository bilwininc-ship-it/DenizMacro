# 🏗️ DNZ Assistant - EXE Oluşturma Talimatları

Bu dosya, DNZ Assistant uygulamasını **tek dosya EXE** haline getirmek için adım adım talimatlar içerir.

---

## 📋 Ön Gereksinimler

### 1. Python Kurulumu
- Python 3.7 veya üzeri yüklü olmalı
- Python PATH'e eklenmiş olmalı

Kontrol için:
```bash
python --version
```

### 2. Gerekli Kütüphaneleri Yükleyin
```bash
cd dnz_project
pip install -r requirements.txt
```

Bu şunları yükleyecek:
- `pyinstaller` (EXE oluşturma)
- `customtkinter` (Modern GUI)
- `psutil` (Süreç yönetimi)
- `pywin32` (Windows API)

---

## 🚀 Yöntem 1: Otomatik Build (Önerilen)

### Basit Kullanım

```bash
cd dnz_project
python build.py
```

Bu komut:
✅ Eski build dosyalarını temizler  
✅ PyInstaller ile tek dosya EXE oluşturur  
✅ Çıktıyı `dist/DNZ_Assistant.exe` klasörüne yerleştirir

### Build Çıktısı

```
dist/
└── DNZ_Assistant.exe    (15-20 MB)
```

---

## 🔧 Yöntem 2: Manuel Build

### PyInstaller Komutu

```bash
pyinstaller --onefile --windowed --name DNZ_Assistant --clean main.py
```

#### Parametre Açıklamaları:
- `--onefile`: Tek bir EXE dosyası oluşturur
- `--windowed`: Console penceresini gizler (GUI uygulamaları için)
- `--name DNZ_Assistant`: EXE dosyasının adı
- `--clean`: Önbellekleri temizler
- `main.py`: Ana giriş dosyası

### İkon Eklemek İsterseniz

Eğer bir `.ico` dosyanız varsa:

```bash
pyinstaller --onefile --windowed --name DNZ_Assistant --icon=icon.ico --clean main.py
```

---

## 📦 Yöntem 3: Nuitka ile Build (İleri Seviye)

Nuitka daha hızlı ve optimize edilmiş EXE oluşturur:

### Kurulum
```bash
pip install nuitka
```

### Build
```bash
python build.py nuitka
```

veya manuel:

```bash
python -m nuitka --standalone --onefile --windows-disable-console --output-filename=DNZ_Assistant.exe --enable-plugin=tk-inter main.py
```

**Not:** Nuitka build süreci 5-10 dakika sürebilir.

---

## ✅ Build Sonrası Kontroller

### 1. EXE Dosyasını Test Edin

```bash
cd dist
DNZ_Assistant.exe
```

### 2. Yönetici Olarak Çalıştırın

Daha iyi performans için EXE'yi yönetici yetkisiyle çalıştırın:
- EXE'ye sağ tıklayın
- "Yönetici olarak çalıştır" seçeneğini seçin

### 3. Kontrol Listesi

✅ Uygulama açılıyor mu?  
✅ GUI düzgün görünüyor mu?  
✅ Log mesajları görünüyor mu?  
✅ "Başlat" butonu çalışıyor mu?  
✅ Hedef pencere algılanıyor mu?

---

## 🖥️ Masaüstüne Kurulum

### 1. EXE'yi Masaüstüne Kopyalayın

```bash
copy dist\DNZ_Assistant.exe %USERPROFILE%\Desktop\
```

veya manuel olarak `dist/DNZ_Assistant.exe` dosyasını masaüstüne sürükleyip bırakın.

### 2. Kısayol Oluşturun (Opsiyonel)

1. EXE'ye sağ tıklayın
2. "Kısayol oluştur" seçin
3. Kısayola sağ tıklayın → "Özellikler"
4. "Gelişmiş" butonuna tıklayın
5. "Yönetici olarak çalıştır" seçeneğini işaretleyin
6. "Tamam" → "Uygula" → "Tamam"

Artık kısayola çift tıklayarak uygulamayı yönetici yetkisiyle başlatabilirsiniz!

---

## 🐛 Sorun Giderme

### Hata: "PyInstaller bulunamadı"

```bash
pip install pyinstaller
```

### Hata: "tkinter modülü bulunamadı"

Windows üzerinde Python kurulumu sırasında "tcl/tk and IDLE" seçeneğini işaretleyin.

### Hata: "Failed to execute script"

1. `--windowed` parametresini kaldırıp console modda test edin:
   ```bash
   pyinstaller --onefile --name DNZ_Assistant --clean main.py
   ```

2. Hata mesajlarını okuyun ve eksik modülleri tespit edin

### EXE Boyutu Çok Büyük

PyInstaller tüm bağımlılıkları paketler. Bu normaldir (~15-20 MB).

Daha küçük boyut için:
- Nuitka kullanın (daha optimize)
- Gereksiz kütüphaneleri `requirements.txt`'den çıkarın

---

## 📊 Build Karşılaştırması

| Özellik | PyInstaller | Nuitka |
|---------|-------------|--------|
| Hız | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Boyut | 15-20 MB | 10-15 MB |
| Build Süresi | 1-2 dakika | 5-10 dakika |
| Kullanım Kolaylığı | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Önerilen | ✅ Başlangıç | ⚡ İleri Seviye |

---

## 🎯 Dağıtım için Öneriler

### 1. Test Edin
Farklı Windows sürümlerinde test edin:
- Windows 10
- Windows 11

### 2. Dokümantasyon Ekleyin
EXE ile birlikte şunları ekleyin:
- `README.md`
- `USAGE_GUIDE.md`
- `LICENSE`

### 3. Virüs Taraması
Bazı antivirüs programları PyInstaller EXE'leri yanlış tespit edebilir. Kullanıcıları bilgilendirin.

### 4. Dijital İmza (Opsiyonel)
Profesyonel dağıtım için EXE'yi dijital olarak imzalayın.

---

## 📝 Notlar

- **EXE dosyası sadece Windows'ta çalışır**
- **İlk çalıştırma biraz yavaş olabilir** (PyInstaller geçici dosyaları açar)
- **Antivirüs programı uyarı verebilir** (false positive)
- **Yönetici yetkisi olmadan bazı özellikler çalışmayabilir**

---

## 🆘 Destek

Build sırasında sorun yaşarsanız:

1. Log dosyalarını kontrol edin: `build/build.log`
2. GitHub Issues'da arama yapın
3. Yeni issue açın (hata mesajlarını ekleyin)

---

<div align="center">

**Başarılı build'lar diliyoruz! 🚀**

Made with ❤️ by DNZ Team

</div>
