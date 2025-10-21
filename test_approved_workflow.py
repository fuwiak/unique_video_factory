#!/usr/bin/env python3
"""
Skrypt testowania workflow approved
"""

import os
import asyncio
from dotenv import load_dotenv
import yadisk


def test_approved_workflow():
    """Testuje workflow approved"""
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
        approved_folder = f"{base_folder}/approved"
        
        print(f"📁 Sprawdzanie folderu approved: {approved_folder}")
        
        if yandex.exists(approved_folder):
            print(f"✅ Folder approved istnieje: {approved_folder}")
            
            # Sprawdzamy zawartość
            try:
                contents = yandex.listdir(approved_folder)
                print(f"📋 Zawartość folderu approved:")
                for item in contents:
                    print(f"  - {item['name']} ({item['type']})")
            except Exception as e:
                print(f"⚠️ Nie można odczytać zawartości: {e}")
        else:
            print(f"❌ Folder approved nie istnieje: {approved_folder}")
            return False
        
        # Testujemy tworzenie testowego folderu
        test_folder = f"{approved_folder}/test_approval"
        try:
            if not yandex.exists(test_folder):
                yandex.mkdir(test_folder)
                print(f"✅ Utworzono test folder: {test_folder}")
            else:
                print(f"📁 Test folder już istnieje: {test_folder}")
        except Exception as e:
            print(f"❌ Błąd tworzenia test folderu: {e}")
            return False
        
        print("\n🎉 Workflow approved działa poprawnie!")
        return True
        
    except Exception as e:
        print(f"❌ Błąd testowania workflow approved: {e}")
        return False


def main():
    """Główna funkcja"""
    print("🧪 TEST WORKFLOW APPROVED")
    print("=" * 40)
    
    success = test_approved_workflow()
    
    if success:
        print("\n✅ Test zakończony pomyślnie!")
        print("📁 Workflow approved jest gotowy")
        print("🚀 Bot może teraz przenosić pliki do approved")
    else:
        print("\n❌ Test nie powiódł się!")
        print("💡 Sprawdź konfigurację Yandex Disk")


if __name__ == "__main__":
    main()




