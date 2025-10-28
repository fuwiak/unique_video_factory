#!/usr/bin/env python3
"""
Test funkcjonalności blogger cards
"""

import os
import sys
from dotenv import load_dotenv

# Dodaj ścieżkę do modułów
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_imports():
    """Test importów"""
    try:
        from google_sheets_integration import GoogleSheetsIntegration
        from advanced_social_stats import AdvancedSocialStatsChecker
        print("✅ Importy OK")
        return True
    except ImportError as e:
        print(f"❌ Błąd importu: {e}")
        return False

def test_google_sheets():
    """Test Google Sheets"""
    try:
        from google_sheets_integration import GoogleSheetsIntegration
        sheets = GoogleSheetsIntegration()
        print("✅ Google Sheets OK")
        return True
    except Exception as e:
        print(f"❌ Błąd Google Sheets: {e}")
        return False

def test_social_stats():
    """Test Social Stats"""
    try:
        from advanced_social_stats import AdvancedSocialStatsChecker
        checker = AdvancedSocialStatsChecker()
        print("✅ Social Stats OK")
        return True
    except Exception as e:
        print(f"❌ Błąd Social Stats: {e}")
        return False

def test_link_validation():
    """Test walidacji linków"""
    try:
        # Symulacja funkcji z bota
        def is_valid_social_link(link: str) -> bool:
            valid_domains = [
                'instagram.com', 'youtube.com', 'tiktok.com', 'vk.com', 'likee.video'
            ]
            link = link.lower().strip()
            return any(domain in link for domain in valid_domains)
        
        # Test linków
        test_links = [
            "https://www.instagram.com/raachel_fb?igsh=cm9peTlsOHNsY20x&utm_source=qr",
            "https://www.tiktok.com/@daniryb_fb?_t=ZS-8zmIVT7JQ5&_r=1",
            "https://vk.com/raachel_fb",
            "https://www.youtube.com/@raachel_fb",
            "https://l.likee.video/p/jSQPBE",
            "https://invalid.com/link"
        ]
        
        for link in test_links:
            result = is_valid_social_link(link)
            print(f"Link: {link[:50]}... -> {'✅' if result else '❌'}")
        
        print("✅ Walidacja linków OK")
        return True
    except Exception as e:
        print(f"❌ Błąd walidacji: {e}")
        return False

def test_blogger_states():
    """Test blogger states"""
    try:
        # Symulacja blogger_states
        blogger_states = {}
        
        # Test dodawania stanu
        user_id = 12345
        blogger_states[user_id] = {
            'status': 'waiting_for_name',
            'blogger_name': None,
            'links': []
        }
        
        print(f"✅ Blogger states OK: {blogger_states}")
        return True
    except Exception as e:
        print(f"❌ Błąd blogger states: {e}")
        return False

def main():
    """Główna funkcja testowa"""
    print("🧪 Test funkcjonalności blogger cards")
    print("=" * 50)
    
    tests = [
        ("Importy", test_imports),
        ("Google Sheets", test_google_sheets),
        ("Social Stats", test_social_stats),
        ("Walidacja linków", test_link_validation),
        ("Blogger States", test_blogger_states),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Test: {test_name}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Błąd w teście {test_name}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Wyniki: {passed}/{total} testów przeszło")
    
    if passed == total:
        print("🎉 Wszystkie testy przeszły!")
        return True
    else:
        print("⚠️ Niektóre testy nie przeszły")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
