# ⏰ Automatyczne Uruchamianie Daily Views Report

## 📋 Jak to działa

Daily views report jest teraz automatycznie uruchamiany codziennie o określonej godzinie przez wbudowany scheduler w `telegram_bot.py`.

## 🕐 Konfiguracja godziny uruchomienia

Domyślnie raport uruchamia się codziennie o **00:00 UTC**.

Aby zmienić godzinę uruchomienia, ustaw zmienną środowiskową w Railway:

### W Railway Dashboard:

1. Otwórz projekt na Railway
2. Przejdź do **Variables** (Zmienne środowiskowe)
3. Dodaj nową zmienną:
   - **Nazwa**: `DAILY_REPORT_TIME`
   - **Wartość**: `HH:MM` (format 24-godzinny, UTC)
   - **Przykład**: `08:00` (dla 8:00 UTC), `14:30` (dla 14:30 UTC)

### Przykładowe wartości:

- `00:00` - Północ UTC (domyślne)
- `08:00` - 8:00 rano UTC
- `14:30` - 14:30 UTC (południe)
- `23:59` - Prawie północ UTC

## 📊 Co robi automatyczny raport?

1. Przeszukuje wszystkie arkusze w Google Sheets
2. Dla każdego unikalnego URL wideo w kolumnie "Видео":
   - Pobiera aktualne wyświetlenia z YouTube/VK/Instagram API
   - Dodaje nowy wiersz do arkusza z dzisiejszą datą
   - Zapisuje aktualne wyświetlenia

## ✅ Weryfikacja działania

Sprawdź logi w Railway Dashboard:
- Szukaj: `⏰ Daily views report scheduled for XX:XX UTC every day`
- Po uruchomieniu: `📊 Uruchamiam codzienny raport wyświetleń...`
- Po zakończeniu: `✅ Codzienny raport zakończony pomyślnie`

## 🔧 Ręczne uruchomienie

Możesz również ręcznie uruchomić raport przez endpoint HTTP:
```
GET https://twoja-domena.railway.app/trigger-daily-report
```

## 🌍 Timezone

**Ważne:** Scheduler używa czasu UTC. Jeśli chcesz uruchomić raport o określonej godzinie lokalnej, przelicz to na UTC.

**Przykłady:**
- Warszawa (CET, UTC+1): 09:00 lokalnie = 08:00 UTC
- Warszawa (CEST, UTC+2): 10:00 lokalnie = 08:00 UTC
- Moskwa (MSK, UTC+3): 11:00 lokalnie = 08:00 UTC

