#!/usr/bin/env python3
"""
Automatyczne uruchamianie ekstraktora statystyk
"""

import os
import sys
import subprocess
from datetime import datetime

def check_requirements():
    """Sprawdza wymagania"""
    print("🔍 SPRAWDZANIE WYMAGAŃ")
    print("=" * 30)
    
    # Sprawdzamy plik .env
    if not os.path.exists(".env"):
        print("❌ Brak pliku .env")
        return False
    
    # Sprawdzamy klucze API
    with open(".env", "r") as f:
        env_content = f.read()
    
    required_keys = ["VK_TOKEN", "YOUTUBE_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if key not in env_content or f"{key}=" in env_content and not env_content.split(f"{key}=")[1].split("\n")[0].strip():
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Brakujące klucze API: {missing_keys}")
        return False
    
    print("✅ Wszystkie klucze API są skonfigurowane")
    return True

def check_google_sheets():
    """Sprawdza konfigurację Google Sheets"""
    print("\n🔍 SPRAWDZANIE GOOGLE SHEETS")
    print("=" * 30)
    
    if not os.path.exists("google_credentials.json"):
        print("❌ Brak pliku google_credentials.json")
        print("📋 Wykonaj kroki z GOOGLE_CLOUD_SETUP_GUIDE.md")
        return False
    
    print("✅ Plik google_credentials.json istnieje")
    return True

def run_extractor():
    """Uruchamia ekstraktor"""
    print("\n🚀 URUCHAMIANIE EKSTRAKTORA")
    print("=" * 30)
    
    try:
        # Uruchamiamy ekstraktor
        result = subprocess.run([
            sys.executable, "official_api_extractor.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Ekstraktor zakończony pomyślnie!")
            print("\n📊 WYNIKI:")
            print(result.stdout)
            return True
        else:
            print("❌ Błąd ekstraktora:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Błąd uruchamiania: {e}")
        return False

def main():
    """Główna funkcja"""
    print("🎬 AUTOMATYCZNY EKSTRAKTOR STATYSTYK")
    print("=" * 50)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Sprawdzamy wymagania
    if not check_requirements():
        print("\n❌ KONFIGURACJA WYMAGANA")
        print("📋 Sprawdź plik .env i dodaj brakujące klucze API")
        return
    
    # Sprawdzamy Google Sheets
    if not check_google_sheets():
        print("\n❌ GOOGLE SHEETS WYMAGANE")
        print("📋 Wykonaj kroki z GOOGLE_CLOUD_SETUP_GUIDE.md")
        return
    
    # Uruchamiamy ekstraktor
    if run_extractor():
        print("\n🎉 WSZYSTKO ZAKOŃCZONE POMYŚLNIE!")
        print("📊 Sprawdź swój arkusz Google Sheets")
    else:
        print("\n❌ BŁĄD EKSTRAKTORA")
        print("📋 Sprawdź logi powyżej")

if __name__ == "__main__":
    main()




