#!/usr/bin/env python3
"""
Test bezpośredniego pobierania danych z URL video
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_social_stats import AdvancedSocialStatsChecker
import json

def test_direct_url_processing():
    """Test pobierania danych z bezpośrednich URL video"""
    print("🧪 Test bezpośredniego pobierania danych z URL video")
    
    # Tworzymy checker
    checker = AdvancedSocialStatsChecker()
    
    # Test URL-e
    test_urls = {
        "VK Clip": "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129",
        "YouTube Short": "https://www.youtube.com/shorts/LHyvxcekiV4"
    }
    
    results = {}
    
    for platform, url in test_urls.items():
        print(f"\n📊 Test {platform}: {url}")
        
        try:
            if platform == "VK Clip":
                result = checker.get_vk_clip_data(url)
            elif platform == "YouTube Short":
                result = checker.get_youtube_short_data(url)
            else:
                continue
            
            results[platform] = result
            
            if 'error' in result:
                print(f"❌ Błąd: {result['error']}")
            else:
                print(f"✅ Sukces: {result.get('method', 'Unknown method')}")
                
                # Wyświetlamy dane
                if 'clips' in result:
                    for clip in result['clips']:
                        print(f"  📹 Tytuł: {clip.get('title', 'N/A')}")
                        print(f"  👀 Wyświetlenia: {clip.get('views', 'N/A')}")
                        print(f"  📅 Data: {clip.get('date', 'N/A')}")
                        print(f"  🔗 URL: {clip.get('url', 'N/A')}")
                
                if 'shorts' in result:
                    for short in result['shorts']:
                        print(f"  📹 Tytuł: {short.get('title', 'N/A')}")
                        print(f"  👀 Wyświetlenia: {short.get('views', 'N/A')}")
                        print(f"  📅 Data: {short.get('published_at', 'N/A')}")
                        print(f"  🔗 URL: {short.get('url', 'N/A')}")
        
        except Exception as e:
            print(f"❌ Wyjątek: {e}")
            results[platform] = {'error': str(e)}
    
    return results

def test_url_extraction():
    """Test wyciągania ID z URL"""
    print("\n🔍 Test wyciągania ID z URL")
    
    checker = AdvancedSocialStatsChecker()
    
    # Test VK URL
    vk_url = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129"
    
    print(f"\nVK URL: {vk_url}")
    owner_id = checker._extract_vk_owner_id(vk_url)
    video_id = checker._extract_vk_video_id(vk_url)
    
    print(f"Owner ID: {owner_id}")
    print(f"Video ID: {video_id}")
    
    # Test YouTube URL
    youtube_url = "https://www.youtube.com/shorts/LHyvxcekiV4"
    
    print(f"\nYouTube URL: {youtube_url}")
    youtube_video_id = checker._extract_youtube_video_id(youtube_url)
    
    print(f"YouTube Video ID: {youtube_video_id}")
    
    return {
        'vk_owner_id': owner_id,
        'vk_video_id': video_id,
        'youtube_video_id': youtube_video_id
    }

def test_google_sheets_format():
    """Test formatowania danych dla Google Sheets"""
    print("\n📊 Test formatowania danych dla Google Sheets")
    
    from google_sheets_integration import GoogleSheetsIntegration
    
    integration = GoogleSheetsIntegration()
    
    # Test danych VK clip
    vk_data = {
        "VK": {
            "platform": "VK",
            "url": "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129",
            "clips": [
                {
                    "title": "Test VK Clip",
                    "views": 1500,
                    "date": "2025-01-15",
                    "video_id": "456239129"
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
    
    print("\nVK Clip formatowanie:")
    vk_rows = integration.format_data_for_sheets(vk_data)
    for i, row in enumerate(vk_rows):
        print(f"Wiersz {i+1}: {row}")
    
    print("\nYouTube Short formatowanie:")
    youtube_rows = integration.format_data_for_sheets(youtube_data)
    for i, row in enumerate(youtube_rows):
        print(f"Wiersz {i+1}: {row}")
    
    return {
        'vk_rows': vk_rows,
        'youtube_rows': youtube_rows
    }

if __name__ == "__main__":
    print("🚀 Uruchamianie testów bezpośredniego pobierania danych")
    
    # Test 1: Wyciąganie ID z URL
    test1_results = test_url_extraction()
    
    # Test 2: Pobieranie danych z URL
    test2_results = test_direct_url_processing()
    
    # Test 3: Formatowanie dla Google Sheets
    test3_results = test_google_sheets_format()
    
    print(f"\n📊 Podsumowanie testów:")
    print(f"✅ Test wyciągania ID: {'PASSED' if test1_results['vk_owner_id'] and test1_results['youtube_video_id'] else 'FAILED'}")
    
    success_count = sum(1 for result in test2_results.values() if 'error' not in result)
    print(f"✅ Test pobierania danych: {success_count}/{len(test2_results)} PASSED")
    
    print(f"✅ Test formatowania: {'PASSED' if test3_results['vk_rows'] and test3_results['youtube_rows'] else 'FAILED'}")
    
    if success_count > 0:
        print("\n🎉 Przynajmniej jeden test przeszedł pomyślnie!")
    else:
        print("\n❌ Wszystkie testy nie przeszły")
