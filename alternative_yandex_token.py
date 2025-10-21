#!/usr/bin/env python3
"""
Alternatywny skrypt do uzyskania Yandex token
"""

import webbrowser
import os


def main():
    """Alternatywna metoda uzyskania tokenu"""
    print("🔐 ALTERNATYWNY POMOCNIK TOKENU YANDEX")
    print("=" * 50)
    print()
    
    print("📋 Ta metoda używa alternatywnego redirect_uri")
    print("   Może działać gdy oficjalna metoda nie działa")
    print()
    
    # Różne opcje URL
    url_options = [
        {
            "name": "Opcja 1: Oficjalna",
            "url": "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d&redirect_uri=https://oauth.yandex.ru/verification_code"
        },
        {
            "name": "Opcja 2: Z końcowym slash",
            "url": "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d&redirect_uri=https://oauth.yandex.ru/verification_code/"
        },
        {
            "name": "Opcja 3: Z parametrem",
            "url": "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d&redirect_uri=https://oauth.yandex.ru/verification_code?"
        },
        {
            "name": "Opcja 4: OOB (Out-of-Band)",
            "url": "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
        }
    ]
    
    print("🔧 Wybierz opcję URL:")
    print()
    for i, option in enumerate(url_options, 1):
        print(f"{i}. {option['name']}")
    print()
    
    while True:
        try:
            choice = input("Wybierz opcję (1-4): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(url_options):
                selected_option = url_options[choice_num - 1]
                break
            else:
                print("❌ Nieprawidłowy wybór!")
                continue
        except ValueError:
            print("❌ Wprowadź liczbę!")
            continue
    
    oauth_url = selected_option['url']
    
    print(f"\n🌐 Otwieram: {selected_option['name']}")
    print(f"   URL: {oauth_url}")
    
    webbrowser.open(oauth_url)
    print("✅ Strona otwarta w przeglądarce")
    print()
    
    print("📋 Instrukcja:")
    print("1. Zaloguj się swoim mailem i hasłem Yandex")
    print("2. Jeśli masz 2FA, wprowadź kod")
    print("3. Po zalogowaniu zostaniesz przekierowany")
    print("4. W adresie URL znajdziesz: access_token=TOKEN")
    print("5. Skopiuj tylko TOKEN (bez 'access_token=')")
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
            print(f"❌ Błąd testowania: {e}")
            continue


def save_token(token):
    """Zapisuje token do pliku .env"""
    env_path = ".env"
    
    print(f"\n💾 Zapisuję token do {env_path}...")
    
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
            print("✅ Token zaktualizowany!")
        else:
            # Dodajemy nowy token
            with open(env_path, 'a', encoding='utf-8') as f:
                f.write(f'\nYANDEX_DISK_TOKEN={token}\n')
            print("✅ Token dodany!")
    else:
        # Tworzymy nowy plik
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f'YANDEX_DISK_TOKEN={token}\n')
        print("✅ Plik .env utworzony z tokenem!")
    
    print("\n🎉 SUKCES!")
    print("✅ Token Yandex Disk został uzyskany i zapisany")
    print("🚀 Możesz teraz uruchomić bota: python telegram_bot.py")


if __name__ == "__main__":
    main()
