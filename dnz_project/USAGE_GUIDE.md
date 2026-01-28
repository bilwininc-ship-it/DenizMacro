# DNZ Assistant - Kullanım Kılavuzu

## İçindekiler

1. [Hızlı Başlangıç](#hızlı-başlangıç)
2. [Detaylı Kullanım](#detaylı-kullanım)
3. [Yapılandırma](#yapılandırma)
4. [Sorun Giderme](#sorun-giderme)
5. [İpuçları ve Püf Noktaları](#ipuçları-ve-püf-noktaları)

---

## Hızlı Başlangıç

### 1. İlk Kurulum

#### A. Kaynak Kod ile Çalıştırma

```bash
# 1. Dosyaları indirin
git clone https://github.com/your-repo/dnz-assistant.git
cd dnz-assistant

# 2. Programı başlatın
python main.py
```

#### B. EXE Dosyası ile Çalıştırma

1. `DNZ_Assistant.exe` dosyasını indirin
2. Sağ tıklayın → "Yönetici olarak çalıştır"
3. Hazır!

### 2. İlk Çalıştırma

1. **DNZ Assistant'ı açın**
   - Yönetici yetkileri ile çalıştırmayı unutmayın

2. **Hedef uygulamayı başlatın**
   - DNZ, otomatik olarak hedef pencereyi bulacaktır

3. **Başlat'a tıklayın**
   - Yeşil LED göstergesi aktif hale gelir
   - Log ekranında işlemler görünür

4. **İzleyin**
   - Sistem otomatik olarak çalışacaktır
   - Her işlem log'a kaydedilir

---

## Detaylı Kullanım

### Arayüz Bileşenleri

#### 1. Başlık Bölümü
```
DNZ Assistant v1.0.0
Dinamik Nesne Zamanlayıcı - Profesyonel Otomasyon Asistanı
```
- Uygulama bilgileri ve versiyon numarası

#### 2. Durum Göstergesi
```
Durum: [Bekleniyor...] [●]
```
- **Bekleniyor (Gri)**: Sistem aktif değil
- **Aktif (Yeşil)**: Sistem çalışıyor
- **Duraklatıldı (Sarı)**: Geçici olarak durduruldu
- **İşlem Yapılıyor (Mavi)**: İşlem gerçekleştiriliyor

#### 3. Kontrol Butonları

##### Başlat Butonu
- **İşlevi**: Sistemi başlatır
- **Durum**: İlk açılışta aktif
- **Sonrası**: Sistem çalışırken pasif

##### Duraklat Butonu
- **İşlevi**: Sistemi geçici olarak durdurur
- **Durum**: Sistem çalışırken aktif
- **Toggle**: "Duraklat" ↔ "Devam Et"

##### Durdur Butonu
- **İşlevi**: Sistemi tamamen durdurur
- **Durum**: Sistem çalışırken aktif
- **Sonrası**: Sistem başlangıç durumuna döner

#### 4. Log Ekranı
```
[2025-01-28 14:23:45] [INFO] DNZ motoru başlatıldı
[2025-01-28 14:23:50] [SUCCESS] Hedef pencereye bağlanıldı
```
- Tüm işlemler renklendirilmiş olarak gösterilir
- Otomatik scroll (en son mesaj görünür)
- Kopyala/yapıştır destekli

### İş Akışı

#### Normal Kullanım Akışı

```
1. Program Başlatma
   └─> Yönetici kontrolü
   └─> Platform kontrolü
   └─> Arayüz açılır

2. Hedef Bağlantı
   └─> "Başlat" butonuna tıkla
   └─> Otomatik pencere taraması
   └─> Hedef bulundu / bulunamadı

3. Aktif İzleme
   └─> Sürekli tarama (0.5 sn aralıkla)
   └─> Hedef değişken kontrolü
   └─> Değer değişimi algılandı mı?

4. İşlem Gerçekleştirme
   └─> İnsan simülasyonu (4-14 sn)
   └─> Internal trigger gönderimi
   └─> Başarılı / Başarısız log

5. Döngü Devam
   └─> Adım 3'e dön
```

---

## Yapılandırma

### config.py Dosyası

#### Zamanlama Ayarları

```python
# Minimum ve maksimum gecikme süreleri (saniye)
MIN_DELAY = 4    # Minimum: 4 saniye
MAX_DELAY = 14   # Maksimum: 14 saniye

# Tarama sıklığı
SCAN_INTERVAL = 0.5  # Her 0.5 saniyede bir tara
```

**Ne zaman değiştirmeli?**
- Daha hızlı tepki için: `MIN_DELAY = 2, MAX_DELAY = 8`
- Daha doğal davranış için: `MIN_DELAY = 6, MAX_DELAY = 20`

#### Hedef Pencere İsimleri

```python
TARGET_WINDOW_NAMES = [
    "metin2client",
    "Metin2",
    "METIN2"
]
```

**Kendi hedef pencerenizi eklemek için:**
```python
TARGET_WINDOW_NAMES = [
    "metin2client",
    "Metin2",
    "YourGameWindow"  # Yeni pencere adı
]
```

#### Log Ayarları

```python
LOG_FILE = "dnz_logs.txt"
MAX_LOG_LINES = 1000  # Maksimum log satırı
```

#### GUI Ayarları

```python
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
THEME = "dark-blue"  # dark-blue, dark-green, light
```

### Özel Pattern Tanımlama

`engine.py` dosyasında özel AOB pattern'leri tanımlayabilirsiniz:

```python
# Örnek: Kendi pattern'inizi ekleyin
custom_pattern = b"\x48\x8B\x05\x00\x00\x00\x00"
addresses = scanner.scan_pattern(
    custom_pattern,
    start_address=0x00400000,
    end_address=0x00500000
)
```

---

## Sorun Giderme

### Yaygın Hatalar ve Çözümleri

#### 1. "Hedef pencere bulunamadı"

**Sebep**: Hedef uygulama çalışmıyor veya pencere adı eşleşmiyor

**Çözüm**:
```python
# config.py dosyasını düzenleyin
TARGET_WINDOW_NAMES = [
    "DogruPencereAdi"  # Doğru pencere adını yazın
]
```

**Pencere adını bulmak için**:
1. Task Manager'ı açın (Ctrl + Shift + Esc)
2. "Details" sekmesine gidin
3. Hedef uygulamanın adını bulun

#### 2. "Yönetici yetkileri gerekli"

**Sebep**: Bazı işlemler yönetici gerektirir

**Çözüm**:
- Programı sağ tıklayın
- "Yönetici olarak çalıştır" seçin

#### 3. "Process handle alınamadı"

**Sebep**: Hedef uygulamanın koruması var

**Çözüm**:
- Anti-cheat yazılımını geçici olarak devre dışı bırakın
- Firewall ayarlarını kontrol edin
- Yönetici yetkileri ile çalıştırın

#### 4. Log dosyası yazılamıyor

**Sebep**: Dosya izinleri yetersiz

**Çözüm**:
```bash
# Yazılabilir bir dizinde çalıştırın
cd C:\Users\YourName\Documents
python main.py
```

### Performans Sorunları

#### Yüksek CPU Kullanımı

**Sebep**: Çok sık tarama

**Çözüm**:
```python
# config.py
SCAN_INTERVAL = 1.0  # 0.5'ten 1.0'a çıkar
```

#### Bellek Kullanımı Artışı

**Sebep**: Log dosyası çok büyüdü

**Çözüm**:
```python
# Log dosyasını temizle
import os
os.remove("dnz_logs.txt")
```

---

## İpuçları ve Püf Noktaları

### En İyi Pratikler

#### 1. Optimal Ayarlar

```python
# Dengeli performans için
MIN_DELAY = 5
MAX_DELAY = 12
SCAN_INTERVAL = 0.5
```

#### 2. Log Yönetimi

```python
# Periyodik log temizliği
# Her 1000 satırda bir temizle
if log_line_count > 1000:
    clear_old_logs()
```

#### 3. Çoklu Hedef Pencere

```python
# Birden fazla oyun için
TARGET_WINDOW_NAMES = [
    "Game1",
    "Game2", 
    "Game3"
]
```

### Gelişmiş Kullanım

#### Custom Pattern Oluşturma

```python
from utils import PatternGenerator

# Hex string'den pattern
pattern = PatternGenerator.from_hex_string("48 8B 05 ?? ?? ?? ??")

# Integer'dan pattern
pattern = PatternGenerator.create_int_pattern(123456)

# String'den pattern
pattern = PatternGenerator.create_string_pattern("AUTOBAN")
```

#### Manuel Pencere Seçimi

```python
# gui.py içinde
def select_window_manually(self):
    windows = self.engine.process_manager.get_all_windows()
    # Kullanıcıya liste göster
    # Seçilen pencereye bağlan
```

### Güvenlik İpuçları

1. **Antivirüs Uyarıları**
   - EXE dosyaları false-positive verebilir
   - Güvenilir kaynaklardan indirin
   - Kaynak kodunu kendiniz derleyin

2. **Veri Güvenliği**
   - Log dosyaları hassas bilgi içerebilir
   - Düzenli olarak temizleyin
   - Başkalarıyla paylaşmayın

3. **Ağ Güvenliği**
   - DNZ internet bağlantısı gerektirmez
   - Firewall bloğu normaldir
   - Sadece lokal işlem yapar

### Performans Optimizasyonu

#### CPU Kullanımını Azaltma

```python
# Daha uzun scan interval
SCAN_INTERVAL = 1.0

# Daha az pattern tarama
AOB_PATTERNS = [
    b"\x00\x00\x00\x00"  # Sadece bir pattern
]
```

#### Hız Artırma

```python
# Daha kısa gecikme
MIN_DELAY = 2
MAX_DELAY = 6

# Daha sık tarama
SCAN_INTERVAL = 0.2
```

---

## Klavye Kısayolları

| Kısayol | İşlev |
|---------|-------|
| Ctrl + L | Log'u temizle |
| F5 | Yeniden başlat |
| Esc | Durdur |
| Space | Duraklat/Devam |

*(Not: Klavye kısayolları ileride eklenebilir)*

---

## Sık Sorulan Sorular

**S: Birden fazla pencerede çalışabilir mi?**
C: Hayır, aynı anda sadece bir hedef pencere desteklenir.

**S: Arka planda çalışır mı?**
C: Evet, pencere minimize edilebilir.

**S: Otomatik başlatma var mı?**
C: Şu an için manuel başlatma gereklidir.

**S: MacOS/Linux desteği var mı?**
C: Hayır, sadece Windows desteklenmektedir.

---

## Destek ve Yardım

### Yardım Almak İçin

1. **README.md dosyasını okuyun**
2. **Bu kılavuzu inceleyin**
3. **Log dosyasını kontrol edin**
4. **GitHub Issues açın**
5. **E-posta gönderin**: support@dnz-assistant.com

### Bug Raporu

Sorun bildirirken şunları ekleyin:
- Windows versiyonu
- DNZ versiyonu
- Hata mesajı
- Log dosyası (son 50 satır)
- Yeniden oluşturma adımları

---

**DNZ Assistant ile verimli çalışmalar! 🚀**