#!/usr/bin/env python3
"""
Sprawdza czy credentials są prawidłowe
"""

import os
import json

def check_credentials():
    """Sprawdza plik credentials"""
    print("🔍 SPRAWDZANIE CREDENTIALS")
    print("=" * 40)
    
    if not os.path.exists("google_credentials.json"):
        print("❌ Brak pliku google_credentials.json")
        return False
    
    try:
        with open("google_credentials.json", "r") as f:
            credentials = json.load(f)
        
        print("✅ Plik credentials istnieje")
        
        # Sprawdzamy typ
        if credentials.get("type") != "service_account":
            print("❌ Nieprawidłowy typ credentials")
            print(f"   Oczekiwany: service_account")
            print(f"   Znaleziony: {credentials.get('type')}")
            print("   💡 Potrzebujesz Service Account credentials, nie OAuth 2.0 Web Application")
            return False
        
        print("✅ Typ credentials: service_account")
        
        # Sprawdzamy wymagane pola
        required_fields = [
            "project_id",
            "private_key_id", 
            "private_key",
            "client_email",
            "client_id"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Brakujące pola: {missing_fields}")
            return False
        
        print("✅ Wszystkie wymagane pola są obecne")
        
        # Sprawdzamy czy to nie są dane OAuth 2.0 Web Application
        if "client_secret" in credentials:
            print("❌ To są dane OAuth 2.0 Web Application!")
            print("   💡 Potrzebujesz Service Account credentials")
            print("   📋 Wykonaj kroki z SERVICE_ACCOUNT_SETUP.md")
            return False
        
        # Sprawdzamy czy private_key ma poprawny format
        private_key = credentials.get("private_key", "")
        if not private_key.startswith("-----BEGIN PRIVATE KEY-----"):
            print("❌ Nieprawidłowy format private_key")
            print("   💡 Sprawdź czy private_key jest poprawny")
            return False
        
        print("✅ Format private_key jest poprawny")
        
        # Sprawdzamy czy client_email ma poprawny format
        client_email = credentials.get("client_email", "")
        if not client_email.endswith(".iam.gserviceaccount.com"):
            print("❌ Nieprawidłowy format client_email")
            print(f"   Znaleziony: {client_email}")
            print("   💡 client_email powinien kończyć się na .iam.gserviceaccount.com")
            return False
        
        print("✅ Format client_email jest poprawny")
        
        print(f"\n📧 Service Account: {client_email}")
        print(f"🏗️ Project ID: {credentials.get('project_id')}")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Nieprawidłowy format JSON")
        return False
    except Exception as e:
        print(f"❌ Błąd odczytu credentials: {e}")
        return False

def main():
    """Główna funkcja"""
    print("🔧 SPRAWDZANIE GOOGLE CREDENTIALS")
    print("=" * 50)
    
    if check_credentials():
        print("\n✅ CREDENTIALS SĄ PRAWIDŁOWE!")
        print("📊 Możesz teraz uruchomić:")
        print("   python test_google_sheets.py")
        print("   python official_api_extractor.py")
    else:
        print("\n❌ CREDENTIALS WYMAGAJĄ POPRAWKI")
        print("📋 Wykonaj kroki z SERVICE_ACCOUNT_SETUP.md")
        print("\n💡 Pamiętaj:")
        print("   - Potrzebujesz Service Account credentials")
        print("   - Nie OAuth 2.0 Web Application credentials")
        print("   - Service Account musi mieć dostęp do arkusza")

if __name__ == "__main__":
    main()




