# Railway Deployment Guide

## 🚀 Deploy Telegram Bot na Railway

### 1. Przygotowanie

1. **Fork/Clone repository** na GitHub
2. **Skonfiguruj zmienne środowiskowe** w Railway
3. **Deploy na Railway**

### 2. Railway Configuration

#### Wymagane zmienne środowiskowe:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Yandex Disk
YANDEX_DISK_TOKEN=your_yandex_disk_token_here
YANDEX_DISK_FOLDER=unique_video_factory

# Railway
PORT=8000
PYTHONPATH=/app
PYTHONUNBUFFERED=1
```

#### Opcjonalne zmienne:

```bash
# Self-hosted Bot API (dla plików >20MB)
USE_SELF_HOSTED_API=false
SELF_HOSTED_API_URL=https://your-bot-api-server.com
MAX_FILE_SIZE_MB=50

# Video Processing
MAX_VIDEO_SIZE_MB=50
VIDEO_COMPRESSION_QUALITY=30
VIDEO_SCALE=1280:720

# Social Media APIs
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
TIKTOK_USERNAME=your_tiktok_username
VK_ACCESS_TOKEN=your_vk_access_token
YOUTUBE_API_KEY=your_youtube_api_key

# Google Sheets
GOOGLE_CREDENTIALS_FILE=google_credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id
```

### 3. Deployment Steps

1. **Zaloguj się na Railway**: https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. **Wybierz repository** z tym kodem
4. **Skonfiguruj zmienne środowiskowe** w Railway dashboard
5. **Deploy**

### 4. Railway Features

- ✅ **Automatic deployment** z GitHub
- ✅ **Environment variables** management
- ✅ **Health checks** na `/health` endpoint
- ✅ **Logs** w Railway dashboard
- ✅ **Scaling** automatyczne
- ✅ **Custom domains** (opcjonalnie)

### 5. Health Check

Bot automatycznie uruchamia health check server na porcie 8000:

```bash
curl https://your-app.railway.app/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-21T19:45:00.000Z",
  "service": "telegram-bot"
}
```

### 6. Monitoring

- **Logs**: Railway dashboard → Logs
- **Metrics**: Railway dashboard → Metrics
- **Health**: `/health` endpoint
- **Uptime**: Railway monitoring

### 7. Troubleshooting

#### Bot nie startuje:
- Sprawdź zmienne środowiskowe
- Sprawdź logs w Railway dashboard
- Upewnij się że `TELEGRAM_BOT_TOKEN` jest poprawny

#### Health check fails:
- Sprawdź czy port 8000 jest dostępny
- Sprawdź logs dla błędów HTTP server

#### Video processing fails:
- Sprawdź czy `ffmpeg` jest zainstalowany (jest w Dockerfile)
- Sprawdź zmienne Yandex Disk

### 8. Custom Domain (opcjonalnie)

1. Railway dashboard → Settings → Domains
2. Dodaj custom domain
3. Skonfiguruj DNS records
4. Bot będzie dostępny na twojej domenie

### 9. Scaling

Railway automatycznie skaluje aplikację w zależności od obciążenia. Dla większego ruchu:

1. Railway dashboard → Settings → Scaling
2. Ustaw min/max instances
3. Skonfiguruj resource limits

### 10. Backup

Railway automatycznie tworzy backup:
- **Code**: GitHub repository
- **Environment**: Railway dashboard
- **Data**: Yandex Disk (external storage)

## 🎯 Gotowe!

Bot jest teraz gotowy do deployment na Railway z pełną konfiguracją!
