# 📊 Daily Views Report - Instrukcja

## 🎯 Cel

Automatyczne dodawanie codziennych danych o wyświetleniach z YouTube do Google Sheets.

## 📋 Jak to działa?

1. **Odczytuje wszystkie wideo** z arkusza Google Sheets (kolumna A - Референс)
2. **Pobiera aktualne wyświetlenia** z YouTube API
3. **Dodaje nowy wiersz** z dzisiejszą datą i wyświetleniami

## 🚀 Użycie

### Ręczne uruchomienie:

```bash
python3 daily_views_report.py
```

### Automatyczne uruchomienie (cron):

Dodaj do crontab aby uruchamiać codziennie o 00:00:

```bash
crontab -e
```

Dodaj linijkę:

```
0 0 * * * cd /path/to/unique_video_factory && python3 daily_views_report.py >> logs/daily_report.log 2>&1
```

Lub dla Railway/deployment:

```bash
# Uruchamiamy daily script przez scheduler
railway cron "0 0 * * * cd /app && python3 daily_views_report.py"
```

## 📊 Format danych w Google Sheets

| Kolumna | Opis | Przykład |
|---------|------|----------|
| **Референс** | URL do wideo | `https://www.youtube.com/shorts/VIDEO_ID` |
| **Видео** | Tytuł wideo | `Test video` |
| **Дата поста** | Data publikacji | `2024-03-31` |
| **Кол-во просмотров 1 день** | Wyświetlenia dzisiaj | `1200087` |
| **Кол-во просмотров 1 нед** | Wyświetlenia z tygodnia | `1200087` |
| **Кол-во просмотров 1 мес** | Wyświetlenia z miesiąca | `1200087` |

## ⚙️ Wymagania

### 1. Google Sheets API

Potrzebujesz `google_credentials.json` lub zmienne środowiskowe:

```env
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY_ID=your-private-key-id
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=your-client-id
```

### 2. YouTube API

```env
YOUTUBE_API_KEY=your-youtube-api-key
```

## 📊 Przykład pracy

```
🚀 Uruchamianie daily views reporter
✅ Google Sheets połączone pomyślnie
📊 Przetwarzam wideo 1: https://www.youtube.com/shorts/Sxht9D7gG9c
✅ Dodano wiersz: Test video - 1200087 wyświetleń
📊 Przetwarzam wideo 2: https://www.youtube.com/shorts/HKLQy3ufgH0
✅ Dodano wiersz: Another video - 6667547 wyświetleń
✅ Przetworzono 2 wideo
✅ Raport codzienny zakończony pomyślnie
```

## 🔄 Workflow

1. **Dzień 1**: Dodajesz wideo do arkusza → otrzymujesz wiersz z wyświetleniami
2. **Dzień 2**: Uruchamiasz script → dodaje nowy wiersz z wyświetleniami z dnia 2
3. **Dzień 3**: Uruchamiasz script → dodaje nowy wiersz z wyświetleniami z dnia 3
4. **itd.**

## 📈 Historia

Każde uruchomienie dodaje nowy wiersz, więc:
- Możesz zobaczyć historię wzrostu wyświetleń
- Możesz obliczyć średni dzienny wzrost
- Możesz zobaczyć trendy

## ⚠️ Ważne

- Script **NIE usuwa** starych danych
- Script **NIE aktualizuje** istniejących wierszy
- Każde uruchomienie **dodaje nowy wiersz**
- Tylko **unikalne URL** są przetwarzane

## 🐛 Troubleshooting

### Błąd: "Google Sheets nie jest zainicjalizowany"

```bash
# Sprawdź czy masz credentials
ls google_credentials.json

# Lub sprawdź zmienne środowiskowe
echo $GOOGLE_PROJECT_ID
```

### Błąd: "YouTube API key is invalid"

```bash
# Sprawdź API key
echo $YOUTUBE_API_KEY
```

### Błąd: "Nie można połączyć z Google Sheets"

Sprawdź czy masz dostęp do arkusza:
```bash
# ID arkusza
1dU9dv4R2-POC_VDlX7U4l_qkla23iZ4SxboLn66XXPw
```

## 🔗 Linki

- [Google Sheets](https://docs.google.com/spreadsheets/d/1dU9dv4R2-POC_VDlX7U4l_qkla23iZ4SxboLn66XXPw/edit?gid=1033065886#gid=1033065886)
- [YouTube API](https://developers.google.com/youtube/v3)

