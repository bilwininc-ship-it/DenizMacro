import os
import re

def unpack_root():
    # Dosyanın olabileceği yolları kontrol et
    possible_paths = [
        "root", 
        "pack/root", 
        "root.epk", 
        "pack/root.epk"
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break

    if not file_path:
        print("[!] Hata: 'root' dosyası ne ana klasörde ne de 'pack' klasöründe bulundu!")
        print(f"[*] Şu anki konumun: {os.getcwd()}")
        return

    print(f"[*] Hedef dosya bulundu: {file_path}")
    output_dir = "root_extracted"
    os.makedirs(output_dir, exist_ok=True)

    with open(file_path, "rb") as f:
        data = f.read()

    # Eğer dosya içinde Python kodları varsa (uiquestion gibi) ayıkla
    if b"uiquestion" in data.lower() or b"import " in data:
        print("[+] Hazine bulundu! Python scriptleri tespit edildi.")
        
        # Bu kısım dosya içindeki düz metinleri (scriptleri) ayıklar
        with open(f"{output_dir}/extracted_scripts.txt", "w", encoding="utf-8") as out:
            # 6 karakterden uzun, kod olabilecek metinleri bulur
            scripts = re.findall(rb"[\x20-\x7E]{6,}", data)
            for s in scripts:
                try:
                    line = s.decode('utf-8')
                    if "import" in line or "self." in line or "SetText" in line:
                        out.write(line + "\n---\n")
                except:
                    continue
        
        print(f"[+] İşlem bitti. '{output_dir}/extracted_scripts.txt' dosyasını kontrol et!")
    else:
        print("[!] Dosya bulundu ama içeriği şifreli (FoxFS veya farklı bir kilit var).")

if __name__ == "__main__":
    unpack_root()