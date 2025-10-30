# 🔧 Szybki Setup Cron-Job.org

## Krok po kroku

### 1. Zarejestruj się
- Idź na https://cron-job.org
- Kliknij "Sign up for free"
- Zarejestruj się (darmowe)

### 2. Utwórz nowe zadanie
- Kliknij "Create cronjob"
- Uzupełnij formularz:

**Title:** `Daily YouTube Views Report`

**Address (URL):** 
```
https://YOUR_RAILWAY_DOMAIN.railway.app/trigger-daily-report
```
*(Zamień YOUR_RAILWAY_DOMAIN na rzeczywistą domenę)*

**Schedule:**
- Wybierz: "Daily"
- Czas: `00:00` (UTC)

**Request settings:**
- Method: `GET`
- Save auth: `No`

### 3. Zapisz i aktywuj
- Kliknij "Create cronjob"
- Upewnij się, że switch "Active" jest włączony

### 4. Test
- Kliknij "Trigger cronjob now" aby przetestować
- Sprawdź Railway logs: `📊 Daily report triggered via API endpoint`

## ✅ Gotowe!

Codziennie o północy UTC external cron wywoła twój endpoint i zaktualizuje YouTube views w Google Sheets.

## 🔍 Monitoring

- **cron-job.org** → "Execution history" - widzisz kiedy zadanie było uruchomione
- **Railway** → "Logs" - widzisz szczegóły wykonania

## 📅 Zmiana harmonogramu

W każdej chwili możesz zmienić harmonogram w cron-job.org:
- Co godzinę: `0 * * * *`
- Co 12 godzin: `0 */12 * * *`
- Tylko w dni robocze: `0 0 * * 1-5`

## 🆓 Darmowe limity

cron-job.org darmowy plan:
- Do 2 cronjobs ✅ (wystarczy!)
- Do 100 wykonanych zadań/miesiąc ✅ (30 dni × 1 dziennie = 30)

