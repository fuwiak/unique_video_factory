#!/usr/bin/env python3
"""
Skrypt do logowania do Yandex i uzyskania tokenu
"""

import requests
import json
import re
from urllib.parse import urljoin, urlparse
import time


class YandexLogin:
    """Klasa do logowania do Yandex"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def login(self, email, password):
        """Loguje się do Yandex"""
        try:
            # Krok 1: Pobieramy stronę logowania
            login_url = "https://passport.yandex.ru/auth"
            response = self.session.get(login_url)
            response.raise_for_status()
            
            # Krok 2: Wysyłamy dane logowania
            auth_url = "https://passport.yandex.ru/auth"
            
            # Pobieramy potrzebne parametry z formularza
            csrf_token = self._extract_csrf_token(response.text)
            
            auth_data = {
                'login': email,
                'passwd': password,
                'retpath': 'https://yandex.ru',
                'csrf_token': csrf_token
            }
            
            # Wysyłamy żądanie logowania
            auth_response = self.session.post(auth_url, data=auth_data, allow_redirects=True)
            
            # Sprawdzamy czy logowanie się powiodło
            if 'yandex.ru' in auth_response.url and 'auth' not in auth_response.url:
                print("✅ Logowanie do Yandex powiodło się!")
                return True
            else:
                print("❌ Logowanie nie powiodło się!")
                return False
                
        except Exception as e:
            print(f"❌ Błąd logowania: {e}")
            return False
    
    def _extract_csrf_token(self, html):
        """Wyciąga token CSRF z HTML"""
        csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
        if csrf_match:
            return csrf_match.group(1)
        
        # Alternatywny sposób
        csrf_match = re.search(r'"csrf_token":"([^"]+)"', html)
        if csrf_match:
            return csrf_match.group(1)
        
        return ""
    
    def get_oauth_token(self):
        """Uzyskuje token OAuth po zalogowaniu"""
        try:
            # Próbujemy uzyskać token przez API
            oauth_url = "https://oauth.yandex.ru/authorize"
            params = {
                'response_type': 'token',
                'client_id': '23cabbbdc6cd418abb4b39c32c41195d',
                'redirect_uri': 'https://oauth.yandex.ru/verification_code',
                'scope': 'cloud_api:disk'
            }
            
            # Wysyłamy żądanie OAuth
            response = self.session.get(oauth_url, params=params)
            
            # Sprawdzamy czy otrzymaliśmy token
            if 'access_token' in response.url:
                token_match = re.search(r'access_token=([^&]+)', response.url)
                if token_match:
                    return token_match.group(1)
            
            # Alternatywnie, próbujemy przez API
            api_url = "https://cloud-api.yandex.net/v1/disk"
            response = self.session.get(api_url)
            
            if response.status_code == 200:
                # Sprawdzamy czy mamy dostęp do API
                print("✅ Dostęp do Yandex Disk API potwierdzony!")
                
                # Próbujemy uzyskać token przez inne API
                token_url = "https://oauth.yandex.ru/token"
                token_data = {
                    'grant_type': 'authorization_code',
                    'client_id': '23cabbbdc6cd418abb4b39c32c41195d',
                    'client_secret': '53bc75238f0c4d08a118e51fe9203300'
                }
                
                token_response = self.session.post(token_url, data=token_data)
                if token_response.status_code == 200:
                    token_info = token_response.json()
                    return token_info.get('access_token')
            
            return None
            
        except Exception as e:
            print(f"❌ Błąd uzyskiwania tokenu: {e}")
            return None


def main():
    """Główna funkcja"""
    print("🔐 LOGOWANIE DO YANDEX DISK")
    print("=" * 40)
    
    # Pobieramy dane logowania
    email = input("Wprowadź email Yandex: ").strip()
    if not email:
        print("❌ Email jest wymagany!")
        return
    
    password = input("Wprowadź hasło: ").strip()
    if not password:
        print("❌ Hasło jest wymagane!")
        return
    
    print("\n🔄 Logowanie...")
    
    # Logujemy się
    yandex = YandexLogin()
    if yandex.login(email, password):
        print("🔄 Próba uzyskania tokenu...")
        
        token = yandex.get_oauth_token()
        if token:
            print(f"✅ Token uzyskany: {token[:20]}...")
            
            # Testujemy token
            try:
                import yadisk
                yandex_disk = yadisk.YaDisk(token=token)
                if yandex_disk.check_token():
                    print("✅ Token działa!")
                    
                    # Zapisujemy token
                    with open('.env', 'a', encoding='utf-8') as f:
                        f.write(f'\nYANDEX_DISK_TOKEN={token}\n')
                    
                    print("💾 Token zapisany do .env")
                    print("🚀 Możesz teraz uruchomić bota!")
                else:
                    print("❌ Token nie działa")
            except Exception as e:
                print(f"❌ Błąd testowania tokenu: {e}")
        else:
            print("❌ Nie udało się uzyskać tokenu")
            print("💡 Spróbuj użyć get_yandex_token.py dla ręcznego procesu OAuth")
    else:
        print("❌ Logowanie nie powiodło się")
        print("💡 Sprawdź email i hasło")


if __name__ == "__main__":
    main()
