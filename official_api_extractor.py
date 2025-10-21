#!/usr/bin/env python3
"""
Oficjalny ekstraktor wyświetleń używający VK API i YouTube Data API
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from urllib.parse import urlparse
import vk_api
from vk_api.exceptions import VkApiError
from dotenv import load_dotenv
from google_sheets_integration import GoogleSheetsIntegration

# Ładujemy zmienne środowiskowe z .env
load_dotenv()

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OfficialAPIExtractor:
    """Oficjalny ekstraktor wyświetleń używający API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Inicjalizacja VK API
        self.vk_session = None
        vk_token = os.getenv('VK_TOKEN')
        if vk_token:
            try:
                self.vk_session = vk_api.VkApi(token=vk_token)
                logger.info("VK API zainicjalizowany")
            except Exception as e:
                logger.warning(f"Nie udało się zainicjalizować VK API: {e}")
        
        # YouTube API key
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        if self.youtube_api_key:
            logger.info("YouTube API key załadowany")
        else:
            logger.warning("Brak YouTube API key")
        
        # Inicjalizacja Google Sheets
        self.google_sheets = GoogleSheetsIntegration()
    
    def extract_vk_clips_views(self, clips_url: str) -> Dict[str, Any]:
        """Ekstraktuje wyświetlenia z VK Clips używając VK API"""
        try:
            if not self.vk_session:
                return {'error': 'VK API nie jest dostępny'}
            
            logger.info(f"Ekstraktowanie wyświetleń VK Clips: {clips_url}")
            
            # Wyciągamy username z URL
            if '/clips/' in clips_url:
                username = clips_url.split('/clips/')[-1].split('/')[0]
            else:
                return {'error': 'Nieprawidłowy URL VK Clips'}
            
            vk = self.vk_session.get_api()
            
            # Szukamy użytkownika po username
            try:
                user_info = vk.users.get(user_ids=username, fields='counters')
                if not user_info:
                    return {'error': 'Nie znaleziono użytkownika VK'}
                
                user = user_info[0]
                user_id = user['id']
                
                # Pobieramy posty użytkownika (ostatnie 10)
                posts = vk.wall.get(owner_id=user_id, count=10, filter='owner')
                
                clips_data = {
                    'platform': 'VK Clips',
                    'username': username,
                    'user_id': user_id,
                    'user_name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                    'method': 'VK API',
                    'clips': []
                }
                
                if posts.get('items'):
                    for post in posts['items']:
                        # Sprawdzamy czy to clip (ma video)
                        if post.get('attachments'):
                            for attachment in post['attachments']:
                                if attachment['type'] == 'video':
                                    video = attachment['video']
                                    clip_info = {
                                        'post_id': post['id'],
                                        'video_id': video.get('id'),
                                        'title': video.get('title', ''),
                                        'description': video.get('description', ''),
                                        'views': video.get('views', 0),
                                        'duration': video.get('duration', 0),
                                        'date': datetime.fromtimestamp(post['date']).strftime('%Y-%m-%d %H:%M:%S'),
                                        'likes': post.get('likes', {}).get('count', 0),
                                        'comments': post.get('comments', {}).get('count', 0),
                                        'reposts': post.get('reposts', {}).get('count', 0)
                                    }
                                    clips_data['clips'].append(clip_info)
                
                # Sortujemy po dacie (najnowsze pierwsze)
                clips_data['clips'].sort(key=lambda x: x['date'], reverse=True)
                
                # Dodajemy statystyki
                total_views = sum(clip['views'] for clip in clips_data['clips'])
                clips_data['total_views'] = total_views
                clips_data['clips_count'] = len(clips_data['clips'])
                
                return clips_data
                
            except VkApiError as e:
                return {'error': f'Błąd VK API: {e}'}
                
        except Exception as e:
            logger.error(f"Błąd VK Clips: {e}")
            return {'error': f'Błąd VK Clips: {str(e)}'}
    
    def extract_youtube_views(self, channel_url: str) -> Dict[str, Any]:
        """Ekstraktuje wyświetlenia z YouTube używając YouTube Data API"""
        try:
            if not self.youtube_api_key:
                return {'error': 'Brak YouTube API key'}
            
            logger.info(f"Ekstraktowanie wyświetleń YouTube: {channel_url}")
            
            # Wyciągamy username z URL
            if '@' in channel_url:
                username = channel_url.split('@')[-1].split('/')[0]
            else:
                return {'error': 'Nieprawidłowy URL YouTube'}
            
            # Szukamy kanału po username
            search_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': username,
                'type': 'channel',
                'key': self.youtube_api_key
            }
            
            response = self.session.get(search_url, params=params)
            if response.status_code != 200:
                return {'error': f'Błąd YouTube API: {response.status_code}'}
            
            data = response.json()
            if not data.get('items'):
                return {'error': 'Nie znaleziono kanału YouTube'}
            
            channel_id = data['items'][0]['snippet']['channelId']
            channel_title = data['items'][0]['snippet']['title']
            
            # Pobieramy ostatnie wideo z kanału
            search_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'channelId': channel_id,
                'type': 'video',
                'order': 'date',
                'maxResults': 10,
                'key': self.youtube_api_key
            }
            
            response = self.session.get(search_url, params=params)
            if response.status_code != 200:
                return {'error': f'Błąd pobierania wideo: {response.status_code}'}
            
            videos_data = response.json()
            if not videos_data.get('items'):
                return {'error': 'Brak wideo na kanale'}
            
            # Pobieramy statystyki dla każdego wideo
            video_ids = [video['id']['videoId'] for video in videos_data['items']]
            
            stats_url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'statistics,snippet',
                'id': ','.join(video_ids),
                'key': self.youtube_api_key
            }
            
            stats_response = self.session.get(stats_url, params=params)
            if stats_response.status_code != 200:
                return {'error': f'Błąd pobierania statystyk: {stats_response.status_code}'}
            
            stats_data = stats_response.json()
            
            videos_info = {
                'platform': 'YouTube',
                'channel_id': channel_id,
                'channel_title': channel_title,
                'username': username,
                'method': 'YouTube Data API',
                'videos': []
            }
            
            for video in stats_data.get('items', []):
                statistics = video.get('statistics', {})
                snippet = video.get('snippet', {})
                
                video_info = {
                    'video_id': video['id'],
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') and len(snippet.get('description', '')) > 200 else snippet.get('description', ''),
                    'views': int(statistics.get('viewCount', 0)),
                    'likes': int(statistics.get('likeCount', 0)),
                    'comments': int(statistics.get('commentCount', 0)),
                    'date': snippet.get('publishedAt', ''),
                    'duration': snippet.get('duration', ''),
                    'url': f"https://www.youtube.com/watch?v={video['id']}"
                }
                videos_info['videos'].append(video_info)
            
            # Sortujemy po dacie (najnowsze pierwsze)
            videos_info['videos'].sort(key=lambda x: x['date'], reverse=True)
            
            # Dodajemy statystyki
            total_views = sum(video['views'] for video in videos_info['videos'])
            videos_info['total_views'] = total_views
            videos_info['videos_count'] = len(videos_info['videos'])
            
            return videos_info
            
        except Exception as e:
            logger.error(f"Błąd YouTube: {e}")
            return {'error': f'Błąd YouTube: {str(e)}'}
    
    def extract_all_views(self, urls: Dict[str, str]) -> Dict[str, Any]:
        """Ekstraktuje wyświetlenia ze wszystkich platform"""
        results = {}
        
        for platform, url in urls.items():
            logger.info(f"Ekstraktowanie wyświetleń {platform}: {url}")
            
            try:
                if platform.lower() == 'vk_clips':
                    results[platform] = self.extract_vk_clips_views(url)
                elif platform.lower() == 'youtube':
                    results[platform] = self.extract_youtube_views(url)
                else:
                    results[platform] = {'error': f'Nieznana platforma: {platform}'}
                
                # Pauza między requestami
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Błąd ekstraktowania {platform}: {e}")
                results[platform] = {'error': str(e)}
        
        return results

def main():
    """Główna funkcja"""
    print("🔍 OFICJALNY EKSTRAKTOR WYŚWIETLEŃ (VK API + YouTube API)")
    print("=" * 70)
    
    # URL-e do sprawdzenia
    urls = {
        'VK_Clips': 'https://vk.com/clips/raachel_fb',
        'YouTube': 'https://www.youtube.com/@raachel_fb'
    }
    
    print("📋 Używamy oficjalnych API:")
    print("✅ VK API - dla VK Clips")
    print("✅ YouTube Data API - dla YouTube")
    print()
    
    # Tworzymy ekstraktor
    extractor = OfficialAPIExtractor()
    
    # Ekstraktujemy wyświetlenia
    print("📊 Ekstraktowanie wyświetleń...")
    results = extractor.extract_all_views(urls)
    
    # Wyświetlamy wyniki
    print("\n📈 WYNIKI EKSTRAKCJI WYŚWIETLEŃ:")
    print("=" * 70)
    
    for platform, data in results.items():
        print(f"\n🔸 {platform}:")
        if 'error' in data:
            print(f"   ❌ {data['error']}")
        else:
            for key, value in data.items():
                if key not in ['platform', 'method', 'clips', 'videos']:
                    print(f"   📊 {key}: {value}")
            
            # Wyświetlamy szczegóły clips/videos
            if 'clips' in data and data['clips']:
                print(f"   🎬 Ostatnie {min(3, len(data['clips']))} clips:")
                for i, clip in enumerate(data['clips'][:3]):
                    print(f"      {i+1}. {clip['title'][:50]}... - {clip['views']} wyświetleń")
            
            if 'videos' in data and data['videos']:
                print(f"   🎥 Ostatnie {min(3, len(data['videos']))} wideo:")
                for i, video in enumerate(data['videos'][:3]):
                    print(f"      {i+1}. {video['title'][:50]}... - {video['views']} wyświetleń")
            
            print(f"   🔧 Metoda: {data.get('method', 'Nieznana')}")
    
    # Zapisujemy wyniki do JSON
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'official_api_extraction_{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Wyniki zapisane do: {filename}")
    
    # Zapisujemy do Google Sheets
    print("\n📊 Zapisujemy do Google Sheets...")
    try:
        if extractor.google_sheets.save_to_sheets(results):
            print("✅ Dane zapisane do Google Sheets!")
        else:
            print("❌ Błąd zapisywania do Google Sheets")
    except Exception as e:
        print(f"❌ Błąd Google Sheets: {e}")
        print("💡 Sprawdź czy masz plik google_credentials.json")

if __name__ == "__main__":
    main()
