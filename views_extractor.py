#!/usr/bin/env python3
"""
Ekstraktor wyświetleń z platform społecznościowych
Próbuje wyciągnąć konkretne liczby wyświetleń
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from urllib.parse import urlparse
import re
from dotenv import load_dotenv

# Ładujemy zmienne środowiskowe z .env
load_dotenv()

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ViewsExtractor:
    """Ekstraktor wyświetleń z platform społecznościowych"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
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
    
    def extract_instagram_views(self, url: str) -> Dict[str, Any]:
        """Ekstraktuje wyświetlenia z Instagram"""
        try:
            username = self.extract_username(url, 'instagram')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Ekstraktowanie wyświetleń Instagram: @{username}")
            
            # Próbujemy pobrać stronę profilu
            profile_url = f"https://www.instagram.com/{username}/"
            response = self.session.get(profile_url)
            
            if response.status_code == 200:
                content = response.text
                
                # Szukamy informacji o wyświetleniach
                views_info = {
                    'platform': 'Instagram',
                    'username': username,
                    'profile_url': profile_url,
                    'method': 'scraping'
                }
                
                # Szukamy liczb w tekście (podstawowe podejście)
                numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?[KMB]?\b', content)
                if numbers:
                    views_info['found_numbers'] = numbers[:10]  # Pierwsze 10 liczb
                
                # Szukamy konkretnych wzorców
                view_patterns = [
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*views?',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*wyświetleń',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*likes?',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*polubień'
                ]
                
                for pattern in view_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        views_info[f'pattern_{pattern}'] = matches
                
                return views_info
            else:
                return {'error': f'Błąd HTTP: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Błąd Instagram: {e}")
            return {'error': f'Błąd Instagram: {str(e)}'}
    
    def extract_youtube_views(self, url: str) -> Dict[str, Any]:
        """Ekstraktuje wyświetlenia z YouTube (API + scraping fallback)"""
        try:
            username = self.extract_username(url, 'youtube')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Ekstraktowanie wyświetleń YouTube: {username}")
            
            # Sprawdzamy czy mamy API key
            api_key = os.getenv('YOUTUBE_API_KEY')
            if api_key:
                return self._extract_youtube_with_api(username, api_key)
            else:
                return self._extract_youtube_with_scraping(username)
                
        except Exception as e:
            logger.error(f"Błąd YouTube: {e}")
            return {'error': f'Błąd YouTube: {str(e)}'}
    
    def _extract_youtube_with_api(self, username: str, api_key: str) -> Dict[str, Any]:
        """Ekstraktuje wyświetlenia z YouTube używając API"""
        try:
            # Zawsze szukamy channel ID, bo username może nie być channel ID
            search_url = f"https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': username if not username.startswith('@') else username[1:],  # Usuwamy @ jeśli jest
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
            logger.error(f"Błąd YouTube API: {e}")
            return {'error': f'Błąd YouTube API: {str(e)}'}
    
    def _extract_youtube_with_scraping(self, username: str) -> Dict[str, Any]:
        """Ekstraktuje wyświetlenia z YouTube używając scraping (fallback)"""
        try:
            # Próbujemy pobrać stronę kanału
            if username.startswith('@'):
                channel_url = f"https://www.youtube.com/{username}"
            else:
                channel_url = f"https://www.youtube.com/channel/{username}"
            
            response = self.session.get(channel_url)
            
            if response.status_code == 200:
                content = response.text
                
                # Szukamy informacji o wyświetleniach
                views_info = {
                    'platform': 'YouTube',
                    'username': username,
                    'channel_url': channel_url,
                    'method': 'scraping'
                }
                
                # Szukamy liczb w tekście
                numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?[KMB]?\b', content)
                if numbers:
                    views_info['found_numbers'] = numbers[:10]
                
                # Szukamy konkretnych wzorców YouTube
                view_patterns = [
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*views?',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*wyświetleń',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*subscribers?',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*subskrybentów'
                ]
                
                for pattern in view_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        views_info[f'pattern_{pattern}'] = matches
                
                return views_info
            else:
                return {'error': f'Błąd HTTP: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Błąd YouTube scraping: {e}")
            return {'error': f'Błąd YouTube scraping: {str(e)}'}
    
    def extract_tiktok_views(self, url: str) -> Dict[str, Any]:
        """Ekstraktuje wyświetlenia z TikTok"""
        try:
            username = self.extract_username(url, 'tiktok')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Ekstraktowanie wyświetleń TikTok: @{username}")
            
            # Próbujemy pobrać stronę profilu
            profile_url = f"https://www.tiktok.com/@{username}"
            response = self.session.get(profile_url)
            
            if response.status_code == 200:
                content = response.text
                
                # Szukamy informacji o wyświetleniach
                views_info = {
                    'platform': 'TikTok',
                    'username': username,
                    'profile_url': profile_url,
                    'method': 'scraping'
                }
                
                # Szukamy liczb w tekście
                numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?[KMB]?\b', content)
                if numbers:
                    views_info['found_numbers'] = numbers[:10]
                
                # Szukamy konkretnych wzorców TikTok
                view_patterns = [
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*views?',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*wyświetleń',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*likes?',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*polubień'
                ]
                
                for pattern in view_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        views_info[f'pattern_{pattern}'] = matches
                
                return views_info
            else:
                return {'error': f'Błąd HTTP: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Błąd TikTok: {e}")
            return {'error': f'Błąd TikTok: {str(e)}'}
    
    def extract_vk_views(self, url: str) -> Dict[str, Any]:
        """Ekstraktuje wyświetlenia z VK"""
        try:
            username = self.extract_username(url, 'vk')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Ekstraktowanie wyświetleń VK: {username}")
            
            # Próbujemy pobrać stronę profilu
            profile_url = f"https://vk.com/{username}"
            response = self.session.get(profile_url)
            
            if response.status_code == 200:
                content = response.text
                
                # Szukamy informacji o wyświetleniach
                views_info = {
                    'platform': 'VK',
                    'username': username,
                    'profile_url': profile_url,
                    'method': 'scraping'
                }
                
                # Szukamy liczb w tekście
                numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?[KMB]?\b', content)
                if numbers:
                    views_info['found_numbers'] = numbers[:10]
                
                # Szukamy konkretnych wzorców VK
                view_patterns = [
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*views?',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*wyświetleń',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*likes?',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*polubień'
                ]
                
                for pattern in view_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        views_info[f'pattern_{pattern}'] = matches
                
                return views_info
            else:
                return {'error': f'Błąd HTTP: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Błąd VK: {e}")
            return {'error': f'Błąd VK: {str(e)}'}
    
    def extract_likee_views(self, url: str) -> Dict[str, Any]:
        """Ekstraktuje wyświetlenia z Likee"""
        try:
            username = self.extract_username(url, 'likee')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Ekstraktowanie wyświetleń Likee: {username}")
            
            # Próbujemy pobrać stronę profilu
            response = self.session.get(url)
            
            if response.status_code == 200:
                content = response.text
                
                # Szukamy informacji o wyświetleniach
                views_info = {
                    'platform': 'Likee',
                    'username': username,
                    'profile_url': url,
                    'method': 'scraping'
                }
                
                # Szukamy liczb w tekście
                numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?[KMB]?\b', content)
                if numbers:
                    views_info['found_numbers'] = numbers[:10]
                
                # Szukamy konkretnych wzorców Likee
                view_patterns = [
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*views?',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*wyświetleń',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*likes?',
                    r'(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\s*polubień'
                ]
                
                for pattern in view_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        views_info[f'pattern_{pattern}'] = matches
                
                return views_info
            else:
                return {'error': f'Błąd HTTP: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Błąd Likee: {e}")
            return {'error': f'Błąd Likee: {str(e)}'}
    
    def extract_all_views(self, urls: Dict[str, str]) -> Dict[str, Any]:
        """Ekstraktuje wyświetlenia ze wszystkich platform"""
        results = {}
        
        for platform, url in urls.items():
            logger.info(f"Ekstraktowanie wyświetleń {platform}: {url}")
            
            try:
                if platform.lower() == 'instagram':
                    results[platform] = self.extract_instagram_views(url)
                elif platform.lower() == 'youtube':
                    results[platform] = self.extract_youtube_views(url)
                elif platform.lower() == 'tiktok':
                    results[platform] = self.extract_tiktok_views(url)
                elif platform.lower() == 'vk':
                    results[platform] = self.extract_vk_views(url)
                elif platform.lower() == 'likee':
                    results[platform] = self.extract_likee_views(url)
                else:
                    results[platform] = {'error': f'Nieznana platforma: {platform}'}
                
                # Pauza między requestami
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Błąd ekstraktowania {platform}: {e}")
                results[platform] = {'error': str(e)}
        
        return results

def main():
    """Główna funkcja"""
    print("🔍 EKSTRAKTOR WYŚWIETLEŃ Z PLATFORM SPOŁECZNOŚCIOWYCH")
    print("=" * 60)
    
    # URL-e do sprawdzenia
    urls = {
        'Instagram': 'https://www.instagram.com/raachel_fb',
        'YouTube': 'https://www.youtube.com/@raachel_fb',
        'TikTok': 'https://www.tiktok.com/@daniryb_fb',
        'VK': 'https://vk.com/raachel_fb',
        'Likee': 'https://l.likee.video/p/jSQPBE'
    }
    
    print("📋 Ekstraktujemy wyświetlenia używając scraping...")
    print("⚠️ Niektóre platformy mogą blokować automatyczne zapytania")
    print()
    
    # Tworzymy ekstraktor
    extractor = ViewsExtractor()
    
    # Ekstraktujemy wyświetlenia
    print("📊 Ekstraktowanie wyświetleń...")
    results = extractor.extract_all_views(urls)
    
    # Wyświetlamy wyniki
    print("\n📈 WYNIKI EKSTRAKCJI WYŚWIETLEŃ:")
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
    filename = f'views_extraction_{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Wyniki zapisane do: {filename}")

if __name__ == "__main__":
    main()
