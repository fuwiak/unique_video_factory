#!/usr/bin/env python3
"""
Skrypt sprawdzania struktury folderów na Yandex Disk
"""

import os
from dotenv import load_dotenv
import yadisk


def check_yandex_structure():
    """Sprawdza strukturę folderów na Yandex Disk"""
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
        
        # Sprawdzamy strukturę folderów
        base_folder = "Медиабанк/Команда 1"
        
        print(f"📁 Sprawdzanie struktury w: {base_folder}")
        
        # Sprawdzamy czy istnieje główny folder
        if not yandex.exists(base_folder):
            print(f"❌ Główny folder nie istnieje: {base_folder}")
            return False
        
        print(f"✅ Główny folder istnieje: {base_folder}")
        
        # Sprawdzamy zawartość głównego folderu
        try:
            contents = yandex.listdir(base_folder)
            print(f"📋 Zawartość głównego folderu:")
            for item in contents:
                print(f"  - {item['name']} ({item['type']})")
        except Exception as e:
            print(f"❌ Błąd odczytu zawartości: {e}")
            return False
        
        # Sprawdzamy foldery Нина i Рэйчел
        bloggers = ["Нина", "Рэйчел"]
        
        for blogger in bloggers:
            blogger_folder = f"{base_folder}/{blogger}"
            print(f"\n👤 Sprawdzanie folderu: {blogger}")
            
            if yandex.exists(blogger_folder):
                print(f"✅ Folder {blogger} istnieje")
                
                # Sprawdzamy zawartość folderu blogera
                try:
                    blogger_contents = yandex.listdir(blogger_folder)
                    print(f"📋 Zawartość folderu {blogger}:")
                    for item in blogger_contents:
                        print(f"  - {item['name']} ({item['type']})")
                except Exception as e:
                    print(f"❌ Błąd odczytu folderu {blogger}: {e}")
                
                # Sprawdzamy foldery approved i not_approved
                for status in ["approved", "not_approved"]:
                    status_folder = f"{blogger_folder}/{status}"
                    if yandex.exists(status_folder):
                        print(f"✅ Folder {status} istnieje w {blogger}")
                    else:
                        print(f"❌ Folder {status} nie istnieje w {blogger}")
                        # Tworzymy folder
                        try:
                            yandex.mkdir(status_folder)
                            print(f"✅ Utworzono folder {status} w {blogger}")
                        except Exception as e:
                            print(f"❌ Błąd tworzenia folderu {status}: {e}")
            else:
                print(f"❌ Folder {blogger} nie istnieje")
                # Tworzymy folder blogera
                try:
                    yandex.mkdir(blogger_folder)
                    print(f"✅ Utworzono folder {blogger}")
                    
                    # Tworzymy foldery approved i not_approved
                    for status in ["approved", "not_approved"]:
                        status_folder = f"{blogger_folder}/{status}"
                        yandex.mkdir(status_folder)
                        print(f"✅ Utworzono folder {status} w {blogger}")
                        
                except Exception as e:
                    print(f"❌ Błąd tworzenia folderu {blogger}: {e}")
        
        print("\n🎉 Struktura folderów została sprawdzona i utworzona!")
        return True
        
    except Exception as e:
        print(f"❌ Błąd sprawdzania struktury Yandex Disk: {e}")
        return False


def create_new_folder(blogger_name, folder_name):
    """Tworzy nowy folder dla blogera"""
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
        
        base_folder = "Медиабанк/Команда 1"
        blogger_folder = f"{base_folder}/{blogger_name}"
        
        # Sprawdzamy czy folder blogera istnieje
        if not yandex.exists(blogger_folder):
            yandex.mkdir(blogger_folder)
            print(f"✅ Utworzono folder blogera: {blogger_name}")
        
        # Tworzymy nowy folder
        new_folder = f"{blogger_folder}/{folder_name}"
        if not yandex.exists(new_folder):
            yandex.mkdir(new_folder)
            print(f"✅ Utworzono nowy folder: {new_folder}")
            
            # Tworzymy foldery approved i not_approved w nowym folderze
            for status in ["approved", "not_approved"]:
                status_folder = f"{new_folder}/{status}"
                yandex.mkdir(status_folder)
                print(f"✅ Utworzono folder {status} w {folder_name}")
            
            return True
        else:
            print(f"⚠️ Folder już istnieje: {new_folder}")
            return True
            
    except Exception as e:
        print(f"❌ Błąd tworzenia nowego folderu: {e}")
        return False


def main():
    """Główna funkcja"""
    print("🔍 SPRAWDZANIE STRUKTURY YANDEX DISK")
    print("=" * 50)
    
    # Sprawdzamy strukturę
    if check_yandex_structure():
        print("\n✅ Struktura folderów jest gotowa!")
        
        # Pytamy czy utworzyć nowy folder
        print("\n📁 Czy chcesz utworzyć nowy folder?")
        print("1. Tak")
        print("2. Nie")
        
        choice = input("Wybierz opcję (1/2): ").strip()
        
        if choice == "1":
            blogger_name = input("Podaj nazwę blogera: ").strip()
            folder_name = input("Podaj nazwę nowego folderu: ").strip()
            
            if blogger_name and folder_name:
                if create_new_folder(blogger_name, folder_name):
                    print(f"✅ Nowy folder utworzony: {blogger_name}/{folder_name}")
                else:
                    print("❌ Błąd tworzenia nowego folderu")
            else:
                print("❌ Nie podano nazwy blogera lub folderu")
        else:
            print("👋 Zakończono bez tworzenia nowego folderu")
    else:
        print("❌ Błąd sprawdzania struktury folderów")


if __name__ == "__main__":
    main()
