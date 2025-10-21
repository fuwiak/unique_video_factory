#!/usr/bin/env python3
"""
Główny pomocnik do uzyskania Yandex Disk token
"""

import os
import sys
from pathlib import Path


def show_menu():
    """Pokazuje menu wyboru"""
    print("🔐 POMOCNIK TOKENU YANDEX DISK")
    print("=" * 50)
    print()
    print("Wybierz metodę uzyskania tokenu:")
    print()
    print("1. 🌐 Automatyczna (otwiera przeglądarkę)")
    print("   - Najłatwiejsza metoda")
    print("   - Otwiera stronę Yandex w przeglądarce")
    print("   - Wymaga ręcznego skopiowania tokenu")
    print()
    print("2. 🔑 Z loginu i hasła (eksperymentalna)")
    print("   - Próbuje automatycznie zalogować")
    print("   - Może nie działać z 2FA")
    print()
    print("3. 📋 Instrukcja krok po kroku")
    print("   - Szczegółowa instrukcja")
    print("   - Dla zaawansowanych użytkowników")
    print()
    print("4. ❓ Pomoc i rozwiązywanie problemów")
    print()
    print("0. 🚪 Wyjście")
    print()


def method_automatic():
    """Metoda automatyczna"""
    print("🌐 METODA AUTOMATYCZNA")
    print("=" * 30)
    
    try:
        from simple_yandex_token import main as simple_main
        simple_main()
    except ImportError:
        print("❌ Nie można zaimportować modułu")
        print("💡 Uruchom: python simple_yandex_token.py")


def method_login():
    """Metoda z loginu i hasła"""
    print("🔑 METODA Z LOGINU I HASŁA")
    print("=" * 30)
    
    try:
        from yandex_login import main as login_main
        login_main()
    except ImportError:
        print("❌ Nie można zaimportować modułu")
        print("💡 Uruchom: python yandex_login.py")


def method_instructions():
    """Metoda z instrukcjami"""
    print("📋 INSTRUKCJA KROK PO KROKU")
    print("=" * 40)
    print()
    print("🔗 Krok 1: Otwórz stronę Yandex OAuth")
    print("   https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d&redirect_uri=https://oauth.yandex.ru/verification_code")
    print()
    print("🔐 Krok 2: Zaloguj się")
    print("   - Wprowadź swój email Yandex")
    print("   - Wprowadź hasło")
    print("   - Jeśli masz 2FA, wprowadź kod")
    print()
    print("📋 Krok 3: Skopiuj token")
    print("   Po zalogowaniu zostaniesz przekierowany do:")
    print("   https://oauth.yandex.ru/verification_code#access_token=TOKEN&token_type=bearer")
    print()
    print("   Skopiuj tylko część TOKEN (bez 'access_token=' i '&token_type=bearer')")
    print()
    print("💾 Krok 4: Zapisz token")
    print("   Uruchom: python simple_yandex_token.py")
    print("   Lub dodaj do pliku .env:")
    print("   YANDEX_DISK_TOKEN=twój_token_tutaj")
    print()


def method_help():
    """Pomoc i rozwiązywanie problemów"""
    print("❓ POMOC I ROZWIĄZYWANIE PROBLEMÓW")
    print("=" * 50)
    print()
    print("🔍 Częste problemy:")
    print()
    print("❌ 'Token nie działa'")
    print("   ✅ Sprawdź czy skopiowałeś pełny token")
    print("   ✅ Token nie może zawierać spacji")
    print("   ✅ Token musi zaczynać się od 'AQAAAAA'")
    print()
    print("❌ 'Nie mogę się zalogować'")
    print("   ✅ Sprawdź email i hasło")
    print("   ✅ Wyłącz 2FA tymczasowo")
    print("   ✅ Spróbuj w trybie incognito")
    print()
    print("❌ 'Strona się nie otwiera'")
    print("   ✅ Skopiuj URL ręcznie:")
    print("   https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d&redirect_uri=https://oauth.yandex.ru/verification_code")
    print()
    print("🔧 Sprawdzanie tokenu:")
    print("   python test_bot.py")
    print()
    print("📁 Pliki konfiguracyjne:")
    print("   .env - główny plik konfiguracji")
    print("   env_example.txt - przykład konfiguracji")
    print()


def check_existing_token():
    """Sprawdza czy token już istnieje"""
    env_path = Path(".env")
    
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            existing_token = os.getenv('YANDEX_DISK_TOKEN')
            if existing_token:
                print(f"📁 Znaleziono istniejący token: {existing_token[:20]}...")
                
                # Testujemy token
                try:
                    import yadisk
                    yandex = yadisk.YaDisk(token=existing_token)
                    
                    if yandex.check_token():
                        print("✅ Istniejący token działa!")
                        choice = input("Czy chcesz użyć nowego tokenu? (y/N): ").strip().lower()
                        if choice not in ['y', 'yes', 'tak', 't']:
                            print("✅ Używamy istniejący token")
                            return True
                    else:
                        print("❌ Istniejący token nie działa")
                except:
                    print("❌ Błąd testowania istniejącego tokenu")
            
        except ImportError:
            pass
    
    return False


def main():
    """Główna funkcja"""
    # Sprawdzamy czy token już istnieje
    if check_existing_token():
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("Wybierz opcję (0-4): ").strip()
            
            if choice == "1":
                method_automatic()
                break
            elif choice == "2":
                method_login()
                break
            elif choice == "3":
                method_instructions()
                input("\nNaciśnij Enter aby kontynuować...")
            elif choice == "4":
                method_help()
                input("\nNaciśnij Enter aby kontynuować...")
            elif choice == "0":
                print("👋 Do widzenia!")
                break
            else:
                print("❌ Nieprawidłowy wybór!")
                input("Naciśnij Enter aby kontynuować...")
        
        except KeyboardInterrupt:
            print("\n👋 Do widzenia!")
            break
        except Exception as e:
            print(f"❌ Błąd: {e}")
            input("Naciśnij Enter aby kontynuować...")


if __name__ == "__main__":
    main()
