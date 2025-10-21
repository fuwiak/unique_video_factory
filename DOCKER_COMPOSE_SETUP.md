# 🚀 Docker Compose Setup - Self-Hosted Bot API

## Problem: "File is too big" dla plików .MOV 29MB

**Przyczyna:** Standardowy Telegram API ma limit 20MB dla video files.

**Rozwiązanie:** Użyj docker-compose z oddzielnym kontenerem dla self-hosted Bot API.

## ⚙️ Konfiguracja

### 1. Pobierz Telegram API credentials

1. Idź na https://my.telegram.org/apps
2. Zaloguj się swoim numerem telefonu
3. Utwórz nową aplikację:
   - **App title**: Unique Video Factory Bot
   - **Short name**: unique_video_factory
   - **Platform**: Desktop
4. Skopiuj **API ID** i **API Hash**

### 2. Skopiuj plik konfiguracyjny

```bash
cp env.example .env
```

### 3. Edytuj .env z twoimi danymi

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Self-hosted Bot API credentials
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here

# Self-hosted Bot API configuration
USE_SELF_HOSTED_API=true
SELF_HOSTED_API_URL=http://telegram-bot-api:8081
MAX_FILE_SIZE_MB=2000

# Yandex Disk (optional)
YANDEX_DISK_TOKEN=your_yandex_token_here
YANDEX_DISK_FOLDER=unique_video_factory
```

### 4. Uruchom z docker-compose

```bash
# Uruchom tylko self-hosted Bot API
docker-compose up telegram-bot-api

# Lub uruchom wszystko razem
docker-compose up
```

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
| Self-hosted (Docker) | 2GB | 2GB | 2GB |

## 🔧 Troubleshooting

### Problem: "API ID/Hash not found"
- Sprawdź czy dodałeś `TELEGRAM_API_ID` i `TELEGRAM_API_HASH` do `.env`
- Upewnij się że credentials są poprawne

### Problem: "Self-hosted API not available"
- Sprawdź czy kontener działa: `docker-compose ps`
- Sprawdź logi: `docker-compose logs telegram-bot-api`
- Restart: `docker-compose restart telegram-bot-api`

### Problem: "Still getting 20MB limit"
- Sprawdź czy `USE_SELF_HOSTED_API=true` w `.env`
- Sprawdź czy `SELF_HOSTED_API_URL=http://telegram-bot-api:8081`
- Restart bota: `docker-compose restart bot`

## 🚀 Railway Deployment

Dla Railway deployment, użyj docker-compose:

1. **Railway automatycznie wykryje docker-compose.yml**
2. **Uruchomi telegram-bot-api w oddzielnym kontenerze**
3. **Skonfiguruje bot do używania self-hosted API**
4. **Obsłuży pliki do 2GB**

## 💡 Alternatywa

Jeśli nie chcesz konfigurować self-hosted API:
- Bot automatycznie skompresuje pliki >20MB
- Użytkownicy dostaną instrukcje kompresji
- Standardowy API będzie używany z fallback
