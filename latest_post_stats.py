#!/usr/bin/env python3
"""
Skrypt do sprawdzania wyświetleń ostatniego postu na platformach społecznościowych
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from urllib.parse import urlparse
import instaloader
from TikTokApi import TikTokApi
import vk_api
from vk_api.exceptions import VkApiError

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LatestPostStatsChecker:
    """Checker wyświetleń ostatniego postu"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Inicjalizacja TikTokApi
        self.tiktok_api = None
        try:
            self.tiktok_api = TikTokApi()
            logger.info("TikTokApi zainicjalizowany")
        except Exception as e:
            logger.warning(f"Nie udało się zainicjalizować TikTokApi: {e}")
        
        # Inicjalizacja instaloader
        self.instaloader = instaloader.Instaloader()
        self.instaloader.context._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # VK API (jeśli mamy token)
        self.vk_session = None
        vk_token = os.getenv('VK_TOKEN')
        if vk_token:
            try:
                self.vk_session = vk_api.VkApi(token=vk_token)
                logger.info("VK API zainicjalizowany")
            except Exception as e:
                logger.warning(f"Nie udało się zainicjalizować VK API: {e}")
    
    def extract_username(self, url: str, platform: str) -> Optional[str]:
        """Wyciąga username z URL"""
        try:
            if platform == 'instagram':
                if 'instagram.com/' in url:
                    username = url.split('instagram.com/')[-1].split('/')[0].split('?')[0]
                    return username
            elif platform == 'youtube':
                if 'youtube.com/@' in url:
                    return url.split('@')[-1].split('/')[0]
                elif 'youtube.com/channel/' in url:
                    return url.split('channel/')[-1].split('/')[0]
            elif platform == 'tiktok':
                if 'tiktok.com/@' in url:
                    return url.split('@')[-1].split('/')[0]
            elif platform == 'vk':
                if 'vk.com/' in url:
                    return url.split('vk.com/')[-1].split('/')[0]
            elif platform == 'likee':
                if 'likee.video/p/' in url:
                    return url.split('p/')[-1].split('/')[0]
        except Exception as e:
            logger.error(f"Błąd wyciągania username z {url}: {e}")
        return None
    
    def check_instagram_latest_post(self, url: str) -> Dict[str, Any]:
        """Sprawdza wyświetlenia ostatniego postu na Instagram"""
        try:
            username = self.extract_username(url, 'instagram')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Sprawdzanie ostatniego postu Instagram: @{username}")
            
            # Pobieramy profil
            profile = instaloader.Profile.from_username(self.instaloader.context, username)
            
            # Pobieramy ostatni post
            posts = list(profile.get_posts())
            if not posts:
                return {
                    'platform': 'Instagram',
                    'username': username,
                    'error': 'Brak postów na profilu'
                }
            
            latest_post = posts[0]  # Najnowszy post
            
            return {
                'platform': 'Instagram',
                'username': username,
                'post_id': latest_post.shortcode,
                'post_url': f"https://www.instagram.com/p/{latest_post.shortcode}/",
                'likes': latest_post.likes,
                'comments': latest_post.comments,
                'views': getattr(latest_post, 'video_view_count', None),  # Dla video
                'is_video': latest_post.is_video,
                'caption': latest_post.caption[:100] + '...' if latest_post.caption and len(latest_post.caption) > 100 else latest_post.caption,
                'date': latest_post.date.strftime('%Y-%m-%d %H:%M:%S'),
                'method': 'instaloader'
            }
            
        except Exception as e:
            logger.error(f"Błąd Instagram: {e}")
            return {'error': f'Błąd Instagram: {str(e)}'}
    
    def check_tiktok_latest_post(self, url: str) -> Dict[str, Any]:
        """Sprawdza wyświetlenia ostatniego postu na TikTok"""
        try:
            username = self.extract_username(url, 'tiktok')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Sprawdzanie ostatniego postu TikTok: @{username}")
            
            if not self.tiktok_api:
                return {'error': 'TikTokApi nie jest dostępny'}
            
            # Pobieramy użytkownika
            user = self.tiktok_api.user(username=username)
            
            # Pobieramy ostatni post
            videos = user.videos(count=1)  # Tylko ostatni post
            if not videos:
                return {
                    'platform': 'TikTok',
                    'username': username,
                    'error': 'Brak postów na profilu'
                }
            
            latest_video = videos[0]
            
            return {
                'platform': 'TikTok',
                'username': username,
                'post_id': latest_video.id,
                'post_url': f"https://www.tiktok.com/@{username}/video/{latest_video.id}",
                'likes': latest_video.stats.digg_count,
                'comments': latest_video.stats.comment_count,
                'views': latest_video.stats.play_count,
                'shares': latest_video.stats.share_count,
                'caption': latest_video.desc[:100] + '...' if latest_video.desc and len(latest_video.desc) > 100 else latest_video.desc,
                'date': latest_video.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'method': 'TikTokApi'
            }
            
        except Exception as e:
            logger.error(f"Błąd TikTok: {e}")
            return {'error': f'Błąd TikTok: {str(e)}'}
    
    def check_youtube_latest_video(self, url: str) -> Dict[str, Any]:
        """Sprawdza wyświetlenia ostatniego wideo na YouTube"""
        try:
            api_key = os.getenv('YOUTUBE_API_KEY')
            if not api_key:
                return {'error': 'Brak YouTube API key'}
            
            # Wyciągamy channel ID lub username
            channel_id = self.extract_username(url, 'youtube')
            if not channel_id:
                return {'error': 'Nie można wyciągnąć channel ID z URL'}
            
            logger.info(f"Sprawdzanie ostatniego wideo YouTube: {channel_id}")
            
            # Jeśli to username (zaczyna się od @), szukamy channel ID
            if channel_id.startswith('@'):
                search_url = f"https://www.googleapis.com/youtube/v3/search"
                params = {
                    'part': 'snippet',
                    'q': channel_id,
                    'type': 'channel',
                    'key': api_key
                }
                response = self.session.get(search_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('items'):
                        channel_id = data['items'][0]['snippet']['channelId']
                    else:
                        return {'error': 'Nie znaleziono kanału YouTube'}
                else:
                    return {'error': f'Błąd YouTube API: {response.status_code}'}
            
            # Pobieramy ostatnie wideo z kanału
            search_url = f"https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'channelId': channel_id,
                'type': 'video',
                'order': 'date',
                'maxResults': 1,
                'key': api_key
            }
            
            response = self.session.get(search_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    video = data['items'][0]
                    video_id = video['id']['videoId']
                    
                    # Pobieramy statystyki wideo
                    stats_url = f"https://www.googleapis.com/youtube/v3/videos"
                    stats_params = {
                        'part': 'statistics,snippet',
                        'id': video_id,
                        'key': api_key
                    }
                    
                    stats_response = self.session.get(stats_url, params=stats_params)
                    if stats_response.status_code == 200:
                        stats_data = stats_response.json()
                        if stats_data.get('items'):
                            video_stats = stats_data['items'][0]
                            statistics = video_stats.get('statistics', {})
                            snippet = video_stats.get('snippet', {})
                            
                            return {
                                'platform': 'YouTube',
                                'channel_id': channel_id,
                                'video_id': video_id,
                                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                                'title': snippet.get('title', ''),
                                'views': int(statistics.get('viewCount', 0)),
                                'likes': int(statistics.get('likeCount', 0)),
                                'comments': int(statistics.get('commentCount', 0)),
                                'date': snippet.get('publishedAt', ''),
                                'method': 'YouTube Data API'
                            }
                        else:
                            return {'error': 'Nie znaleziono statystyk wideo'}
                    else:
                        return {'error': f'Błąd pobierania statystyk: {stats_response.status_code}'}
                else:
                    return {'error': 'Brak wideo na kanale'}
            else:
                return {'error': f'Błąd YouTube API: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Błąd YouTube: {e}")
            return {'error': f'Błąd YouTube: {str(e)}'}
    
    def check_vk_latest_post(self, url: str) -> Dict[str, Any]:
        """Sprawdza wyświetlenia ostatniego postu na VK"""
        try:
            username = self.extract_username(url, 'vk')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Sprawdzanie ostatniego postu VK: {username}")
            
            if self.vk_session:
                # Używamy VK API
                vk = self.vk_session.get_api()
                
                # Jeśli to ID (cyfry), używamy go bezpośrednio
                if username.isdigit():
                    user_id = username
                else:
                    # Szukamy ID użytkownika po username
                    try:
                        user_info = vk.users.get(user_ids=username)
                        if user_info:
                            user_id = user_info[0]['id']
                        else:
                            return {'error': 'Nie znaleziono użytkownika VK'}
                    except VkApiError as e:
                        return {'error': f'Błąd VK API: {e}'}
                
                # Pobieramy ostatni post
                posts = vk.wall.get(owner_id=user_id, count=1)
                
                if posts.get('items'):
                    post = posts['items'][0]
                    
                    return {
                        'platform': 'VK',
                        'username': username,
                        'user_id': user_id,
                        'post_id': post['id'],
                        'post_url': f"https://vk.com/wall{user_id}_{post['id']}",
                        'likes': post.get('likes', {}).get('count', 0),
                        'comments': post.get('comments', {}).get('count', 0),
                        'reposts': post.get('reposts', {}).get('count', 0),
                        'views': post.get('views', {}).get('count', 0),
                        'text': post.get('text', '')[:100] + '...' if post.get('text') and len(post.get('text', '')) > 100 else post.get('text', ''),
                        'date': datetime.fromtimestamp(post['date']).strftime('%Y-%m-%d %H:%M:%S'),
                        'method': 'VK API'
                    }
                else:
                    return {'error': 'Brak postów na profilu'}
            else:
                # Fallback - scraping
                return self._scrape_vk_latest_post(url)
                
        except Exception as e:
            logger.error(f"Błąd VK: {e}")
            return {'error': f'Błąd VK: {str(e)}'}
    
    def _scrape_vk_latest_post(self, url: str) -> Dict[str, Any]:
        """Fallback scraping dla VK"""
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return {
                    'platform': 'VK',
                    'username': self.extract_username(url, 'vk'),
                    'method': 'scraping',
                    'note': 'Podstawowe informacje z HTML'
                }
            else:
                return {'error': f'Błąd HTTP: {response.status_code}'}
        except Exception as e:
            return {'error': f'Błąd scraping VK: {str(e)}'}
    
    def check_likee_latest_post(self, url: str) -> Dict[str, Any]:
        """Sprawdza wyświetlenia ostatniego postu na Likee (scraping)"""
        try:
            username = self.extract_username(url, 'likee')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Sprawdzanie ostatniego postu Likee: {username}")
            
            # Likee nie ma oficjalnego API, więc używamy scraping
            response = self.session.get(url)
            if response.status_code == 200:
                return {
                    'platform': 'Likee',
                    'username': username,
                    'method': 'scraping',
                    'note': 'Podstawowe informacje z HTML'
                }
            else:
                return {'error': f'Błąd HTTP: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Błąd Likee: {e}")
            return {'error': f'Błąd Likee: {str(e)}'}
    
    def check_all_latest_posts(self, urls: Dict[str, str]) -> Dict[str, Any]:
        """Sprawdza wyświetlenia ostatnich postów na wszystkich platformach"""
        results = {}
        
        for platform, url in urls.items():
            logger.info(f"Sprawdzanie ostatniego postu {platform}: {url}")
            
            try:
                if platform.lower() == 'instagram':
                    results[platform] = self.check_instagram_latest_post(url)
                elif platform.lower() == 'youtube':
                    results[platform] = self.check_youtube_latest_video(url)
                elif platform.lower() == 'tiktok':
                    results[platform] = self.check_tiktok_latest_post(url)
                elif platform.lower() == 'vk':
                    results[platform] = self.check_vk_latest_post(url)
                elif platform.lower() == 'likee':
                    results[platform] = self.check_likee_latest_post(url)
                else:
                    results[platform] = {'error': f'Nieznana platforma: {platform}'}
                
                # Krótka pauza między requestami
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Błąd sprawdzania {platform}: {e}")
                results[platform] = {'error': str(e)}
        
        return results

def main():
    """Główna funkcja"""
    print("🔍 SPRAWDZANIE WYŚWIETLEŃ OSTATNIEGO POSTU")
    print("=" * 60)
    
    # URL-e do sprawdzenia
    urls = {
        'Instagram': 'https://www.instagram.com/raachel_fb',
        'YouTube': 'https://www.youtube.com/@raachel_fb',
        'TikTok': 'https://www.tiktok.com/@daniryb_fb',
        'VK': 'https://vk.com/raachel_fb',
        'Likee': 'https://l.likee.video/p/jSQPBE'
    }
    
    # Sprawdzamy czy mamy API keys
    print("📋 Sprawdzanie konfiguracji...")
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    vk_token = os.getenv('VK_TOKEN')
    
    if not youtube_key:
        print("⚠️ Brak YOUTUBE_API_KEY - YouTube będzie niedostępny")
    if not vk_token:
        print("⚠️ Brak VK_TOKEN - VK będzie używać scraping")
    
    print(f"✅ Instagram: instaloader")
    print(f"✅ TikTok: TikTokApi")
    print(f"✅ YouTube: {'API' if youtube_key else 'Niedostępny'}")
    print(f"✅ VK: {'API' if vk_token else 'Scraping'}")
    print(f"✅ Likee: Scraping")
    print()
    
    # Tworzymy checker
    checker = LatestPostStatsChecker()
    
    # Sprawdzamy wyświetlenia ostatnich postów
    print("📊 Sprawdzanie wyświetleń ostatnich postów...")
    results = checker.check_all_latest_posts(urls)
    
    # Wyświetlamy wyniki
    print("\n📈 WYNIKI OSTATNICH POSTÓW:")
    print("=" * 60)
    
    for platform, data in results.items():
        print(f"\n🔸 {platform}:")
        if 'error' in data:
            print(f"   ❌ {data['error']}")
        else:
            for key, value in data.items():
                if key not in ['platform', 'method']:
                    print(f"   📊 {key}: {value}")
            print(f"   🔧 Metoda: {data.get('method', 'Nieznana')}")
    
    # Zapisujemy wyniki do JSON
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'latest_posts_{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Wyniki zapisane do: {filename}")

if __name__ == "__main__":
    main()




