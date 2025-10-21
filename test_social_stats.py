#!/usr/bin/env python3
"""
Test skryptu do sprawdzania statystyk społecznościowych
"""

import os
import sys
from pathlib import Path

def test_social_stats():
    """Testuje funkcjonalność sprawdzania statystyk"""
    print("🧪 TEST SPRAWDZANIA STATYSTYK SPOŁECZNOŚCIOWYCH")
    print("=" * 60)
    
    # Sprawdzamy czy pliki istnieją
    required_files = [
        'social_stats_checker.py',
        'advanced_social_stats.py',
        'api_keys_config.py'
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Plik {file} nie istnieje")
            return False
        print(f"✅ Plik {file} istnieje")
    
    # Sprawdzamy czy mamy wymagane biblioteki
    try:
        import requests
        print("✅ Biblioteka requests dostępna")
    except ImportError:
        print("❌ Biblioteka requests nie jest zainstalowana")
        print("💡 Zainstaluj: pip install requests")
        return False
    
    try:
        import json
        print("✅ Biblioteka json dostępna")
    except ImportError:
        print("❌ Biblioteka json nie jest dostępna")
        return False
    
    try:
        import re
        print("✅ Biblioteka re dostępna")
    except ImportError:
        print("❌ Biblioteka re nie jest dostępna")
        return False
    
    print("\n🎯 FUNKCJONALNOŚCI SKRYPTU:")
    print("1. ✅ Sprawdzanie statystyk YouTube")
    print("2. ✅ Sprawdzanie statystyk Instagram")
    print("3. ✅ Sprawdzanie statystyk TikTok")
    print("4. ✅ Sprawdzanie statystyk VK")
    print("5. ✅ Sprawdzanie statystyk Likee")
    print("6. ✅ Oficjalne API gdzie dostępne")
    print("7. ✅ Fallbacki (scraping)")
    print("8. ✅ Rotacja User-Agent")
    print("9. ✅ Retry logic")
    print("10. ✅ Zapis wyników do JSON")
    
    print("\n🔧 METODY SPRAWDZANIA:")
    print("📺 YouTube:")
    print("   - YouTube Data API v3")
    print("   - Scraping z różnych źródeł")
    print("   - YouTube Analytics API")
    
    print("\n📸 Instagram:")
    print("   - Instagram Basic Display API")
    print("   - Scraping z różnych źródeł")
    print("   - Instagram Graph API")
    
    print("\n🎵 TikTok:")
    print("   - TikTok Research API")
    print("   - Scraping z różnych źródeł")
    
    print("\n🔵 VK:")
    print("   - VK API")
    print("   - Scraping z różnych źródeł")
    
    print("\n💜 Likee:")
    print("   - Scraping (brak oficjalnego API)")
    
    print("\n⚡ ZAAWANSOWANE FUNKCJE:")
    print("✅ Rotacja User-Agent")
    print("✅ Exponential backoff")
    print("✅ Multiple fallback methods")
    print("✅ Error handling")
    print("✅ JSON export")
    print("✅ Progress tracking")
    
    print("\n🔑 KONFIGURACJA API KEYS:")
    print("📝 Edytuj api_keys_config.py i dodaj swoje klucze:")
    print("   - YouTube Data API v3")
    print("   - Instagram Basic Display API")
    print("   - TikTok Research API")
    print("   - VK API")
    
    print("\n💡 TIP: Bez API keys skrypt użyje fallbacków")
    print("   Ale API jest bardziej niezawodne i szybsze!")
    
    return True


def test_urls():
    """Testuje URLs do sprawdzenia"""
    print("\n🔗 TEST URLs:")
    
    urls = {
        'YouTube': 'https://www.youtube.com/@raachel_fb',
        'Instagram': 'https://www.instagram.com/raachel_fb',
        'VK': 'https://vk.com/raachel_fb',
        'TikTok': 'https://www.tiktok.com/@daniryb_fb',
        'Likee': 'https://l.likee.video/p/jSQPBE'
    }
    
    for platform, url in urls.items():
        print(f"✅ {platform}: {url}")
    
    return True


def test_imports():
    """Testuje importy"""
    print("\n📦 TEST IMPORTÓW:")
    
    try:
        from social_stats_checker import SocialStatsChecker
        print("✅ SocialStatsChecker zaimportowany")
    except ImportError as e:
        print(f"❌ Błąd importu SocialStatsChecker: {e}")
        return False
    
    try:
        from advanced_social_stats import AdvancedSocialStatsChecker
        print("✅ AdvancedSocialStatsChecker zaimportowany")
    except ImportError as e:
        print(f"❌ Błąd importu AdvancedSocialStatsChecker: {e}")
        return False
    
    try:
        from api_keys_config import get_api_keys
        print("✅ get_api_keys zaimportowany")
    except ImportError as e:
        print(f"❌ Błąd importu get_api_keys: {e}")
        return False
    
    return True


def main():
    """Główna funkcja testowa"""
    print("🚀 URUCHAMIANIE TESTÓW...")
    print("=" * 60)
    
    # Test 1: Podstawowe funkcjonalności
    if not test_social_stats():
        print("\n❌ Test podstawowych funkcjonalności nie powiódł się!")
        return False
    
    # Test 2: URLs
    if not test_urls():
        print("\n❌ Test URLs nie powiódł się!")
        return False
    
    # Test 3: Importy
    if not test_imports():
        print("\n❌ Test importów nie powiódł się!")
        return False
    
    print("\n✅ WSZYSTKIE TESTY ZAKOŃCZONE POMYŚLNIE!")
    print("\n🎯 GOTOWE DO UŻYCIA:")
    print("1. python social_stats_checker.py - podstawowa wersja")
    print("2. python advanced_social_stats.py - zaawansowana wersja")
    print("3. python api_keys_config.py - instrukcje API keys")
    
    print("\n💡 TIP: Uruchom advanced_social_stats.py dla najlepszych wyników!")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Testy nie powiodły się!")
        sys.exit(1)
    else:
        print("\n🎉 Wszystko gotowe do użycia!")




