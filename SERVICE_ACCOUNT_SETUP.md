# 🔧 Konfiguracja Service Account dla Google Sheets

## 📋 Masz już projekt: `bold-origin-465417-c2`

### 🔧 Krok 1: Utwórz Service Account

1. **Idź do Google Cloud Console:**
   - Otwórz: https://console.cloud.google.com/
   - Wybierz projekt: `bold-origin-465417-c2`

2. **Idź do Service Accounts:**
   - W menu po lewej: **IAM & Admin** → **Service Accounts**
   - Kliknij **"Create Service Account"**

3. **Wypełnij dane:**
   - **Service account name**: `unique-video-factory-sheets`
   - **Service account ID**: `unique-video-factory-sheets` (automatycznie)
   - **Description**: `Service account for Google Sheets integration`
   - Kliknij **"Create and Continue"**

4. **Nadaj uprawnienia:**
   - **Role**: Wybierz `Editor` (lub `Google Sheets API` + `Google Drive API`)
   - Kliknij **"Continue"**

5. **Zakończ:**
   - Kliknij **"Done"**

### 🔧 Krok 2: Utwórz klucz JSON

1. **Znajdź utworzony Service Account:**
   - Na liście Service Accounts kliknij na `unique-video-factory-sheets`

2. **Utwórz klucz:**
   - Idź do zakładki **"Keys"**
   - Kliknij **"Add Key"** → **"Create new key"**
   - Wybierz **"JSON"**
   - Kliknij **"Create"**

3. **Pobierz plik:**
   - Plik JSON zostanie automatycznie pobrany
   - **Zastąp** zawartość pliku `google_credentials.json` pobranymi danymi

### 🔧 Krok 3: Włącz wymagane API

1. **Włącz Google Sheets API:**
   - W menu po lewej: **APIs & Services** → **Library**
   - Wyszukaj: `Google Sheets API`
   - Kliknij na wynik
   - Kliknij **"Enable"**

2. **Włącz Google Drive API:**
   - Wyszukaj: `Google Drive API`
   - Kliknij na wynik
   - Kliknij **"Enable"**

### 🔧 Krok 4: Udostępnij arkusz Service Account

1. **Otwórz swój arkusz:**
   - Idź do: https://docs.google.com/spreadsheets/d/1p6bQ3Ck7qMv8M6vobXQcnEjXXdECAoBOlmy2_n9sUPI/edit

2. **Udostępnij Service Account:**
   - Kliknij **"Share"** (prawy górny róg)
   - W polu **"Add people and groups"** wpisz email Service Account
   - Email znajdziesz w pliku JSON jako `client_email`
   - **Role**: Wybierz **"Editor"**
   - Kliknij **"Send"**

### 🔧 Krok 5: Sprawdź konfigurację

1. **Sprawdź plik credentials:**
   ```bash
   cat google_credentials.json | head -5
   ```

2. **Przetestuj połączenie:**
   ```bash
   python test_google_sheets.py
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




