#!/usr/bin/env python3
"""
Szybki skrypt do uzyskania Yandex token
"""

import webbrowser
import os


def main():
    """Szybki sposób na uzyskanie tokenu"""
    print("🔐 SZYBKI POMOCNIK TOKENU YANDEX")
    print("=" * 40)
    print()
    
    # Otwieramy stronę Yandex z oficjalnym redirect_uri
    oauth_url = "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d&redirect_uri=https://oauth.yandex.ru/verification_code"
    
    print("🌐 Otwieram stronę Yandex...")
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
                
                # Zapisujemy token
                with open('.env', 'a', encoding='utf-8') as f:
                    f.write(f'\nYANDEX_DISK_TOKEN={token}\n')
                
                print("💾 Token zapisany do .env")
                print("🚀 Możesz teraz uruchomić bota: python telegram_bot.py")
                return
            else:
                print("❌ Token nie działa!")
                print("💡 Sprawdź czy skopiowałeś pełny token")
                continue
                
        except Exception as e:
            print(f"❌ Błąd: {e}")
            continue


if __name__ == "__main__":
    main()
