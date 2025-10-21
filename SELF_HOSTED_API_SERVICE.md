# 🚀 Self-Hosted Bot API Service Setup

## Problem: Standardowy API ma limit 20MB

**Rozwiązanie:** Uruchom self-hosted Bot API jako oddzielny serwis.

## ⚙️ Opcje uruchamiania

### 1. Docker Compose (Zalecane)

```bash
# Uruchom tylko self-hosted API
docker-compose up telegram-bot-api

# Lub uruchom wszystko razem
docker-compose up
```

### 2. Oddzielny serwis (Linux)

```bash
# Uruchom self-hosted API jako oddzielny serwis
./start_self_hosted_api.sh

# Sprawdź czy działa
curl http://localhost:8081/health
```

### 3. Systemd Service

```bash
# Skopiuj service file
sudo cp telegram-bot-api.service /etc/systemd/system/

# Włącz serwis
sudo systemctl enable telegram-bot-api@29924508:7708c2662778b5ca636c0d8fb578301a

# Uruchom serwis
sudo systemctl start telegram-bot-api@29924508:7708c2662778b5ca636c0d8fb578301a

# Sprawdź status
sudo systemctl status telegram-bot-api@29924508:7708c2662778b5ca636c0d8fb578301a
```

## 🔧 Konfiguracja

### 1. Ustaw zmienne środowiskowe

```bash
export TELEGRAM_API_ID=your_api_id_here
export TELEGRAM_API_HASH=your_api_hash_here
```

### 2. Sprawdź czy telegram-bot-api jest zainstalowany

```bash
# Sprawdź czy binary istnieje
which telegram-bot-api

# Lub sprawdź w standardowych lokalizacjach
ls -la /usr/local/bin/telegram-bot-api
ls -la /usr/bin/telegram-bot-api
```

### 3. Uruchom serwis

```bash
# Docker Compose
docker-compose up telegram-bot-api

# Lub natywnie
./start_self_hosted_api.sh
```

## 🎯 Rezultat

Po uruchomieniu self-hosted API:

- ✅ **Pliki do 2GB** (zamiast 20MB)
- ✅ **29MB .MOV files** - bez problemów
- ✅ **Brak limitów** na pobieranie/upload
- ✅ **Szybsze przesyłanie** (lokalny serwer)

## 📊 Porównanie limitów:

| API Type | Video Limit | Document Limit | Download Limit |
|----------|-------------|----------------|----------------|
| Standard Telegram | 20MB | 50MB | 20MB |
| Self-hosted Service | 2GB | 2GB | 2GB |

## 🔧 Troubleshooting

### Problem: "telegram-bot-api binary not found"
```bash
# Zainstaluj z Docker
docker-compose up telegram-bot-api

# Lub pobierz binary
wget https://github.com/tdlib/telegram-bot-api/releases/latest/download/telegram-bot-api
chmod +x telegram-bot-api
sudo mv telegram-bot-api /usr/local/bin/
```

### Problem: "Port 8081 already in use"
```bash
# Zabij proces na porcie 8081
sudo lsof -ti:8081 | xargs kill -9

# Lub zmień port w konfiguracji
export SELF_HOSTED_API_URL=http://localhost:8082
```

### Problem: "API credentials not found"
```bash
# Ustaw zmienne środowiskowe
export TELEGRAM_API_ID=your_api_id_here
export TELEGRAM_API_HASH=your_api_hash_here

# Lub dodaj do .env
echo "TELEGRAM_API_ID=your_api_id_here" >> .env
echo "TELEGRAM_API_HASH=your_api_hash_here" >> .env
```

## 🚀 Railway Deployment

Dla Railway deployment:

1. **Railway automatycznie wykryje docker-compose.yml**
2. **Uruchomi telegram-bot-api w oddzielnym kontenerze**
3. **Skonfiguruje bot do używania self-hosted API**
4. **Obsłuży pliki do 2GB**

## 💡 Alternatywa

Jeśli nie chcesz konfigurować self-hosted API:
- Bot automatycznie skompresuje pliki >20MB
- Użytkownicy dostaną instrukcje kompresji
- Standardowy API będzie używany z fallback
