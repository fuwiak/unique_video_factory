#!/usr/bin/env python3
"""
Test nowej funkcjonalności blogger cards z Google Sheets
"""

import os
import sys
from dotenv import load_dotenv

# Dodaj ścieżkę do modułów
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_blogger_cards_format():
    """Test formatowania danych blogger cards"""
    try:
        from google_sheets_integration import GoogleSheetsIntegration
        
        # Symulacja danych blogger cards
        blogger_data = {
            'VK': {
                'platform': 'VK',
                'followers': 1234,
                'friends': 567,
                'method': 'VK API',
                'blogger_name': 'Лиза',
                'user_name': 'Лиза',
                'url': 'https://vk.com/lizaaaakorzh'
            },
            'YouTube': {
                'platform': 'YouTube',
                'subscribers': 2345,
                'videos': 45,
                'views': 123456,
                'method': 'YouTube API',
                'blogger_name': 'Лиза',
                'user_name': 'Лиза',
                'url': 'https://www.youtube.com/@elizavetakorzh_fb'
            }
        }
        
        sheets = GoogleSheetsIntegration()
        formatted_data = sheets.format_data_for_sheets(blogger_data)
        
        print(f"✅ Formatowanie OK - {len(formatted_data)} wierszy")
        for i, row in enumerate(formatted_data):
            print(f"  Wiersz {i+1}: {row[:5]}...")  # Pierwsze 5 kolumn
        
        return True
    except Exception as e:
        print(f"❌ Błąd formatowania: {e}")
        return False

def test_mixed_data_format():
    """Test formatowania mieszanych danych (blogger cards + clips)"""
    try:
        from google_sheets_integration import GoogleSheetsIntegration
        
        # Mieszane dane - blogger cards + clips
        mixed_data = {
            'VK': {
                'platform': 'VK',
                'followers': 1234,
                'blogger_name': 'Лиза',
                'user_name': 'Лиза',
                'url': 'https://vk.com/lizaaaakorzh'
            },
            'Instagram': {
                'platform': 'Instagram',
                'clips': [
                    {
                        'title': 'Test Clip',
                        'views': 1000,
                        'likes': 50,
                        'comments': 10,
                        'date': '2025-10-28',
                        'duration': 30,
                        'video_id': '123456'
                    }
                ],
                'user_name': 'Test User'
            }
        }
        
        sheets = GoogleSheetsIntegration()
        formatted_data = sheets.format_data_for_sheets(mixed_data)
        
        print(f"✅ Mieszane formatowanie OK - {len(formatted_data)} wierszy")
        for i, row in enumerate(formatted_data):
            print(f"  Wiersz {i+1}: {row[:5]}...")  # Pierwsze 5 kolumn
        
        return True
    except Exception as e:
        print(f"❌ Błąd mieszanego formatowania: {e}")
        return False

def test_google_sheets_save():
    """Test zapisu do Google Sheets"""
    try:
        from google_sheets_integration import GoogleSheetsIntegration
        
        # Test danych blogger cards
        test_data = {
            'VK': {
                'platform': 'VK',
                'followers': 1234,
                'videos': 45,
                'views': 12345,
                'blogger_name': 'Лиза',
                'user_name': 'Лиза',
                'url': 'https://vk.com/lizaaaakorzh'
            }
        }
        
        sheets = GoogleSheetsIntegration()
        success = sheets.save_to_sheets(test_data)
        
        if success:
            print("✅ Zapis do Google Sheets OK")
        else:
            print("❌ Błąd zapisu do Google Sheets")
        
        return success
    except Exception as e:
        print(f"❌ Błąd testu zapisu: {e}")
        return False

def main():
    """Główna funkcja testowa"""
    print("🧪 Test funkcjonalności blogger cards z Google Sheets")
    print("=" * 60)
    
    tests = [
        ("Formatowanie blogger cards", test_blogger_cards_format),
        ("Mieszane formatowanie", test_mixed_data_format),
        ("Zapis do Google Sheets", test_google_sheets_save),
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
