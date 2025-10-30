# ⏰ Railway Cron Setup - Daily Views Report

## 🎯 Autoamtyzacja zadań

Railway automatycznie uruchamia codzienny raport wyświetleń z YouTube.

## 📋 Jak to działa?

Railway używa **Procfile** aby uruchomić wiele procesów:

```procfile
web: python telegram_bot.py     # Główny bot
cron: python daily_cron.py       # Cron service
```

Proces `cron` uruchamia się automatycznie i:
1. **Uruchamia raport codziennie o 00:00 UTC**
2. **Sprawdza nowe wideo** w Google Sheets
3. **Dodaje wyświetlenia** do arkusza

## 🚀 Instalacja na Railway

### 1. Dodaj `schedule` do requirements.txt

✅ **Już dodane:**
```
schedule>=1.2.0
```

### 2. Zaktualizuj Procfile

✅ **Już zaktualizowany:**
```procfile
web: python telegram_bot.py
cron: python daily_cron.py
```

### 3. Deploy na Railway

```bash
# Push zmian
git add .
git commit -m "Add cron service for daily views report"
git push

# Railway automatycznie wykryje nowy proces
```

### 4. Sprawdź w Railway Dashboard

1. Otwórz Railway Dashboard
2. Zobaczysz **2 procesy**:
   - **web** - Telegram bot
   - **cron** - Daily views reporter

## ⏰ Harmonogram

**Domyślnie:** Codziennie o **00:00 UTC**

**Możesz zmienić w `daily_cron.py`:**

```python
# Domyślnie: codziennie o północy UTC
schedule.every().day.at("00:00").do(run_daily_report)

# Inne opcje:
schedule.every().day.at("10:30").do(run_daily_report)  # 10:30 UTC
schedule.every(2).hours.do(run_daily_report)            # Co 2 godziny
schedule.every(1).hours.do(run_daily_report)            # Co godzinę
```

## 📊 Logi

Logi są zapisywane w:
- Railway Dashboard → Cron Process → Logs
- Lub lokalnie w: `logs/daily_report.log`

## 🐛 Troubleshooting

### Cron nie działa

**Sprawdź:**
1. Czy proces `cron` jest uruchomiony w Railway Dashboard
2. Czy logi pokazują błędy
3. Czy `schedule` jest zainstalowany: `pip list | grep schedule`

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

