# ⏰ Railway Cron Setup - Daily Views Report

> 📖 **Szybki setup:** Zobacz [CRON_SETUP_GUIDE.md](CRON_SETUP_GUIDE.md) dla instrukcji krok po kroku z cron-job.org

## 🎯 Autoamtyzacja zadań

Railway automatycznie uruchamia codzienny raport wyświetleń z YouTube.

## 📋 Jak to działa?

Railway używa **Procfile** aby uruchomić aplikację:

```procfile
web: python telegram_bot.py     # Główny bot z endpointem dla cron
```

Bot ma wbudowany endpoint `/trigger-daily-report` który:
1. **Uruchamia raport** na żądanie
2. **Sprawdza nowe wideo** w Google Sheets  
3. **Dodaje wyświetlenia** do arkusza
4. **Pracuje w tle** bez blokowania bota

## 🚀 Instalacja na Railway

### 1. Dodaj `schedule` do requirements.txt

✅ **Już dodane:**
```
schedule>=1.2.0
```

### 2. Procfile

✅ **Już skonfigurowany:**
```procfile
web: python telegram_bot.py
```

Endpoint jest wbudowany w telegram_bot.py

### 3. Deploy na Railway

```bash
# Push zmian
git add .
git commit -m "Add daily views report endpoint"
git push

# Railway automatycznie zrestartuje aplikację
```

### 4. Sprawdź w Railway Dashboard

1. Otwórz Railway Dashboard
2. Zobaczysz **1 proces**:
   - **web** - Telegram bot (z endpointem /trigger-daily-report)
   
3. Sprawdź logi:
   ```
   Railway Dashboard → Deployments → Logs
   Powinno być: Health server started on port 8000
   ```

## ⏰ Konfiguracja Cron

**Zalecana metoda:** Używaj **external cron service** (darmowy):

### External Cron Service (Zalecane)

Najpewniejsza metoda - darmowy external cron service:

**Darmowe cron services:**
- [cron-job.org](https://cron-job.org) - Darmowy, łatwy
- [UptimeRobot](https://uptimerobot.com) - Darmowy, niezawodny
- [EasyCron](https://www.easycron.com) - Darmowy tier

**Jak skonfigurować:**
1. Zarejestruj się na wybranej stronie
2. Dodaj nowe zadanie cron:
   - URL: `https://twoja-domena.onrender.com/trigger-daily-report`
   - Schedule: `0 0 * * *` (codziennie o północy UTC)
   - Method: GET
3. Save i gotowe!

**Endpoint jest już dostępny:**
- `GET/POST https://twoja-domena.onrender.com/trigger-daily-report`
- Automatycznie wywołuje raport codzienny

## 🔍 Testowanie Endpointu

```bash
# Lokalnie
curl http://localhost:8000/trigger-daily-report

# Na Railway (po deploy)
curl https://twoja-domena.railway.app/trigger-daily-report

# Odpowiedź:
# {"status": "triggered", "message": "Daily report triggered successfully", "timestamp": "..."}
```

## ⏰ Harmonogram

**Konfigurujesz w external cron service:**
- Domyślnie: Codziennie o **00:00 UTC** (`0 0 * * *`)
- Możesz zmienić na dowolny harmonogram

## 📊 Logi

Logi są zapisywane w:
- Railway Dashboard → Deployments → Logs
- Szukaj linii z: `📊 Daily report triggered via API endpoint`
- Błędy: `❌ Error triggering daily report`

## 🐛 Troubleshooting

### Cron nie działa

**Sprawdź:**
1. Czy endpoint działa: `curl https://twoja-domena.railway.app/trigger-daily-report`
2. Czy external cron service wysyła request (sprawdź logi w cron service)
3. Czy zmienne środowiskowe są ustawione (Google Sheets API)
4. Czy bot jest online w Railway Dashboard

### Błędy autoryzacji Google Sheets

**Sprawdź:**
1. Zmienne środowiskowe w Railway:
   - `GOOGLE_PROJECT_ID`
   - `GOOGLE_PRIVATE_KEY_ID`
   - `GOOGLE_PRIVATE_KEY`
   - `GOOGLE_CLIENT_EMAIL`
   - `GOOGLE_CLIENT_ID`

### Błędy YouTube API

**Sprawdź:**
1. `YOUTUBE_API_KEY` w zmiennych środowiskowych
2. Czy API key jest aktywny w Google Cloud Console

## 💰 Koszt

Railway pobiera opłatę za każdy proces:
- **web**: ~$5-10/miesiąc (bot)
- **cron**: ~$5/miesiąc (codzienny raport)

**Łącznie:** ~$10-15/miesiąc

## 🔧 Monitorowanie

### Sprawdź czy cron działa:

```bash
# Zobacz logi
railway logs --service cron

# Albo w Railway Dashboard
# Services → Cron → Logs
```

### Test ręczny:

```bash
# Lokalnie
python3 daily_cron.py

# Na Railway (SSH)
railway shell
python3 daily_cron.py
```

## 📋 Alternatywy

Jeśli nie chcesz płacić za dodatkowy proces, możesz:

1. **External Cron (darmowe):**
   - Użyj [cron-job.org](https://cron-job.org)
   - Konfiguruj URL Webhook
   - Railway stworzy endpoint `/trigger-report`

2. **Railway Cron (w przyszłości):**
   - Railway może dodać cron jako funkcję
   - Będzie to jedna linia w `railway.toml`

## 🔗 Linki

- [Railway Docs](https://docs.railway.app)
- [Procfile Guide](https://docs.railway.app/deploy/builds#procfile)
- [Google Sheets](https://docs.google.com/spreadsheets/d/1dU9dv4R2-POC_VDlX7U4l_qkla23iZ4SxboLn66XXPw/)

