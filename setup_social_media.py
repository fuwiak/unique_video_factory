#!/usr/bin/env python3
"""
Skrypt do konfiguracji API keys dla social media
"""

import os
from pathlib import Path

def setup_env_file():
    """Tworzy/aktualizuje plik .env z API keys"""
    
    env_file = Path('.env')
    
    # Sprawdzamy czy plik .env istnieje
    if env_file.exists():
        print("📄 Plik .env już istnieje")
        with open(env_file, 'r') as f:
            content = f.read()
    else:
        print("📄 Tworzenie nowego pliku .env")
        content = ""
    
    # Sprawdzamy jakie API keys już mamy
    has_youtube = 'YOUTUBE_API_KEY' in content
    has_vk = 'VK_TOKEN' in content
    
    print("\n🔧 KONFIGURACJA API KEYS")
    print("=" * 50)
    
    # YouTube API Key
    if not has_youtube:
        print("\n📺 YouTube Data API v3:")
        print("1. Idź do: https://console.developers.google.com/")
        print("2. Utwórz projekt lub wybierz istniejący")
        print("3. Włącz YouTube Data API v3")
        print("4. Utwórz klucz API")
        
        youtube_key = input("\nWprowadź YouTube API key (lub naciśnij Enter aby pominąć): ").strip()
        if youtube_key:
            content += f"\n# YouTube Data API v3\nYOUTUBE_API_KEY={youtube_key}\n"
            print("✅ YouTube API key dodany")
        else:
            print("⚠️ YouTube API key pominięty")
    else:
        print("✅ YouTube API key już skonfigurowany")
    
    # VK Token
    if not has_vk:
        print("\n🔵 VK API:")
        print("1. Idź do: https://vk.com/apps?act=manage")
        print("2. Utwórz aplikację")
        print("3. Uzyskaj access token")
        
        vk_token = input("\nWprowadź VK token (lub naciśnij Enter aby pominąć): ").strip()
        if vk_token:
            content += f"\n# VK API\nVK_TOKEN={vk_token}\n"
            print("✅ VK token dodany")
        else:
            print("⚠️ VK token pominięty")
    else:
        print("✅ VK token już skonfigurowany")
    
    # Instagram (nie wymaga API key)
    print("\n📸 Instagram:")
    print("✅ Używa instaloader - nie wymaga API key")
    
    # TikTok (nie wymaga API key)
    print("\n🎵 TikTok:")
    print("✅ Używa TikTokApi - nie wymaga API key")
    
    # Likee (nie wymaga API key)
    print("\n💜 Likee:")
    print("✅ Używa scraping - nie wymaga API key")
    
    # Zapisujemy plik .env
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"\n💾 Plik .env zaktualizowany: {env_file.absolute()}")
    
    # Sprawdzamy status
    print("\n📊 STATUS KONFIGURACJI:")
    print("=" * 30)
    
    # Sprawdzamy co mamy w .env
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    youtube_status = "✅" if 'YOUTUBE_API_KEY' in env_content else "❌"
    vk_status = "✅" if 'VK_TOKEN' in env_content else "❌"
    
    print(f"YouTube API: {youtube_status}")
    print(f"VK Token: {vk_status}")
    print("Instagram: ✅ (instaloader)")
    print("TikTok: ✅ (TikTokApi)")
    print("Likee: ✅ (scraping)")
    
    print("\n🚀 Możesz teraz uruchomić:")
    print("python enhanced_social_stats.py")
    print("python test_enhanced_social.py")

def main():
    """Główna funkcja"""
    print("🔧 KONFIGURACJA SOCIAL MEDIA API KEYS")
    print("=" * 60)
    
    setup_env_file()
    
    print("\n✅ Konfiguracja zakończona!")

if __name__ == "__main__":
    main()




