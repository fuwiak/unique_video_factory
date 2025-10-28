#!/usr/bin/env python3
"""
Test różnych metod VK API żeby znaleźć dostępne metody dla clips
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_social_stats import AdvancedSocialStatsChecker
import requests
import json

def test_vk_api_methods():
    """Test różnych metod VK API"""
    print("🧪 Test różnych metod VK API")
    
    checker = AdvancedSocialStatsChecker()
    
    if not checker.api_keys.get('vk'):
        print("❌ Brak VK API key")
        return
    
    access_token = checker.api_keys['vk']
    base_url = "https://api.vk.com/method"
    
    # Lista metod do przetestowania
    methods_to_test = [
        # Video related methods
        "video.get",
        "video.getById", 
        "video.getUserVideos",
        "video.search",
        "video.getComments",
        
        # Wall/Posts methods
        "wall.get",
        "wall.getById",
        "wall.search",
        
        # User methods
        "users.get",
        "users.getFollowers",
        "users.getSubscriptions",
        
        # Groups methods
        "groups.get",
        "groups.getById",
        
        # Newsfeed methods
        "newsfeed.get",
        "newsfeed.search",
        
        # Other methods
        "execute",
        "utils.resolveScreenName"
    ]
    
    print(f"🔍 Testowanie {len(methods_to_test)} metod VK API...")
    
    available_methods = []
    
    for method in methods_to_test:
        try:
            url = f"{base_url}/{method}"
            
            # Różne parametry dla różnych metod
            if method == "video.get":
                params = {
                    'access_token': access_token,
                    'v': '5.131',
                    'count': 1
                }
            elif method == "video.getById":
                params = {
                    'access_token': access_token,
                    'v': '5.131',
                    'videos': '1069245351_456239129'
                }
            elif method == "users.get":
                params = {
                    'access_token': access_token,
                    'v': '5.131',
                    'user_ids': '1069245351'
                }
            elif method == "utils.resolveScreenName":
                params = {
                    'access_token': access_token,
                    'v': '5.131',
                    'screen_name': 'id1069245351'
                }
            else:
                params = {
                    'access_token': access_token,
                    'v': '5.131'
                }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if 'error' in data:
                error_code = data['error'].get('error_code', 'Unknown')
                error_msg = data['error'].get('error_msg', 'Unknown error')
                print(f"  ❌ {method}: {error_code} - {error_msg}")
            else:
                print(f"  ✅ {method}: DOSTĘPNA")
                available_methods.append(method)
                
        except Exception as e:
            print(f"  ❌ {method}: Exception - {e}")
    
    print(f"\n📊 Dostępne metody: {len(available_methods)}")
    for method in available_methods:
        print(f"  ✅ {method}")
    
    return available_methods

def test_available_methods(available_methods):
    """Test dostępnych metod z konkretnymi danymi"""
    print(f"\n🧪 Test dostępnych metod z konkretnymi danymi")
    
    checker = AdvancedSocialStatsChecker()
    access_token = checker.api_keys['vk']
    base_url = "https://api.vk.com/method"
    
    owner_id = "1069245351"
    video_id = "456239129"
    
    for method in available_methods:
        print(f"\n📊 Test {method}:")
        
        try:
            url = f"{base_url}/{method}"
            
            if method == "video.getById":
                params = {
                    'access_token': access_token,
                    'v': '5.131',
                    'videos': f"{owner_id}_{video_id}"
                }
            elif method == "users.get":
                params = {
                    'access_token': access_token,
                    'v': '5.131',
                    'user_ids': owner_id,
                    'fields': 'counters'
                }
            elif method == "utils.resolveScreenName":
                params = {
                    'access_token': access_token,
                    'v': '5.131',
                    'screen_name': f"id{owner_id}"
                }
            elif method == "wall.get":
                params = {
                    'access_token': access_token,
                    'v': '5.131',
                    'owner_id': owner_id,
                    'count': 5
                }
            elif method == "wall.getById":
                params = {
                    'access_token': access_token,
                    'v': '5.131',
                    'posts': f"{owner_id}_{video_id}"
                }
            else:
                params = {
                    'access_token': access_token,
                    'v': '5.131'
                }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'error' in data:
                error_code = data['error'].get('error_code', 'Unknown')
                error_msg = data['error'].get('error_msg', 'Unknown error')
                print(f"  ❌ Błąd: {error_code} - {error_msg}")
            else:
                print(f"  ✅ Sukces!")
                print(f"  📊 Odpowiedź: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
                
                # Sprawdzamy czy są dane o video/clips
                if 'response' in data:
                    response_data = data['response']
                    if isinstance(response_data, dict):
                        if 'items' in response_data:
                            items = response_data['items']
                            if items and len(items) > 0:
                                print(f"  📹 Znaleziono {len(items)} elementów")
                                first_item = items[0]
                                if 'views' in first_item:
                                    print(f"  👀 Views: {first_item['views']}")
                                if 'title' in first_item:
                                    print(f"  📝 Tytuł: {first_item['title']}")
                                if 'date' in first_item:
                                    print(f"  📅 Data: {first_item['date']}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")

def test_execute_method():
    """Test metody execute - może pozwolić na bardziej zaawansowane zapytania"""
    print(f"\n🧪 Test metody execute")
    
    checker = AdvancedSocialStatsChecker()
    access_token = checker.api_keys['vk']
    
    # Próbujemy różnych kodów execute
    execute_codes = [
        # Kod 1: Pobierz informacje o użytkowniku
        """
        return API.users.get({
            "user_ids": "1069245351",
            "fields": "counters"
        });
        """,
        
        # Kod 2: Pobierz wall użytkownika
        """
        return API.wall.get({
            "owner_id": 1069245351,
            "count": 10
        });
        """,
        
        # Kod 3: Pobierz video użytkownika
        """
        return API.video.get({
            "owner_id": 1069245351,
            "count": 10
        });
        """,
        
        # Kod 4: Pobierz informacje o konkretnym video
        """
        return API.video.getById({
            "videos": "1069245351_456239129"
        });
        """
    ]
    
    for i, code in enumerate(execute_codes, 1):
        print(f"\n📊 Test execute kod {i}:")
        
        try:
            url = "https://api.vk.com/method/execute"
            params = {
                'access_token': access_token,
                'v': '5.131',
                'code': code
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'error' in data:
                error_code = data['error'].get('error_code', 'Unknown')
                error_msg = data['error'].get('error_msg', 'Unknown error')
                print(f"  ❌ Błąd: {error_code} - {error_msg}")
            else:
                print(f"  ✅ Sukces!")
                print(f"  📊 Odpowiedź: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Uruchamianie testów metod VK API")
    
    # Test 1: Sprawdzenie dostępnych metod
    available_methods = test_vk_api_methods()
    
    # Test 2: Test dostępnych metod z konkretnymi danymi
    if available_methods:
        test_available_methods(available_methods)
    
    # Test 3: Test metody execute
    test_execute_method()
    
    print(f"\n💡 Rekomendacje:")
    print("1. Sprawdź które metody zwracają dane o video/clips")
    print("2. Użyj dostępnych metod zamiast video.get")
    print("3. Rozważ użycie metody execute dla bardziej zaawansowanych zapytań")
    print("4. Jeśli API nie działa, ulepsz scraping")
