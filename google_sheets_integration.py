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
        self.sheet_id = "1p6bQ3Ck7qMv8M6vobXQcnEjXXdECAoBOlmy2_n9sUPI"
        self.credentials_file = "google_credentials.json"
        self.sheet = None
        
        # Inicjalizacja Google Sheets
        self.init_google_sheets()
    
    def init_google_sheets(self):
        """Inicjalizacja Google Sheets"""
        try:
            if not os.path.exists(self.credentials_file):
                logger.error(f"Brak pliku {self.credentials_file}")
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
            gc = gspread.authorize(creds)
            self.sheet = gc.open_by_key(self.sheet_id).sheet1
            
            logger.info("Google Sheets połączone pomyślnie")
            return True
            
        except Exception as e:
            logger.error(f"Błąd inicjalizacji Google Sheets: {e}")
            return False
    
    def prepare_headers(self):
        """Przygotowuje nagłówки kolumn"""
        headers = [
            "Дата",
            "Платформа", 
            "Пользователь",
            "Название видео",
            "Просмотры сегодня",
            "Просмотры вчера",
            "Просмотры неделю назад",
            "Изменение за день (%)",
            "Изменение за неделю (%)",
            "Дата публикации",
            "Длительность",
            "Лайки",
            "Комментарии",
            "Ссылка на видео"
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
        """Formatuje dane dla Google Sheets - każdy clip/video ma swój wiersz"""
        rows = []
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for platform, platform_data in data.items():
            if 'error' in platform_data:
                continue
            
            platform_name = platform_data.get('platform', platform)
            user_name = platform_data.get('user_name', platform_data.get('username', ''))
            
            # Przetwarzamy każdy clip/video osobno
            if 'clips' in platform_data and platform_data['clips']:
                for clip in platform_data['clips']:
                    # Obliczamy historyczne wyświetlenia dla tego konkretnego clipa
                    current_views = clip.get('views', 0)
                    historical = self.calculate_historical_views(current_views, platform)
                    
                    # Obliczamy zmiany procentowe
                    daily_change = self.calculate_percentage_change(
                        current_views, historical['yesterday']
                    )
                    weekly_change = self.calculate_percentage_change(
                        current_views, historical['week_ago']
                    )
                    
                    # Przygotowujemy wiersz dla tego clipa
                    row = [
                        current_date,
                        platform_name,
                        user_name,
                        clip.get('title', '')[:100],  # Nazwa clipa
                        str(current_views),  # Просмотры сегодня
                        str(historical['yesterday']),  # Просмотры вчера
                        str(historical['week_ago']),  # Просмотры неделю назад
                        f"{daily_change}%",  # Изменение за день
                        f"{weekly_change}%",  # Изменение за неделю
                        clip.get('date', ''),  # Дата публикации
                        f"{clip.get('duration', 0)} сек",  # Длительность
                        str(clip.get('likes', 0)),  # Лайки
                        str(clip.get('comments', 0)),  # Комментарии
                        f"https://vk.com/video{clip.get('video_id', '')}"  # Ссылка
                    ]
                    
                    rows.append(row)
            
            elif 'videos' in platform_data and platform_data['videos']:
                for video in platform_data['videos']:
                    # Obliczamy historyczne wyświetlenia dla tego konkretnego wideo
                    current_views = video.get('views', 0)
                    historical = self.calculate_historical_views(current_views, platform)
                    
                    # Obliczamy zmiany procentowe
                    daily_change = self.calculate_percentage_change(
                        current_views, historical['yesterday']
                    )
                    weekly_change = self.calculate_percentage_change(
                        current_views, historical['week_ago']
                    )
                    
                    # Przygotowujemy wiersz dla tego wideo
                    row = [
                        current_date,
                        platform_name,
                        user_name,
                        video.get('title', '')[:100],  # Nazwa wideo
                        str(current_views),  # Просмотры сегодня
                        str(historical['yesterday']),  # Просмотры вчера
                        str(historical['week_ago']),  # Просмотры неделю назад
                        f"{daily_change}%",  # Изменение за день
                        f"{weekly_change}%",  # Изменение за неделю
                        video.get('date', '')[:10],  # Дата публикации
                        video.get('duration', ''),  # Длительность
                        str(video.get('likes', 0)),  # Лайки
                        str(video.get('comments', 0)),  # Комментарии
                        video.get('url', '')  # Ссылка на видео
                    ]
                    
                    rows.append(row)
        
        return rows
    
    def save_to_sheets(self, data: Dict[str, Any]) -> bool:
        """Zapisuje dane do Google Sheets"""
        try:
            if not self.sheet:
                logger.error("Google Sheets nie jest zainicjalizowane")
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
