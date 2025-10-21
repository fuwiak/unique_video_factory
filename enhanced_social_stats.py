#!/usr/bin/env python3
"""
Ulepszony skrypt do sprawdzania statystyk społecznościowych
Używa instaloader dla Instagram i TikTokApi dla TikTok
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

class EnhancedSocialStatsChecker:
    """Ulepszony checker statystyk społecznościowych"""
    
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
                # Instagram: https://www.instagram.com/username/
                if 'instagram.com/' in url:
                    username = url.split('instagram.com/')[-1].split('/')[0].split('?')[0]
                    return username
            elif platform == 'youtube':
                # YouTube: https://www.youtube.com/@username lub /channel/ID
                if 'youtube.com/@' in url:
                    return url.split('@')[-1].split('/')[0]
                elif 'youtube.com/channel/' in url:
                    return url.split('channel/')[-1].split('/')[0]
            elif platform == 'tiktok':
                # TikTok: https://www.tiktok.com/@username
                if 'tiktok.com/@' in url:
                    return url.split('@')[-1].split('/')[0]
            elif platform == 'vk':
                # VK: https://vk.com/username lub /id123456
                if 'vk.com/' in url:
                    return url.split('vk.com/')[-1].split('/')[0]
            elif platform == 'likee':
                # Likee: https://l.likee.video/p/username
                if 'likee.video/p/' in url:
                    return url.split('p/')[-1].split('/')[0]
        except Exception as e:
            logger.error(f"Błąd wyciągania username z {url}: {e}")
        return None
    
    def check_instagram_stats(self, url: str) -> Dict[str, Any]:
        """Sprawdza statystyki Instagram używając instaloader"""
        try:
            username = self.extract_username(url, 'instagram')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Sprawdzanie Instagram: @{username}")
            
            # Pobieramy profil
            profile = instaloader.Profile.from_username(self.instaloader.context, username)
            
            return {
                'platform': 'Instagram',
                'username': username,
                'followers': profile.followers,
                'following': profile.followees,
                'posts': profile.mediacount,
                'is_verified': profile.is_verified,
                'is_private': profile.is_private,
                'biography': profile.biography,
                'external_url': profile.external_url,
                'method': 'instaloader'
            }
            
        except Exception as e:
            logger.error(f"Błąd Instagram: {e}")
            return {'error': f'Błąd Instagram: {str(e)}'}
    
    def check_tiktok_stats(self, url: str) -> Dict[str, Any]:
        """Sprawdza statystyki TikTok używając TikTokApi"""
        try:
            username = self.extract_username(url, 'tiktok')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Sprawdzanie TikTok: @{username}")
            
            if not self.tiktok_api:
                return {'error': 'TikTokApi nie jest dostępny'}
            
            # Pobieramy informacje o użytkowniku
            user_info = self.tiktok_api.user(username=username)
            
            # TikTokApi zwraca obiekt User, nie dict
            return {
                'platform': 'TikTok',
                'username': username,
                'followers': getattr(user_info, 'follower_count', 0),
                'following': getattr(user_info, 'following_count', 0),
                'posts': getattr(user_info, 'video_count', 0),
                'likes': getattr(user_info, 'heart_count', 0),
                'is_verified': getattr(user_info, 'verified', False),
                'method': 'TikTokApi'
            }
            
        except Exception as e:
            logger.error(f"Błąd TikTok: {e}")
            # Fallback do scraping
            return self._scrape_tiktok_stats(url)
    
    def check_youtube_stats(self, url: str) -> Dict[str, Any]:
        """Sprawdza statystyki YouTube używając YouTube Data API"""
        try:
            api_key = os.getenv('YOUTUBE_API_KEY')
            if not api_key:
                return {'error': 'Brak YouTube API key'}
            
            # Wyciągamy channel ID lub username
            channel_id = self.extract_username(url, 'youtube')
            if not channel_id:
                return {'error': 'Nie można wyciągnąć channel ID z URL'}
            
            logger.info(f"Sprawdzanie YouTube: {channel_id}")
            
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
            
            # Pobieramy statystyki kanału
            stats_url = f"https://www.googleapis.com/youtube/v3/channels"
            params = {
                'part': 'statistics,snippet',
                'id': channel_id,
                'key': api_key
            }
            
            response = self.session.get(stats_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    channel = data['items'][0]
                    stats = channel.get('statistics', {})
                    snippet = channel.get('snippet', {})
                    
                    return {
                        'platform': 'YouTube',
                        'channel_id': channel_id,
                        'title': snippet.get('title', ''),
                        'subscribers': int(stats.get('subscriberCount', 0)),
                        'videos': int(stats.get('videoCount', 0)),
                        'views': int(stats.get('viewCount', 0)),
                        'is_verified': snippet.get('brandingSettings', {}).get('channel', {}).get('showRelatedChannels', False),
                        'method': 'YouTube Data API'
                    }
                else:
                    return {'error': 'Nie znaleziono kanału YouTube'}
            else:
                return {'error': f'Błąd YouTube API: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Błąd YouTube: {e}")
            return {'error': f'Błąd YouTube: {str(e)}'}
    
    def check_vk_stats(self, url: str) -> Dict[str, Any]:
        """Sprawdza statystyki VK"""
        try:
            username = self.extract_username(url, 'vk')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Sprawdzanie VK: {username}")
            
            if self.vk_session:
                # Używamy VK API
                vk = self.vk_session.get_api()
                
                # Jeśli to ID (cyfry), używamy go bezpośrednio
                if username.isdigit():
                    user_id = username
                else:
                    # Szukamy ID użytkownika po username
                    try:
                        user_info = vk.users.get(user_ids=username, fields='counters')
                        if user_info:
                            user_id = user_info[0]['id']
                        else:
                            return {'error': 'Nie znaleziono użytkownika VK'}
                    except VkApiError as e:
                        return {'error': f'Błąd VK API: {e}'}
                
                # Pobieramy statystyki
                user_info = vk.users.get(user_ids=user_id, fields='counters,verified')
                
                if user_info:
                    user = user_info[0]
                    counters = user.get('counters', {})
                    
                    return {
                        'platform': 'VK',
                        'username': username,
                        'user_id': user_id,
                        'followers': counters.get('followers', 0),
                        'friends': counters.get('friends', 0),
                        'photos': counters.get('photos', 0),
                        'videos': counters.get('videos', 0),
                        'is_verified': user.get('verified', False),
                        'method': 'VK API'
                    }
                else:
                    return {'error': 'Nie znaleziono użytkownika VK'}
            else:
                # Fallback - scraping
                return self._scrape_vk_stats(url)
                
        except Exception as e:
            logger.error(f"Błąd VK: {e}")
            return {'error': f'Błąd VK: {str(e)}'}
    
    def _scrape_tiktok_stats(self, url: str) -> Dict[str, Any]:
        """Fallback scraping dla TikTok"""
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                # Proste parsowanie HTML
                content = response.text
                
                return {
                    'platform': 'TikTok',
                    'username': self.extract_username(url, 'tiktok'),
                    'method': 'scraping',
                    'note': 'Podstawowe informacje z HTML'
                }
            else:
                return {'error': f'Błąd HTTP: {response.status_code}'}
        except Exception as e:
            return {'error': f'Błąd scraping TikTok: {str(e)}'}
    
    def _scrape_vk_stats(self, url: str) -> Dict[str, Any]:
        """Fallback scraping dla VK"""
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                # Proste parsowanie HTML (można ulepszyć)
                content = response.text
                
                # Szukamy podstawowych informacji w HTML
                # To jest bardzo podstawowa implementacja
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
    
    def check_likee_stats(self, url: str) -> Dict[str, Any]:
        """Sprawdza statystyki Likee (scraping)"""
        try:
            username = self.extract_username(url, 'likee')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Sprawdzanie Likee: {username}")
            
            # Likee nie ma oficjalnego API, więc używamy scraping
            response = self.session.get(url)
            if response.status_code == 200:
                # Parsowanie HTML (można ulepszyć)
                content = response.text
                
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
    
    def check_all_platforms(self, urls: Dict[str, str]) -> Dict[str, Any]:
        """Sprawdza statystyki na wszystkich platformach"""
        results = {}
        
        for platform, url in urls.items():
            logger.info(f"Sprawdzanie {platform}: {url}")
            
            try:
                if platform.lower() == 'instagram':
                    results[platform] = self.check_instagram_stats(url)
                elif platform.lower() == 'youtube':
                    results[platform] = self.check_youtube_stats(url)
                elif platform.lower() == 'tiktok':
                    results[platform] = self.check_tiktok_stats(url)
                elif platform.lower() == 'vk':
                    results[platform] = self.check_vk_stats(url)
                elif platform.lower() == 'likee':
                    results[platform] = self.check_likee_stats(url)
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
    print("🔍 ULEPSZONE SPRAWDZANIE STATYSTYK SPOŁECZNOŚCIOWYCH")
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
    checker = EnhancedSocialStatsChecker()
    
    # Sprawdzamy statystyki
    print("📊 Sprawdzanie statystyk...")
    results = checker.check_all_platforms(urls)
    
    # Wyświetlamy wyniki
    print("\n📈 WYNIKI:")
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
    filename = f'social_stats_{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Wyniki zapisane do: {filename}")

if __name__ == "__main__":
    main()
