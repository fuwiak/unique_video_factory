#!/usr/bin/env python3
"""
Daily views report for Google Sheets - adds daily views data with date
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import requests
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

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
        
        # Inicjalizacja Google Sheets
        self.init_google_sheets()
    
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
    
    def get_video_id_from_url(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        try:
            if '/shorts/' in url:
                # YouTube Shorts format: https://www.youtube.com/shorts/VIDEO_ID
                video_id = url.split('/shorts/')[-1].split('?')[0]
            elif 'watch?v=' in url:
                # Standard YouTube format: https://www.youtube.com/watch?v=VIDEO_ID
                video_id = url.split('watch?v=')[-1].split('&')[0]
            else:
                logger.error(f"❌ Nieznany format URL: {url}")
                return None
            return video_id
        except Exception as e:
            logger.error(f"❌ Błąd parsowania URL: {e}")
            return None
    
    def get_video_views(self, video_id: str) -> Dict[str, Any]:
        """Get current views for a video"""
        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'statistics,snippet',
                'id': video_id,
                'key': self.youtube_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
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
        except Exception as e:
            logger.error(f"❌ Błąd pobierania wyświetleń: {e}")
            return None
    
    def add_daily_row(self, video_url: str):
        """Add a new daily row for a video"""
        try:
            if not self.sheet:
                logger.error("❌ Google Sheets nie jest zainicjalizowany")
                return False
            
            # Get video ID from URL
            video_id = self.get_video_id_from_url(video_url)
            if not video_id:
                return False
            
            # Get current views
            video_data = self.get_video_views(video_id)
            if not video_data:
                return False
            
            # Prepare row data
            current_date = datetime.now().strftime('%Y-%m-%d')
            row = [
                video_url,  # Референс (URL)
                video_data['title'],  # Видео
                video_data['published_at'][:10],  # Дата поста
                video_data['views'],  # Кол-во просмотров 1 день
                video_data['views'],  # Кол-во просмотров 1 нед (same for now)
                video_data['views']   # Кол-во просмотров 1 мес (same for now)
            ]
            
            # Add row to sheet (append to end)
            self.sheet.append_row(row)
            
            logger.info(f"✅ Dodano wiersz: {video_data['title']} - {video_data['views']} wyświetleń")
            return True
            
        except Exception as e:
            logger.error(f"❌ Błąd dodawania wiersza: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def process_all_videos(self):
        """Process all videos from sheet"""
        try:
            if not self.sheet:
                logger.error("❌ Google Sheets nie jest zainicjalizowany")
                return False
            
            # Get all rows
            all_rows = self.sheet.get_all_values()
            
            if len(all_rows) < 2:
                logger.info("📋 Brak danych w arkuszu")
                return True
            
            # Process unique video URLs (column A - Референс)
            processed_urls = set()
            for i, row in enumerate(all_rows[1:], start=2):  # Skip header row
                if len(row) > 0 and row[0]:  # Column A has data
                    url = row[0]
                    if url not in processed_urls:
                        processed_urls.add(url)
                        logger.info(f"📊 Przetwarzam wideo {len(processed_urls)}: {url}")
                        self.add_daily_row(url)
            
            logger.info(f"✅ Przetworzono {len(processed_urls)} wideo")
            return True
            
        except Exception as e:
            logger.error(f"❌ Błąd przetwarzania: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


def main():
    """Main function"""
    logger.info("🚀 Uruchamianie daily views reporter")
    
    reporter = DailyViewsReporter()
    
    if not reporter.sheet:
        logger.error("❌ Nie można połączyć z Google Sheets")
        return
    
    # Process all videos
    success = reporter.process_all_videos()
    
    if success:
        logger.info("✅ Raport codzienny zakończony pomyślnie")
    else:
        logger.error("❌ Błąd podczas tworzenia raportu")


if __name__ == "__main__":
    main()

