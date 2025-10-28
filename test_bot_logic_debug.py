#!/usr/bin/env python3
"""
Test symulujący dokładnie to co robi Telegram bot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_social_stats import AdvancedSocialStatsChecker
from google_sheets_integration import GoogleSheetsIntegration

def test_bot_logic():
    """Test dokładnie tego co robi bot"""
    print("🧪 Test logiki bota")
    
    checker = AdvancedSocialStatsChecker()
    integration = GoogleSheetsIntegration()
    
    # Symulujemy to co robi bot
    blogger_name = "Лиза"
    platform_urls = {
        'VK': 'https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129'
    }
    
    print(f"Blogger name: {blogger_name}")
    print(f"Platform URLs: {platform_urls}")
    
    # Krok 1: Zbieramy statystyki (jak bot)
    stats_results = {}
    for platform, url in platform_urls.items():
        print(f"\n📊 Zbieram statystyki {platform}...")
        
        if platform.lower() == 'vk':
            if '/clips/' in url:
                result = checker.get_vk_clip_data(url)
            else:
                result = checker.check_vk_stats(url)
        
        stats_results[platform] = result
        print(f"Result: {result}")
    
    # Krok 2: Dodajemy dane blogera (jak bot)
    print(f"\n📝 Dodaję dane blogera...")
    for platform, data in stats_results.items():
        if 'error' not in data:
            data['blogger_name'] = blogger_name
            data['user_name'] = blogger_name
            data['url'] = platform_urls.get(platform, '')
            print(f"Added blogger data to {platform}")
    
    print(f"\n📊 Final stats_results: {stats_results}")
    
    # Krok 3: Formatujemy dla Google Sheets
    print(f"\n📊 Formatuję dla Google Sheets...")
    rows = integration.format_data_for_sheets(stats_results)
    print(f"Formatted rows: {rows}")
    
    if not rows:
        print("❌ BŁĄD: Brak danych do zapisania")
        return False
    else:
        print("✅ SUKCES: Dane sformatowane poprawnie")
        return True

if __name__ == "__main__":
    print("🚀 Uruchamianie testu logiki bota")
    
    success = test_bot_logic()
    
    if success:
        print("\n✅ Test przeszedł pomyślnie!")
    else:
        print("\n❌ Test nie przeszedł - znaleziono problem!")
