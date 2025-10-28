#!/usr/bin/env python3
"""
Test dla bezpośrednich URL-ów VK Clips
Sprawdza czy funkcja poprawnie ekstraktuje dane z konkretnych clipów
"""

import unittest
from unittest.mock import MagicMock, patch
from advanced_social_stats import AdvancedSocialStatsChecker
from api_keys_config import get_api_keys
import json

class TestVkClipsDirectUrls(unittest.TestCase):
    def setUp(self):
        self.checker = AdvancedSocialStatsChecker()
        self.api_keys = get_api_keys()
        self.checker.api_keys = self.api_keys

    def test_extract_vk_clip_ids_from_url(self):
        """Test wyciągania ID z bezpośrednich URL-ów VK Clips"""
        print("\n🔍 Test wyciągania ID z bezpośrednich URL-ów VK Clips")
        
        # Test URL 1: 10 просмотров
        url1 = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129"
        owner_id1 = self.checker._extract_vk_owner_id(url1)
        video_id1 = self.checker._extract_vk_video_id(url1)
        
        print(f"URL 1: {url1}")
        print(f"Owner ID: {owner_id1}")
        print(f"Video ID: {video_id1}")
        
        self.assertEqual(owner_id1, "1069245351")
        self.assertEqual(video_id1, "456239129")
        
        # Test URL 2: 4 просмотров
        url2 = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239124"
        owner_id2 = self.checker._extract_vk_owner_id(url2)
        video_id2 = self.checker._extract_vk_video_id(url2)
        
        print(f"\nURL 2: {url2}")
        print(f"Owner ID: {owner_id2}")
        print(f"Video ID: {video_id2}")
        
        self.assertEqual(owner_id2, "1069245351")
        self.assertEqual(video_id2, "456239124")

    @patch('advanced_social_stats.AdvancedSocialStatsChecker._make_request')
    @patch('advanced_social_stats.AdvancedSocialStatsChecker._get_vk_clip_by_id')
    def test_vk_clip_direct_data_fetching(self, mock_get_vk_clip_by_id, mock_make_request):
        """Test pobierania danych z bezpośrednich URL-ów VK Clips"""
        print("\n🧪 Test pobierania danych z bezpośrednich URL-ów VK Clips")
        
        # Mock VK API response dla pierwszego clip (10 просмотров)
        mock_get_vk_clip_by_id.side_effect = [
            {
                'title': 'VK Clip 1',
                'video_id': '456239129',
                'views': 10,
                'likes': 5,
                'comments': 2,
                'date': '2025-01-15',
                'duration': 30,
                'url': 'https://vk.com/video1069245351_456239129'
            },
            {
                'title': 'VK Clip 2', 
                'video_id': '456239124',
                'views': 4,
                'likes': 2,
                'comments': 1,
                'date': '2025-01-15',
                'duration': 25,
                'url': 'https://vk.com/video1069245351_456239124'
            }
        ]
        
        # Mock scraping response (fallback)
        mock_make_request.side_effect = [
            MagicMock(text='<html><title>VK Clip 1 | VK</title></html>'),
            MagicMock(text='<html><title>VK Clip 2 | VK</title></html>')
        ]
        
        # Test pierwszego clip (10 просмотров)
        url1 = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129"
        result1 = self.checker.get_vk_clip_data(url1)
        
        print(f"\n📊 Test VK Clip 1 (10 просмотров): {url1}")
        if 'error' not in result1:
            print(f"✅ Sukces: {result1.get('method', 'N/A')}")
            print(f"  📹 Tytuł: {result1['clips'][0]['title']}")
            print(f"  👀 Wyświetlenia: {result1['clips'][0]['views']}")
            print(f"  📅 Data: {result1['clips'][0]['date']}")
            print(f"  🔗 URL: {result1['clips'][0]['url']}")
            self.assertEqual(result1['clips'][0]['views'], 10)
        else:
            print(f"❌ Błąd: {result1['error']}")
            self.fail(f"Błąd pobierania danych VK Clip 1: {result1['error']}")
        
        # Test drugiego clip (4 просмотров)
        url2 = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239124"
        result2 = self.checker.get_vk_clip_data(url2)
        
        print(f"\n📊 Test VK Clip 2 (4 просмотров): {url2}")
        if 'error' not in result2:
            print(f"✅ Sukces: {result2.get('method', 'N/A')}")
            print(f"  📹 Tytuł: {result2['clips'][0]['title']}")
            print(f"  👀 Wyświetlenia: {result2['clips'][0]['views']}")
            print(f"  📅 Data: {result2['clips'][0]['date']}")
            print(f"  🔗 URL: {result2['clips'][0]['url']}")
            self.assertEqual(result2['clips'][0]['views'], 4)
        else:
            print(f"❌ Błąd: {result2['error']}")
            self.fail(f"Błąd pobierania danych VK Clip 2: {result2['error']}")

    def test_real_vk_api_call(self):
        """Test rzeczywistego wywołania VK API"""
        print("\n🌐 Test rzeczywistego wywołania VK API")
        
        if not self.api_keys.get('vk'):
            print("❌ Brak VK API key - pomijam test")
            return
        
        print("✅ VK API key dostępny")
        
        # Test pierwszego clip
        url1 = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129"
        owner_id1 = self.checker._extract_vk_owner_id(url1)
        video_id1 = self.checker._extract_vk_video_id(url1)
        
        print(f"\n📊 Test rzeczywistego API dla clip 1:")
        print(f"Owner ID: {owner_id1}")
        print(f"Video ID: {video_id1}")
        
        # Wywołujemy rzeczywiste API
        clip_data1 = self.checker._get_vk_clip_by_id(owner_id1, video_id1)
        if clip_data1:
            print(f"✅ Sukces API:")
            print(f"  📹 Tytuł: {clip_data1.get('title', 'N/A')}")
            print(f"  👀 Wyświetlenia: {clip_data1.get('views', 0)}")
            print(f"  📅 Data: {clip_data1.get('date', 'N/A')}")
            print(f"  🔗 URL: {clip_data1.get('url', 'N/A')}")
            
            # Sprawdzamy czy views = 10
            if clip_data1.get('views') == 10:
                print("✅ POPRAWNE: Views = 10")
            else:
                print(f"⚠️ Oczekiwano 10 views, otrzymano: {clip_data1.get('views', 0)}")
        else:
            print("❌ Brak danych z API")
        
        # Test drugiego clip
        url2 = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239124"
        owner_id2 = self.checker._extract_vk_owner_id(url2)
        video_id2 = self.checker._extract_vk_video_id(url2)
        
        print(f"\n📊 Test rzeczywistego API dla clip 2:")
        print(f"Owner ID: {owner_id2}")
        print(f"Video ID: {video_id2}")
        
        clip_data2 = self.checker._get_vk_clip_by_id(owner_id2, video_id2)
        if clip_data2:
            print(f"✅ Sukces API:")
            print(f"  📹 Tytuł: {clip_data2.get('title', 'N/A')}")
            print(f"  👀 Wyświetlenia: {clip_data2.get('views', 0)}")
            print(f"  📅 Data: {clip_data2.get('date', 'N/A')}")
            print(f"  🔗 URL: {clip_data2.get('url', 'N/A')}")
            
            # Sprawdzamy czy views = 4
            if clip_data2.get('views') == 4:
                print("✅ POPRAWNE: Views = 4")
            else:
                print(f"⚠️ Oczekiwano 4 views, otrzymano: {clip_data2.get('views', 0)}")
        else:
            print("❌ Brak danych z API")

    def test_format_data_for_google_sheets(self):
        """Test formatowania danych dla Google Sheets"""
        print("\n📊 Test formatowania danych dla Google Sheets")
        
        from google_sheets_integration import GoogleSheetsIntegration
        google_sheets = GoogleSheetsIntegration()
        
        # Mock data dla pierwszego clip (10 просмотров)
        vk_data1 = {
            'VK': {
                'platform': 'VK',
                'url': 'https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129',
                'clips': [{
                    'title': 'VK Clip 1',
                    'video_id': '456239129',
                    'views': 10,
                    'likes': 5,
                    'comments': 2,
                    'date': '2025-01-15',
                    'duration': 30,
                    'url': 'https://vk.com/video1069245351_456239129'
                }]
            }
        }
        
        formatted1 = google_sheets.format_data_for_sheets(vk_data1)
        print(f"\n📋 Formatowanie clip 1 (10 просмотров):")
        for i, row in enumerate(formatted1):
            print(f"Wiersz {i+1}: {row}")
        
        self.assertEqual(len(formatted1), 1)
        self.assertEqual(formatted1[0][0], 'https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129')
        self.assertEqual(formatted1[0][2], '10')  # Views
        
        # Mock data dla drugiego clip (4 просмотров)
        vk_data2 = {
            'VK': {
                'platform': 'VK',
                'url': 'https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239124',
                'clips': [{
                    'title': 'VK Clip 2',
                    'video_id': '456239124',
                    'views': 4,
                    'likes': 2,
                    'comments': 1,
                    'date': '2025-01-15',
                    'duration': 25,
                    'url': 'https://vk.com/video1069245351_456239124'
                }]
            }
        }
        
        formatted2 = google_sheets.format_data_for_sheets(vk_data2)
        print(f"\n📋 Formatowanie clip 2 (4 просмотров):")
        for i, row in enumerate(formatted2):
            print(f"Wiersz {i+1}: {row}")
        
        self.assertEqual(len(formatted2), 1)
        self.assertEqual(formatted2[0][0], 'https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239124')
        self.assertEqual(formatted2[0][2], '4')  # Views

if __name__ == '__main__':
    print("🚀 Uruchamianie testów VK Clips bezpośrednich URL-ów")
    unittest.main()
