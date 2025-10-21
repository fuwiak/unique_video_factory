#!/usr/bin/env python3
"""
Poprawiony skrypt do uzyskania Yandex token z różnymi opcjami redirect_uri
"""

import webbrowser
import os


def main():
    """Poprawiony sposób na uzyskanie tokenu"""
    print("🔐 POPRAWIONY POMOCNIK TOKENU YANDEX")
    print("=" * 50)
    print()
    
    # Różne opcje redirect_uri
    redirect_options = [
        "https://oauth.yandex.ru/verification_code",
        "https://oauth.yandex.ru/verification_code/",
        "https://oauth.yandex.ru/verification_code?",
        "urn:ietf:wg:oauth:2.0:oob",
        "http://localhost:8080",
        "https://localhost:8080"
    ]
    
    print("🔧 Wybierz opcję redirect_uri:")
    print()
    for i, uri in enumerate(redirect_options, 1):
        print(f"{i}. {uri}")
    print()
    
    while True:
        try:
            choice = input("Wybierz opcję (1-6): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(redirect_options):
                redirect_uri = redirect_options[choice_num - 1]
                break
            else:
                print("❌ Nieprawidłowy wybór!")
                continue
        except ValueError:
            print("❌ Wprowadź liczbę!")
            continue
    
    # Tworzymy URL z wybranym redirect_uri
    oauth_url = f"https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d&redirect_uri={redirect_uri}"
    
    print(f"\n🌐 Otwieram stronę Yandex...")
    print(f"   URL: {oauth_url}")
    
    webbrowser.open(oauth_url)
    print("✅ Strona otwarta w przeglądarce")
    print()
    
    print("📋 Instrukcja:")
    print("1. Zaloguj się swoim mailem i hasłem Yandex")
    print("2. Po zalogowaniu zostaniesz przekierowany")
    print("3. W adresie URL znajdziesz: access_token=TOKEN")
    print("4. Skopiuj tylko TOKEN (bez 'access_token=')")
    print()
    
    # Pobieramy token
    while True:
        token = input("Wprowadź token (lub 'q' aby zakończyć): ").strip()
        
        if token.lower() == 'q':
            print("👋 Zakończono")
            return
        
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
                    disk_info = yandex.get_disk_info()
                    user_name = disk_info.get('user', {}).get('display_name', 'Nieznany')
                    total_space = disk_info.get('total_space', 0) / (1024**3)
                    
                    print(f"👤 Użytkownik: {user_name}")
                    print(f"💾 Dostępne miejsce: {total_space:.1f} GB")
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
            print(f"❌ Błąd: {e}")
            continue


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


if __name__ == "__main__":
    main()
