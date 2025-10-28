#!/usr/bin/env python3
"""
Test nowej funkcjonalności blogger cards z osobnymi arkuszami
"""

import os
import sys
from dotenv import load_dotenv

# Dodaj ścieżkę do modułów
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_vk_url_conversion():
    """Test konwersji VK URL"""
    try:
        from telegram_bot import TelegramVideoBot
        
        bot = TelegramVideoBot()
        
        test_cases = [
            ("https://vk.com/lizaaaakorzh", "https://vk.com/clips/lizaaaakorzh"),
            ("https://vk.com/user123", "https://vk.com/clips/user123"),
            ("https://vk.com/test?param=1", "https://vk.com/clips/test"),
        ]
        
        for original, expected in test_cases:
            result = bot.convert_vk_to_clips_url(original)
            if result == expected:
                print(f"✅ {original} -> {result}")
            else:
                print(f"❌ {original} -> {result} (expected: {expected})")
                return False
        
        print("✅ VK URL konwersja OK")
        return True
    except Exception as e:
        print(f"❌ Błąd VK URL konwersji: {e}")
        return False

def test_blogger_sheet_creation():
    """Test tworzenia arkuszy dla blogerów"""
    try:
        from google_sheets_integration import GoogleSheetsIntegration
        
        sheets = GoogleSheetsIntegration()
        
        # Test danych dla blogera
        test_data = {
            'VK': {
                'platform': 'VK',
                'followers': 1234,
                'videos': 45,
                'views': 12345,
                'blogger_name': 'Лиза',
                'user_name': 'Лиза',
                'url': 'https://vk.com/clips/lizaaaakorzh'
            },
            'YouTube': {
                'platform': 'YouTube',
                'subscribers': 2345,
                'shorts': [
                    {
                        'title': 'Test Short 1',
                        'views': 1000,
                        'likes': 50,
                        'comments': 10,
                        'url': 'https://www.youtube.com/shorts/123',
                        'published_at': '2025-10-28T10:00:00Z',
                        'duration': 'PT30S'
                    },
                    {
                        'title': 'Test Short 2',
                        'views': 2000,
                        'likes': 100,
                        'comments': 20,
                        'url': 'https://www.youtube.com/shorts/456',
                        'published_at': '2025-10-27T10:00:00Z',
                        'duration': 'PT45S'
                    }
                ],
                'blogger_name': 'Лиза',
                'user_name': 'Лиза',
                'url': 'https://www.youtube.com/@elizavetakorzh_fb'
            }
        }
        
        # Test zapisu do arkusza blogera
        success = sheets.save_to_blogger_sheet('Лиза', test_data)
        
        if success:
            print("✅ Zapis do arkusza blogera OK")
        else:
            print("❌ Błąd zapisu do arkusza blogera")
        
        return success
    except Exception as e:
        print(f"❌ Błąd testu arkusza blogera: {e}")
        return False

def test_youtube_shorts_structure():
    """Test struktury danych YouTube shorts"""
    try:
        from advanced_social_stats import AdvancedSocialStatsChecker
        
        checker = AdvancedSocialStatsChecker()
        
        # Test danych shortsów
        test_shorts = [
            {
                'title': 'Test Short 1',
                'video_id': '123',
                'url': 'https://www.youtube.com/shorts/123',
                'duration': 'PT30S',
                'views': 1000,
                'likes': 50,
                'comments': 10,
                'published_at': '2025-10-28T10:00:00Z'
            }
        ]
        
        # Test formatowania
        from google_sheets_integration import GoogleSheetsIntegration
        sheets = GoogleSheetsIntegration()
        
        test_data = {
            'YouTube': {
                'platform': 'YouTube',
                'shorts': test_shorts,
                'user_name': 'Test User'
            }
        }
        
        formatted = sheets.format_data_for_sheets(test_data)
        
        if formatted and len(formatted) > 0:
            print(f"✅ Formatowanie shortsów OK - {len(formatted)} wierszy")
            for i, row in enumerate(formatted):
                print(f"  Wiersz {i+1}: {row[:5]}...")
        else:
            print("❌ Błąd formatowania shortsów")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Błąd testu shortsów: {e}")
        return False

def main():
    """Główna funkcja testowa"""
    print("🧪 Test nowej funkcjonalności blogger cards")
    print("=" * 60)
    
    tests = [
        ("VK URL konwersja", test_vk_url_conversion),
        ("Tworzenie arkuszy blogerów", test_blogger_sheet_creation),
        ("Struktura YouTube shorts", test_youtube_shorts_structure),
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
    
    print("\n" + "=" * 60)
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
