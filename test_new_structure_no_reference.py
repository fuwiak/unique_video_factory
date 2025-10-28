#!/usr/bin/env python3
"""
Test nowej struktury Google Sheets bez kolumny Референс
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_sheets_integration import GoogleSheetsIntegration
from advanced_social_stats import AdvancedSocialStatsChecker
import json

def test_new_structure():
    """Test nowej struktury bez kolumny Референс"""
    print("🧪 Test nowej struktury Google Sheets (bez Референс)")
    
    # Tworzymy integrację
    integration = GoogleSheetsIntegration()
    
    # Test danych VK clip
    vk_data = {
        "VK": {
            "platform": "VK",
            "url": "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239128",
            "clips": [
                {
                    "title": "Test VK Clip",
                    "views": 1500,
                    "date": "2025-01-15",
                    "video_id": "456239128"
                }
            ]
        }
    }
    
    # Test danych YouTube Short
    youtube_data = {
        "YouTube": {
            "platform": "YouTube",
            "url": "https://www.youtube.com/shorts/LHyvxcekiV4",
            "shorts": [
                {
                    "title": "Test YouTube Short",
                    "views": 5000,
                    "published_at": "2025-01-15",
                    "video_id": "LHyvxcekiV4"
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
    print("\n📋 Nowe nagłówki:")
    headers = integration.prepare_headers()
    print(headers)
    
    return True

def test_vk_api_data():
    """Test pobierania danych z VK API"""
    print("\n🧪 Test pobierania danych z VK API")
    
    checker = AdvancedSocialStatsChecker()
    
    # Test URL z VK
    vk_url = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239128"
    
    print(f"VK URL: {vk_url}")
    
    # Wyciągamy ID
    owner_id = checker._extract_vk_owner_id(vk_url)
    video_id = checker._extract_vk_video_id(vk_url)
    
    print(f"Owner ID: {owner_id}")
    print(f"Video ID: {video_id}")
    
    # Pobieramy dane
    result = checker.get_vk_clip_data(vk_url)
    
    if 'error' in result:
        print(f"❌ Błąd: {result['error']}")
    else:
        print(f"✅ Sukces: {result.get('method', 'Unknown method')}")
        
        if 'clips' in result:
            for clip in result['clips']:
                print(f"  📹 Tytuł: {clip.get('title', 'N/A')}")
                print(f"  👀 Wyświetlenia: {clip.get('views', 'N/A')}")
                print(f"  📅 Data: {clip.get('date', 'N/A')}")
                print(f"  🔗 URL: {clip.get('url', 'N/A')}")
    
    return result

if __name__ == "__main__":
    print("🚀 Uruchamianie testów nowej struktury Google Sheets")
    
    # Test 1: Nowa struktura danych
    test1_success = test_new_structure()
    
    # Test 2: VK API data
    test2_result = test_vk_api_data()
    
    print(f"\n📊 Podsumowanie testów:")
    print(f"✅ Test struktury danych: {'PASSED' if test1_success else 'FAILED'}")
    print(f"✅ Test VK API: {'PASSED' if 'error' not in test2_result else 'FAILED'}")
    
    if test1_success and 'error' not in test2_result:
        print("\n🎉 Wszystkie testy przeszły pomyślnie!")
    else:
        print("\n❌ Niektóre testy nie przeszły")
