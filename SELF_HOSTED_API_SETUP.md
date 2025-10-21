# Self-Hosted Bot API Setup

## 🚀 Konfiguracja dla plików do 2GB

### 1. Dodaj do pliku `.env`:

```bash
# Self-hosted Bot API configuration
USE_SELF_HOSTED_API=true
SELF_HOSTED_API_URL=https://your-bot-api-server.com
MAX_FILE_SIZE_MB=2000
```

### 2. Uruchom self-hosted Bot API server:

```bash
# Pobierz i uruchom oficjalny Bot API server
docker run -d \
  --name telegram-bot-api \
  -p 8081:8081 \
  -v /path/to/your/data:/var/lib/telegram-bot-api \
  telegram-bot-api:latest \
  --api-id=YOUR_API_ID \
  --api-hash=YOUR_API_HASH \
  --local
```

### 3. Skonfiguruj bota:

```bash
# W pliku .env ustaw:
USE_SELF_HOSTED_API=true
SELF_HOSTED_API_URL=http://localhost:8081
MAX_FILE_SIZE_MB=2000
```

### 4. Restart bota:

```bash
./stop_bot.sh && ./start_bot.sh
```

## 📋 Korzyści:

- ✅ **Pliki do 2GB** (zamiast 20MB)
- ✅ **Szybsze przesyłanie** (lokalny serwer)
- ✅ **Większa kontrola** nad API
- ✅ **Brak limitów Telegram**

## 🔧 Alternatywnie - użyj standardowego API z kompresją:

Jeśli nie chcesz konfigurować self-hosted API, bot automatycznie skompresuje pliki .MOV do <20MB.
