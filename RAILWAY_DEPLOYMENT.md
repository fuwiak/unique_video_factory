# 🚀 Railway Deployment - Self-Hosted Bot API

## Problem: 20MB File Size Limit

**Standardowy Telegram API ma limit 20MB dla video files.** Railway deployment automatycznie uruchamia self-hosted Bot API dla plików do 2GB.

## ✅ Automatyczne uruchamianie na Railway

Railway automatycznie:

1. **Kompiluje telegram-bot-api** z source code
2. **Uruchamia self-hosted API server** w tle
3. **Skonfiguruje bot** do używania self-hosted API
4. **Obsłuży pliki do 2GB**

## ⚙️ Konfiguracja Railway

### 1. Pobierz Telegram API credentials

1. Idź na https://my.telegram.org/apps
2. Zaloguj się swoim numerem telefonu
3. Utwórz nową aplikację:
   - **App title**: Unique Video Factory Bot
   - **Short name**: unique_video_factory
   - **Platform**: Desktop
4. Skopiuj **API ID** i **API Hash**

### 2. Dodaj do Railway Environment Variables

W Railway dashboard, dodaj następujące zmienne środowiskowe:

```bash
# Telegram Bot Token (już masz)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Self-hosted Bot API credentials
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here

# Self-hosted Bot API configuration
USE_SELF_HOSTED_API=true
SELF_HOSTED_API_URL=http://localhost:8081
MAX_FILE_SIZE_MB=2000

# Yandex Disk (opcjonalnie)
YANDEX_DISK_TOKEN=your_yandex_token_here
YANDEX_DISK_FOLDER=unique_video_factory
```

### 3. Deploy na Railway

Railway automatycznie:
- ✅ Skompiluje telegram-bot-api z source
- ✅ Uruchomi self-hosted Bot API server
- ✅ Skonfiguruje bot do używania self-hosted API
- ✅ Obsłuży pliki do 2GB

## 🎯 Rezultat

Po konfiguracji:

- ✅ **Pliki do 2GB** (zamiast 20MB)
- ✅ **29MB .MOV files** - bez problemów
- ✅ **Brak limitów** na pobieranie/upload
- ✅ **Szybsze przesyłanie** (lokalny serwer)

## 📊 Porównanie limitów:

| API Type | Video Limit | Document Limit | Download Limit |
|----------|-------------|----------------|----------------|
| Standard Telegram | 20MB | 50MB | 20MB |
| Self-hosted (Railway) | 2GB | 2GB | 2GB |

## 🔧 Troubleshooting

### Problem: "API ID/Hash not found"
- Sprawdź czy dodałeś `TELEGRAM_API_ID` i `TELEGRAM_API_HASH` do Railway environment variables
- Upewnij się że credentials są poprawne

### Problem: "Self-hosted API not available"
- Sprawdź logi Railway deployment
- Upewnij się że `USE_SELF_HOSTED_API=true`
- Sprawdź czy telegram-bot-api został skompilowany

### Problem: "Still getting 20MB limit"
- Sprawdź logi bota - powinien pokazać "🚀 Self-hosted Bot API is running"
- Sprawdź czy `ACTUAL_MAX_FILE_SIZE: 2000MB` w logach

## 🚀 Automatyczne funkcje

Railway deployment automatycznie:

1. **Kompiluje telegram-bot-api** z source code
2. **Uruchamia self-hosted API server** w tle
3. **Skonfiguruje bot** do używania self-hosted API
4. **Fallback** do standard API jeśli self-hosted nie działa

## 💡 Alternatywa

Jeśli nie chcesz konfigurować self-hosted API:
- Bot automatycznie skompresuje pliki >20MB
- Użytkownicy dostaną instrukcje kompresji
- Standardowy API będzie używany z fallback