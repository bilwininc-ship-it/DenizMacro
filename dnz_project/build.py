"""
DNZ (Dinamik Nesne Zamanlayıcı) - Build Script
PyInstaller veya Nuitka ile tek dosya EXE oluşturur
"""

import os
import sys
import shutil
import subprocess


class DNZBuilder:
    """DNZ için build yöneticisi"""
    
    def __init__(self):
        self.project_name = "DNZ_Assistant"
        self.main_file = "main.py"
        self.icon_file = "icon.ico"  # Eğer varsa
        self.dist_dir = "dist"
        self.build_dir = "build"
        
    def clean_build_dirs(self):
        """Build dizinlerini temizler"""
        print("Eski build dosyaları temizleniyor...")
        
        dirs_to_clean = [self.dist_dir, self.build_dir, "__pycache__"]
        
        for dir_name in dirs_to_clean:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(f"  ✓ {dir_name} silindi")
        
        # .spec dosyasını sil
        spec_file = f"{self.project_name}.spec"
        if os.path.exists(spec_file):
            os.remove(spec_file)
            print(f"  ✓ {spec_file} silindi")
        
        print()
    
    def build_with_pyinstaller(self):
        """PyInstaller ile build yapar"""
        print("=" * 60)
        print("PyInstaller ile build yapılıyor...")
        print("=" * 60)
        print()
        
        # PyInstaller komutunu oluştur
        cmd = [
            "pyinstaller",
            "--onefile",  # Tek dosya
            "--windowed",  # Console penceresini gizle (GUI için)
            "--name", self.project_name,
            "--clean",  # Cache temizle
        ]
        
        # İkon varsa ekle
        if os.path.exists(self.icon_file):
            cmd.extend(["--icon", self.icon_file])
        
        # Ana dosyayı ekle
        cmd.append(self.main_file)
        
        try:
            # Build işlemini başlat
            print("Komut:", " ".join(cmd))
            print()
            result = subprocess.run(cmd, check=True)
            
            if result.returncode == 0:
                print()
                print("=" * 60)
                print("✓ Build başarıyla tamamlandı!")
                print(f"✓ EXE dosyası: {os.path.join(self.dist_dir, self.project_name + '.exe')}")
                print("=" * 60)
                return True
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Build hatası: {e}")
            return False
        except FileNotFoundError:
            print("\n✗ HATA: PyInstaller bulunamadı!")
            print("Yüklemek için: pip install pyinstaller")
            return False
    
    def build_with_nuitka(self):
        """Nuitka ile build yapar (daha optimize)"""
        print("=" * 60)
        print("Nuitka ile build yapılıyor...")
        print("=" * 60)
        print()
        
        # Nuitka komutunu oluştur
        cmd = [
            "python", "-m", "nuitka",
            "--standalone",  # Bağımsız çalışabilir
            "--onefile",  # Tek dosya
            "--windows-disable-console",  # Console gizle
            f"--output-filename={self.project_name}.exe",
            "--enable-plugin=tk-inter",  # Tkinter desteği
        ]
        
        # İkon varsa ekle
        if os.path.exists(self.icon_file):
            cmd.append(f"--windows-icon-from-ico={self.icon_file}")
        
        # Ana dosyayı ekle
        cmd.append(self.main_file)
        
        try:
            # Build işlemini başlat
            print("Komut:", " ".join(cmd))
            print()
            print("NOT: Nuitka build süreci uzun sürebilir (5-10 dakika)...")
            print()
            result = subprocess.run(cmd, check=True)
            
            if result.returncode == 0:
                print()
                print("=" * 60)
                print("✓ Build başarıyla tamamlandı!")
                print(f"✓ EXE dosyası: {self.project_name}.exe")
                print("=" * 60)
                return True
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Build hatası: {e}")
            return False
        except FileNotFoundError:
            print("\n✗ HATA: Nuitka bulunamadı!")
            print("Yüklemek için: pip install nuitka")
            return False
    
    def run(self, builder_type="pyinstaller"):
        """Build işlemini çalıştırır"""
        print()
        print("=" * 60)
        print(f"  DNZ Assistant - Build Aracı")
        print("=" * 60)
        print()
        
        # Temizlik
        self.clean_build_dirs()
        
        # Build
        if builder_type.lower() == "pyinstaller":
            success = self.build_with_pyinstaller()
        elif builder_type.lower() == "nuitka":
            success = self.build_with_nuitka()
        else:
            print(f"✗ Bilinmeyen builder tipi: {builder_type}")
            print("Geçerli tipler: pyinstaller, nuitka")
            success = False
        
        if success:
            print()
            print("Build işlemi tamamlandı! 🎉")
            print()
        else:
            print()
            print("Build işlemi başarısız oldu! ❌")
            print()


def main():
    """Ana fonksiyon"""
    builder = DNZBuilder()
    
    # Komut satırı argümanlarını kontrol et
    if len(sys.argv) > 1:
        builder_type = sys.argv[1]
    else:
        # Varsayılan: PyInstaller
        builder_type = "pyinstaller"
    
    builder.run(builder_type)


if __name__ == "__main__":
    main()