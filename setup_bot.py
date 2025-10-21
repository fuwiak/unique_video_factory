#!/usr/bin/env python3
"""
Skrypt konfiguracji bota Telegram
"""

import os
from pathlib import Path


def create_env_file():
    """Tworzy plik .env z konfiguracją"""
    env_path = Path(".env")
    
    if env_path.exists():
        print("⚠️ Plik .env już istnieje!")
        overwrite = input("Czy nadpisać? (y/N): ").strip().lower()
        if overwrite not in ['y', 'yes', 'tak', 't']:
            print("❌ Anulowano.")
            return
    
    print("🔧 Konfiguracja bota Telegram")
    print("=" * 40)
    
    # Telegram Bot Token
    print("\n1. Telegram Bot Token:")
    print("   - Przejdź do @BotFather na Telegram")
    print("   - Wyślij /newbot")
    print("   - Podaj nazwę i username bota")
    print("   - Skopiuj token")
    
    bot_token = input("Wprowadź TELEGRAM_BOT_TOKEN: ").strip()
    
    # Telegram Admin ID - nie jest potrzebne
    print("\n2. Telegram Admin ID:")
    print("   - Nie jest potrzebne - bot jest otwarty dla wszystkich")
    print("   - Każdy może używać bota")
    
    admin_id = "0"  # Nie używamy
    
    # Yandex Disk Token
    print("\n3. Yandex Disk Token:")
    print("   - Opcja A: Użyj własnych credentials (python setup_yandex_credentials.py)")
    print("   - Opcja B: Użyj domyślnych credentials (python official_yandex_token.py)")
    
    yandex_token = input("Wprowadź YANDEX_DISK_TOKEN (opcjonalnie): ").strip()
    
    # Yandex Disk Folder
    yandex_folder = input("Wprowadź nazwę folderu na Yandex Disk (domyślnie: unique_video_factory): ").strip()
    if not yandex_folder:
        yandex_folder = "unique_video_factory"
    
    # Tworzymy plik .env
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={bot_token}

# Yandex Disk Configuration
YANDEX_DISK_TOKEN={yandex_token}
YANDEX_DISK_FOLDER={yandex_folder}

# Bot Settings
MAX_VIDEO_SIZE_MB=100
PROCESSING_TIMEOUT_MINUTES=30
"""
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n✅ Plik .env utworzony!")
    print(f"📁 Lokalizacja: {env_path.absolute()}")
    
    # Sprawdzamy konfigurację
    print("\n🔍 Sprawdzanie konfiguracji...")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN jest wymagany!")
        return False
    
    # TELEGRAM_ADMIN_ID nie jest potrzebne
    
    if not yandex_token:
        print("⚠️ YANDEX_DISK_TOKEN nie jest ustawiony - upload na Yandex Disk będzie wyłączony")
    
    print("✅ Konfiguracja poprawna!")
    return True


def test_telegram_connection():
    """Testuje połączenie z Telegram"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("❌ TELEGRAM_BOT_TOKEN nie znaleziony!")
            return False
        
        import requests
        
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                bot_info = data['result']
                print(f"✅ Połączenie z Telegram OK!")
                print(f"🤖 Bot: @{bot_info['username']} ({bot_info['first_name']})")
                return True
        
        print(f"❌ Błąd połączenia z Telegram: {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Błąd testowania połączenia: {e}")
        return False


def test_yandex_connection():
    """Testuje połączenie z Yandex Disk"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        yandex_token = os.getenv('YANDEX_DISK_TOKEN')
        if not yandex_token:
            print("⚠️ YANDEX_DISK_TOKEN nie ustawiony - pomijam test")
            return True
        
        import yadisk
        
        yandex = yadisk.YaDisk(token=yandex_token)
        
        # Testujemy połączenie
        if yandex.check_token():
            print("✅ Połączenie z Yandex Disk OK!")
            
            # Sprawdzamy folder
            folder = os.getenv('YANDEX_DISK_FOLDER', 'unique_video_factory')
            if not yandex.exists(folder):
                yandex.mkdir(folder)
                print(f"📁 Utworzono folder: {folder}")
            else:
                print(f"📁 Folder istnieje: {folder}")
            
            return True
        else:
            print("❌ Nieprawidłowy token Yandex Disk!")
            return False
            
    except Exception as e:
        print(f"❌ Błąd testowania Yandex Disk: {e}")
        return False


def main():
    """Główna funkcja"""
    print("🤖 KONFIGURACJA BOTA TELEGRAM")
    print("=" * 50)
    
    # Sprawdzamy czy .env istnieje
    if Path(".env").exists():
        print("📁 Plik .env już istnieje.")
        choice = input("Czy chcesz go zaktualizować? (y/N): ").strip().lower()
        if choice in ['y', 'yes', 'tak', 't']:
            create_env_file()
    else:
        create_env_file()
    
    print("\n🧪 Testowanie konfiguracji...")
    
    # Test Telegram
    telegram_ok = test_telegram_connection()
    
    # Test Yandex Disk
    yandex_ok = test_yandex_connection()
    
    print("\n📊 PODSUMOWANIE:")
    print(f"   Telegram: {'✅ OK' if telegram_ok else '❌ Błąd'}")
    print(f"   Yandex Disk: {'✅ OK' if yandex_ok else '❌ Błąd'}")
    
    if telegram_ok:
        print("\n🚀 Bot gotowy do uruchomienia!")
        print("   Uruchom: python telegram_bot.py")
    else:
        print("\n❌ Napraw błędy konfiguracji przed uruchomieniem bota.")


if __name__ == "__main__":
    main()
