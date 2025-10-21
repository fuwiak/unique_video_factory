# 🚀 Przewodnik konfiguracji Google Cloud Console

## 📋 Krok po kroku - Konfiguracja Google Sheets API

### 🔧 Krok 1: Utwórz projekt w Google Cloud Console

1. **Idź do Google Cloud Console:**
   - Otwórz: https://console.cloud.google.com/
   - Zaloguj się na swoje konto Google

2. **Utwórz nowy projekt:**
   - Kliknij **"Select a project"** (góra strony)
   - Kliknij **"New Project"**
   - **Project name**: `unique-video-factory`
   - **Organization**: Wybierz swoją organizację (lub zostaw puste)
   - Kliknij **"Create"**

### 🔧 Krok 2: Włącz wymagane API

1. **Włącz Google Sheets API:**
   - W menu po lewej: **APIs & Services** → **Library**
   - Wyszukaj: `Google Sheets API`
   - Kliknij na wynik
   - Kliknij **"Enable"**

2. **Włącz Google Drive API:**
   - Wyszukaj: `Google Drive API`
   - Kliknij na wynik
   - Kliknij **"Enable"**

### 🔧 Krok 3: Utwórz Service Account

1. **Idź do Service Accounts:**
   - W menu po lewej: **IAM & Admin** → **Service Accounts**
   - Kliknij **"Create Service Account"**

2. **Wypełnij dane Service Account:**
   - **Service account name**: `unique-video-factory-sheets`
   - **Service account ID**: `unique-video-factory-sheets` (automatycznie)
   - **Description**: `Service account for Google Sheets integration`
   - Kliknij **"Create and Continue"**

3. **Nadaj uprawnienia:**
   - **Role**: Wybierz `Editor` (lub `Google Sheets API` + `Google Drive API`)
   - Kliknij **"Continue"**

4. **Zakończ tworzenie:**
   - Kliknij **"Done"**

### 🔧 Krok 4: Utwórz klucz JSON

1. **Znajdź utworzony Service Account:**
   - Na liście Service Accounts kliknij na `unique-video-factory-sheets`

2. **Utwórz klucz:**
   - Idź do zakładki **"Keys"**
   - Kliknij **"Add Key"** → **"Create new key"**
   - Wybierz **"JSON"**
   - Kliknij **"Create"**

3. **Pobierz plik:**
   - Plik JSON zostanie automatycznie pobrany
   - Zapisz go jako `google_credentials.json` w folderze projektu

### 🔧 Krok 5: Udostępnij arkusz Google Sheets

1. **Otwórz swój arkusz:**
   - Idź do: https://docs.google.com/spreadsheets/d/1p6bQ3Ck7qMv8M6vobXQcnEjXXdECAoBOlmy2_n9sUPI/edit

2. **Udostępnij Service Account:**
   - Kliknij **"Share"** (prawy górny róg)
   - W polu **"Add people and groups"** wpisz email Service Account
   - Email znajdziesz w pliku JSON jako `client_email`
   - **Role**: Wybierz **"Editor"**
   - Kliknij **"Send"**

### 🔧 Krok 6: Sprawdź konfigurację

1. **Sprawdź plik credentials:**
   ```bash
   ls -la google_credentials.json
   ```

2. **Sprawdź zawartość pliku:**
   ```bash
   cat google_credentials.json | head -5
   ```

3. **Przetestuj połączenie:**
   ```bash
   python google_sheets_integration.py
   ```

## 🧪 Test końcowy

Po skonfigurowaniu uruchom:

```bash
python official_api_extractor.py
```

Powinieneś zobaczyć:
```
✅ Dane zapisane do Google Sheets!
```

## 🔧 Rozwiązywanie problemów

### ❌ "Brak pliku google_credentials.json"
- Sprawdź czy plik istnieje w folderze projektu
- Sprawdź czy ma poprawną strukturę JSON

### ❌ "Permission denied"
- Sprawdź czy Service Account ma dostęp do arkusza
- Sprawdź czy arkusz jest udostępniony dla Service Account

### ❌ "Invalid credentials"
- Sprawdź czy plik JSON jest poprawny
- Sprawdź czy Service Account ma odpowiednie uprawnienia

### ❌ "API not enabled"
- Sprawdź czy Google Sheets API i Google Drive API są włączone
- Idź do **APIs & Services** → **Library** i włącz API

## 📊 Struktura danych w arkuszu

System automatycznie utworzy kolumny:

| Kolumna | Opis |
|---------|------|
| Дата | Data i czas |
| Платформа | Platforma (VK Clips, YouTube) |
| Пользователь | Nazwa użytkownika |
| Всего просмотров | Łączne wyświetlenia |
| Количество видео | Liczba video/clips |
| Просмотры вчера | Wyświetlenia z wczoraj |
| Просмотры неделю назад | Wyświetlenia sprzed tygodnia |
| Изменение за день (%) | Zmiana dzienna (%) |
| Изменение за неделю (%) | Zmiana tygodniowa (%) |
| Последнее видео | Tytuł ostatniego video |
| Просмотры последнего | Wyświetlenia ostatniego video |
| Дата последнего | Data ostatniego video |

## 🎯 Rezultat

Po skonfigurowaniu system będzie:
- ✅ Automatycznie zapisywać statystyki do Google Sheets
- ✅ Dodawać kolumny z historią (wczoraj, tydzień temu)
- ✅ Obliczać zmiany procentowe
- ✅ Wszystko po rosyjsku jak żądałeś




