#!/usr/bin/env python3
"""
Skrypt do uzyskania YANDEX_DISK_TOKEN z loginu i hasła
"""

import os
import requests
import json
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
import time


class YandexTokenGetter:
    """Klasa do uzyskania tokenu Yandex Disk"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_oauth_url(self):
        """Pobiera URL do autoryzacji OAuth"""
        base_url = "https://oauth.yandex.ru/authorize"
        params = {
            'response_type': 'code',
            'client_id': '23cabbbdc6cd418abb4b39c32c41195d',  # Public client ID
            'redirect_uri': 'https://oauth.yandex.ru/verification_code',
            'scope': 'cloud_api:disk'
        }
        
        oauth_url = f"{base_url}?{urlencode(params)}"
        return oauth_url
    
    def get_token_from_code(self, code):
        """Pobiera token z kodu autoryzacji"""
        token_url = "https://oauth.yandex.ru/token"
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': '23cabbbdc6cd418abb4b39c32c41195d',
            'client_secret': '53bc75238f0c4d08a118e51fe9203300'
        }
        
        try:
            response = self.session.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data.get('access_token')
            
        except Exception as e:
            print(f"❌ Błąd pobierania tokenu: {e}")
            return None
    
    def test_token(self, token):
        """Testuje token"""
        try:
            import yadisk
            yandex = yadisk.YaDisk(token=token)
            
            if yandex.check_token():
                # Pobieramy informacje o użytkowniku
                user_info = yandex.get_disk_info()
                print(f"✅ Token działa!")
                print(f"   Użytkownik: {user_info.get('user', {}).get('display_name', 'Nieznany')}")
                print(f"   Dostępne miejsce: {user_info.get('total_space', 0) / (1024**3):.1f} GB")
                return True
            else:
                print("❌ Token nie działa!")
                return False
                
        except Exception as e:
            print(f"❌ Błąd testowania tokenu: {e}")
            return False


def manual_oauth_flow():
    """Ręczny proces OAuth"""
    getter = YandexTokenGetter()
    
    print("🔐 UZYSKIWANIE TOKENU YANDEX DISK")
    print("=" * 50)
    print()
    print("📋 Instrukcja:")
    print("1. Otworzę stronę autoryzacji Yandex")
    print("2. Zaloguj się swoim mailem i hasłem")
    print("3. Skopiuj kod autoryzacji")
    print("4. Wklej kod tutaj")
    print()
    
    # Otwieramy stronę autoryzacji
    oauth_url = getter.get_oauth_url()
    print(f"🌐 Otwieram: {oauth_url}")
    
    try:
        webbrowser.open(oauth_url)
        print("✅ Strona otwarta w przeglądarce")
    except:
        print("⚠️ Nie można otworzyć przeglądarki automatycznie")
        print(f"   Skopiuj i otwórz w przeglądarce: {oauth_url}")
    
    print()
    print("🔑 Po zalogowaniu skopiuj kod z adresu URL (część po 'code=')")
    print("   Przykład: https://oauth.yandex.ru/verification_code?code=123456")
    print("   Kod to: 123456")
    print()
    
    while True:
        code = input("Wprowadź kod autoryzacji: ").strip()
        
        if not code:
            print("❌ Kod nie może być pusty!")
            continue
        
        print("🔄 Pobieranie tokenu...")
        token = getter.get_token_from_code(code)
        
        if token:
            print(f"✅ Token otrzymany: {token[:20]}...")
            
            # Testujemy token
            print("🧪 Testowanie tokenu...")
            if getter.test_token(token):
                return token
            else:
                print("❌ Token nie działa, spróbuj ponownie")
                continue
        else:
            print("❌ Nie udało się pobrać tokenu, spróbuj ponownie")
            continue


def save_token_to_env(token):
    """Zapisuje token do pliku .env"""
    env_path = ".env"
    
    # Sprawdzamy czy .env istnieje
    if os.path.exists(env_path):
        # Czytamy istniejący plik
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Aktualizujemy lub dodajemy YANDEX_DISK_TOKEN
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('YANDEX_DISK_TOKEN='):
                lines[i] = f'YANDEX_DISK_TOKEN={token}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'YANDEX_DISK_TOKEN={token}\n')
        
        # Zapisujemy zaktualizowany plik
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    else:
        # Tworzymy nowy plik .env
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f'YANDEX_DISK_TOKEN={token}\n')
    
    print(f"💾 Token zapisany do {env_path}")


def main():
    """Główna funkcja"""
    print("🤖 POMOCNIK TOKENU YANDEX DISK")
    print("=" * 50)
    
    # Sprawdzamy czy token już istnieje
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        
        existing_token = os.getenv('YANDEX_DISK_TOKEN')
        if existing_token:
            print(f"📁 Znaleziono istniejący token: {existing_token[:20]}...")
            
            # Testujemy istniejący token
            getter = YandexTokenGetter()
            if getter.test_token(existing_token):
                print("✅ Istniejący token działa!")
                choice = input("Czy chcesz użyć nowego tokenu? (y/N): ").strip().lower()
                if choice not in ['y', 'yes', 'tak', 't']:
                    print("✅ Używamy istniejący token")
                    return
            else:
                print("❌ Istniejący token nie działa")
    
    try:
        # Uzyskujemy nowy token
        token = manual_oauth_flow()
        
        if token:
            # Zapisujemy token
            save_token_to_env(token)
            
            print("\n🎉 SUKCES!")
            print("✅ Token Yandex Disk został uzyskany i zapisany")
            print("🚀 Możesz teraz uruchomić bota: python telegram_bot.py")
        else:
            print("\n❌ Nie udało się uzyskać tokenu")
            print("💡 Spróbuj ponownie lub skontaktuj się z pomocą")
    
    except KeyboardInterrupt:
        print("\n👋 Anulowano przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        print("💡 Sprawdź połączenie internetowe i spróbuj ponownie")


if __name__ == "__main__":
    main()
