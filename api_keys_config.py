#!/usr/bin/env python3
"""
Konfiguracja API keys dla różnych platform społecznościowych
"""

# Dodaj swoje API keys tutaj
API_KEYS = {
    # YouTube Data API v3
    # Pobierz z: https://console.developers.google.com/
    'youtube': None,  # 'YOUR_YOUTUBE_API_KEY'
    
    # Instagram Basic Display API
    # Pobierz z: https://developers.facebook.com/
    'instagram': None,  # 'YOUR_INSTAGRAM_ACCESS_TOKEN'
    
    # TikTok Research API
    # Pobierz z: https://developers.tiktok.com/
    'tiktok': None,  # 'YOUR_TIKTOK_ACCESS_TOKEN'
    
    # VK API
    # Pobierz z: https://vk.com/apps?act=manage
    'vk': None,  # 'YOUR_VK_ACCESS_TOKEN'
    
    # Likee API (jeśli dostępne)
    'likee': None,  # 'YOUR_LIKEE_ACCESS_TOKEN'
}

# Instrukcje uzyskania API keys:

YOUTUBE_API_INSTRUCTIONS = """
YouTube Data API v3:
1. Idź do: https://console.developers.google.com/
2. Utwórz nowy projekt lub wybierz istniejący
3. Włącz YouTube Data API v3
4. Utwórz credentials (API key)
5. Skopiuj klucz i wklej do API_KEYS['youtube']
"""

INSTAGRAM_API_INSTRUCTIONS = """
Instagram Basic Display API:
1. Idź do: https://developers.facebook.com/
2. Utwórz nową aplikację
3. Dodaj Instagram Basic Display
4. Skonfiguruj OAuth
5. Uzyskaj access token
6. Wklej do API_KEYS['instagram']
"""

TIKTOK_API_INSTRUCTIONS = """
TikTok Research API:
1. Idź do: https://developers.tiktok.com/
2. Utwórz konto dewelopera
3. Złóż wniosek o dostęp do Research API
4. Po zatwierdzeniu uzyskaj access token
5. Wklej do API_KEYS['tiktok']
"""

VK_API_INSTRUCTIONS = """
VK API:
1. Idź do: https://vk.com/apps?act=manage
2. Utwórz nową aplikację
3. Skonfiguruj uprawnienia
4. Uzyskaj access token
5. Wklej do API_KEYS['vk']
"""

def get_api_keys():
    """Zwraca skonfigurowane API keys z .env"""
    import os
    from dotenv import load_dotenv
    
    # Ładujemy zmienne środowiskowe
    load_dotenv()
    
    # Zwracamy klucze z .env
    return {
        'youtube': os.getenv('YOUTUBE_API_KEY'),
        'instagram': os.getenv('INSTAGRAM_ACCESS_TOKEN'),
        'tiktok': os.getenv('TIKTOK_ACCESS_TOKEN'),
        'vk': os.getenv('VK_TOKEN'),  # Zmieniono z VK_ACCESS_TOKEN na VK_TOKEN
        'likee': os.getenv('LIKEE_ACCESS_TOKEN')
    }

def print_instructions():
    """Wyświetla instrukcje uzyskania API keys"""
    print("🔑 INSTRUKCJE UZYSKANIA API KEYS:")
    print("=" * 50)
    print(YOUTUBE_API_INSTRUCTIONS)
    print(INSTAGRAM_API_INSTRUCTIONS)
    print(TIKTOK_API_INSTRUCTIONS)
    print(VK_API_INSTRUCTIONS)
    print("\n💡 TIP: Bez API keys skrypt użyje fallbacków (scraping)")
    print("   Ale API jest bardziej niezawodne i szybsze!")

if __name__ == "__main__":
    print_instructions()




