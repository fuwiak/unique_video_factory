#!/usr/bin/env python3
"""
Test ulepszonego skryptu do sprawdzania statystyk społecznościowych
"""

import os
import sys
from enhanced_social_stats import EnhancedSocialStatsChecker

def test_instagram():
    """Test Instagram z instaloader"""
    print("📸 Test Instagram...")
    checker = EnhancedSocialStatsChecker()
    
    url = "https://www.instagram.com/raachel_fb"
    result = checker.check_instagram_stats(url)
    
    if 'error' in result:
        print(f"❌ Błąd: {result['error']}")
    else:
        print(f"✅ Username: {result['username']}")
        print(f"📊 Followers: {result['followers']}")
        print(f"📊 Following: {result['following']}")
        print(f"📊 Posts: {result['posts']}")
        print(f"🔒 Private: {result['is_private']}")
        print(f"✅ Verified: {result['is_verified']}")

def test_tiktok():
    """Test TikTok z TikTokApi"""
    print("\n🎵 Test TikTok...")
    checker = EnhancedSocialStatsChecker()
    
    url = "https://www.tiktok.com/@daniryb_fb"
    result = checker.check_tiktok_stats(url)
    
    if 'error' in result:
        print(f"❌ Błąd: {result['error']}")
    else:
        print(f"✅ Username: {result['username']}")
        print(f"📊 Followers: {result.get('followers', 'N/A')}")
        print(f"📊 Following: {result.get('following', 'N/A')}")
        print(f"📊 Posts: {result.get('posts', 'N/A')}")
        print(f"❤️ Likes: {result.get('likes', 'N/A')}")
        print(f"✅ Verified: {result.get('is_verified', 'N/A')}")

def test_youtube():
    """Test YouTube (wymaga API key)"""
    print("\n📺 Test YouTube...")
    checker = EnhancedSocialStatsChecker()
    
    url = "https://www.youtube.com/@raachel_fb"
    result = checker.check_youtube_stats(url)
    
    if 'error' in result:
        print(f"❌ Błąd: {result['error']}")
    else:
        print(f"✅ Channel: {result.get('title', 'N/A')}")
        print(f"📊 Subscribers: {result.get('subscribers', 'N/A')}")
        print(f"📊 Videos: {result.get('videos', 'N/A')}")
        print(f"📊 Views: {result.get('views', 'N/A')}")

def test_vk():
    """Test VK"""
    print("\n🔵 Test VK...")
    checker = EnhancedSocialStatsChecker()
    
    url = "https://vk.com/raachel_fb"
    result = checker.check_vk_stats(url)
    
    if 'error' in result:
        print(f"❌ Błąd: {result['error']}")
    else:
        print(f"✅ Username: {result['username']}")
        print(f"📊 Followers: {result.get('followers', 'N/A')}")
        print(f"📊 Friends: {result.get('friends', 'N/A')}")
        print(f"📊 Photos: {result.get('photos', 'N/A')}")
        print(f"📊 Videos: {result.get('videos', 'N/A')}")

def test_likee():
    """Test Likee"""
    print("\n💜 Test Likee...")
    checker = EnhancedSocialStatsChecker()
    
    url = "https://l.likee.video/p/jSQPBE"
    result = checker.check_likee_stats(url)
    
    if 'error' in result:
        print(f"❌ Błąd: {result['error']}")
    else:
        print(f"✅ Username: {result['username']}")
        print(f"🔧 Method: {result.get('method', 'N/A')}")

def main():
    """Główna funkcja testowa"""
    print("🧪 TEST ULEPSZONEGO SPRAWDZANIA STATYSTYK")
    print("=" * 60)
    
    # Sprawdzamy konfigurację
    print("📋 Sprawdzanie konfiguracji...")
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    vk_token = os.getenv('VK_TOKEN')
    
    print(f"YouTube API: {'✅' if youtube_key else '❌'}")
    print(f"VK Token: {'✅' if vk_token else '❌'}")
    print()
    
    # Testujemy każdą platformę
    try:
        test_instagram()
    except Exception as e:
        print(f"❌ Błąd testu Instagram: {e}")
    
    try:
        test_tiktok()
    except Exception as e:
        print(f"❌ Błąd testu TikTok: {e}")
    
    try:
        test_youtube()
    except Exception as e:
        print(f"❌ Błąd testu YouTube: {e}")
    
    try:
        test_vk()
    except Exception as e:
        print(f"❌ Błąd testu VK: {e}")
    
    try:
        test_likee()
    except Exception as e:
        print(f"❌ Błąd testu Likee: {e}")
    
    print("\n✅ Test zakończony!")

if __name__ == "__main__":
    main()




