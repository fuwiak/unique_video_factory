#!/usr/bin/env python3
"""
Oficjalny skrypt do uzyskania Yandex token używając oficjalnej metody
"""

import webbrowser
import os


def main():
    """Oficjalna metoda uzyskania tokenu"""
    print("🔐 OFICJALNY POMOCNIK TOKENU YANDEX")
    print("=" * 50)
    print()
    
    print("📋 Ta metoda używa oficjalnej aplikacji Yandex")
    print("   Nie wymaga rejestracji własnej aplikacji")
    print()
    
    # Używamy oficjalnego client_id i redirect_uri
    oauth_url = "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d&redirect_uri=https://oauth.yandex.ru/verification_code"
    
    print("🌐 Otwieram oficjalną stronę Yandex...")
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
    print("💡 Przykład URL:")
    print("   https://oauth.yandex.ru/verification_code#access_token=AQAAAAA...&token_type=bearer")
    print("   Token to: AQAAAAA...")
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
        
        # Sprawdzamy format tokenu
        if not token.startswith('AQAAAAA'):
            print("⚠️ Token powinien zaczynać się od 'AQAAAAA'")
            print("💡 Sprawdź czy skopiowałeś pełny token")
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
                    used_space = disk_info.get('used_space', 0) / (1024**3)
                    
                    print(f"👤 Użytkownik: {user_name}")
                    print(f"💾 Całkowite miejsce: {total_space:.1f} GB")
                    print(f"📁 Użyte miejsce: {used_space:.1f} GB")
                    print(f"🆓 Wolne miejsce: {total_space - used_space:.1f} GB")
                except Exception as e:
                    print(f"⚠️ Nie można pobrać informacji o użytkowniku: {e}")
                
                # Zapisujemy token
                save_token(token)
                return
            else:
                print("❌ Token nie działa!")
                print("💡 Sprawdź czy skopiowałeś pełny token")
                continue
                
        except Exception as e:
            print(f"❌ Błąd testowania: {e}")
            print("💡 Sprawdź czy masz zainstalowaną bibliotekę yadisk")
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
    print("📁 Sprawdź plik .env")
    print("🚀 Możesz teraz uruchomić bota: python telegram_bot.py")
    print("🧪 Lub przetestuj: python test_bot.py")


if __name__ == "__main__":
    main()
