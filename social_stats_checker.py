#!/usr/bin/env python3
"""
Skrypt do sprawdzania statystyk wyświetleń na różnych platformach społecznościowych
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import Dict, Optional, Any
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SocialStatsChecker:
    """Klasa do sprawdzania statystyk na różnych platformach"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Konfiguracja API keys (dodaj swoje klucze)
        self.api_keys = {
            'youtube': None,  # YouTube Data API v3 key
            'instagram': None,  # Instagram Basic Display API
            'tiktok': None,  # TikTok Research API
            'vk': None,  # VK API token
            'likee': None  # Likee API (jeśli dostępne)
        }
    
    def check_youtube_stats(self, channel_url: str) -> Dict[str, Any]:
        """Sprawdzanie statystyk YouTube"""
        try:
            # Extract channel ID from URL
            channel_id = self._extract_youtube_channel_id(channel_url)
            if not channel_id:
                return self._fallback_youtube_stats(channel_url)
            
            # YouTube Data API v3
            if self.api_keys['youtube']:
                return self._youtube_api_stats(channel_id)
            else:
                return self._fallback_youtube_stats(channel_url)
                
        except Exception as e:
            logger.error(f"Błąd YouTube: {e}")
            return self._fallback_youtube_stats(channel_url)
    
    def _extract_youtube_channel_id(self, url: str) -> Optional[str]:
        """Wyciąganie ID kanału z URL"""
        patterns = [
            r'youtube\.com/@([^/?]+)',
            r'youtube\.com/channel/([^/?]+)',
            r'youtube\.com/c/([^/?]+)',
            r'youtube\.com/user/([^/?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _youtube_api_stats(self, channel_id: str) -> Dict[str, Any]:
        """Statystyki przez YouTube API"""
        try:
            api_key = self.api_keys['youtube']
            url = f"https://www.googleapis.com/youtube/v3/channels"
            params = {
                'part': 'statistics,snippet',
                'id': channel_id,
                'key': api_key
            }
            
            response = self.session.get(url, params=params)
            data = response.json()
            
            if 'items' in data and data['items']:
                stats = data['items'][0]['statistics']
                return {
                    'platform': 'YouTube',
                    'subscribers': int(stats.get('subscriberCount', 0)),
                    'total_views': int(stats.get('viewCount', 0)),
                    'video_count': int(stats.get('videoCount', 0)),
                    'method': 'API'
                }
        except Exception as e:
            logger.error(f"Błąd YouTube API: {e}")
        
        return self._fallback_youtube_stats(f"https://youtube.com/@{channel_id}")
    
    def _fallback_youtube_stats(self, url: str) -> Dict[str, Any]:
        """Fallback - scraping YouTube"""
        try:
            response = self.session.get(url)
            content = response.text
            
            # Szukanie danych w HTML
            subscribers_match = re.search(r'"subscriberCountText":\{"simpleText":"([^"]+)"', content)
            views_match = re.search(r'"viewCountText":\{"simpleText":"([^"]+)"', content)
            
            subscribers = self._parse_number(subscribers_match.group(1) if subscribers_match else "0")
            views = self._parse_number(views_match.group(1) if views_match else "0")
            
            return {
                'platform': 'YouTube',
                'subscribers': subscribers,
                'total_views': views,
                'video_count': 0,
                'method': 'Scraping'
            }
        except Exception as e:
            logger.error(f"Błąd YouTube fallback: {e}")
            return {'platform': 'YouTube', 'error': str(e)}
    
    def check_instagram_stats(self, profile_url: str) -> Dict[str, Any]:
        """Sprawdzanie statystyk Instagram"""
        try:
            username = self._extract_instagram_username(profile_url)
            if not username:
                return {'platform': 'Instagram', 'error': 'Nie można wyciągnąć username'}
            
            # Instagram Basic Display API
            if self.api_keys['instagram']:
                return self._instagram_api_stats(username)
            else:
                return self._fallback_instagram_stats(username)
                
        except Exception as e:
            logger.error(f"Błąd Instagram: {e}")
            return {'platform': 'Instagram', 'error': str(e)}
    
    def _extract_instagram_username(self, url: str) -> Optional[str]:
        """Wyciąganie username z URL Instagram"""
        match = re.search(r'instagram\.com/([^/?]+)', url)
        return match.group(1) if match else None
    
    def _instagram_api_stats(self, username: str) -> Dict[str, Any]:
        """Statystyki przez Instagram API"""
        try:
            # Instagram Basic Display API wymaga autoryzacji
            # To jest uproszczona wersja
            return self._fallback_instagram_stats(username)
        except Exception as e:
            logger.error(f"Błąd Instagram API: {e}")
            return self._fallback_instagram_stats(username)
    
    def _fallback_instagram_stats(self, username: str) -> Dict[str, Any]:
        """Fallback - scraping Instagram"""
        try:
            url = f"https://www.instagram.com/{username}/"
            response = self.session.get(url)
            content = response.text
            
            # Szukanie danych w JSON-LD
            json_match = re.search(r'window\._sharedData = ({.*?});', content)
            if json_match:
                data = json.loads(json_match.group(1))
                user_info = data['entry_data']['ProfilePage'][0]['graphql']['user']
                
                return {
                    'platform': 'Instagram',
                    'followers': user_info['edge_followed_by']['count'],
                    'following': user_info['edge_follow']['count'],
                    'posts': user_info['edge_owner_to_timeline_media']['count'],
                    'method': 'Scraping'
                }
        except Exception as e:
            logger.error(f"Błąd Instagram fallback: {e}")
            return {'platform': 'Instagram', 'error': str(e)}
    
    def check_tiktok_stats(self, profile_url: str) -> Dict[str, Any]:
        """Sprawdzanie statystyk TikTok"""
        try:
            username = self._extract_tiktok_username(profile_url)
            if not username:
                return {'platform': 'TikTok', 'error': 'Nie można wyciągnąć username'}
            
            # TikTok Research API
            if self.api_keys['tiktok']:
                return self._tiktok_api_stats(username)
            else:
                return self._fallback_tiktok_stats(username)
                
        except Exception as e:
            logger.error(f"Błąd TikTok: {e}")
            return {'platform': 'TikTok', 'error': str(e)}
    
    def _extract_tiktok_username(self, url: str) -> Optional[str]:
        """Wyciąganie username z URL TikTok"""
        match = re.search(r'tiktok\.com/@([^/?]+)', url)
        return match.group(1) if match else None
    
    def _tiktok_api_stats(self, username: str) -> Dict[str, Any]:
        """Statystyki przez TikTok API"""
        try:
            # TikTok Research API wymaga specjalnej autoryzacji
            return self._fallback_tiktok_stats(username)
        except Exception as e:
            logger.error(f"Błąd TikTok API: {e}")
            return self._fallback_tiktok_stats(username)
    
    def _fallback_tiktok_stats(self, username: str) -> Dict[str, Any]:
        """Fallback - scraping TikTok"""
        try:
            url = f"https://www.tiktok.com/@{username}"
            response = self.session.get(url)
            content = response.text
            
            # Szukanie danych w JSON
            json_match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">({.*?})</script>', content)
            if json_match:
                data = json.loads(json_match.group(1))
                # Parsowanie danych TikTok (struktura może się zmieniać)
                return {
                    'platform': 'TikTok',
                    'followers': 0,  # Trudne do wyciągnięcia
                    'following': 0,
                    'likes': 0,
                    'method': 'Scraping'
                }
        except Exception as e:
            logger.error(f"Błąd TikTok fallback: {e}")
            return {'platform': 'TikTok', 'error': str(e)}
    
    def check_vk_stats(self, profile_url: str) -> Dict[str, Any]:
        """Sprawdzanie statystyk VK"""
        try:
            user_id = self._extract_vk_user_id(profile_url)
            if not user_id:
                return {'platform': 'VK', 'error': 'Nie można wyciągnąć user ID'}
            
            # VK API
            if self.api_keys['vk']:
                return self._vk_api_stats(user_id)
            else:
                return self._fallback_vk_stats(profile_url)
                
        except Exception as e:
            logger.error(f"Błąd VK: {e}")
            return {'platform': 'VK', 'error': str(e)}
    
    def _extract_vk_user_id(self, url: str) -> Optional[str]:
        """Wyciąganie user ID z URL VK"""
        match = re.search(r'vk\.com/([^/?]+)', url)
        return match.group(1) if match else None
    
    def _vk_api_stats(self, user_id: str) -> Dict[str, Any]:
        """Statystyki przez VK API"""
        try:
            access_token = self.api_keys['vk']
            url = "https://api.vk.com/method/users.get"
            params = {
                'user_ids': user_id,
                'fields': 'followers_count,counters',
                'access_token': access_token,
                'v': '5.131'
            }
            
            response = self.session.get(url, params=params)
            data = response.json()
            
            if 'response' in data and data['response']:
                user_data = data['response'][0]
                return {
                    'platform': 'VK',
                    'followers': user_data.get('followers_count', 0),
                    'friends': user_data.get('counters', {}).get('friends', 0),
                    'method': 'API'
                }
        except Exception as e:
            logger.error(f"Błąd VK API: {e}")
        
        return self._fallback_vk_stats(f"https://vk.com/{user_id}")
    
    def _fallback_vk_stats(self, url: str) -> Dict[str, Any]:
        """Fallback - scraping VK"""
        try:
            response = self.session.get(url)
            content = response.text
            
            # Szukanie danych w HTML
            followers_match = re.search(r'"followers_count":(\d+)', content)
            friends_match = re.search(r'"friends_count":(\d+)', content)
            
            return {
                'platform': 'VK',
                'followers': int(followers_match.group(1)) if followers_match else 0,
                'friends': int(friends_match.group(1)) if friends_match else 0,
                'method': 'Scraping'
            }
        except Exception as e:
            logger.error(f"Błąd VK fallback: {e}")
            return {'platform': 'VK', 'error': str(e)}
    
    def check_likee_stats(self, profile_url: str) -> Dict[str, Any]:
        """Sprawdzanie statystyk Likee"""
        try:
            # Likee nie ma oficjalnego API
            return self._fallback_likee_stats(profile_url)
        except Exception as e:
            logger.error(f"Błąd Likee: {e}")
            return {'platform': 'Likee', 'error': str(e)}
    
    def _fallback_likee_stats(self, url: str) -> Dict[str, Any]:
        """Fallback - scraping Likee"""
        try:
            response = self.session.get(url)
            content = response.text
            
            # Szukanie danych w HTML (struktura może się zmieniać)
            followers_match = re.search(r'"fans":(\d+)', content)
            following_match = re.search(r'"follow":(\d+)', content)
            
            return {
                'platform': 'Likee',
                'followers': int(followers_match.group(1)) if followers_match else 0,
                'following': int(following_match.group(1)) if following_match else 0,
                'method': 'Scraping'
            }
        except Exception as e:
            logger.error(f"Błąd Likee fallback: {e}")
            return {'platform': 'Likee', 'error': str(e)}
    
    def _parse_number(self, text: str) -> int:
        """Parsowanie liczb z tekstu (np. '1.2M' -> 1200000)"""
        if not text:
            return 0
        
        text = text.replace(',', '').replace(' ', '')
        
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
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Błąd {platform}: {e}")
                results[platform] = {'platform': platform, 'error': str(e)}
        
        return results


def main():
    """Główna funkcja"""
    print("🔍 SPRAWDZANIE STATYSTYK SPOŁECZNOŚCIOWYCH")
    print("=" * 50)
    
    # URLs do sprawdzenia
    urls = {
        'YouTube': 'https://www.youtube.com/@raachel_fb',
        'Instagram': 'https://www.instagram.com/raachel_fb',
        'VK': 'https://vk.com/raachel_fb',
        'TikTok': 'https://www.tiktok.com/@daniryb_fb',
        'Likee': 'https://l.likee.video/p/jSQPBE'
    }
    
    checker = SocialStatsChecker()
    
    print("📊 Sprawdzanie statystyk...")
    results = checker.check_all_stats(urls)
    
    print("\n📈 WYNIKI:")
    print("=" * 50)
    
    for platform, data in results.items():
        print(f"\n🔹 {platform}:")
        if 'error' in data:
            print(f"   ❌ Błąd: {data['error']}")
        else:
            for key, value in data.items():
                if key != 'platform':
                    print(f"   {key}: {value:,}" if isinstance(value, int) else f"   {key}: {value}")
    
    # Zapisanie wyników do pliku
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"social_stats_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Wyniki zapisane do: {filename}")
    
    # Podsumowanie
    total_followers = 0
    for platform, data in results.items():
        if 'error' not in data:
            if 'followers' in data:
                total_followers += data['followers']
            elif 'subscribers' in data:
                total_followers += data['subscribers']
    
    print(f"\n📊 ŁĄCZNA LICZBA OBSERWATORÓW: {total_followers:,}")


if __name__ == "__main__":
    main()




