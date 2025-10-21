#!/usr/bin/env python3
"""
Skrypt testowania folderów Yandex Disk
"""

import os
from dotenv import load_dotenv
import yadisk


def test_yandex_folders():
    """Testuje tworzenie folderów na Yandex Disk"""
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
        
        # Testujemy tworzenie folderów
        base_folder = os.getenv('YANDEX_DISK_FOLDER', 'unique_video_factory')
        
        print(f"📁 Testowanie folderów w: {base_folder}")
        
        # Tworzymy podstawowe foldery
        folders_to_create = [
            base_folder,
            f"{base_folder}/runs",
            f"{base_folder}/approved"
        ]
        
        for folder in folders_to_create:
            try:
                if not yandex.exists(folder):
                    yandex.mkdir(folder)
                    print(f"✅ Utworzono folder: {folder}")
                else:
                    print(f"📁 Folder już istnieje: {folder}")
            except Exception as e:
                print(f"❌ Błąd tworzenia folderu {folder}: {e}")
                return False
        
        # Testujemy tworzenie podfolderu
        test_folder = f"{base_folder}/runs/test_run"
        try:
            if not yandex.exists(test_folder):
                yandex.mkdir(test_folder)
                print(f"✅ Utworzono test folder: {test_folder}")
            else:
                print(f"📁 Test folder już istnieje: {test_folder}")
        except Exception as e:
            print(f"❌ Błąd tworzenia test folderu: {e}")
            return False
        
        print("\n🎉 Wszystkie foldery zostały utworzone pomyślnie!")
        return True
        
    except Exception as e:
        print(f"❌ Błąd testowania Yandex Disk: {e}")
        return False


def main():
    """Główna funkcja"""
    print("🧪 TEST FOLDERÓW YANDEX DISK")
    print("=" * 40)
    
    success = test_yandex_folders()
    
    if success:
        print("\n✅ Test zakończony pomyślnie!")
        print("📁 Foldery Yandex Disk są gotowe")
        print("🚀 Bot może teraz zapisywać pliki")
    else:
        print("\n❌ Test nie powiódł się!")
        print("💡 Sprawdź token Yandex Disk")


if __name__ == "__main__":
    main()




