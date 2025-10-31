#!/usr/bin/env python3
"""
Zaawansowany skrypt do sprawdzania statystyk społecznościowych
z lepszymi fallbackami i obsługą błędów
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import Dict, Optional, Any, List
import logging
from urllib.parse import urlparse, parse_qs
import random
import yt_dlp
import os
import tempfile

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedSocialStatsChecker:
    """Zaawansowana klasa do sprawdzania statystyk społecznościowych"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Różne User-Agents dla rotacji
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # API keys (zaimportuj z api_keys_config.py)
        try:
            from api_keys_config import get_api_keys
            self.api_keys = get_api_keys()
        except ImportError:
            self.api_keys = {}
    
    def _rotate_user_agent(self):
        """Rotacja User-Agent"""
        self.session.headers['User-Agent'] = random.choice(self.user_agents)
    
    def _make_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Wykonywanie requestu z retry logic"""
        for attempt in range(max_retries):
            try:
                self._rotate_user_agent()
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"Próba {attempt + 1} nieudana dla {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Wszystkie próby nieudane dla {url}")
                    return None
    
    def check_youtube_stats(self, channel_url: str) -> Dict[str, Any]:
        """Sprawdzanie statystyk YouTube z wieloma metodami"""
        try:
            # Metoda 1: YouTube Data API
            if self.api_keys.get('youtube'):
                api_result = self._youtube_api_stats(channel_url)
                if api_result and 'error' not in api_result:
                    return api_result
            
            # Metoda 2: Scraping z różnych źródeł
            scraping_result = self._youtube_scraping_stats(channel_url)
            if scraping_result and 'error' not in scraping_result:
                return scraping_result
            
            # Metoda 3: YouTube Analytics API (jeśli dostępne)
            analytics_result = self._youtube_analytics_stats(channel_url)
            if analytics_result and 'error' not in analytics_result:
                return analytics_result
            
            return {'platform': 'YouTube', 'error': 'Wszystkie metody nieudane'}
            
        except Exception as e:
            logger.error(f"Błąd YouTube: {e}")
            return {'platform': 'YouTube', 'error': str(e)}
    
    def get_youtube_short_data(self, short_url: str) -> Dict[str, Any]:
        """Pobiera dane konkretnego YouTube Short z URL"""
        try:
            # Wyciągamy video ID z URL
            video_id = self._extract_youtube_video_id(short_url)
            if not video_id:
                return {'platform': 'YouTube', 'error': 'Nie można wyciągnąć video ID z URL'}
            
            # Pobieramy dane przez YouTube API
            if self.api_keys.get('youtube'):
                short_data = self._get_youtube_short_by_id(video_id)
                if short_data:
                    return {
                        'platform': 'YouTube',
                        'url': short_url,
                        'shorts': [short_data],
                        'method': 'YouTube API'
                    }
            
            # Fallback - scraping
            short_data = self._get_youtube_short_scraping(short_url)
            if short_data:
                return {
                    'platform': 'YouTube',
                    'url': short_url,
                    'shorts': [short_data],
                    'method': 'Scraping'
                }
            
            return {'platform': 'YouTube', 'error': 'Nie można pobrać danych short'}
            
        except Exception as e:
            logger.error(f"Błąd pobierania YouTube short: {e}")
            return {'platform': 'YouTube', 'error': str(e)}
    
    def _youtube_api_stats(self, channel_url: str) -> Optional[Dict[str, Any]]:
        """YouTube Data API v3 - pobiera ostatnie 5 shortsów"""
        try:
            channel_id = self._extract_youtube_channel_id(channel_url)
            if not channel_id:
                return None
            
            api_key = self.api_keys['youtube']
            
            # Pobieramy podstawowe statystyki kanału
            url = "https://www.googleapis.com/youtube/v3/channels"
            params = {
                'part': 'statistics,snippet',
                'id': channel_id,
                'key': api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'items' not in data or not data['items']:
                return None
            
            stats = data['items'][0]['statistics']
            
            # Pobieramy ostatnie 5 shortsów
            shorts_data = self._get_youtube_shorts(channel_id, api_key)
            
            return {
                'platform': 'YouTube',
                'subscribers': int(stats.get('subscriberCount', 0)),
                'total_views': int(stats.get('viewCount', 0)),
                'video_count': int(stats.get('videoCount', 0)),
                'shorts': shorts_data,
                'method': 'YouTube API'
            }
        except Exception as e:
            logger.error(f"Błąd YouTube API: {e}")
        return None
    
    def _get_youtube_shorts(self, channel_id: str, api_key: str) -> List[Dict[str, Any]]:
        """Pobiera ostatnie 5 shortsów z kanału YouTube"""
        try:
            # Pobieramy ostatnie filmy z kanału
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'channelId': channel_id,
                'type': 'video',
                'maxResults': 50,  # Pobieramy więcej żeby znaleźć shortsy
                'order': 'date',
                'key': api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'items' not in data:
                return []
            
            # Filtrujemy shortsy (mają krótki czas trwania)
            shorts = []
            for item in data['items']:
                video_id = item['id']['videoId']
                video_details = self._get_video_details(video_id, api_key)
                
                if video_details and self._is_short(video_details):
                    shorts.append({
                        'title': item['snippet']['title'],
                        'video_id': video_id,
                        'url': f"https://www.youtube.com/shorts/{video_id}",
                        'duration': video_details.get('duration', ''),
                        'views': video_details.get('views', 0),
                        'likes': video_details.get('likes', 0),
                        'comments': video_details.get('comments', 0),
                        'published_at': item['snippet']['publishedAt']
                    })
                    
                    if len(shorts) >= 5:  # Ostatnie 5 shortsów
                        break
            
            return shorts
            
        except Exception as e:
            logger.error(f"Błąd pobierania shortsów: {e}")
            return []
    
    def _get_youtube_short_by_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera konkretny YouTube Short przez API"""
        try:
            api_key = self.api_keys['youtube']
            
            # Pobieramy szczegóły video
            video_details = self._get_video_details(video_id, api_key)
            if not video_details:
                return None
            
            # Sprawdzamy czy to short
            if not self._is_short(video_details):
                logger.warning(f"Video {video_id} nie jest shortem")
                return None
            
            # Konwertujemy datę
            published_at = video_details.get('snippet', {}).get('publishedAt', '')
            date_str = published_at[:10] if published_at else ''  # YYYY-MM-DD
            
            return {
                'title': video_details.get('snippet', {}).get('title', ''),
                'video_id': video_id,
                'views': int(video_details.get('statistics', {}).get('viewCount', 0)),
                'likes': int(video_details.get('statistics', {}).get('likeCount', 0)),
                'comments': int(video_details.get('statistics', {}).get('commentCount', 0)),
                'published_at': date_str,
                'duration': video_details.get('contentDetails', {}).get('duration', ''),
                'url': f"https://www.youtube.com/shorts/{video_id}"
            }
            
        except Exception as e:
            logger.error(f"Błąd pobierania YouTube short przez API: {e}")
            return None
    
    def _get_youtube_short_scraping(self, short_url: str) -> Optional[Dict[str, Any]]:
        """Pobiera konkretny YouTube Short przez scraping"""
        try:
            response = self._make_request(short_url)
            if not response:
                logger.warning(f"Nie można pobrać YouTube short z {short_url}")
                return None
            
            content = response.text
            
            # Wyciągamy video ID z URL
            video_id = self._extract_youtube_video_id(short_url)
            if not video_id:
                return None
            
            # Szukamy danych w HTML
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', content)
            title = title_match.group(1) if title_match else ''
            
            # Usuwamy "YouTube" z tytułu
            if title.endswith(' - YouTube'):
                title = title[:-10]
            
            return {
                'title': title,
                'video_id': video_id,
                'views': 0,  # Nie można łatwo wyciągnąć przez scraping
                'likes': 0,
                'comments': 0,
                'published_at': '',
                'duration': '',
                'url': short_url
            }
            
        except Exception as e:
            logger.error(f"Błąd YouTube scraping konkretnego short: {e}")
            return None
    
    def _get_video_details(self, video_id: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Pobiera szczegóły konkretnego filmu"""
        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'snippet,statistics,contentDetails',
                'id': video_id,
                'key': api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'items' not in data or not data['items']:
                return None
            
            item = data['items'][0]
            snippet = item.get('snippet', {})
            stats = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            
            return {
                'snippet': snippet,
                'statistics': stats,
                'contentDetails': content_details,
                'duration': content_details.get('duration', ''),
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0))
            }
            
        except Exception as e:
            logger.error(f"Błąd pobierania szczegółów filmu {video_id}: {e}")
            return None
    
    def _is_short(self, video_details: Dict[str, Any]) -> bool:
        """Sprawdza czy film to short (krótszy niż 60 sekund)"""
        try:
            duration = video_details.get('duration', '')
            if not duration:
                return False
            
            # YouTube duration format: PT1M30S (1 minuta 30 sekund)
            import re
            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
            if not match:
                return False
            
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            
            total_seconds = hours * 3600 + minutes * 60 + seconds
            return total_seconds <= 60  # Shorts są krótsze niż 60 sekund
            
        except Exception as e:
            logger.error(f"Błąd sprawdzania czy to short: {e}")
            return False
    
    def _youtube_scraping_stats(self, channel_url: str) -> Optional[Dict[str, Any]]:
        """Scraping YouTube z różnych źródeł"""
        try:
            # Główna strona kanału
            response = self._make_request(channel_url)
            if not response:
                return None
            
            content = response.text
            
            # Szukanie danych w różnych formatach
            patterns = {
                'subscribers': [
                    r'"subscriberCountText":\{"simpleText":"([^"]+)"',
                    r'"subscriberCountText":\{"runs":\[.*?"text":"([^"]+)"',
                    r'subscriberCount["\']:\s*["\']([^"\']+)["\']',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*subscribers?'
                ],
                'views': [
                    r'"viewCountText":\{"simpleText":"([^"]+)"',
                    r'viewCount["\']:\s*["\']([^"\']+)["\']',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*views?'
                ]
            }
            
            subscribers = self._extract_with_patterns(content, patterns['subscribers'])
            views = self._extract_with_patterns(content, patterns['views'])
            
            if subscribers or views:
                return {
                    'platform': 'YouTube',
                    'subscribers': subscribers,
                    'total_views': views,
                    'method': 'Scraping'
                }
        except Exception as e:
            logger.error(f"Błąd YouTube scraping: {e}")
        return None
    
    def _youtube_analytics_stats(self, channel_url: str) -> Optional[Dict[str, Any]]:
        """YouTube Analytics API (wymaga specjalnych uprawnień)"""
        # Ta metoda wymaga OAuth2 i specjalnych uprawnień
        # Implementacja zależna od konfiguracji
        return None
    
    def _extract_youtube_channel_id(self, url: str) -> Optional[str]:
        """Wyciąganie ID kanału z różnych formatów URL"""
        patterns = [
            r'youtube\.com/@([^/?]+)',
            r'youtube\.com/channel/([^/?]+)',
            r'youtube\.com/c/([^/?]+)',
            r'youtube\.com/user/([^/?]+)',
            r'youtube\.com/([^/?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Wyciąganie video ID z URL YouTube"""
        patterns = [
            r'youtube\.com/shorts/([a-zA-Z0-9_-]+)',  # YouTube Shorts
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',  # Regular YouTube video
            r'youtu\.be/([a-zA-Z0-9_-]+)',  # Short URL
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def check_instagram_stats(self, profile_url: str) -> Dict[str, Any]:
        """Sprawdzanie statystyk Instagram z wieloma metodami"""
        try:
            username = self._extract_instagram_username(profile_url)
            if not username:
                return {'platform': 'Instagram', 'error': 'Nie można wyciągnąć username'}
            
            # Metoda 1: Instagram Basic Display API
            if self.api_keys.get('instagram'):
                api_result = self._instagram_api_stats(username)
                if api_result and 'error' not in api_result:
                    return api_result
            
            # Metoda 2: Scraping z różnych źródeł
            scraping_result = self._instagram_scraping_stats(username)
            if scraping_result and 'error' not in scraping_result:
                return scraping_result
            
            # Metoda 3: Instagram Graph API (dla biznesowych kont)
            graph_result = self._instagram_graph_stats(username)
            if graph_result and 'error' not in graph_result:
                return graph_result
            
            return {'platform': 'Instagram', 'error': 'Wszystkie metody nieudane'}
            
        except Exception as e:
            logger.error(f"Błąd Instagram: {e}")
            return {'platform': 'Instagram', 'error': str(e)}
    
    def _instagram_scraping_stats(self, username: str) -> Optional[Dict[str, Any]]:
        """Scraping Instagram z różnych źródeł"""
        try:
            # Główna strona profilu
            url = f"https://www.instagram.com/{username}/"
            response = self._make_request(url)
            if not response:
                return None
            
            content = response.text
            
            # Szukanie danych w różnych formatach
            patterns = {
                'followers': [
                    r'"edge_followed_by":\{"count":(\d+)\}',
                    r'"follower_count":(\d+)',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*followers?'
                ],
                'following': [
                    r'"edge_follow":\{"count":(\d+)\}',
                    r'"following_count":(\d+)',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*following'
                ],
                'posts': [
                    r'"edge_owner_to_timeline_media":\{"count":(\d+)\}',
                    r'"media_count":(\d+)',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*posts?'
                ]
            }
            
            followers = self._extract_with_patterns(content, patterns['followers'])
            following = self._extract_with_patterns(content, patterns['following'])
            posts = self._extract_with_patterns(content, patterns['posts'])
            
            if followers or following or posts:
                return {
                    'platform': 'Instagram',
                    'followers': followers,
                    'following': following,
                    'posts': posts,
                    'method': 'Scraping'
                }
        except Exception as e:
            logger.error(f"Błąd Instagram scraping: {e}")
        return None
    
    def _instagram_api_stats(self, username: str) -> Optional[Dict[str, Any]]:
        """Instagram Basic Display API"""
        # Implementacja wymaga OAuth2
        return None
    
    def _instagram_graph_stats(self, username: str) -> Optional[Dict[str, Any]]:
        """Instagram Graph API (dla biznesowych kont)"""
        # Implementacja wymaga specjalnych uprawnień
        return None
    
    def _extract_instagram_username(self, url: str) -> Optional[str]:
        """Wyciąganie username z URL Instagram"""
        match = re.search(r'instagram\.com/([^/?]+)', url)
        return match.group(1) if match else None
    
    def get_instagram_reel_data(self, reel_url: str, download_path: Optional[str] = None) -> Dict[str, Any]:
        """Pobiera dane konkretnego Instagram Reel z URL i pobiera video używając yt-dlp"""
        try:
            logger.info(f"🎬 Pobieram dane Instagram Reel z URL: {reel_url}")
            
            # Wyciągamy reel ID z URL
            reel_id = self._extract_instagram_reel_id(reel_url)
            if not reel_id:
                logger.error(f"❌ Nie można wyciągnąć reel ID z URL: {reel_url}")
                return {'platform': 'Instagram', 'error': 'Nie można wyciągnąć reel ID z URL'}
            
            logger.info(f"✅ Reel ID: {reel_id}")
            
            # Pobieramy video używając yt-dlp
            video_path = self._download_instagram_reel_with_ytdlp(reel_url, download_path)
            
            if video_path:
                return {
                    'platform': 'Instagram',
                    'url': reel_url,
                    'reel_id': reel_id,
                    'video_path': video_path,
                    'method': 'yt-dlp',
                    'reels': [{
                        'reel_id': reel_id,
                        'url': reel_url,
                        'video_path': video_path
                    }]
                }
            else:
                return {'platform': 'Instagram', 'error': 'Nie można pobrać video'}
            
        except Exception as e:
            logger.error(f"❌ Błąd pobierania Instagram Reel: {e}")
            return {'platform': 'Instagram', 'error': str(e)}
    
    def _extract_instagram_reel_id(self, url: str) -> Optional[str]:
        """Wyciąganie reel ID z URL Instagram"""
        logger.info(f"🔍 Wyciągam reel ID z URL: {url}")
        
        # Format: https://www.instagram.com/reels/DNhNjlYsQR4/
        # Lub: https://www.instagram.com/reel/DNhNjlYsQR4/
        patterns = [
            r'instagram\.com/reels?/([^/?]+)',
            r'instagram\.com/p/([^/?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                reel_id = match.group(1)
                logger.info(f"✅ Znaleziono reel ID: {reel_id}")
                return reel_id
        
        logger.warning(f"❌ Nie można wyciągnąć reel ID z URL: {url}")
        return None
    
    def _download_instagram_reel_with_ytdlp(self, reel_url: str, download_path: Optional[str] = None) -> Optional[str]:
        """Pobiera Instagram Reel video używając yt-dlp"""
        try:
            logger.info(f"📥 Pobieram Instagram Reel video z: {reel_url}")
            
            # Określamy ścieżkę do zapisu
            if download_path is None:
                # Tworzymy tymczasowy folder jeśli nie podano ścieżki
                temp_dir = tempfile.mkdtemp()
                download_path = os.path.join(temp_dir, 'instagram_reel_%(id)s.%(ext)s')
            elif os.path.isdir(download_path):
                # Jeśli podano folder, tworzymy nazwę pliku
                download_path = os.path.join(download_path, 'instagram_reel_%(id)s.%(ext)s')
            
            ydl_opts = {
                'outtmpl': download_path,
                'quiet': True,  # Cichy tryb podobnie jak w przykładzie
                'no_warnings': False,
                'format': 'best',  # Pobieramy najlepszą jakość
            }
            
            downloaded_file = None
            
            def download_hook(d):
                """Hook do przechwycenia nazwy pobranego pliku"""
                nonlocal downloaded_file
                if d['status'] == 'finished':
                    downloaded_file = d.get('filename')
            
            ydl_opts['progress_hooks'] = [download_hook]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Pobieramy video
                ydl.download([reel_url])
                
                # Jeśli mamy nazwę pliku z hooka, używamy jej
                if downloaded_file and os.path.exists(downloaded_file):
                    logger.info(f"✅ Pobrano video: {downloaded_file}")
                    return downloaded_file
                
                # Fallback: szukamy pliku w folderze output
                output_dir = os.path.dirname(download_path) if os.path.dirname(download_path) else '.'
                
                if os.path.exists(output_dir):
                    import glob
                    # Szukamy wszystkich plików video w folderze
                    video_extensions = ['*.mp4', '*.webm', '*.mkv', '*.mov']
                    files = []
                    for ext in video_extensions:
                        files.extend(glob.glob(os.path.join(output_dir, ext)))
                    
                    if files:
                        # Wybieramy najnowszy plik
                        video_file = max(files, key=os.path.getctime)
                        logger.info(f"✅ Znaleziono pobrany video: {video_file}")
                        return video_file
                
                logger.warning(f"⚠️ Nie znaleziono pobranego pliku")
                return None
                
        except Exception as e:
            logger.error(f"❌ Błąd pobierania Instagram Reel przez yt-dlp: {e}")
            return None
    
    def check_tiktok_stats(self, profile_url: str) -> Dict[str, Any]:
        """Sprawdzanie statystyk TikTok z wieloma metodami"""
        try:
            username = self._extract_tiktok_username(profile_url)
            if not username:
                return {'platform': 'TikTok', 'error': 'Nie można wyciągnąć username'}
            
            # Metoda 1: TikTok Research API
            if self.api_keys.get('tiktok'):
                api_result = self._tiktok_api_stats(username)
                if api_result and 'error' not in api_result:
                    return api_result
            
            # Metoda 2: Scraping z różnych źródeł
            scraping_result = self._tiktok_scraping_stats(username)
            if scraping_result and 'error' not in scraping_result:
                return scraping_result
            
            return {'platform': 'TikTok', 'error': 'Wszystkie metody nieudane'}
            
        except Exception as e:
            logger.error(f"Błąd TikTok: {e}")
            return {'platform': 'TikTok', 'error': str(e)}
    
    def _tiktok_scraping_stats(self, username: str) -> Optional[Dict[str, Any]]:
        """Scraping TikTok z różnych źródeł"""
        try:
            # Główna strona profilu
            url = f"https://www.tiktok.com/@{username}"
            response = self._make_request(url)
            if not response:
                return None
            
            content = response.text
            
            # Szukanie danych w różnych formatach
            patterns = {
                'followers': [
                    r'"followerCount":(\d+)',
                    r'"fans":(\d+)',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*followers?'
                ],
                'following': [
                    r'"followingCount":(\d+)',
                    r'"follow":(\d+)',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*following'
                ],
                'likes': [
                    r'"heartCount":(\d+)',
                    r'"likes":(\d+)',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*likes?'
                ]
            }
            
            followers = self._extract_with_patterns(content, patterns['followers'])
            following = self._extract_with_patterns(content, patterns['following'])
            likes = self._extract_with_patterns(content, patterns['likes'])
            
            if followers or following or likes:
                return {
                    'platform': 'TikTok',
                    'followers': followers,
                    'following': following,
                    'likes': likes,
                    'method': 'Scraping'
                }
        except Exception as e:
            logger.error(f"Błąd TikTok scraping: {e}")
        return None
    
    def _tiktok_api_stats(self, username: str) -> Optional[Dict[str, Any]]:
        """TikTok Research API"""
        # Implementacja wymaga specjalnych uprawnień
        return None
    
    def _extract_tiktok_username(self, url: str) -> Optional[str]:
        """Wyciąganie username z URL TikTok"""
        match = re.search(r'tiktok\.com/@([^/?]+)', url)
        return match.group(1) if match else None
    
    def check_vk_stats(self, profile_url: str) -> Dict[str, Any]:
        """Sprawdzanie statystyk VK - pobiera ostatnie 5 clipsów"""
        try:
            user_id = self._extract_vk_user_id(profile_url)
            if not user_id:
                return {'platform': 'VK', 'error': 'Nie można wyciągnąć user ID'}
            
            # Pobieramy ostatnie clipsy
            clips_result = self._get_vk_clips(user_id, profile_url)
            if clips_result and 'error' not in clips_result:
                return clips_result
            
            return {'platform': 'VK', 'error': 'Nie można pobrać clipsów'}
            
        except Exception as e:
            logger.error(f"Błąd VK: {e}")
            return {'platform': 'VK', 'error': str(e)}
    
    def get_vk_clip_data(self, clip_url: str) -> Dict[str, Any]:
        """Pobiera dane konkretnego VK clip z URL"""
        try:
            logger.info(f"🎬 Pobieram dane VK clip z URL: {clip_url}")
            
            # Wyciągamy video_id z URL
            video_id = self._extract_vk_video_id(clip_url)
            if not video_id:
                logger.error(f"❌ Nie można wyciągnąć video ID z URL: {clip_url}")
                return {'platform': 'VK', 'error': 'Nie można wyciągnąć video ID z URL'}
            
            logger.info(f"✅ Video ID: {video_id}")
            
            # Wyciągamy owner_id z URL
            owner_id = self._extract_vk_owner_id(clip_url)
            if not owner_id:
                logger.error(f"❌ Nie można wyciągnąć owner ID z URL: {clip_url}")
                return {'platform': 'VK', 'error': 'Nie można wyciągnąć owner ID z URL'}
            
            logger.info(f"✅ Owner ID: {owner_id}")
            
            # Pobieramy dane TYLKO przez VK API
            if self.api_keys.get('vk'):
                logger.info(f"🔑 VK API key dostępny, pobieram dane przez API")
                clip_data = self._get_vk_clip_by_id(owner_id, video_id)
                if clip_data:
                    logger.info(f"✅ Pobrano dane przez VK API: {clip_data}")
                    return {
                        'platform': 'VK',
                        'url': clip_url,
                        'clips': [clip_data],
                        'method': 'VK API'
                    }
                else:
                    logger.error(f"❌ Brak danych z VK API")
                    return {'platform': 'VK', 'error': 'VK API nie zwrócił danych'}
            else:
                logger.error(f"❌ Brak VK API key")
                return {'platform': 'VK', 'error': 'Brak VK API key'}

        except Exception as e:
            logger.error(f"❌ Błąd pobierania VK clip: {e}")
            return {'platform': 'VK', 'error': str(e)}
    
    def _get_vk_clips(self, user_id: str, profile_url: str) -> Optional[Dict[str, Any]]:
        """Pobiera ostatnie 5 clipsów z VK"""
        try:
            # Metoda 1: VK API (jeśli dostępne)
            if self.api_keys.get('vk'):
                api_clips = self._get_vk_clips_api(user_id)
                if api_clips:
                    return {
                        'platform': 'VK',
                        'clips': api_clips,
                        'method': 'VK API'
                    }
            
            # Metoda 2: Scraping (fallback)
            scraping_clips = self._get_vk_clips_scraping(user_id, profile_url)
            if scraping_clips:
                return {
                    'platform': 'VK',
                    'clips': scraping_clips,
                    'method': 'Scraping'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Błąd pobierania VK clipsów: {e}")
            return None
    
    def _get_vk_clips_api(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Pobiera clipsy przez VK API"""
        try:
            access_token = self.api_keys['vk']
            
            # Pobieramy ostatnie filmy użytkownika
            url = "https://api.vk.com/method/video.get"
            params = {
                'owner_id': user_id,
                'count': 20,  # Pobieramy więcej żeby znaleźć clipsy
                'sort': 2,    # Sortowanie według daty
                'access_token': access_token,
                'v': '5.131'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'response' not in data or 'items' not in data['response']:
                return None
            
            clips = []
            for video in data['response']['items']:
                # Sprawdzamy czy to clip (krótki film)
                duration = video.get('duration', 0)
                if duration <= 60:  # Clipsy są krótsze niż 60 sekund
                    clips.append({
                        'title': video.get('title', ''),
                        'video_id': video.get('id', ''),
                        'views': video.get('views', 0),
                        'likes': video.get('likes', 0),
                        'comments': video.get('comments', 0),
                        'date': video.get('date', ''),
                        'duration': duration,
                        'url': f"https://vk.com/video{video.get('owner_id', '')}_{video.get('id', '')}"
                    })
                    
                    if len(clips) >= 5:  # Ostatnie 5 clipsów
                        break
            
            return clips
            
        except Exception as e:
            logger.error(f"Błąd VK API clipsów: {e}")
            return None
    
    def _get_vk_clip_by_id(self, owner_id: str, video_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera konkretny VK clip przez wall.get API"""
        try:
            logger.info(f"🔍 Pobieram VK clip przez API: owner_id={owner_id}, video_id={video_id}")
            access_token = self.api_keys['vk']
            
            # Używamy wall.get zamiast video.get
            url = "https://api.vk.com/method/wall.get"
            params = {
                'access_token': access_token,
                'v': '5.131',
                'owner_id': owner_id,
                'count': 50,  # Pobierz więcej postów żeby znaleźć video
                'extended': 1
            }
            
            logger.info(f"📡 Wywołuję VK API: {url}")
            response = self.session.get(url, params=params, timeout=15)
            data = response.json()
            
            logger.info(f"📊 Odpowiedź VK API: {data}")
            
            if 'error' in data:
                logger.error(f"❌ Błąd VK wall.get API: {data['error']}")
                return None
            
            if 'response' not in data or 'items' not in data['response']:
                logger.warning(f"⚠️ Brak danych w odpowiedzi wall.get dla {owner_id}")
                return None
            
            items = data['response']['items']
            logger.info(f"📋 Znaleziono {len(items)} postów w wall.get")
            
            # Szukamy konkretnego video w postach
            for i, item in enumerate(items):
                logger.info(f"🔍 Sprawdzam post {i+1}: {item.get('id', 'N/A')}")
                if 'attachments' in item:
                    logger.info(f"📎 Post {i+1} ma {len(item['attachments'])} attachments")
                    for j, attachment in enumerate(item['attachments']):
                        logger.info(f"📎 Attachment {j+1}: {attachment.get('type', 'N/A')}")
                        if attachment.get('type') == 'video':
                            video = attachment['video']
                            logger.info(f"🎬 Znaleziono video: id={video.get('id')}, title={video.get('title', 'N/A')}")
                            if str(video.get('id')) == video_id:
                                logger.info(f"✅ Znaleziono nasze video! {video_id}")
                                # Znaleźliśmy nasze video!

                                # Konwertujemy timestamp na datę
                                date_timestamp = item.get('date', 0)
                                date_str = datetime.fromtimestamp(date_timestamp).strftime('%Y-%m-%d') if date_timestamp else ''

                                result = {
                                    'title': video.get('title', ''),
                                    'video_id': video.get('id', ''),
                                    'views': video.get('views', 0),
                                    'likes': video.get('likes', {}).get('count', 0) if isinstance(video.get('likes'), dict) else video.get('likes', 0),
                                    'comments': video.get('comments', 0),
                                    'date': date_str,
                                    'duration': video.get('duration', 0),
                                    'url': video.get('player', f"https://vk.com/video{owner_id}_{video_id}")
                                }
                                logger.info(f"✅ Zwracam dane video: {result}")
                                return result
            
            logger.warning(f"⚠️ Nie znaleziono video {video_id} w postach użytkownika {owner_id}")
            return None

        except Exception as e:
            logger.error(f"❌ Błąd VK wall.get API konkretnego clip: {e}")
            return None
    
    def _get_vk_clips_scraping(self, user_id: str, profile_url: str) -> Optional[List[Dict[str, Any]]]:
        """Pobiera clipsy przez scraping (fallback)"""
        try:
            # Sprawdzamy czy user_id to numer (ID użytkownika)
            if user_id.isdigit():
                # Jeśli mamy numer ID, próbujemy VK API
                if self.api_keys.get('vk'):
                    return self._get_vk_clips_api(user_id)
                else:
                    logger.warning(f"Brak VK API key, nie można pobrać clipsów dla ID {user_id}")
                    return None
            
            # Jeśli to username, próbujemy scraping
            # Konwertujemy clips URL na profil URL jeśli potrzeba
            if '/clips/' in profile_url:
                username = self._extract_vk_user_id(profile_url)
                if username:
                    profile_url = f"https://vk.com/{username}"
            
            # Pobieramy stronę profilu
            response = self._make_request(profile_url)
            if not response:
                logger.warning(f"Nie można pobrać danych VK dla {user_id}")
                return None
            
            content = response.text
            
            # Szukamy clipsów w HTML
            clips = self._extract_vk_clips_from_html(content, user_id)
            
            return clips[:5] if clips else None
            
        except Exception as e:
            logger.error(f"Błąd VK scraping clipsów: {e}")
            return None
    
    def _create_mock_vk_clips(self, user_id: str) -> List[Dict[str, Any]]:
        """Tworzy mock data dla VK clipsów"""
        import time
        current_time = int(time.time())
        
        mock_clips = []
        for i in range(5):
            clip_id = f"{user_id}_{i+1}"
            mock_clips.append({
                'title': f'VK Clip {i+1} - {user_id}',
                'video_id': clip_id,
                'views': 1000 + (i * 200),  # Różne liczby wyświetleń
                'likes': 50 + (i * 10),
                'comments': 10 + i,
                'date': current_time - (i * 86400),  # Ostatnie 5 dni
                'duration': 30 + (i * 5),  # 30-50 sekund
                'url': f"https://vk.com/video{user_id}_{clip_id}"
            })
        
        return mock_clips
    
    def _extract_vk_clips_from_html(self, html_content: str, user_id: str) -> List[Dict[str, Any]]:
        """Wyciąga clipsy z HTML VK"""
        try:
            clips = []
            
            # Szukamy clipsów w różnych formatach JSON
            import re
            import json
            
            # Pattern 1: Szukamy w window.vkData
            vk_data_pattern = r'window\.vkData\s*=\s*({.*?});'
            vk_data_match = re.search(vk_data_pattern, html_content, re.DOTALL)
            
            if vk_data_match:
                try:
                    vk_data = json.loads(vk_data_match.group(1))
                    clips.extend(self._parse_vk_data_clips(vk_data))
                except json.JSONDecodeError:
                    pass
            
            # Pattern 2: Szukamy w innych miejscach
            clips_pattern = r'"video":\s*({[^}]+})'
            clips_matches = re.findall(clips_pattern, html_content)
            
            for clip_match in clips_matches:
                try:
                    clip_data = json.loads(clip_match)
                    if self._is_valid_vk_clip(clip_data):
                        clips.append(self._format_vk_clip(clip_data))
                except json.JSONDecodeError:
                    continue
            
            # Ograniczamy do 5 clipsów
            return clips[:5]
            
        except Exception as e:
            logger.error(f"Błąd wyciągania VK clipsów: {e}")
            return []
    
    def _parse_vk_data_clips(self, vk_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parsuje clipsy z vkData"""
        clips = []
        
        # Szukamy w różnych miejscach vkData
        for key, value in vk_data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and self._is_valid_vk_clip(item):
                        clips.append(self._format_vk_clip(item))
        
        return clips
    
    def _is_valid_vk_clip(self, clip_data: Dict[str, Any]) -> bool:
        """Sprawdza czy to jest prawidłowy VK clip"""
        required_fields = ['id', 'title', 'views']
        return all(field in clip_data for field in required_fields)
    
    def _format_vk_clip(self, clip_data: Dict[str, Any]) -> Dict[str, Any]:
        """Formatuje dane VK clip"""
        return {
            'title': clip_data.get('title', ''),
            'video_id': clip_data.get('id', ''),
            'views': clip_data.get('views', 0),
            'likes': clip_data.get('likes', 0),
            'comments': clip_data.get('comments', 0),
            'date': clip_data.get('date', ''),
            'duration': clip_data.get('duration', 0),
            'url': f"https://vk.com/video{clip_data.get('id', '')}"
        }
    
    def _vk_api_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """VK API"""
        try:
            access_token = self.api_keys['vk']
            url = "https://api.vk.com/method/users.get"
            params = {
                'user_ids': user_id,
                'fields': 'followers_count,counters',
                'access_token': access_token,
                'v': '5.131'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'response' in data and data['response']:
                user_data = data['response'][0]
                return {
                    'platform': 'VK',
                    'followers': user_data.get('followers_count', 0),
                    'friends': user_data.get('counters', {}).get('friends', 0),
                    'method': 'VK API'
                }
        except Exception as e:
            logger.error(f"Błąd VK API: {e}")
        return None
    
    def _vk_scraping_stats(self, url: str) -> Optional[Dict[str, Any]]:
        """Scraping VK z różnych źródeł"""
        try:
            # Jeśli to clips URL, konwertujemy na profil URL
            if '/clips/' in url:
                username = self._extract_vk_user_id(url)
                if username:
                    url = f"https://vk.com/{username}"
            
            response = self._make_request(url)
            if not response:
                return None
            
            content = response.text
            
            # Szukanie danych w różnych formatach
            patterns = {
                'followers': [
                    r'"followers_count":(\d+)',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*followers?'
                ],
                'friends': [
                    r'"friends_count":(\d+)',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*friends?'
                ]
            }
            
            followers = self._extract_with_patterns(content, patterns['followers'])
            friends = self._extract_with_patterns(content, patterns['friends'])
            
            if followers or friends:
                return {
                    'platform': 'VK',
                    'followers': followers,
                    'friends': friends,
                    'method': 'Scraping'
                }
        except Exception as e:
            logger.error(f"Błąd VK scraping: {e}")
        return None
    
    def _extract_vk_video_id(self, url: str) -> Optional[str]:
        """Wyciąganie video ID z URL VK clip"""
        logger.info(f"🔍 Wyciągam video ID z URL: {url}")
        
        # Format: https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129
        # Szukamy clip{owner_id}_{video_id}
        clip_match = re.search(r'clip(\d+)_(\d+)', url)
        if clip_match:
            video_id = clip_match.group(2)  # video_id
            logger.info(f"✅ Znaleziono video ID przez clip_match: {video_id}")
            return video_id
        
        # Alternatywnie szukamy w parametrze z
        z_match = re.search(r'z=clip\d+_(\d+)', url)
        if z_match:
            video_id = z_match.group(1)
            logger.info(f"✅ Znaleziono video ID przez z_match: {video_id}")
            return video_id
        
        logger.warning(f"❌ Nie można wyciągnąć video ID z URL: {url}")
        return None
    
    def _extract_vk_owner_id(self, url: str) -> Optional[str]:
        """Wyciąganie owner ID z URL VK clip"""
        logger.info(f"🔍 Wyciągam owner ID z URL: {url}")
        
        # Format: https://vk.com/clips/id1069245351?feedType=ownerFeed&owner=1069245351&z=clip1069245351_456239129
        # Szukamy owner=123456
        owner_match = re.search(r'owner=(\d+)', url)
        if owner_match:
            owner_id = owner_match.group(1)
            logger.info(f"✅ Znaleziono owner ID przez owner_match: {owner_id}")
            return owner_id
        
        # Alternatywnie z clip{owner_id}_{video_id}
        clip_match = re.search(r'clip(\d+)_\d+', url)
        if clip_match:
            owner_id = clip_match.group(1)
            logger.info(f"✅ Znaleziono owner ID przez clip_match: {owner_id}")
            return owner_id
        
        logger.warning(f"❌ Nie można wyciągnąć owner ID z URL: {url}")
        return None
    
    def check_likee_stats(self, profile_url: str) -> Dict[str, Any]:
        """Sprawdzanie statystyk Likee"""
        try:
            # Likee nie ma oficjalnego API
            scraping_result = self._likee_scraping_stats(profile_url)
            if scraping_result and 'error' not in scraping_result:
                return scraping_result
            
            return {'platform': 'Likee', 'error': 'Wszystkie metody nieudane'}
            
        except Exception as e:
            logger.error(f"Błąd Likee: {e}")
            return {'platform': 'Likee', 'error': str(e)}
    
    def _likee_scraping_stats(self, url: str) -> Optional[Dict[str, Any]]:
        """Scraping Likee z różnych źródeł"""
        try:
            response = self._make_request(url)
            if not response:
                return None
            
            content = response.text
            
            # Szukanie danych w różnych formatach
            patterns = {
                'followers': [
                    r'"fans":(\d+)',
                    r'"followerCount":(\d+)',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*followers?'
                ],
                'following': [
                    r'"follow":(\d+)',
                    r'"followingCount":(\d+)',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*following'
                ]
            }
            
            followers = self._extract_with_patterns(content, patterns['followers'])
            following = self._extract_with_patterns(content, patterns['following'])
            
            if followers or following:
                return {
                    'platform': 'Likee',
                    'followers': followers,
                    'following': following,
                    'method': 'Scraping'
                }
        except Exception as e:
            logger.error(f"Błąd Likee scraping: {e}")
        return None
    
    def _extract_with_patterns(self, content: str, patterns: List[str]) -> int:
        """Wyciąganie danych z różnych wzorców"""
        for pattern in patterns:
            try:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return self._parse_number(match.group(1))
            except Exception:
                continue
        return 0
    
    def _parse_number(self, text: str) -> int:
        """Parsowanie liczb z tekstu (np. '1.2M' -> 1200000)"""
        if not text:
            return 0
        
        text = text.replace(',', '').replace(' ', '').replace('"', '')
        
        multipliers = {
            'K': 1000,
            'M': 1000000,
            'B': 1000000000
        }
        
        for suffix, multiplier in multipliers.items():
            if suffix in text.upper():
                number = float(re.findall(r'[\d.]+', text)[0])
                return int(number * multiplier)
        
        # Jeśli nie ma sufiksu, spróbuj wyciągnąć liczbę
        numbers = re.findall(r'[\d.]+', text)
        if numbers:
            return int(float(numbers[0]))
        
        return 0
    
    def check_all_stats(self, urls: Dict[str, str]) -> Dict[str, Any]:
        """Sprawdzanie statystyk na wszystkich platformach"""
        results = {}
        
        for platform, url in urls.items():
            logger.info(f"Sprawdzanie {platform}: {url}")
            
            try:
                if platform.lower() == 'youtube':
                    results[platform] = self.check_youtube_stats(url)
                elif platform.lower() == 'instagram':
                    results[platform] = self.check_instagram_stats(url)
                elif platform.lower() == 'tiktok':
                    results[platform] = self.check_tiktok_stats(url)
                elif platform.lower() == 'vk':
                    results[platform] = self.check_vk_stats(url)
                elif platform.lower() == 'likee':
                    results[platform] = self.check_likee_stats(url)
                
                # Pauza między requestami
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"Błąd {platform}: {e}")
                results[platform] = {'platform': platform, 'error': str(e)}
        
        return results

    def extract_vk_clips_views(self, clips_url: str) -> Dict[str, Any]:
        """Ekstraktuje wyświetlenia z VK Clips używając VK API"""
        try:
            if not self.api_keys.get('vk'):
                return {'error': 'VK API nie jest dostępny'}
            
            logger.info(f"Ekstraktowanie wyświetleń VK Clips: {clips_url}")
            
            # Wyciągamy username z URL
            if '/clips/' in clips_url:
                username = clips_url.split('/clips/')[-1].split('/')[0]
            else:
                return {'error': 'Nieprawidłowy URL VK Clips'}
            
            # Używamy VK API przez requests (nie vk_api)
            access_token = self.api_keys['vk']
            
            # Szukamy użytkownika po username
            try:
                url = "https://api.vk.com/method/users.get"
                params = {
                    'access_token': access_token,
                    'v': '5.131',
                    'user_ids': username,
                    'fields': 'counters'
                }
                
                response = self.session.get(url, params=params, timeout=15)
                data = response.json()
                
                if 'error' in data:
                    return {'error': f'Błąd VK API: {data["error"]}'}
                
                if 'response' not in data or not data['response']:
                    return {'error': 'Nie znaleziono użytkownika VK'}
                
                user = data['response'][0]
                user_id = user['id']
                
                # Pobieramy posty użytkownika (ostatnie 10)
                wall_url = "https://api.vk.com/method/wall.get"
                wall_params = {
                    'access_token': access_token,
                    'v': '5.131',
                    'owner_id': user_id,
                    'count': 10,
                    'filter': 'owner',
                    'extended': 1
                }
                
                wall_response = self.session.get(wall_url, params=wall_params, timeout=15)
                wall_data = wall_response.json()
                
                clips_data = {
                    'platform': 'VK Clips',
                    'username': username,
                    'user_id': user_id,
                    'user_name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                    'method': 'VK API',
                    'clips': []
                }
                
                if 'response' in wall_data and 'items' in wall_data['response']:
                    for post in wall_data['response']['items']:
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
                
            except Exception as e:
                return {'error': f'Błąd VK API: {e}'}
                
        except Exception as e:
            logger.error(f"Błąd VK Clips: {e}")
            return {'error': f'Błąd VK Clips: {str(e)}'}


def main():
    """Główna funkcja"""
    print("🔍 ZAAWANSOWANE SPRAWDZANIE STATYSTYK SPOŁECZNOŚCIOWYCH")
    print("=" * 60)
    
    # URLs do sprawdzenia
    urls = {
        'YouTube': 'https://www.youtube.com/@raachel_fb',
        'Instagram': 'https://www.instagram.com/raachel_fb',
        'VK': 'https://vk.com/raachel_fb',
        'TikTok': 'https://www.tiktok.com/@daniryb_fb',
        'Likee': 'https://l.likee.video/p/jSQPBE'
    }
    
    checker = AdvancedSocialStatsChecker()
    
    print("📊 Sprawdzanie statystyk z wieloma metodami...")
    results = checker.check_all_stats(urls)
    
    print("\n📈 WYNIKI:")
    print("=" * 60)
    
    total_followers = 0
    successful_platforms = 0
    
    for platform, data in results.items():
        print(f"\n🔹 {platform}:")
        if 'error' in data:
            print(f"   ❌ Błąd: {data['error']}")
        else:
            successful_platforms += 1
            for key, value in data.items():
                if key not in ['platform', 'method']:
                    if isinstance(value, int):
                        print(f"   {key}: {value:,}")
                    else:
                        print(f"   {key}: {value}")
            
            # Zliczanie obserwatorów
            if 'followers' in data:
                total_followers += data['followers']
            elif 'subscribers' in data:
                total_followers += data['subscribers']
    
    # Zapisanie wyników do pliku
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"advanced_social_stats_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Wyniki zapisane do: {filename}")
    
    # Podsumowanie
    print(f"\n📊 PODSUMOWANIE:")
    print(f"   ✅ Udane platformy: {successful_platforms}/{len(urls)}")
    print(f"   👥 Łączna liczba obserwatorów: {total_followers:,}")
    
    if successful_platforms == 0:
        print("   ⚠️  Wszystkie platformy nieudane - sprawdź połączenie internetowe")
    elif successful_platforms < len(urls):
        print("   ⚠️  Niektóre platformy nieudane - sprawdź konfigurację API keys")


if __name__ == "__main__":
    main()




