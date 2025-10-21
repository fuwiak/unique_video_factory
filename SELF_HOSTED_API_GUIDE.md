# 🚀 Self-Hosted Bot API Setup Guide

## Problem: 20MB File Size Limit

**Standardowy Telegram API ma limit 20MB dla video files.** To jest fundamentalne ograniczenie, którego nie można obejść bez self-hosted Bot API.

## ✅ Rozwiązanie: Self-Hosted Bot API

### 1. Pobierz Telegram API credentials

1. Idź na https://my.telegram.org/apps
2. Zaloguj się swoim numerem telefonu
3. Utwórz nową aplikację:
   - **App title**: Unique Video Factory Bot
   - **Short name**: unique_video_factory
   - **Platform**: Desktop
4. Skopiuj **API ID** i **API Hash**

### 2. Dodaj do `.env`:

```bash
# Self-hosted Bot API credentials
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here

# Self-hosted Bot API configuration
USE_SELF_HOSTED_API=true
SELF_HOSTED_API_URL=http://localhost:8081
MAX_FILE_SIZE_MB=2000
```

### 3. Uruchom setup script:

```bash
python setup_self_hosted_api.py
```

### 4. Restart bota:

```bash
./stop_bot.sh && ./start_bot.sh
```

## 🎯 Rezultat

Po konfiguracji self-hosted Bot API:

- ✅ **Pliki do 2GB** (zamiast 20MB)
- ✅ **Brak limitów** na pobieranie/upload
- ✅ **29MB .MOV files** - bez problemów
- ✅ **Szybsze przesyłanie** (lokalny serwer)

## 📊 Porównanie limitów:

| API Type | Video Limit | Document Limit | Download Limit |
|----------|-------------|----------------|----------------|
| Standard Telegram | 20MB | 50MB | 20MB |
| Self-hosted | 2GB | 2GB | 2GB |

## 🔧 Troubleshooting

### Problem: "API ID/Hash not found"
- Sprawdź czy dodałeś `TELEGRAM_API_ID` i `TELEGRAM_API_HASH` do `.env`
- Upewnij się że credentials są poprawne

### Problem: "Self-hosted API not available"
- Sprawdź czy serwer działa: `curl http://localhost:8081/health`
- Restart setup script: `python setup_self_hosted_api.py`

### Problem: "Still getting 20MB limit"
- Sprawdź czy `USE_SELF_HOSTED_API=true` w `.env`
- Restart bota po zmianie konfiguracji

## 🚀 Railway Deployment

Dla Railway deployment, self-hosted Bot API będzie działać automatycznie jeśli:

1. Dodasz credentials do Railway environment variables
2. Bot automatycznie wykryje i użyje self-hosted API
3. Pliki do 2GB będą obsługiwane bez problemów

## 💡 Alternatywa

Jeśli nie chcesz konfigurować self-hosted API:
- Bot automatycznie skompresuje pliki >20MB
- Użytkownicy dostaną instrukcje kompresji
- Standardowy API będzie używany z fallback
