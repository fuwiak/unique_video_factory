#!/usr/bin/env python3
"""
Test struktury danych z VK Clips
Sprawdza dokładnie co zwraca get_vk_clip_data i czy format_data_for_sheets to poprawnie przetwarza
"""

import unittest
from advanced_social_stats import AdvancedSocialStatsChecker
from google_sheets_integration import GoogleSheetsIntegration
from api_keys_config import get_api_keys
import json

class TestVkDataStructure(unittest.TestCase):
    def setUp(self):
        self.checker = AdvancedSocialStatsChecker()
        self.api_keys = get_api_keys()
        self.checker.api_keys = self.api_keys
        self.google_sheets = GoogleSheetsIntegration()
        self.google_sheets.init_google_sheets()

    def test_vk_clip_data_structure(self):
        """Test struktury danych z VK Clips"""
        print("\n🔍 Test struktury danych z VK Clips")
        
        # Test URL VK Clips
        vk_url = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129"
        print(f"VK URL: {vk_url}")
        
        # Pobieramy dane z VK API
        result = self.checker.get_vk_clip_data(vk_url)
        print(f"\n📊 Wynik get_vk_clip_data:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Sprawdzamy strukturę
        if 'error' not in result:
            print(f"\n✅ Sukces - brak błędów")
            print(f"Platform: {result.get('platform')}")
            print(f"Method: {result.get('method')}")
            print(f"URL: {result.get('url')}")
            
            if 'clips' in result:
                print(f"Clips count: {len(result['clips'])}")
                for i, clip in enumerate(result['clips']):
                    print(f"Clip {i+1}:")
                    print(f"  - Title: {clip.get('title')}")
                    print(f"  - Views: {clip.get('views')}")
                    print(f"  - Date: {clip.get('date')}")
                    print(f"  - Video ID: {clip.get('video_id')}")
            else:
                print("❌ Brak 'clips' w wyniku!")
        else:
            print(f"❌ Błąd: {result['error']}")

    def test_format_data_for_sheets_with_vk_data(self):
        """Test formatowania danych VK dla Google Sheets"""
        print("\n📊 Test formatowania danych VK dla Google Sheets")
        
        # Pobieramy rzeczywiste dane
        vk_url = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129"
        vk_result = self.checker.get_vk_clip_data(vk_url)
        
        if 'error' in vk_result:
            print(f"❌ Błąd pobierania danych VK: {vk_result['error']}")
            return
        
        # Przygotowujemy dane w formacie oczekiwanym przez format_data_for_sheets
        test_data = {
            'VK': vk_result
        }
        
        print(f"\n📋 Dane do formatowania:")
        print(json.dumps(test_data, indent=2, ensure_ascii=False))
        
        # Formatujemy dane
        formatted_rows = self.google_sheets.format_data_for_sheets(test_data)
        
        print(f"\n📊 Sformatowane wiersze:")
        for i, row in enumerate(formatted_rows):
            print(f"Wiersz {i+1}: {row}")
        
        # Sprawdzamy czy są dane
        if formatted_rows:
            print(f"\n✅ Sukces: {len(formatted_rows)} wierszy sformatowanych")
            print(f"Pierwszy wiersz: {formatted_rows[0]}")
        else:
            print(f"\n❌ Brak sformatowanych wierszy!")
            print("To może być przyczyną 'Brak danych do zapisania'")

    def test_mock_vk_data_structure(self):
        """Test z mock danymi VK"""
        print("\n🧪 Test z mock danymi VK")
        
        # Mock dane VK w formacie zwracanym przez get_vk_clip_data
        mock_vk_data = {
            'VK': {
                'platform': 'VK',
                'url': 'https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129',
                'clips': [{
                    'title': 'Test VK Clip',
                    'video_id': '456239129',
                    'views': 11,
                    'likes': 5,
                    'comments': 2,
                    'date': '2025-10-27',
                    'duration': 30,
                    'url': 'https://vk.com/video1069245351_456239129'
                }],
                'method': 'VK API'
            }
        }
        
        print(f"\n📋 Mock dane VK:")
        print(json.dumps(mock_vk_data, indent=2, ensure_ascii=False))
        
        # Formatujemy mock dane
        formatted_rows = self.google_sheets.format_data_for_sheets(mock_vk_data)
        
        print(f"\n📊 Sformatowane wiersze z mock danych:")
        for i, row in enumerate(formatted_rows):
            print(f"Wiersz {i+1}: {row}")
        
        # Sprawdzamy czy są dane
        if formatted_rows:
            print(f"\n✅ Mock test sukces: {len(formatted_rows)} wierszy")
            self.assertEqual(len(formatted_rows), 1)
            self.assertEqual(formatted_rows[0][2], '11')  # Views
        else:
            print(f"\n❌ Mock test błąd: brak wierszy!")
            self.fail("Mock dane nie zostały sformatowane!")

if __name__ == '__main__':
    print("🚀 Uruchamianie testów struktury danych VK")
    unittest.main()
