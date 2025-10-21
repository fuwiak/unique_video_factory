#!/usr/bin/env python3
"""
Skrypt testowania przenoszenia plików na Yandex Disk
"""

import os
from dotenv import load_dotenv
import yadisk


def test_yandex_move():
    """Testuje przenoszenie plików na Yandex Disk"""
    load_dotenv()
    
    yandex_token = os.getenv('YANDEX_DISK_TOKEN')
    if not yandex_token:
        print("❌ YANDEX_DISK_TOKEN nie ustawiony!")
        return False
    
    try:
        yandex = yadisk.YaDisk(token=yandex_token)
        
        if not yandex.check_token():
            print("❌ Nieprawidłowy token Yandex Disk!")
            return False
        
        print("✅ Połączenie z Yandex Disk OK!")
        
        # Testujemy strukturę folderów
        base_folder = os.getenv('YANDEX_DISK_FOLDER', 'unique_video_factory')
        runs_folder = f"{base_folder}/runs"
        approved_folder = f"{base_folder}/approved"
        
        print(f"📁 Sprawdzanie folderów:")
        print(f"  - Runs: {runs_folder}")
        print(f"  - Approved: {approved_folder}")
        
        # Sprawdzamy runs folder
        if yandex.exists(runs_folder):
            print(f"✅ Folder runs istnieje")
            try:
                runs_contents = yandex.listdir(runs_folder)
                print(f"📋 Zawartość folderu runs:")
                for item in runs_contents:
                    print(f"  - {item['name']} ({item['type']})")
                    
                    # Sprawdzamy zawartość podfolderów
                    if item['type'] == 'dir':
                        run_path = f"{runs_folder}/{item['name']}"
                        try:
                            run_contents = yandex.listdir(run_path)
                            for file_item in run_contents:
                                print(f"    - {file_item['name']} ({file_item['type']})")
                        except Exception as e:
                            print(f"    ❌ Błąd odczytu: {e}")
            except Exception as e:
                print(f"❌ Błąd odczytu runs folderu: {e}")
        else:
            print(f"❌ Folder runs nie istnieje")
            return False
        
        # Sprawdzamy approved folder
        if yandex.exists(approved_folder):
            print(f"✅ Folder approved istnieje")
            try:
                approved_contents = yandex.listdir(approved_folder)
                print(f"📋 Zawartość folderu approved:")
                for item in approved_contents:
                    print(f"  - {item['name']} ({item['type']})")
            except Exception as e:
                print(f"❌ Błąd odczytu approved folderu: {e}")
        else:
            print(f"❌ Folder approved nie istnieje")
            return False
        
        print("\n🎉 Struktura Yandex Disk jest gotowa!")
        print("🚀 Bot może teraz przenosić pliki z runs do approved")
        return True
        
    except Exception as e:
        print(f"❌ Błąd testowania Yandex Disk: {e}")
        return False


def main():
    """Główna funkcja"""
    print("🧪 TEST PRZENOSZENIA PLIKÓW YANDEX DISK")
    print("=" * 50)
    
    success = test_yandex_move()
    
    if success:
        print("\n✅ Test zakończony pomyślnie!")
        print("📁 Yandex Disk jest gotowy do przenoszenia plików")
        print("🔄 Bot będzie przenosić pliki z runs do approved")
    else:
        print("\n❌ Test nie powiódł się!")
        print("💡 Sprawdź konfigurację Yandex Disk")


if __name__ == "__main__":
    main()




