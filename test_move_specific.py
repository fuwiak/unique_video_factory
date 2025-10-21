#!/usr/bin/env python3
"""
Test przenoszenia konkretnego pliku z runs do approved
"""

import os
from dotenv import load_dotenv
import yadisk


def test_move_specific_file():
    """Testuje przenoszenie konkretnego pliku"""
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
        
        # Konkretny folder do testowania
        source_folder = "unique_video_factory/runs/run_20251015_163638"
        target_folder = "unique_video_factory/approved/test_move"
        
        print(f"📁 Testowanie przenoszenia z: {source_folder}")
        print(f"📁 Do: {target_folder}")
        
        # Sprawdzamy czy źródłowy folder istnieje
        if not yandex.exists(source_folder):
            print(f"❌ Źródłowy folder nie istnieje: {source_folder}")
            return False
        
        print(f"✅ Źródłowy folder istnieje")
        
        # Sprawdzamy zawartość źródłowego folderu
        try:
            source_contents = yandex.listdir(source_folder)
            print(f"📋 Zawartość źródłowego folderu:")
            for item in source_contents:
                print(f"  - {item['name']} ({item['type']})")
                
                if item['name'].endswith('.mp4'):
                    source_file = f"{source_folder}/{item['name']}"
                    print(f"    🎬 Znaleziono plik wideo: {source_file}")
                    
                    # Tworzymy folder docelowy
                    if not yandex.exists("unique_video_factory/approved"):
                        yandex.mkdir("unique_video_factory/approved")
                        print("✅ Utworzono folder approved")
                    
                    if not yandex.exists(target_folder):
                        yandex.mkdir(target_folder)
                        print(f"✅ Utworzono folder docelowy: {target_folder}")
                    
                    # Przenosimy plik
                    target_file = f"{target_folder}/video.mp4"
                    try:
                        print(f"🔄 Kopiowanie pliku...")
                        yandex.copy(source_file, target_file)
                        print(f"✅ Plik skopiowany do: {target_file}")
                        
                        print(f"🗑️ Usuwanie oryginalnego pliku...")
                        yandex.remove(source_file)
                        print(f"✅ Oryginalny plik usunięty: {source_file}")
                        
                        print(f"🎉 Plik pomyślnie przeniesiony!")
                        return True
                        
                    except Exception as move_error:
                        print(f"❌ Błąd przenoszenia pliku: {move_error}")
                        return False
                        
        except Exception as e:
            print(f"❌ Błąd odczytu źródłowego folderu: {e}")
            return False
        
        print("❌ Nie znaleziono plików .mp4 w źródłowym folderze")
        return False
        
    except Exception as e:
        print(f"❌ Błąd testowania: {e}")
        return False


def main():
    """Główna funkcja"""
    print("🧪 TEST PRZENOSZENIA KONKRETNEGO PLIKU")
    print("=" * 50)
    
    success = test_move_specific_file()
    
    if success:
        print("\n✅ Test zakończony pomyślnie!")
        print("📁 Plik został przeniesiony z runs do approved")
    else:
        print("\n❌ Test nie powiódł się!")
        print("💡 Sprawdź czy folder źródłowy istnieje")


if __name__ == "__main__":
    main()




