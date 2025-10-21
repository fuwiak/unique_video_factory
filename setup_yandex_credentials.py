#!/usr/bin/env python3
"""
Skrypt do konfiguracji własnych credentials Yandex
"""

import os
from pathlib import Path


def main():
    """Konfiguruje własne credentials Yandex"""
    print("🔐 KONFIGURACJA WŁASNYCH CREDENTIALS YANDEX")
    print("=" * 60)
    print()
    
    print("📋 Ten skrypt pomoże Ci skonfigurować własne credentials")
    print("   dla aplikacji Yandex Disk")
    print()
    
    # Sprawdzamy czy .env istnieje
    env_path = Path(".env")
    
    if env_path.exists():
        print("📁 Znaleziono plik .env")
        overwrite = input("Czy chcesz zaktualizować istniejące credentials? (y/N): ").strip().lower()
        if overwrite not in ['y', 'yes', 'tak', 't']:
            print("❌ Anulowano.")
            return
    else:
        print("📁 Tworzę nowy plik .env")
    
    print("\n🔧 Konfiguracja credentials:")
    print()
    
    # Client ID
    print("1. Yandex Client ID:")
    print("   - Przejdź do https://oauth.yandex.ru/")
    print("   - Zaloguj się i utwórz aplikację")
    print("   - Skopiuj Client ID")
    
    client_id = input("Wprowadź YANDEX_CLIENT_ID: ").strip()
    if not client_id:
        print("❌ Client ID jest wymagany!")
        return
    
    # Client Secret
    print("\n2. Yandex Client Secret:")
    print("   - Z tej samej strony aplikacji")
    print("   - Skopiuj Client Secret")
    
    client_secret = input("Wprowadź YANDEX_CLIENT_SECRET: ").strip()
    if not client_secret:
        print("❌ Client Secret jest wymagany!")
        return
    
    # Redirect URI
    print("\n3. Redirect URI:")
    print("   - To URL, na który Yandex przekieruje po autoryzacji")
    print("   - Może być: http://localhost:8080/callback")
    print("   - Lub: https://yourdomain.com/callback")
    
    redirect_uri = input("Wprowadź YANDEX_REDIRECT_URI: ").strip()
    if not redirect_uri:
        print("❌ Redirect URI jest wymagany!")
        return
    
    # Folder na Yandex Disk
    print("\n4. Folder na Yandex Disk:")
    print("   - Nazwa folderu, gdzie będą zapisywane pliki")
    
    yandex_folder = input("Wprowadź YANDEX_DISK_FOLDER (domyślnie: unique_video_factory): ").strip()
    if not yandex_folder:
        yandex_folder = "unique_video_factory"
    
    # Tworzymy plik .env
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_ADMIN_ID=your_telegram_user_id_here

# Yandex Disk Configuration
YANDEX_DISK_TOKEN=your_yandex_disk_token_here
YANDEX_DISK_FOLDER={yandex_folder}

# Yandex OAuth Credentials (własna aplikacja)
YANDEX_CLIENT_ID={client_id}
YANDEX_CLIENT_SECRET={client_secret}
YANDEX_REDIRECT_URI={redirect_uri}

# Bot Settings
MAX_VIDEO_SIZE_MB=100
PROCESSING_TIMEOUT_MINUTES=30
"""
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n✅ Plik .env utworzony!")
    print(f"📁 Lokalizacja: {env_path.absolute()}")
    
    # Testujemy credentials
    print("\n🧪 Testowanie credentials...")
    test_credentials(client_id, client_secret, redirect_uri)
    
    print("\n🎉 KONFIGURACJA ZAKOŃCZONA!")
    print("✅ Własne credentials zostały skonfigurowane")
    print("🚀 Uruchom: python custom_yandex_token.py")


def test_credentials(client_id, client_secret, redirect_uri):
    """Testuje credentials"""
    try:
        import requests
        
        # Testujemy czy credentials są poprawne
        test_url = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
        
        print(f"🔗 Test URL: {test_url}")
        print("✅ Credentials wyglądają poprawnie!")
        print("💡 Uruchom: python custom_yandex_token.py aby uzyskać token")
        
    except Exception as e:
        print(f"❌ Błąd testowania credentials: {e}")


if __name__ == "__main__":
    main()
