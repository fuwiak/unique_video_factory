#!/usr/bin/env python3
"""
Integracja z Google Sheets dla zapisywania statystyk
"""

import os
import json
import time
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

class GoogleSheetsIntegration:
    """Integracja z Google Sheets"""
    
    def __init__(self):
        self.sheet_id = "1dU9dv4R2-POC_VDlX7U4l_qkla23iZ4SxboLn66XXPw"
        self.credentials_file = "google_credentials.json"
        self.sheet = None
        self.gc = None  # Google Sheets client
        
        # Inicjalizacja Google Sheets
        success = self.init_google_sheets()
        if not success:
            logger.warning("Google Sheets nie zostało zainicjalizowane - funkcje zapisu będą niedostępne")
    
    def _init_from_env(self):
        """Inicjalizacja Google Sheets ze zmiennych środowiskowych"""
        try:
            # Sprawdzamy czy mamy wszystkie wymagane zmienne
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
            
            # Tworzymy credentials ze zmiennych środowiskowych
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
            
            # Zakres uprawnień
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Ładujemy credentials
            creds = Credentials.from_service_account_info(
                credentials_data, 
                scopes=scope
            )
            
            # Łączymy się z Google Sheets
            self.gc = gspread.authorize(creds)
            self.sheet = self.gc.open_by_key(self.sheet_id).sheet1
            
            logger.info("Google Sheets połączone pomyślnie (ze zmiennych środowiskowych)")
            return True
            
        except Exception as e:
            logger.error(f"Błąd inicjalizacji Google Sheets ze zmiennych środowiskowych: {e}")
            return False
    
    def init_google_sheets(self):
        """Inicjalizacja Google Sheets"""
        try:
            # Sprawdzamy czy mamy zmienne środowiskowe dla Google Sheets
            if self._init_from_env():
                return True
            
            # Sprawdzamy czy mamy plik credentials
            if not os.path.exists(self.credentials_file):
                logger.error(f"Brak pliku {self.credentials_file} i zmiennych środowiskowych")
                return False
            
            # Zakres uprawnień
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Ładujemy credentials
            creds = Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=scope
            )
            
            # Łączymy się z Google Sheets
            self.gc = gspread.authorize(creds)
            self.sheet = self.gc.open_by_key(self.sheet_id).sheet1
            
            logger.info("Google Sheets połączone pomyślnie")
            return True
            
        except Exception as e:
            logger.error(f"Błąd inicjalizacji Google Sheets: {e}")
            self.sheet = None
            return False
    
    def prepare_headers(self):
        """Przygotowuje nagłówki kolumn"""
        headers = [
            "Видео", 
            "Дата поста",
            "Кол-во просмотров 1 день",
            "Кол-во просмотров 1 нед",
            "Кол-во просмотров 1 мес"
        ]
        return headers
    
    def calculate_historical_views(self, current_views: int, platform: str) -> Dict[str, int]:
        """Oblicza wyświetlenia z wczoraj i tygodnia temu (symulacja)"""
        # Symulujemy realistyczne dane historyczne
        import random
        
        if platform.lower() == 'vk_clips':
            # VK Clips - mniejsze liczby, wolniejszy wzrost
            daily_growth = random.randint(1, 3)  # 1-3 wyświetlenia dziennie
            weekly_growth = random.randint(5, 15)  # 5-15 wyświetleń tygodniowo
            
            yesterday_views = max(0, current_views - daily_growth)
            week_ago_views = max(0, current_views - weekly_growth)
        else:
            # YouTube - większe liczby, szybszy wzrost
            daily_growth = random.randint(10, 50)  # 10-50 wyświetleń dziennie
            weekly_growth = random.randint(100, 300)  # 100-300 wyświetleń tygodniowo
            
            yesterday_views = max(0, current_views - daily_growth)
            week_ago_views = max(0, current_views - weekly_growth)
        
        return {
            'yesterday': yesterday_views,
            'week_ago': week_ago_views
        }
    
    def calculate_percentage_change(self, current: int, previous: int) -> float:
        """Oblicza procentową zmianę"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)
    
    def format_data_for_sheets(self, data: Dict[str, Any]) -> List[List[str]]:
        """Formatuje dane dla Google Sheets - nowa struktura"""
        logger.info(f"🔍 Formatuję dane dla Google Sheets: {data}")
        rows = []
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        for platform, platform_data in data.items():
            logger.info(f"📊 Przetwarzam platformę: {platform}")
            logger.info(f"📋 Dane platformy: {platform_data}")
            
            if 'error' in platform_data:
                logger.warning(f"❌ Platforma {platform} ma błąd: {platform_data['error']}")
                continue
            
            platform_name = platform_data.get('platform', platform)
            user_name = platform_data.get('user_name', platform_data.get('username', ''))
            
            # Sprawdzamy czy mamy clips/videos/shorts/reels
            has_clips_list = 'clips' in platform_data and isinstance(platform_data.get('clips'), list)
            has_videos_list = 'videos' in platform_data and isinstance(platform_data.get('videos'), list)
            has_shorts_list = 'shorts' in platform_data and isinstance(platform_data.get('shorts'), list)
            has_reels_list = 'reels' in platform_data and isinstance(platform_data.get('reels'), list)

            logger.info(f"🔍 Sprawdzam strukturę danych:")
            logger.info(f"  - has_clips_list: {has_clips_list}")
            logger.info(f"  - has_videos_list: {has_videos_list}")
            logger.info(f"  - has_shorts_list: {has_shorts_list}")
            logger.info(f"  - has_reels_list: {has_reels_list}")
            
            if has_clips_list:
                logger.info(f"📹 Przetwarzam VK clips: {len(platform_data['clips'])} clips")
                # Przetwarzamy VK clips
                for i, clip in enumerate(platform_data['clips']):
                    logger.info(f"📹 Clip {i+1}: {clip}")
                    row = [
                        '',  # Референс (zawsze pusty)
                        platform_data.get('url', ''),  # Видео (URL)
                        clip.get('date', current_date)[:10],  # Дата поста
                        str(clip.get('views', 0)),     # Кол-во просмотров 1 день
                        str(clip.get('views', 0)),     # Кол-во просмотров 1 нед (brak danych historycznych)
                        str(clip.get('views', 0))      # Кол-во просмотров 1 мес (brak danych historycznych)
                    ]
                    logger.info(f"📝 Utworzono wiersz dla clip {i+1}: {row}")
                    rows.append(row)
            
            elif has_videos_list:
                # Przetwarzamy YouTube videos
                for video in platform_data['videos']:
                    row = [
                        '',  # Референс (zawsze pusty)
                        platform_data.get('url', ''),  # Видео (URL)
                        video.get('date', current_date)[:10],  # Дата поста
                        str(video.get('views', 0)),    # Кол-во просмотров 1 день
                        str(video.get('views', 0)),   # Кол-во просмотров 1 нед (brak danych historycznych)
                        str(video.get('views', 0))    # Кол-во просмотров 1 мес (brak danych historycznych)
                    ]
                    rows.append(row)
            
            elif has_shorts_list:
                # Przetwarzamy YouTube shorts
                logger.info(f"📹 Przetwarzam YouTube shorts: {len(platform_data['shorts'])} shorts")
                for short in platform_data['shorts']:
                    row = [
                        '',  # Референс (zawsze pusty)
                        short.get('url', platform_data.get('url', '')),  # Видео (URL)
                        short.get('published_at', current_date)[:10],  # Дата поста
                        str(short.get('views', 0)),    # Кол-во просмотров 1 день
                        str(short.get('views', 0)),   # Кол-во просмотров 1 нед (brak danych historycznych)
                        str(short.get('views', 0))    # Кол-во просмотров 1 мес (brak danych historycznych)
                    ]
                    rows.append(row)
            
            elif has_reels_list:
                # Przetwarzamy Instagram reels
                logger.info(f"📹 Przetwarzam Instagram reels: {len(platform_data['reels'])} reels")
                for reel in platform_data['reels']:
                    logger.info(f"📹 Reel: {reel}")
                    # Dla Instagram reels używamy URL z reels lub video_path jeśli dostępny
                    video_url = reel.get('url', platform_data.get('url', ''))
                    row = [
                        '',  # Референс (zawsze pusty)
                        video_url,  # Видео (URL)
                        current_date,  # Дата поста (nie mamy daty z reels, używamy dzisiejszej)
                        '0',  # Кол-во просмотров 1 день (nie mamy danych o wyświetleniach)
                        '0',  # Кол-во просмотров 1 нед
                        '0'   # Кол-во просмотров 1 мес
                    ]
                    logger.info(f"📝 Utworzono wiersz dla reel: {row}")
                    rows.append(row)
            
            else:
                # Brak danych do przetworzenia
                logger.warning(f"⚠️ Brak clips/videos/shorts/reels dla {platform}")
                logger.info(f"🔍 Dostępne klucze: {list(platform_data.keys())}")
        
        logger.info(f"📊 Łącznie utworzono {len(rows)} wierszy")
        return rows
    
    def get_or_create_blogger_sheet(self, blogger_name: str):
        """Pobiera lub tworzy arkusz dla blogera"""
        try:
            if not self.gc:
                logger.error("Google Sheets client nie jest zainicjalizowany")
                return None
            
            # Otwieramy główny spreadsheet
            spreadsheet = self.gc.open_by_key(self.sheet_id)
            
            # Sprawdzamy czy arkusz dla blogera już istnieje
            try:
                sheet = spreadsheet.worksheet(blogger_name)
                logger.info(f"Znaleziono istniejący arkusz dla {blogger_name}")
                return sheet
            except gspread.WorksheetNotFound:
                # Tworzymy nowy arkusz
                logger.info(f"Tworzenie nowego arkusza dla {blogger_name}")
                sheet = spreadsheet.add_worksheet(title=blogger_name, rows=1000, cols=20)
                
                # Dodajemy nagłówki
                headers = self.prepare_headers()
                sheet.append_row(headers)
                
                logger.info(f"Utworzono arkusz {blogger_name} z nagłówkami")
                return sheet
                
        except Exception as e:
            logger.error(f"Błąd pobierania/tworzenia arkusza dla {blogger_name}: {e}")
            return None
    
    def save_to_blogger_sheet(self, blogger_name: str, data: Dict[str, Any]) -> bool:
        """Zapisuje dane do arkusza konkretnego blogera"""
        try:
            logger.info(f"🔍 Rozpoczynam zapisywanie do arkusza '{blogger_name}'")
            logger.info(f"📊 Dane do zapisania: {data}")
            
            # Pobieramy lub tworzymy arkusz dla blogera
            sheet = self.get_or_create_blogger_sheet(blogger_name)
            if not sheet:
                logger.error(f"❌ Nie można pobrać/utworzyć arkusza dla '{blogger_name}'")
                return False
            
            logger.info(f"✅ Arkusz '{blogger_name}' gotowy")
            
            # Przygotowujemy dane
            logger.info(f"📝 Formatuję dane dla arkusza...")
            rows = self.format_data_for_sheets(data)
            logger.info(f"📊 Sformatowane wiersze: {rows}")
            
            if not rows:
                logger.warning("⚠️ Brak danych do zapisania - format_data_for_sheets zwrócił pustą listę")
                logger.info(f"🔍 Szczegóły danych: {data}")
                return False
            
            logger.info(f"✅ Znaleziono {len(rows)} wierszy do zapisania")
            
            # Dodajemy dane do arkusza blogera
            for i, row in enumerate(rows):
                logger.info(f"📝 Dodaję wiersz {i+1}: {row}")
                sheet.append_row(row)
                logger.info(f"✅ Dodano wiersz {i+1} do arkusza {blogger_name}")
            
            logger.info(f"🎉 Pomyślnie zapisano {len(rows)} wierszy do arkusza {blogger_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Błąd zapisywania do arkusza {blogger_name}: {e}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return False
    
    def save_to_sheets(self, data: Dict[str, Any]) -> bool:
        """Zapisuje dane do Google Sheets"""
        try:
            if not self.sheet:
                logger.error("Google Sheets nie jest zainicjalizowane - sprawdź plik google_credentials.json i uprawnienia")
                return False
            
            # Przygotowujemy dane
            rows = self.format_data_for_sheets(data)
            
            if not rows:
                logger.warning("Brak danych do zapisania")
                return False
            
            # Zawsze dodajemy nagłówki na początku (jeśli arkusz jest pusty)
            if not self.sheet.get_all_values():
                headers = self.prepare_headers()
                self.sheet.append_row(headers)
                logger.info("Добавлены заголовки в таблицу")
            
            # Dodajemy dane
            for row in rows:
                self.sheet.append_row(row)
                logger.info(f"Добавлена строка: {row[1]} - {row[3][:50]}...")
            
            logger.info(f"Успешно сохранено {len(rows)} строк в Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"Błąd zapisywania do Google Sheets: {e}")
            return False
    
    def get_sheet_data(self) -> List[List[str]]:
        """Pobiera dane z arkusza"""
        try:
            if not self.sheet:
                return []
            
            return self.sheet.get_all_values()
            
        except Exception as e:
            logger.error(f"Błąd pobierania danych z arkusza: {e}")
            return []

def create_google_credentials_template():
    """Tworzy szablon pliku credentials dla Google"""
    template = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }
    
    with open("google_credentials_template.json", "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2)
    
    print("📄 Utworzono szablon google_credentials_template.json")
    print("📝 Skopiuj go do google_credentials.json i wypełnij danymi z Google Cloud Console")

def main():
    """Główna funkcja testowa"""
    print("🔗 INTEGRACJA Z GOOGLE SHEETS")
    print("=" * 50)
    
    # Sprawdzamy czy mamy plik credentials
    if not os.path.exists("google_credentials.json"):
        print("❌ Brak pliku google_credentials.json")
        print("📄 Tworzę szablon...")
        create_google_credentials_template()
        print("\n📋 Instrukcje:")
        print("1. Idź do Google Cloud Console")
        print("2. Utwórz Service Account")
        print("3. Pobierz JSON credentials")
        print("4. Skopiuj do google_credentials.json")
        print("5. Uruchom ponownie")
        return
    
    # Tworzymy integrację
    integration = GoogleSheetsIntegration()
    
    if not integration.sheet:
        print("❌ Nie udało się połączyć z Google Sheets")
        return
    
    # Testujemy z przykładowymi danymi
    test_data = {
        "VK_Clips": {
            "platform": "VK Clips",
            "username": "raachel_fb",
            "user_name": "Reychel K",
            "total_views": 47,
            "clips_count": 10,
            "clips": [
                {
                    "title": "Test Clip",
                    "views": 5,
                    "date": "2025-10-15 13:07:36"
                }
            ]
        },
        "YouTube": {
            "platform": "YouTube",
            "username": "raachel_fb",
            "channel_title": "Рэйчел🍕",
            "total_views": 9157,
            "videos_count": 10,
            "videos": [
                {
                    "title": "Test Video",
                    "views": 100,
                    "date": "2025-10-15T13:07:36Z"
                }
            ]
        }
    }
    
    # Zapisujemy do arkusza
    success = integration.save_to_sheets(test_data)
    
    if success:
        print("✅ Dane zapisane do Google Sheets!")
    else:
        print("❌ Błąd zapisywania do Google Sheets")

if __name__ == "__main__":
    main()
