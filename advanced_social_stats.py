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
    
    def _youtube_api_stats(self, channel_url: str) -> Optional[Dict[str, Any]]:
        """YouTube Data API v3"""
        try:
            channel_id = self._extract_youtube_channel_id(channel_url)
            if not channel_id:
                return None
            
            api_key = self.api_keys['youtube']
            url = "https://www.googleapis.com/youtube/v3/channels"
            params = {
                'part': 'statistics,snippet',
                'id': channel_id,
                'key': api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'items' in data and data['items']:
                stats = data['items'][0]['statistics']
                return {
                    'platform': 'YouTube',
                    'subscribers': int(stats.get('subscriberCount', 0)),
                    'total_views': int(stats.get('viewCount', 0)),
                    'video_count': int(stats.get('videoCount', 0)),
                    'method': 'YouTube API'
                }
        except Exception as e:
            logger.error(f"Błąd YouTube API: {e}")
        return None
    
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
        """Sprawdzanie statystyk VK z wieloma metodami"""
        try:
            user_id = self._extract_vk_user_id(profile_url)
            if not user_id:
                return {'platform': 'VK', 'error': 'Nie można wyciągnąć user ID'}
            
            # Metoda 1: VK API
            if self.api_keys.get('vk'):
                api_result = self._vk_api_stats(user_id)
                if api_result and 'error' not in api_result:
                    return api_result
            
            # Metoda 2: Scraping z różnych źródeł
            scraping_result = self._vk_scraping_stats(profile_url)
            if scraping_result and 'error' not in scraping_result:
                return scraping_result
            
            return {'platform': 'VK', 'error': 'Wszystkie metody nieudane'}
            
        except Exception as e:
            logger.error(f"Błąd VK: {e}")
            return {'platform': 'VK', 'error': str(e)}
    
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
    
    def _extract_vk_user_id(self, url: str) -> Optional[str]:
        """Wyciąganie user ID z URL VK"""
        match = re.search(r'vk\.com/([^/?]+)', url)
        return match.group(1) if match else None
    
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




