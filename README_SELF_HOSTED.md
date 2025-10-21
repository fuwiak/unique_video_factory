# 🚀 Self-Hosted Bot API - Pliki do 2GB

## Problem: "File is too big" dla plików .MOV 29MB

**Przyczyna:** Standardowy Telegram API ma limit 20MB dla video files.

**Rozwiązanie:** Użyj self-hosted Bot API dla plików do 2GB.

## ⚙️ Konfiguracja

### 1. Dodaj do `.env`:

```bash
# Self-hosted Bot API (dla plików do 2GB)
USE_SELF_HOSTED_API=true
SELF_HOSTED_API_URL=http://localhost:8081
MAX_FILE_SIZE_MB=2000
```

### 2. Uruchom self-hosted Bot API:

```bash
# Docker
docker run -d \
  --name telegram-bot-api \
  -p 8081:8081 \
  telegram-bot-api:latest \
  --api-id=YOUR_API_ID \
  --api-hash=YOUR_API_HASH \
  --local

# Lub natywnie (Linux)
./telegram-bot-api --api-id=YOUR_API_ID --api-hash=YOUR_API_HASH --local
```

### 3. Restart bota:

```bash
./stop_bot.sh && ./start_bot.sh
```

## 📊 Porównanie limitów:

| API Type | Video Limit | Document Limit |
|----------|-------------|----------------|
| Standard Telegram | 20MB | 50MB |
| Self-hosted | 2GB | 2GB |

## 🎯 Rezultat:

- ✅ **Pliki .MOV 29MB** - bez problemów
- ✅ **Pliki do 2GB** - pełna obsługa
- ✅ **Automatyczna kompresja** - dla bardzo dużych plików
- ✅ **Fallback** - jeśli self-hosted nie działa

## 🔄 Alternatywa:

Jeśli nie chcesz konfigurować self-hosted API, bot automatycznie skompresuje pliki .MOV do <20MB.
