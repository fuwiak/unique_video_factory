#!/usr/bin/env python3
"""
Skrypt do uzyskania Yandex token używając własnych credentials
"""

import webbrowser
import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv


def main():
    """Używa własnych credentials do uzyskania tokenu"""
    print("🔐 YANDEX TOKEN Z WŁASNYMI CREDENTIALS")
    print("=" * 50)
    print()
    
    # Ładujemy zmienne środowiskowe
    load_dotenv()
    
    # Sprawdzamy czy credentials są ustawione
    client_id = os.getenv('YANDEX_CLIENT_ID')
    client_secret = os.getenv('YANDEX_CLIENT_SECRET')
    redirect_uri = os.getenv('YANDEX_REDIRECT_URI')
    
    if not client_id or not client_secret or not redirect_uri:
        print("❌ Brakuje credentials w pliku .env!")
        print()
        print("📋 Dodaj do pliku .env:")
        print("YANDEX_CLIENT_ID=twój_client_id")
        print("YANDEX_CLIENT_SECRET=twój_client_secret")
        print("YANDEX_REDIRECT_URI=twój_redirect_uri")
        print()
        print("💡 Przykład:")
        print("YANDEX_CLIENT_ID=1234567890abcdef")
        print("YANDEX_CLIENT_SECRET=abcdef1234567890")
        print("YANDEX_REDIRECT_URI=https://yourdomain.com/callback")
        return
    
    print(f"✅ Znaleziono credentials:")
    print(f"   Client ID: {client_id[:10]}...")
    print(f"   Client Secret: {client_secret[:10]}...")
    print(f"   Redirect URI: {redirect_uri}")
    print()
    
    # Tworzymy URL OAuth z własnymi credentials
    oauth_url = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    
    print("🌐 Otwieram stronę Yandex z Twoimi credentials...")
    print(f"   URL: {oauth_url}")
    
    webbrowser.open(oauth_url)
    print("✅ Strona otwarta w przeglądarce")
    print()
    
    print("📋 Instrukcja:")
    print("1. Zaloguj się swoim mailem i hasłem Yandex")
    print("2. Jeśli masz 2FA, wprowadź kod")
    print("3. Po zalogowaniu zostaniesz przekierowany")
    print("4. W adresie URL znajdziesz: code=KOD")
    print("5. Skopiuj tylko KOD (bez 'code=')")
    print()
    print("💡 Przykład URL:")
    print(f"   {redirect_uri}?code=1234567890abcdef")
    print("   Kod to: 1234567890abcdef")
    print()
    
    # Pobieramy kod autoryzacji
    while True:
        code = input("Wprowadź kod autoryzacji (lub 'q' aby zakończyć): ").strip()
        
        if code.lower() == 'q':
            print("👋 Zakończono")
            return
        
        if not code:
            print("❌ Kod nie może być pusty!")
            continue
        
        # Wymieniamy kod na token
        print("🔄 Wymieniam kod na token...")
        token = exchange_code_for_token(code, client_id, client_secret, redirect_uri)
        
        if token:
            print(f"✅ Token otrzymany: {token[:20]}...")
            
            # Testujemy token
            if test_token(token):
                save_token(token)
                return
            else:
                print("❌ Token nie działa!")
                continue
        else:
            print("❌ Nie udało się uzyskać tokenu!")
            print("💡 Sprawdź czy kod jest poprawny")
            continue


def exchange_code_for_token(code, client_id, client_secret, redirect_uri):
    """Wymienia kod autoryzacji na token"""
    try:
        token_url = "https://oauth.yandex.ru/token"
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        return token_data.get('access_token')
        
    except Exception as e:
        print(f"❌ Błąd wymiany kodu na token: {e}")
        return None


def test_token(token):
    """Testuje token"""
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
                print(f"⚠️ Nie można pobrać informacji: {e}")
            
            return True
        else:
            print("❌ Token nie działa!")
            return False
            
    except Exception as e:
        print(f"❌ Błąd testowania tokenu: {e}")
        return False


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


if __name__ == "__main__":
    main()
