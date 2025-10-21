#!/usr/bin/env python3
"""
Test YouTube API
"""

import os
import requests
from dotenv import load_dotenv

# Ładujemy zmienne środowiskowe
load_dotenv()

def test_youtube_api():
    """Test YouTube API"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ Brak YouTube API key")
        return
    
    print(f"✅ YouTube API key: {api_key[:10]}...")
    
    # Test 1: Szukamy kanału po nazwie
    print("\n🔍 Test 1: Szukanie kanału 'raachel_fb'")
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': 'raachel_fb',
        'type': 'channel',
        'key': api_key
    }
    
    response = requests.get(search_url, params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Znalezione kanały: {len(data.get('items', []))}")
        for item in data.get('items', [])[:3]:
            print(f"  - {item['snippet']['title']} ({item['snippet']['channelId']})")
    else:
        print(f"Błąd: {response.text}")
    
    # Test 2: Szukamy kanału po @username
    print("\n🔍 Test 2: Szukanie kanału '@raachel_fb'")
    params = {
        'part': 'snippet',
        'q': '@raachel_fb',
        'type': 'channel',
        'key': api_key
    }
    
    response = requests.get(search_url, params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Znalezione kanały: {len(data.get('items', []))}")
        for item in data.get('items', [])[:3]:
            print(f"  - {item['snippet']['title']} ({item['snippet']['channelId']})")
    else:
        print(f"Błąd: {response.text}")
    
    # Test 3: Sprawdzamy czy kanał istnieje
    print("\n🔍 Test 3: Sprawdzanie kanału 'raachel_fb'")
    channels_url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        'part': 'snippet',
        'forUsername': 'raachel_fb',
        'key': api_key
    }
    
    response = requests.get(channels_url, params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Znalezione kanały: {len(data.get('items', []))}")
        for item in data.get('items', []):
            print(f"  - {item['snippet']['title']} ({item['id']})")
    else:
        print(f"Błąd: {response.text}")

if __name__ == "__main__":
    test_youtube_api()




