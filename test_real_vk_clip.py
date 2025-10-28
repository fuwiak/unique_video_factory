#!/usr/bin/env python3
"""
Test rzeczywistego wywołania get_vk_clip_data
"""

from advanced_social_stats import AdvancedSocialStatsChecker
from api_keys_config import get_api_keys
import logging

# Ustawiamy logowanie
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_real_vk_clip_data():
    """Test rzeczywistego wywołania get_vk_clip_data"""
    print("🔍 Test rzeczywistego wywołania get_vk_clip_data")
    
    # Inicjalizujemy checker
    checker = AdvancedSocialStatsChecker()
    api_keys = get_api_keys()
    checker.api_keys = api_keys
    
    print(f"🔑 VK API key dostępny: {bool(api_keys.get('vk'))}")
    
    # Test URL
    url = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129"
    print(f"📊 Test URL: {url}")
    
    # Wywołujemy funkcję
    print("\n🎬 Wywołuję get_vk_clip_data...")
    result = checker.get_vk_clip_data(url)
    
    print(f"\n📊 Wynik:")
    print(f"Platform: {result.get('platform')}")
    print(f"Error: {result.get('error', 'Brak błędu')}")
    print(f"Method: {result.get('method', 'N/A')}")
    
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

if __name__ == '__main__':
    test_real_vk_clip_data()
