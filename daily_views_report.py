#!/usr/bin/env python3
"""
Daily views report for Google Sheets - adds daily views data with date
"""
import argparse
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import gspread
import requests
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

from advanced_social_stats import AdvancedSocialStatsChecker
from sync_tiktok_views_to_sheets import (  # type: ignore[import]
    fetch_tiktok_video_stats,
    load_apify_client,
)

# Ładujemy zmienne środowiskowe
load_dotenv()

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DailyViewsReporter:
    """Raport codziennych wyświetleń dla Google Sheets"""
    
    def __init__(self):
        self.sheet_id = "1dU9dv4R2-POC_VDlX7U4l_qkla23iZ4SxboLn66XXPw"
        self.credentials_file = "google_credentials.json"
        self.sheet = None
        self.gc = None
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.apify_client = None
        
        # Inicjalizacja Google Sheets
        self.init_google_sheets()
        
        # Inicjalizacja AdvancedSocialStatsChecker dla innych platform
        self.social_stats_checker = AdvancedSocialStatsChecker()
    
    def init_google_sheets(self):
        """Inicjalizacja Google Sheets"""
        try:
            # Sprawdzamy czy mamy zmienne środowiskowe
            if self._init_from_env():
                return True
            
            # Sprawdzamy czy mamy plik credentials
            if not os.path.exists(self.credentials_file):
                logger.error(f"❌ Nie znaleziono pliku {self.credentials_file}")
                return False
            
            # Ładujemy credentials z pliku
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=scope
            )
            
            # Łączymy się z Google Sheets
            self.gc = gspread.authorize(creds)
            self.sheet = self.gc.open_by_key(self.sheet_id).sheet1
            
            logger.info("✅ Google Sheets połączone pomyślnie")
            return True
            
        except Exception as e:
            logger.error(f"❌ Błąd inicjalizacji Google Sheets: {e}")
            return False
    
    def _init_from_env(self):
        """Inicjalizacja Google Sheets ze zmiennych środowiskowych"""
        try:
            required_vars = [
                'GOOGLE_PROJECT_ID',
                'GOOGLE_PRIVATE_KEY_ID', 
                'GOOGLE_PRIVATE_KEY',
                'GOOGLE_CLIENT_EMAIL',
                'GOOGLE_CLIENT_ID'
            ]
            
            for var in required_vars:
                if not os.getenv(var):
                    return False
            
            credentials_data = {
                "type": "service_account",
                "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
                "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),
                "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('GOOGLE_CLIENT_EMAIL')}"
            }
            
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_info(credentials_data, scopes=scope)
            self.gc = gspread.authorize(creds)
            self.sheet = self.gc.open_by_key(self.sheet_id).sheet1
            
            logger.info("✅ Google Sheets połączone pomyślnie (ze zmiennych środowiskowych)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Błąd inicjalizacji Google Sheets ze zmiennych środowiskowych: {e}")
            return False
    
    def get_platform_from_url(self, url: str) -> str:
        """Rozpoznaje platformę z URL"""
        url_lower = url.lower()
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'vk.com' in url_lower:
            return 'vk'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        else:
            return 'unknown'
    
    def get_video_id_from_url(self, url: str) -> Optional[str]:
        """Extract video ID from URL (YouTube, Instagram, VK)"""
        try:
            platform = self.get_platform_from_url(url)
            
            if platform == 'youtube':
                if '/shorts/' in url:
                    video_id = url.split('/shorts/')[-1].split('?')[0]
                elif 'watch?v=' in url:
                    video_id = url.split('watch?v=')[-1].split('&')[0]
                else:
                    return None
                return video_id
            elif platform == 'instagram':
                # Instagram Reels format: https://www.instagram.com/reels/VIDEO_ID/
                reel_id = self.social_stats_checker._extract_instagram_reel_id(url)
                return reel_id
            elif platform == 'vk':
                # VK Clips format: https://vk.com/clips/id1069245351?z=clip1069245351_VIDEO_ID
                video_id = self.social_stats_checker._extract_vk_video_id(url)
                return video_id
            else:
                logger.warning(f"⚠️ Nieznana platforma dla URL: {url}")
                return None
        except Exception as e:
            logger.error(f"❌ Błąd parsowania URL: {e}")
            return None
    
    def get_video_views(self, url: str, video_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get current views for a video from any platform"""
        try:
            platform = self.get_platform_from_url(url)
            
            if platform == 'youtube':
                if not video_id:
                    video_id = self.get_video_id_from_url(url)
                if not video_id:
                    return None
                    
                youtube_url = "https://www.googleapis.com/youtube/v3/videos"
                params = {
                    'part': 'statistics,snippet',
                    'id': video_id,
                    'key': self.youtube_api_key
                }
                
                response = requests.get(youtube_url, params=params, timeout=10)
                if response.status_code != 200:
                    logger.error(f"❌ Błąd API YouTube: {response.status_code}")
                    return None
                
                data = response.json()
                if not data.get('items'):
                    logger.error(f"❌ Nie znaleziono wideo: {video_id}")
                    return None
                
                video = data['items'][0]
                return {
                    'video_id': video_id,
                    'views': int(video['statistics'].get('viewCount', 0)),
                    'title': video['snippet'].get('title', ''),
                    'published_at': video['snippet'].get('publishedAt', '')
                }
            
            elif platform == 'instagram':
                # Pobieramy dane Instagram Reel
                logger.info(f"📊 Pobieram dane Instagram Reel: {url}")
                reel_data = self.social_stats_checker.get_instagram_reel_data(url)
                
                if 'error' in reel_data:
                    logger.warning(f"⚠️ Błąd pobierania Instagram Reel: {reel_data['error']}")
                    return None
                
                # Instagram nie zwraca wyświetleń przez yt-dlp, więc używamy 0
                # W przyszłości można dodać scraping lub API
                reel = reel_data.get('reels', [{}])[0] if reel_data.get('reels') else {}
                return {
                    'video_id': reel_data.get('reel_id', ''),
                    'views': 0,  # Instagram nie udostępnia wyświetleń publicznie
                    'title': f"Instagram Reel {reel_data.get('reel_id', '')}",
                    'published_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                }
            
            elif platform == 'vk':
                # Pobieramy dane VK Clip
                logger.info(f"📊 Pobieram dane VK Clip: {url}")
                clip_data = self.social_stats_checker.get_vk_clip_data(url)
                
                if 'error' in clip_data:
                    logger.warning(f"⚠️ Błąd pobierania VK Clip: {clip_data['error']}")
                    return None
                
                clip = clip_data.get('clips', [{}])[0] if clip_data.get('clips') else {}
                return {
                    'video_id': clip.get('video_id', ''),
                    'views': clip.get('views', 0),
                    'title': clip.get('title', f"VK Clip {clip.get('video_id', '')}"),
                    'published_at': clip.get('date', datetime.now().strftime('%Y-%m-%d'))
                }
            
            elif platform == 'tiktok':
                logger.info(f"📊 Pobieram dane TikTok: {url}")
                if not self.apify_client:
                    try:
                        self.apify_client = load_apify_client()
                    except Exception as exc:
                        logger.warning(
                            "⚠️ Nie można zainicjalizować Apify clienta dla TikTok: %s",
                            exc,
                        )
                        return None

                try:
                    stats = fetch_tiktok_video_stats(self.apify_client, [url])
                except Exception as exc:
                    logger.warning(f"⚠️ Błąd pobierania danych TikTok: {exc}")
                    return None

                if not stats:
                    logger.warning("⚠️ Brak danych TikTok dla URL: %s", url)
                    return None

                entry = stats[0]
                views = entry.get('views')
                if views is None:
                    logger.warning("⚠️ Brak liczby wyświetleń TikTok dla URL: %s", url)
                    return {
                        'video_id': entry.get('id') or entry.get('url') or url,
                        'views': '⚠️ Контент доступен только авторизованным пользователям',
                        'title': entry.get('caption', '') or 'TikTok Video',
                        'published_at': (
                            entry.get('create_time')
                            or datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                        ),
                    }

                return {
                    'video_id': entry.get('id') or entry.get('url') or url,
                    'views': int(views),
                    'title': entry.get('caption', '') or 'TikTok Video',
                    'published_at': (
                        entry.get('create_time')
                        or datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                    ),
                }

            else:
                logger.warning(f"⚠️ Nieobsługiwana platforma: {platform}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Błąd pobierania wyświetleń: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def ensure_date_header(self, sheet):
        """Ensure 'Дата добавления записи' header exists in sheet"""
        try:
            all_rows = sheet.get_all_values()
            if len(all_rows) > 0:
                headers = all_rows[0]
                # Check if header exists
                header_exists = any('Дата добавления' in str(h) for h in headers)
                if not header_exists:
                    # Add header
                    headers.append('Дата добавления записи')
                    sheet.update(values=[headers], range_name='A1')
                    logger.info(f"📝 Dodano nagłówek 'Дата добавления записи' do arkusza")
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ Błąd dodawania nagłówka: {e}")
            return False
    
    def add_daily_row(self, sheet, video_url: str, published_date: str = None):
        """Add a new daily row for a video to specific sheet"""
        try:
            if not sheet:
                logger.error("❌ Arkusz nie jest zainicjalizowany")
                return False
            
            original_url = video_url
            video_url = self.normalize_video_url(video_url)
            if video_url != original_url:
                logger.info(f"🔄 Zamieniono URL {original_url} -> {video_url}")
            
            # Get current views (metoda get_video_views przyjmuje teraz URL bezpośrednio)
            video_data = self.get_video_views(video_url)
            if not video_data:
                logger.warning(f"⚠️ Nie można pobrać danych dla: {video_url}")
                return False
            
            # Use published date from video or provided date
            post_date = published_date or (video_data['published_at'][:10] if video_data.get('published_at') else datetime.now().strftime('%Y-%m-%d'))
            
            # Get current date and time for "Дата добавления записи"
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Prepare row data with additional column for "Дата добавления записи"
            row = [
                '',  # Референс (puste)
                video_url,  # Видео (URL)
                post_date,  # Дата поста
                video_data['views'],  # Кол-во просмотров 1 день (dzisiejsze wyświetlenia)
                video_data['views'],  # Кол-во просмотров 1 нед (same for now)
                video_data['views'],  # Кол-во просмотров 1 мес (same for now)
                current_datetime  # Дата добавления записи (new column)
            ]
            
            # Add row to sheet (append to end)
            sheet.append_row(row)
            
            logger.info(f"✅ Dodano wiersz: {video_url} - {video_data['views']} wyświetleń - {current_datetime}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Błąd dodawania wiersza dla {video_url}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def process_sheet(self, sheet_name: str, spreadsheet=None) -> int:
        """Process all unique video URLs in a specific sheet."""
        if not self.gc:
            logger.error("❌ Google Sheets client nie jest zainicjalizowany")
            return 0

        try:
            if spreadsheet is None:
                spreadsheet = self.gc.open_by_key(self.sheet_id)

            sheet = spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            logger.error(f"❌ Nie znaleziono arkusza: {sheet_name}")
            return 0
        except Exception as exc:
            logger.error(f"❌ Błąd otwierania arkusza {sheet_name}: {exc}")
            return 0

        logger.info(f"📊 Przetwarzam arkusz: {sheet_name}")

        self.ensure_date_header(sheet)

        all_rows = sheet.get_all_values()
        if len(all_rows) < 2:
            logger.info(f"📋 Arkusz {sheet_name} jest pusty")
            return 0

        headers = all_rows[0]
        video_col_index = None
        date_col_index = None

        for i, header in enumerate(headers):
            if 'Видео' in header or 'Video' in header:
                video_col_index = i
            if 'Дата поста' in header or 'Дата' in header:
                date_col_index = i

        if video_col_index is None:
            logger.warning(f"⚠️ Nie znaleziono kolumny 'Видео' w arkuszu {sheet_name}")
            return 0

        processed_urls = set()
        for row in all_rows[1:]:  # Skip header row
            if len(row) > video_col_index and row[video_col_index]:
                url = row[video_col_index].strip()
                if url.startswith('http') and url not in processed_urls:
                    processed_urls.add(url)
                    published_date = (
                        row[date_col_index].strip()
                        if date_col_index is not None and len(row) > date_col_index and row[date_col_index]
                        else None
                    )
                    logger.info(
                        f"📊 Przetwarzam wideo {len(processed_urls)} z {sheet_name}: {url}"
                    )
                    self.add_daily_row(sheet, url, published_date)

        logger.info(f"✅ Arkusz {sheet_name}: przetworzono {len(processed_urls)} wideo")
        return len(processed_urls)

    def process_all_videos(self):
        """Process all videos from all sheets dynamically"""
        try:
            if not self.gc:
                logger.error("❌ Google Sheets client nie jest zainicjalizowany")
                return False

            spreadsheet = self.gc.open_by_key(self.sheet_id)
            all_sheets = spreadsheet.worksheets()
            sheet_names = [sheet.title for sheet in all_sheets]

            logger.info(f"📋 Znaleziono {len(sheet_names)} arkuszy: {', '.join(sheet_names)}")

            total_processed = 0
            for sheet_name in sheet_names:
                try:
                    total_processed += self.process_sheet(sheet_name, spreadsheet=spreadsheet)
                except Exception as e:
                    logger.error(f"❌ Błąd przetwarzania arkusza {sheet_name}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    continue

            logger.info(f"✅ Łącznie przetworzono {total_processed} wideo ze wszystkich arkuszy")
            return True

        except Exception as e:
            logger.error(f"❌ Błąd przetwarzania: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def normalize_video_url(self, url: str) -> str:
        """Normalizuje URL przed pobraniem danych (np. konwersja VK wall -> clip)."""
        try:
            if 'vk.com/wall' in url and 'clip' not in url:
                converted = self.social_stats_checker.convert_vk_wall_to_clip_url(url)
                if converted:
                    return converted
        except Exception as exc:
            logger.warning(f"⚠️ Nie udało się znormalizować URL {url}: {exc}")
        return url


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append daily view stats for videos stored in Google Sheets."
    )
    parser.add_argument(
        "--sheet",
        dest="sheets",
        action="append",
        help="Optional sheet title to process. Repeat for multiple sheets. Default: all sheets.",
    )
    return parser.parse_args()


def main():
    """Main function"""
    args = parse_args()
    logger.info("🚀 Uruchamianie daily views reporter")

    reporter = DailyViewsReporter()

    if not reporter.gc:
        logger.error("❌ Nie można połączyć z Google Sheets")
        return

    if args.sheets:
        spreadsheet = reporter.gc.open_by_key(reporter.sheet_id)
        total_processed = 0
        for sheet_name in args.sheets:
            total_processed += reporter.process_sheet(sheet_name, spreadsheet=spreadsheet)
        if total_processed:
            logger.info(
                f"✅ Zakończono przetwarzanie {len(args.sheets)} arkuszy. Łącznie {total_processed} wideo."
            )
        else:
            logger.warning("⚠️ Nie przetworzono żadnych wideo - sprawdź nazwy arkuszy i dane")
    else:
        success = reporter.process_all_videos()
        if success:
            logger.info("✅ Raport codzienny zakończony pomyślnie")
        else:
            logger.error("❌ Błąd podczas tworzenia raportu")


if __name__ == "__main__":
    main()

