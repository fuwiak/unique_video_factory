#!/usr/bin/env python3
"""
Test pobierania rzeczywistych danych z VK Clips
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_social_stats import AdvancedSocialStatsChecker
import json

def test_vk_clip_real_data():
    """Test pobierania rzeczywistych danych z VK Clips"""
    print("🧪 Test pobierania rzeczywistych danych z VK Clips")
    
    # Tworzymy checker
    checker = AdvancedSocialStatsChecker()
    
    # Test URL z VK Clips
    vk_url = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129"
    
    print(f"VK URL: {vk_url}")
    
    # Wyciągamy ID
    owner_id = checker._extract_vk_owner_id(vk_url)
    video_id = checker._extract_vk_video_id(vk_url)
    
    print(f"Owner ID: {owner_id}")
    print(f"Video ID: {video_id}")
    
    # Test 1: Przez API (jeśli dostępne)
    print("\n📊 Test przez VK API:")
    if checker.api_keys.get('vk'):
        print("✅ VK API key dostępny")
        api_result = checker._get_vk_clip_by_id(owner_id, video_id)
        if api_result:
            print(f"  📹 Tytuł: {api_result.get('title', 'N/A')}")
            print(f"  👀 Wyświetlenia: {api_result.get('views', 'N/A')}")
            print(f"  👍 Polubienia: {api_result.get('likes', 'N/A')}")
            print(f"  💬 Komentarze: {api_result.get('comments', 'N/A')}")
            print(f"  📅 Data: {api_result.get('date', 'N/A')}")
            print(f"  🔗 URL: {api_result.get('url', 'N/A')}")
        else:
            print("  ❌ Brak danych z API")
    else:
        print("❌ Brak VK API key")
    
    # Test 2: Przez scraping
    print("\n📊 Test przez scraping:")
    scraping_result = checker._get_vk_clip_scraping(vk_url)
    if scraping_result:
        print(f"  📹 Tytuł: {scraping_result.get('title', 'N/A')}")
        print(f"  👀 Wyświetlenia: {scraping_result.get('views', 'N/A')}")
        print(f"  👍 Polubienia: {scraping_result.get('likes', 'N/A')}")
        print(f"  💬 Komentarze: {scraping_result.get('comments', 'N/A')}")
        print(f"  📅 Data: {scraping_result.get('date', 'N/A')}")
        print(f"  🔗 URL: {scraping_result.get('url', 'N/A')}")
    else:
        print("  ❌ Brak danych z scraping")
    
    # Test 3: Pełna funkcja
    print("\n📊 Test pełnej funkcji get_vk_clip_data:")
    full_result = checker.get_vk_clip_data(vk_url)
    if 'error' in full_result:
        print(f"❌ Błąd: {full_result['error']}")
    else:
        print(f"✅ Sukces: {full_result.get('method', 'Unknown method')}")
        
        if 'clips' in full_result:
            for clip in full_result['clips']:
                print(f"  📹 Tytuł: {clip.get('title', 'N/A')}")
                print(f"  👀 Wyświetlenia: {clip.get('views', 'N/A')}")
                print(f"  👍 Polubienia: {clip.get('likes', 'N/A')}")
                print(f"  💬 Komentarze: {clip.get('comments', 'N/A')}")
                print(f"  📅 Data: {clip.get('date', 'N/A')}")
                print(f"  🔗 URL: {clip.get('url', 'N/A')}")
    
    return full_result

def test_vk_api_direct():
    """Test bezpośredniego wywołania VK API"""
    print("\n🔍 Test bezpośredniego VK API")
    
    checker = AdvancedSocialStatsChecker()
    owner_id = "1069245351"
    video_id = "456239129"
    
    if checker.api_keys.get('vk'):
        print("✅ VK API key dostępny")
        
        # Test video.get API
        try:
            import requests
            url = "https://api.vk.com/method/video.get"
            params = {
                'videos': f"{owner_id}_{video_id}",
                'access_token': checker.api_keys['vk'],
                'v': '5.131'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            print(f"API Response Status: {response.status_code}")
            print(f"API Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if 'response' in data and 'items' in data['response'] and data['response']['items']:
                video = data['response']['items'][0]
                
                print(f"\n📊 Dane z VK API:")
                print(f"  📹 Tytuł: {video.get('title', 'N/A')}")
                print(f"  👀 Wyświetlenia: {video.get('views', 'N/A')}")
                print(f"  👍 Polubienia: {video.get('likes', {}).get('count', 'N/A') if isinstance(video.get('likes'), dict) else video.get('likes', 'N/A')}")
                print(f"  💬 Komentarze: {video.get('comments', 'N/A')}")
                print(f"  📅 Data: {video.get('date', 'N/A')}")
                print(f"  ⏱️ Długość: {video.get('duration', 'N/A')}")
            else:
                print("❌ Brak danych w odpowiedzi API")
                if 'error' in data:
                    print(f"❌ Błąd API: {data['error']}")
                
        except Exception as e:
            print(f"❌ Błąd API: {e}")
    else:
        print("❌ Brak VK API key")

def test_scraping_improvement():
    """Test ulepszonego scrapingu VK"""
    print("\n🔍 Test ulepszonego scrapingu VK")
    
    checker = AdvancedSocialStatsChecker()
    vk_url = "https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129"
    
    try:
        response = checker._make_request(vk_url)
        if response:
            content = response.text
            print(f"Response status: {response.status_code}")
            print(f"Content length: {len(content)}")
            
            # Szukamy danych w HTML
            import re
            
            # Szukamy view count w różnych miejscach
            view_patterns = [
                r'"views":(\d+)',
                r'"view_count":(\d+)',
                r'"views_count":(\d+)',
                r'(\d+)\s*просмотров',
                r'(\d+)\s*views',
                r'(\d+)\s*wyświetleń'
            ]
            
            for pattern in view_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    print(f"  Znaleziono views: {matches}")
                    break
            
            # Szukamy tytułu
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', content)
            if title_match:
                title = title_match.group(1)
                print(f"  Tytuł: {title}")
            
            # Szukamy JSON z danymi
            json_patterns = [
                r'window\.vkData\s*=\s*({.*?});',
                r'window\["vkData"\]\s*=\s*({.*?});',
                r'vkData\s*=\s*({.*?});'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                if matches:
                    print(f"  Znaleziono JSON data: {len(matches[0])} znaków")
                    try:
                        import json
                        data = json.loads(matches[0])
                        print(f"  JSON parsed successfully")
                        
                        # Szukamy view count w JSON
                        def find_views_in_json(obj, path=""):
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    if 'view' in key.lower() and isinstance(value, (str, int)):
                                        print(f"    Found views at {path}.{key}: {value}")
                                    find_views_in_json(value, f"{path}.{key}")
                            elif isinstance(obj, list):
                                for i, item in enumerate(obj):
                                    find_views_in_json(item, f"{path}[{i}]")
                        
                        find_views_in_json(data)
                        break
                    except json.JSONDecodeError:
                        print(f"  Failed to parse JSON")
                        continue
        else:
            print("❌ Nie można pobrać strony")
            
    except Exception as e:
        print(f"❌ Błąd scrapingu: {e}")

def test_vk_api_key():
    """Test czy VK API key jest dostępny"""
    print("\n🔑 Test VK API key")
    
    checker = AdvancedSocialStatsChecker()
    
    print(f"VK API key: {checker.api_keys.get('vk', 'BRAK')}")
    print(f"Wszystkie klucze: {list(checker.api_keys.keys())}")
    
    if checker.api_keys.get('vk'):
        print("✅ VK API key jest dostępny")
        return True
    else:
        print("❌ VK API key nie jest dostępny")
        return False

if __name__ == "__main__":
    print("🚀 Uruchamianie testów VK Clips")
    
    # Test 1: Sprawdzenie API key
    has_vk_key = test_vk_api_key()
    
    # Test 2: Pełna funkcja
    result1 = test_vk_clip_real_data()
    
    # Test 3: Bezpośrednie API
    test_vk_api_direct()
    
    # Test 4: Ulepszony scraping
    test_scraping_improvement()
    
    print(f"\n📊 Podsumowanie:")
    if 'error' not in result1:
        print("✅ Funkcja działa, ale może potrzebować ulepszeń")
    else:
        print("❌ Funkcja ma problemy")
    
    print(f"\n💡 Rekomendacje:")
    if not has_vk_key:
        print("1. Dodaj VK API key do .env")
        print("2. VK API jest bardziej niezawodne niż scraping")
    else:
        print("1. Sprawdź czy VK API key jest poprawny")
        print("2. Ulepsz scraping żeby wyciągać rzeczywiste dane")
    print("3. Dodaj więcej fallback metod")
