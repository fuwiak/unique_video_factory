#!/usr/bin/env python3
"""
Test nowej struktury Google Sheets
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_sheets_integration import GoogleSheetsIntegration
import json

def test_new_structure():
    """Test nowej struktury danych"""
    print("🧪 Test nowej struktury Google Sheets")
    
    # Tworzymy integrację
    integration = GoogleSheetsIntegration()
    
    # Test danych VK clips
    vk_data = {
        "VK": {
            "platform": "VK",
            "user_name": "Лиза",
            "url": "https://vk.com/clips/lizaaaakorzh",
            "clips": [
                {
                    "title": "Test clip 1",
                    "views": 1000,
                    "date": "2025-01-15",
                    "video_id": "123456"
                },
                {
                    "title": "Test clip 2", 
                    "views": 2000,
                    "date": "2025-01-14",
                    "video_id": "123457"
                }
            ]
        }
    }
    
    # Test danych YouTube shorts
    youtube_data = {
        "YouTube": {
            "platform": "YouTube",
            "user_name": "Лиза",
            "url": "https://youtube.com/@lizaaaakorzh",
            "shorts": [
                {
                    "title": "Test short 1",
                    "views": 5000,
                    "published_at": "2025-01-15T10:00:00Z",
                    "url": "https://youtube.com/shorts/abc123"
                },
                {
                    "title": "Test short 2",
                    "views": 3000,
                    "published_at": "2025-01-14T15:30:00Z", 
                    "url": "https://youtube.com/shorts/def456"
                }
            ]
        }
    }
    
    print("\n📊 Test formatowania danych VK:")
    vk_rows = integration.format_data_for_sheets(vk_data)
    for i, row in enumerate(vk_rows):
        print(f"Wiersz {i+1}: {row}")
    
    print("\n📊 Test formatowania danych YouTube:")
    youtube_rows = integration.format_data_for_sheets(youtube_data)
    for i, row in enumerate(youtube_rows):
        print(f"Wiersz {i+1}: {row}")
    
    print("\n✅ Test nowej struktury zakończony")
    
    # Test nagłówków
    print("\n📋 Nagłówki:")
    headers = integration.prepare_headers()
    print(headers)
    
    return True

def test_blogger_sheet_creation():
    """Test tworzenia arkusza dla blogera"""
    print("\n🧪 Test tworzenia arkusza blogera")
    
    integration = GoogleSheetsIntegration()
    
    # Inicjalizujemy Google Sheets
    if not integration.init_google_sheets():
        print("❌ Nie można zainicjalizować Google Sheets")
        return False
    
    # Test tworzenia arkusza dla "Лиза"
    sheet = integration.get_or_create_blogger_sheet("Лиза")
    
    if sheet:
        print(f"✅ Arkusz dla Лиза: {sheet.title}")
        print(f"📊 Liczba wierszy: {sheet.row_count}")
        print(f"📊 Liczba kolumn: {sheet.col_count}")
        
        # Sprawdzamy nagłówki
        try:
            headers = sheet.row_values(1)
            print(f"📋 Nagłówki: {headers}")
        except Exception as e:
            print(f"⚠️ Nie można odczytać nagłówków: {e}")
        
        return True
    else:
        print("❌ Nie można utworzyć arkusza")
        return False

if __name__ == "__main__":
    print("🚀 Uruchamianie testów nowej struktury Google Sheets")
    
    # Test 1: Nowa struktura danych
    test1_success = test_new_structure()
    
    # Test 2: Tworzenie arkusza blogera
    test2_success = test_blogger_sheet_creation()
    
    print(f"\n📊 Podsumowanie testów:")
    print(f"✅ Test struktury danych: {'PASSED' if test1_success else 'FAILED'}")
    print(f"✅ Test tworzenia arkusza: {'PASSED' if test2_success else 'FAILED'}")
    
    if test1_success and test2_success:
        print("\n🎉 Wszystkie testy przeszły pomyślnie!")
    else:
        print("\n❌ Niektóre testy nie przeszły")
