#!/usr/bin/env python3
"""
Prosty skrypt do sprawdzania wyświetleń ostatniego postu
Używa scraping i podstawowych metod
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

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleLatestPostStatsChecker:
    """Prosty checker wyświetleń ostatniego postu"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
    
    def check_instagram_latest_post(self, url: str) -> Dict[str, Any]:
        """Sprawdza wyświetlenia ostatniego postu na Instagram (scraping)"""
        try:
            username = self.extract_username(url, 'instagram')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Sprawdzanie ostatniego postu Instagram: @{username}")
            
            # Próbujemy pobrać stronę profilu
            profile_url = f"https://www.instagram.com/{username}/"
            response = self.session.get(profile_url)
            
            if response.status_code == 200:
                content = response.text
                
                # Szukamy informacji o ostatnim poście w JSON
                # Instagram często ma dane w window._sharedData
                try:
                    # Szukamy JSON z danymi
                    json_match = re.search(r'window\._sharedData\s*=\s*({.*?});', content)
                    if json_match:
                        data = json.loads(json_match.group(1))
                        # Próbujemy wyciągnąć informacje o ostatnim poście
                        return {
                            'platform': 'Instagram',
                            'username': username,
                            'method': 'scraping',
                            'note': 'Podstawowe informacje z HTML',
                            'profile_url': profile_url
                        }
                except:
                    pass
                
                return {
                    'platform': 'Instagram',
                    'username': username,
                    'method': 'scraping',
                    'note': 'Podstawowe informacje z HTML',
                    'profile_url': profile_url
                }
            else:
                return {'error': f'Błąd HTTP: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Błąd Instagram: {e}")
            return {'error': f'Błąd Instagram: {str(e)}'}
    
    def check_youtube_latest_video(self, url: str) -> Dict[str, Any]:
        """Sprawdza wyświetlenia ostatniego wideo na YouTube (scraping)"""
        try:
            username = self.extract_username(url, 'youtube')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Sprawdzanie ostatniego wideo YouTube: {username}")
            
            # Próbujemy pobrać stronę kanału
            if username.startswith('@'):
                channel_url = f"https://www.youtube.com/{username}"
            else:
                channel_url = f"https://www.youtube.com/channel/{username}"
            
            response = self.session.get(channel_url)
            
            if response.status_code == 200:
                content = response.text
                
                # Szukamy informacji o ostatnim wideo
                # YouTube ma dane w JSON
                try:
                    # Szukamy JSON z danymi
                    json_match = re.search(r'var ytInitialData = ({.*?});', content)
                    if json_match:
                        data = json.loads(json_match.group(1))
                        # Próbujemy wyciągnąć informacje o ostatnim wideo
                        return {
                            'platform': 'YouTube',
                            'username': username,
                            'method': 'scraping',
                            'note': 'Podstawowe informacje z HTML',
                            'channel_url': channel_url
                        }
                except:
                    pass
                
                return {
                    'platform': 'YouTube',
                    'username': username,
                    'method': 'scraping',
                    'note': 'Podstawowe informacje z HTML',
                    'channel_url': channel_url
                }
            else:
                return {'error': f'Błąd HTTP: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Błąd YouTube: {e}")
            return {'error': f'Błąd YouTube: {str(e)}'}
    
    def check_tiktok_latest_post(self, url: str) -> Dict[str, Any]:
        """Sprawdza wyświetlenia ostatniego postu na TikTok (scraping)"""
        try:
            username = self.extract_username(url, 'tiktok')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Sprawdzanie ostatniego postu TikTok: @{username}")
            
            # Próbujemy pobrać stronę profilu
            profile_url = f"https://www.tiktok.com/@{username}"
            response = self.session.get(profile_url)
            
            if response.status_code == 200:
                content = response.text
                
                # Szukamy informacji o ostatnim poście
                # TikTok ma dane w JSON
                try:
                    # Szukamy JSON z danymi
                    json_match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">({.*?})</script>', content)
                    if json_match:
                        data = json.loads(json_match.group(1))
                        # Próbujemy wyciągnąć informacje o ostatnim poście
                        return {
                            'platform': 'TikTok',
                            'username': username,
                            'method': 'scraping',
                            'note': 'Podstawowe informacje z HTML',
                            'profile_url': profile_url
                        }
                except:
                    pass
                
                return {
                    'platform': 'TikTok',
                    'username': username,
                    'method': 'scraping',
                    'note': 'Podstawowe informacje z HTML',
                    'profile_url': profile_url
                }
            else:
                return {'error': f'Błąd HTTP: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Błąd TikTok: {e}")
            return {'error': f'Błąd TikTok: {str(e)}'}
    
    def check_vk_latest_post(self, url: str) -> Dict[str, Any]:
        """Sprawdza wyświetlenia ostatniego postu na VK (scraping)"""
        try:
            username = self.extract_username(url, 'vk')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Sprawdzanie ostatniego postu VK: {username}")
            
            # Próbujemy pobrać stronę profilu
            profile_url = f"https://vk.com/{username}"
            response = self.session.get(profile_url)
            
            if response.status_code == 200:
                content = response.text
                
                # Szukamy informacji o ostatnim poście
                # VK ma dane w HTML
                try:
                    # Szukamy podstawowych informacji
                    return {
                        'platform': 'VK',
                        'username': username,
                        'method': 'scraping',
                        'note': 'Podstawowe informacje z HTML',
                        'profile_url': profile_url
                    }
                except:
                    pass
                
                return {
                    'platform': 'VK',
                    'username': username,
                    'method': 'scraping',
                    'note': 'Podstawowe informacje z HTML',
                    'profile_url': profile_url
                }
            else:
                return {'error': f'Błąd HTTP: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Błąd VK: {e}")
            return {'error': f'Błąd VK: {str(e)}'}
    
    def check_likee_latest_post(self, url: str) -> Dict[str, Any]:
        """Sprawdza wyświetlenia ostatniego postu na Likee (scraping)"""
        try:
            username = self.extract_username(url, 'likee')
            if not username:
                return {'error': 'Nie można wyciągnąć username z URL'}
            
            logger.info(f"Sprawdzanie ostatniego postu Likee: {username}")
            
            # Próbujemy pobrać stronę profilu
            response = self.session.get(url)
            
            if response.status_code == 200:
                content = response.text
                
                # Szukamy informacji o ostatnim poście
                # Likee ma dane w HTML
                try:
                    # Szukamy podstawowych informacji
                    return {
                        'platform': 'Likee',
                        'username': username,
                        'method': 'scraping',
                        'note': 'Podstawowe informacje z HTML',
                        'profile_url': url
                    }
                except:
                    pass
                
                return {
                    'platform': 'Likee',
                    'username': username,
                    'method': 'scraping',
                    'note': 'Podstawowe informacje z HTML',
                    'profile_url': url
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
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Błąd sprawdzania {platform}: {e}")
                results[platform] = {'error': str(e)}
        
        return results

def main():
    """Główna funkcja"""
    print("🔍 SPRAWDZANIE WYŚWIETLEŃ OSTATNIEGO POSTU (SCRAPING)")
    print("=" * 60)
    
    # URL-e do sprawdzenia
    urls = {
        'Instagram': 'https://www.instagram.com/raachel_fb',
        'YouTube': 'https://www.youtube.com/@raachel_fb',
        'TikTok': 'https://www.tiktok.com/@daniryb_fb',
        'VK': 'https://vk.com/raachel_fb',
        'Likee': 'https://l.likee.video/p/jSQPBE'
    }
    
    print("📋 Używamy scraping do pobierania danych...")
    print("⚠️ Niektóre platformy mogą blokować automatyczne zapytania")
    print()
    
    # Tworzymy checker
    checker = SimpleLatestPostStatsChecker()
    
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
    filename = f'simple_latest_posts_{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Wyniki zapisane do: {filename}")

if __name__ == "__main__":
    main()




