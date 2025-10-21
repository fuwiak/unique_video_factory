#!/usr/bin/env python3
"""
Prosty skrypt do uzyskania Yandex Disk token
"""

import webbrowser
import time
import os


def main():
    """Prosty sposób na uzyskanie tokenu"""
    print("🔐 UZYSKIWANIE TOKENU YANDEX DISK")
    print("=" * 50)
    print()
    print("📋 Metoda 1: Oficjalna strona Yandex")
    print("1. Otworzę stronę Yandex OAuth")
    print("2. Zaloguj się swoim mailem i hasłem")
    print("3. Skopiuj token z odpowiedzi")
    print()
    
    # Otwieramy oficjalną stronę Yandex
    oauth_url = "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d&redirect_uri=https://oauth.yandex.ru/verification_code"
    
    print(f"🌐 Otwieram: {oauth_url}")
    
    try:
        webbrowser.open(oauth_url)
        print("✅ Strona otwarta w przeglądarce")
    except:
        print("⚠️ Skopiuj i otwórz w przeglądarce:")
        print(f"   {oauth_url}")
    
    print()
    print("📋 Instrukcja:")
    print("1. Zaloguj się na stronie Yandex")
    print("2. Po zalogowaniu zostaniesz przekierowany")
    print("3. W adresie URL znajdziesz: access_token=TOKEN")
    print("4. Skopiuj TOKEN (bez 'access_token=')")
    print()
    print("Przykład URL:")
    print("https://oauth.yandex.ru/verification_code#access_token=AQAAAAA...&token_type=bearer")
    print("Token to: AQAAAAA...")
    print()
    
    while True:
        token = input("Wprowadź token: ").strip()
        
        if not token:
            print("❌ Token nie może być pusty!")
            continue
        
        # Testujemy token
        print("🧪 Testowanie tokenu...")
        try:
            import yadisk
            yandex = yadisk.YaDisk(token=token)
            
            if yandex.check_token():
                print("✅ Token działa!")
                
                # Pobieramy informacje o użytkowniku
                try:
                    user_info = yandex.get_disk_info()
                    print(f"👤 Użytkownik: {user_info.get('user', {}).get('display_name', 'Nieznany')}")
                    print(f"💾 Dostępne miejsce: {user_info.get('total_space', 0) / (1024**3):.1f} GB")
                except:
                    pass
                
                # Zapisujemy token
                save_token(token)
                return
            else:
                print("❌ Token nie działa!")
                print("💡 Sprawdź czy skopiowałeś pełny token")
                continue
                
        except Exception as e:
            print(f"❌ Błąd testowania: {e}")
            continue


def save_token(token):
    """Zapisuje token do pliku .env"""
    env_path = ".env"
    
    # Sprawdzamy czy .env istnieje
    if os.path.exists(env_path):
        # Czytamy plik
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Sprawdzamy czy token już istnieje
        if 'YANDEX_DISK_TOKEN=' in content:
            # Aktualizujemy istniejący token
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('YANDEX_DISK_TOKEN='):
                    lines[i] = f'YANDEX_DISK_TOKEN={token}'
                    break
            
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
        else:
            # Dodajemy nowy token
            with open(env_path, 'a', encoding='utf-8') as f:
                f.write(f'\nYANDEX_DISK_TOKEN={token}\n')
    else:
        # Tworzymy nowy plik
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f'YANDEX_DISK_TOKEN={token}\n')
    
    print(f"💾 Token zapisany do {env_path}")
    print("🚀 Możesz teraz uruchomić bota: python telegram_bot.py")


if __name__ == "__main__":
    main()
