#!/usr/bin/env python3
"""
Test pobierania rzeczywistych danych z YouTube Shorts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_social_stats import AdvancedSocialStatsChecker
import json

def test_youtube_short_real_data():
    """Test pobierania rzeczywistych danych z YouTube Shorts"""
    print("🧪 Test pobierania rzeczywistych danych z YouTube Shorts")
    
    # Tworzymy checker
    checker = AdvancedSocialStatsChecker()
    
    # Test URL z YouTube Shorts
    youtube_url = "https://www.youtube.com/shorts/Fjro6Daa0VM"
    
    print(f"YouTube URL: {youtube_url}")
    
    # Wyciągamy video ID
    video_id = checker._extract_youtube_video_id(youtube_url)
    print(f"YouTube Video ID: {video_id}")
    
    # Test 1: Przez API (jeśli dostępne)
    print("\n📊 Test przez YouTube API:")
    if checker.api_keys.get('youtube'):
        print("✅ YouTube API key dostępny")
        api_result = checker._get_youtube_short_by_id(video_id)
        if api_result:
            print(f"  📹 Tytuł: {api_result.get('title', 'N/A')}")
            print(f"  👀 Wyświetlenia: {api_result.get('views', 'N/A')}")
            print(f"  📅 Data: {api_result.get('published_at', 'N/A')}")
            print(f"  🔗 URL: {api_result.get('url', 'N/A')}")
        else:
            print("  ❌ Brak danych z API")
    else:
        print("❌ Brak YouTube API key")
    
    # Test 2: Przez scraping
    print("\n📊 Test przez scraping:")
    scraping_result = checker._get_youtube_short_scraping(youtube_url)
    if scraping_result:
        print(f"  📹 Tytuł: {scraping_result.get('title', 'N/A')}")
        print(f"  👀 Wyświetlenia: {scraping_result.get('views', 'N/A')}")
        print(f"  📅 Data: {scraping_result.get('published_at', 'N/A')}")
        print(f"  🔗 URL: {scraping_result.get('url', 'N/A')}")
    else:
        print("  ❌ Brak danych z scraping")
    
    # Test 3: Pełna funkcja
    print("\n📊 Test pełnej funkcji get_youtube_short_data:")
    full_result = checker.get_youtube_short_data(youtube_url)
    if 'error' in full_result:
        print(f"❌ Błąd: {full_result['error']}")
    else:
        print(f"✅ Sukces: {full_result.get('method', 'Unknown method')}")
        
        if 'shorts' in full_result:
            for short in full_result['shorts']:
                print(f"  📹 Tytuł: {short.get('title', 'N/A')}")
                print(f"  👀 Wyświetlenia: {short.get('views', 'N/A')}")
                print(f"  📅 Data: {short.get('published_at', 'N/A')}")
                print(f"  🔗 URL: {short.get('url', 'N/A')}")
    
    return full_result

def test_youtube_api_direct():
    """Test bezpośredniego wywołania YouTube API"""
    print("\n🔍 Test bezpośredniego YouTube API")
    
    checker = AdvancedSocialStatsChecker()
    video_id = "Fjro6Daa0VM"
    
    if checker.api_keys.get('youtube'):
        print("✅ YouTube API key dostępny")
        
        # Test video.get API
        try:
            import requests
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'snippet,statistics,contentDetails',
                'id': video_id,
                'key': checker.api_keys['youtube']
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            print(f"API Response Status: {response.status_code}")
            print(f"API Response: {json.dumps(data, indent=2)}")
            
            if 'items' in data and data['items']:
                video = data['items'][0]
                snippet = video.get('snippet', {})
                statistics = video.get('statistics', {})
                
                print(f"\n📊 Dane z API:")
                print(f"  📹 Tytuł: {snippet.get('title', 'N/A')}")
                print(f"  👀 Wyświetlenia: {statistics.get('viewCount', 'N/A')}")
                print(f"  👍 Polubienia: {statistics.get('likeCount', 'N/A')}")
                print(f"  💬 Komentarze: {statistics.get('commentCount', 'N/A')}")
                print(f"  📅 Data publikacji: {snippet.get('publishedAt', 'N/A')}")
                print(f"  ⏱️ Długość: {video.get('contentDetails', {}).get('duration', 'N/A')}")
            else:
                print("❌ Brak danych w odpowiedzi API")
                
        except Exception as e:
            print(f"❌ Błąd API: {e}")
    else:
        print("❌ Brak YouTube API key")

def test_scraping_improvement():
    """Test ulepszonego scrapingu"""
    print("\n🔍 Test ulepszonego scrapingu")
    
    checker = AdvancedSocialStatsChecker()
    youtube_url = "https://www.youtube.com/shorts/Fjro6Daa0VM"
    
    try:
        response = checker._make_request(youtube_url)
        if response:
            content = response.text
            print(f"Response status: {response.status_code}")
            print(f"Content length: {len(content)}")
            
            # Szukamy danych w HTML
            import re
            
            # Szukamy view count w różnych miejscach
            view_patterns = [
                r'"viewCount":"(\d+)"',
                r'"view_count":"(\d+)"',
                r'"views":"(\d+)"',
                r'(\d+)\s*views',
                r'(\d+)\s*просмотров',
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
                r'var ytInitialData = ({.*?});',
                r'window\["ytInitialData"\] = ({.*?});',
                r'ytInitialData = ({.*?});'
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

if __name__ == "__main__":
    print("🚀 Uruchamianie testów YouTube Shorts")
    
    # Test 1: Pełna funkcja
    result1 = test_youtube_short_real_data()
    
    # Test 2: Bezpośrednie API
    test_youtube_api_direct()
    
    # Test 3: Ulepszony scraping
    test_scraping_improvement()
    
    print(f"\n📊 Podsumowanie:")
    if 'error' not in result1:
        print("✅ Funkcja działa, ale może potrzebować ulepszeń")
    else:
        print("❌ Funkcja ma problemy")
    
    print("\n💡 Rekomendacje:")
    print("1. Sprawdź czy YouTube API key jest poprawny")
    print("2. Ulepsz scraping żeby wyciągać rzeczywiste dane")
    print("3. Dodaj więcej fallback metod")
