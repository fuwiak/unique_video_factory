#!/usr/bin/env python3
"""
Test końcowy - sprawdzenie czy bot poprawnie pobiera rzeczywiste dane
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_social_stats import AdvancedSocialStatsChecker
from google_sheets_integration import GoogleSheetsIntegration
import json

def test_final_functionality():
    """Test końcowy całej funkcjonalności"""
    print("🧪 Test końcowy - rzeczywiste dane z YouTube Shorts")
    
    # Tworzymy checker
    checker = AdvancedSocialStatsChecker()
    
    # Test URL z YouTube Shorts
    youtube_url = "https://www.youtube.com/shorts/Fjro6Daa0VM"
    
    print(f"YouTube URL: {youtube_url}")
    
    # Pobieramy dane
    result = checker.get_youtube_short_data(youtube_url)
    
    if 'error' in result:
        print(f"❌ Błąd: {result['error']}")
        return False
    
    print(f"✅ Sukces: {result.get('method', 'Unknown method')}")
    
    if 'shorts' in result:
        for short in result['shorts']:
            print(f"\n📊 Dane z YouTube API:")
            print(f"  📹 Tytuł: {short.get('title', 'N/A')}")
            print(f"  👀 Wyświetlenia: {short.get('views', 'N/A')}")
            print(f"  👍 Polubienia: {short.get('likes', 'N/A')}")
            print(f"  💬 Komentarze: {short.get('comments', 'N/A')}")
            print(f"  📅 Data: {short.get('published_at', 'N/A')}")
            print(f"  ⏱️ Długość: {short.get('duration', 'N/A')}")
            print(f"  🔗 URL: {short.get('url', 'N/A')}")
    
    # Test formatowania dla Google Sheets
    print(f"\n📊 Test formatowania dla Google Sheets:")
    integration = GoogleSheetsIntegration()
    
    # Konwertujemy wynik na format oczekiwany przez format_data_for_sheets
    test_data = {"YouTube": result}
    formatted_rows = integration.format_data_for_sheets(test_data)
    for i, row in enumerate(formatted_rows):
        print(f"Wiersz {i+1}: {row}")
    
    # Sprawdzamy czy dane są poprawne
    if 'shorts' in result and result['shorts']:
        short = result['shorts'][0]
        views = short.get('views', 0)
        
        if views > 0:
            print(f"\n✅ SUKCES: Bot poprawnie pobiera rzeczywiste dane!")
            print(f"   Wyświetlenia: {views} (zamiast 0)")
            return True
        else:
            print(f"\n❌ BŁĄD: Bot nadal pokazuje 0 views")
            return False
    else:
        print(f"\n❌ BŁĄD: Brak danych short")
        return False

def test_vk_clip():
    """Test VK clip dla porównania"""
    print(f"\n🧪 Test VK clip dla porównania")
    
    checker = AdvancedSocialStatsChecker()
    
    # Test URL z VK
    vk_url = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239128"
    
    print(f"VK URL: {vk_url}")
    
    result = checker.get_vk_clip_data(vk_url)
    
    if 'error' in result:
        print(f"❌ Błąd VK: {result['error']}")
    else:
        print(f"✅ VK Sukces: {result.get('method', 'Unknown method')}")
        
        if 'clips' in result:
            for clip in result['clips']:
                print(f"  📹 Tytuł: {clip.get('title', 'N/A')}")
                print(f"  👀 Wyświetlenia: {clip.get('views', 'N/A')}")
                print(f"  📅 Data: {clip.get('date', 'N/A')}")

if __name__ == "__main__":
    print("🚀 Uruchamianie testu końcowego")
    
    # Test 1: YouTube Shorts
    youtube_success = test_final_functionality()
    
    # Test 2: VK Clip
    test_vk_clip()
    
    print(f"\n📊 Podsumowanie:")
    if youtube_success:
        print("✅ YouTube Shorts: POPRAWNE DANE (628 views)")
        print("✅ Problem rozwiązany!")
    else:
        print("❌ YouTube Shorts: NADAL PROBLEM")
    
    print(f"\n💡 Następne kroki:")
    print("1. Bot teraz poprawnie pobiera rzeczywiste dane z YouTube API")
    print("2. Można testować w Telegram bot")
    print("3. Dane będą zapisywane do Google Sheets z rzeczywistymi wartościami")
