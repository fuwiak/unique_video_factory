#!/usr/bin/env python3
"""
Konfiguracja API keys dla social media
"""

import os
from dotenv import load_dotenv

# Ładujemy zmienne środowiskowe
load_dotenv()

class SocialMediaConfig:
    """Konfiguracja API keys dla platform społecznościowych"""
    
    def __init__(self):
        # YouTube Data API v3
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        
        # VK API
        self.vk_token = os.getenv('VK_TOKEN')
        
        # Instagram Basic Display API (opcjonalne)
        self.instagram_access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        
        # TikTok API (nie wymaga klucza, ale może być potrzebny dla niektórych funkcji)
        self.tiktok_api_key = os.getenv('TIKTOK_API_KEY')
    
    def get_config_status(self):
        """Zwraca status konfiguracji"""
        status = {
            'YouTube': '✅ Dostępny' if self.youtube_api_key else '❌ Brak API key',
            'VK': '✅ Dostępny' if self.vk_token else '⚠️ Tylko scraping',
            'Instagram': '✅ instaloader' if True else '❌ Niedostępny',
            'TikTok': '✅ TikTokApi' if True else '❌ Niedostępny',
            'Likee': '⚠️ Tylko scraping'
        }
        return status
    
    def print_setup_instructions(self):
        """Wyświetla instrukcje konfiguracji"""
        print("🔧 KONFIGURACJA API KEYS")
        print("=" * 50)
        print()
        
        print("📺 YouTube Data API v3:")
        print("1. Idź do: https://console.developers.google.com/")
        print("2. Utwórz projekt lub wybierz istniejący")
        print("3. Włącz YouTube Data API v3")
        print("4. Utwórz klucz API")
        print("5. Dodaj do .env: YOUTUBE_API_KEY=your_key_here")
        print()
        
        print("🔵 VK API:")
        print("1. Idź do: https://vk.com/apps?act=manage")
        print("2. Utwórz aplikację")
        print("3. Uzyskaj access token")
        print("4. Dodaj do .env: VK_TOKEN=your_token_here")
        print()
        
        print("📸 Instagram:")
        print("Używa instaloader - nie wymaga API key")
        print()
        
        print("🎵 TikTok:")
        print("Używa TikTokApi - nie wymaga API key")
        print()
        
        print("💜 Likee:")
        print("Używa scraping - nie wymaga API key")
        print()
        
        print("📝 Przykład pliku .env:")
        print("YOUTUBE_API_KEY=your_youtube_api_key_here")
        print("VK_TOKEN=your_vk_token_here")
        print("INSTAGRAM_ACCESS_TOKEN=your_instagram_token_here")
        print("TIKTOK_API_KEY=your_tiktok_key_here")

def main():
    """Główna funkcja"""
    config = SocialMediaConfig()
    
    print("📊 STATUS KONFIGURACJI SOCIAL MEDIA")
    print("=" * 50)
    
    status = config.get_config_status()
    for platform, status_text in status.items():
        print(f"{platform}: {status_text}")
    
    print()
    config.print_setup_instructions()

if __name__ == "__main__":
    main()




