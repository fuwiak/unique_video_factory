#!/usr/bin/env python3
"""
Test pobierania danych VK clips przez wall.get API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_social_stats import AdvancedSocialStatsChecker
import requests
import json
from datetime import datetime

def test_vk_wall_get():
    """Test pobierania danych przez wall.get"""
    print("🧪 Test pobierania danych VK clips przez wall.get")
    
    checker = AdvancedSocialStatsChecker()
    
    if not checker.api_keys.get('vk'):
        print("❌ Brak VK API key")
        return
    
    access_token = checker.api_keys['vk']
    owner_id = "1069245351"
    target_video_id = "456239129"
    
    print(f"Owner ID: {owner_id}")
    print(f"Target Video ID: {target_video_id}")
    
    try:
        url = "https://api.vk.com/method/wall.get"
        params = {
            'access_token': access_token,
            'v': '5.131',
            'owner_id': owner_id,
            'count': 50,  # Pobierz więcej postów
            'extended': 1
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if 'error' in data:
            print(f"❌ Błąd API: {data['error']}")
            return
        
        if 'response' not in data or 'items' not in data['response']:
            print("❌ Brak danych w odpowiedzi")
            return
        
        items = data['response']['items']
        print(f"📊 Znaleziono {len(items)} postów")
        
        # Szukamy konkretnego video
        target_clip = None
        for item in items:
            if 'attachments' in item:
                for attachment in item['attachments']:
                    if attachment.get('type') == 'video':
                        video = attachment['video']
                        video_id = video.get('id')
                        
                        # Sprawdzamy czy to nasze video
                        if str(video_id) == target_video_id:
                            target_clip = {
                                'video': video,
                                'post': item
                            }
                            break
                
                if target_clip:
                    break
        
        if target_clip:
            print(f"\n✅ Znaleziono target clip!")
            video = target_clip['video']
            post = target_clip['post']
            
            print(f"📊 Dane z wall.get:")
            print(f"  📹 Tytuł: {video.get('title', 'N/A')}")
            print(f"  👀 Wyświetlenia: {video.get('views', 'N/A')}")
            print(f"  👍 Polubienia: {video.get('likes', {}).get('count', 'N/A') if isinstance(video.get('likes'), dict) else video.get('likes', 'N/A')}")
            print(f"  💬 Komentarze: {video.get('comments', 'N/A')}")
            print(f"  📅 Data posta: {post.get('date', 'N/A')}")
            print(f"  ⏱️ Długość: {video.get('duration', 'N/A')}")
            print(f"  🔗 URL: {video.get('player', 'N/A')}")
            
            # Konwertujemy timestamp na datę
            if post.get('date'):
                date_str = datetime.fromtimestamp(post['date']).strftime('%Y-%m-%d')
                print(f"  📅 Data (sformatowana): {date_str}")
            
            return {
                'title': video.get('title', ''),
                'views': video.get('views', 0),
                'likes': video.get('likes', {}).get('count', 0) if isinstance(video.get('likes'), dict) else video.get('likes', 0),
                'comments': video.get('comments', 0),
                'date': date_str if post.get('date') else '',
                'duration': video.get('duration', 0),
                'url': video.get('player', '')
            }
        else:
            print(f"❌ Nie znaleziono target clip {target_video_id}")
            
            # Pokaż wszystkie video które znaleźliśmy
            print(f"\n📊 Znalezione video:")
            video_count = 0
            for item in items:
                if 'attachments' in item:
                    for attachment in item['attachments']:
                        if attachment.get('type') == 'video':
                            video = attachment['video']
                            video_count += 1
                            print(f"  {video_count}. ID: {video.get('id')}, Tytuł: {video.get('title', 'N/A')[:50]}, Views: {video.get('views', 'N/A')}")
            
            return None
            
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return None

def test_users_get_stats():
    """Test pobierania statystyk użytkownika"""
    print(f"\n🧪 Test statystyk użytkownika")
    
    checker = AdvancedSocialStatsChecker()
    access_token = checker.api_keys['vk']
    owner_id = "1069245351"
    
    try:
        url = "https://api.vk.com/method/users.get"
        params = {
            'access_token': access_token,
            'v': '5.131',
            'user_ids': owner_id,
            'fields': 'counters'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'error' in data:
            print(f"❌ Błąd API: {data['error']}")
            return
        
        if 'response' in data and data['response']:
            user = data['response'][0]
            counters = user.get('counters', {})
            
            print(f"📊 Statystyki użytkownika:")
            print(f"  👤 Imię: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
            print(f"  📹 Clips: {counters.get('clips', 'N/A')}")
            print(f"  👀 Clips views: {counters.get('clips_views', 'N/A')}")
            print(f"  👍 Clips likes: {counters.get('clips_likes', 'N/A')}")
            print(f"  📸 Photos: {counters.get('photos', 'N/A')}")
            print(f"  👥 Followers: {counters.get('followers', 'N/A')}")
            
            return counters
            
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return None

def test_improved_vk_api():
    """Test ulepszonej funkcji VK API"""
    print(f"\n🧪 Test ulepszonej funkcji VK API")
    
    checker = AdvancedSocialStatsChecker()
    vk_url = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129"
    
    # Wyciągamy ID
    owner_id = checker._extract_vk_owner_id(vk_url)
    video_id = checker._extract_vk_video_id(vk_url)
    
    print(f"Owner ID: {owner_id}")
    print(f"Video ID: {video_id}")
    
    # Test wall.get
    wall_data = test_vk_wall_get()
    
    # Test users.get
    user_stats = test_users_get_stats()
    
    if wall_data:
        print(f"\n✅ SUKCES: Znaleziono dane przez wall.get!")
        print(f"   Wyświetlenia: {wall_data['views']}")
        print(f"   Tytuł: {wall_data['title']}")
        return wall_data
    else:
        print(f"\n❌ Brak danych z wall.get")
        return None

if __name__ == "__main__":
    print("🚀 Uruchamianie testów VK wall.get API")
    
    # Test ulepszonej funkcji
    result = test_improved_vk_api()
    
    print(f"\n📊 Podsumowanie:")
    if result:
        print("✅ VK API działa przez wall.get!")
        print("✅ Można pobrać rzeczywiste dane o clips")
        print("✅ Problem rozwiązany!")
    else:
        print("❌ Nadal problem z pobieraniem danych")
    
    print(f"\n💡 Następne kroki:")
    print("1. Zaktualizuj _get_vk_clip_by_id() żeby używała wall.get")
    print("2. Dodaj fallback na users.get dla statystyk")
    print("3. Testuj w Telegram bot")
