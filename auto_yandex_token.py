#!/usr/bin/env python3
"""
Automatyczny skrypt do uzyskania Yandex token z selenium
"""

import os
import time
import webbrowser
from urllib.parse import urlparse, parse_qs


def get_token_manually():
    """Ręczne uzyskanie tokenu z instrukcjami"""
    print("🤖 AUTOMATYCZNY POMOCNIK TOKENU YANDEX")
    print("=" * 50)
    print()
    print("📋 Ten skrypt pomoże Ci uzyskać token Yandex Disk")
    print()
    
    # Krok 1: Otwieramy stronę autoryzacji
    oauth_url = "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d&redirect_uri=https://oauth.yandex.ru/verification_code"
    
    print("🌐 Krok 1: Otwieranie strony autoryzacji...")
    print(f"   URL: {oauth_url}")
    
    try:
        webbrowser.open(oauth_url)
        print("✅ Strona otwarta w przeglądarce")
    except:
        print("⚠️ Skopiuj i otwórz w przeglądarce:")
        print(f"   {oauth_url}")
    
    print()
    print("📋 Krok 2: Logowanie")
    print("   1. Zaloguj się swoim mailem i hasłem Yandex")
    print("   2. Jeśli masz 2FA, wprowadź kod")
    print("   3. Po zalogowaniu zostaniesz przekierowany")
    print()
    
    print("📋 Krok 3: Kopiowanie tokenu")
    print("   Po przekierowaniu w adresie URL znajdziesz:")
    print("   https://oauth.yandex.ru/verification_code#access_token=TOKEN&token_type=bearer")
    print()
    print("   Skopiuj tylko część TOKEN (bez 'access_token=' i '&token_type=bearer')")
    print()
    
    # Pętla pobierania tokenu
    while True:
        print("🔑 Wprowadź token (lub 'q' aby zakończyć):")
        token = input("> ").strip()
        
        if token.lower() == 'q':
            print("👋 Zakończono")
            return None
        
        if not token:
            print("❌ Token nie może być pusty!")
            continue
        
        # Testujemy token
        print("🧪 Testowanie tokenu...")
        if test_token(token):
            print("✅ Token działa!")
            save_token(token)
            return token
        else:
            print("❌ Token nie działa!")
            print("💡 Sprawdź czy skopiowałeś pełny token")
            continue


def test_token(token):
    """Testuje token Yandex"""
    try:
        import yadisk
        yandex = yadisk.YaDisk(token=token)
        
        if yandex.check_token():
            # Pobieramy dodatkowe informacje
            try:
                disk_info = yandex.get_disk_info()
                user_name = disk_info.get('user', {}).get('display_name', 'Nieznany')
                total_space = disk_info.get('total_space', 0) / (1024**3)
                
                print(f"👤 Użytkownik: {user_name}")
                print(f"💾 Dostępne miejsce: {total_space:.1f} GB")
            except:
                pass
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Błąd testowania: {e}")
        return False


def save_token(token):
    """Zapisuje token do pliku .env"""
    env_path = ".env"
    
    print(f"💾 Zapisuję token do {env_path}...")
    
    # Sprawdzamy czy .env istnieje
    if os.path.exists(env_path):
        # Czytamy plik
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Aktualizujemy lub dodajemy token
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('YANDEX_DISK_TOKEN='):
                lines[i] = f'YANDEX_DISK_TOKEN={token}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'YANDEX_DISK_TOKEN={token}\n')
        
        # Zapisujemy
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    else:
        # Tworzymy nowy plik
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f'YANDEX_DISK_TOKEN={token}\n')
    
    print("✅ Token zapisany!")
    print("🚀 Możesz teraz uruchomić bota: python telegram_bot.py")


def main():
    """Główna funkcja"""
    try:
        token = get_token_manually()
        if token:
            print("\n🎉 SUKCES!")
            print("✅ Token Yandex Disk został uzyskany i zapisany")
            print("📁 Sprawdź plik .env")
            print("🚀 Uruchom bota: python telegram_bot.py")
        else:
            print("\n❌ Nie udało się uzyskać tokenu")
            print("💡 Spróbuj ponownie lub skontaktuj się z pomocą")
    
    except KeyboardInterrupt:
        print("\n👋 Zakończono przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")


if __name__ == "__main__":
    main()
