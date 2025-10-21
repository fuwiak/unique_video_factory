# 🔗 Konfiguracja Google Sheets

## 📋 Instrukcje krok po kroku

### 1. Utwórz projekt w Google Cloud Console

1. Idź do [Google Cloud Console](https://console.cloud.google.com/)
2. Utwórz nowy projekt lub wybierz istniejący
3. Włącz Google Sheets API i Google Drive API

### 2. Utwórz Service Account

1. W Google Cloud Console, idź do **IAM & Admin** → **Service Accounts**
2. Kliknij **Create Service Account**
3. Wypełnij:
   - **Name**: `unique-video-factory-sheets`
   - **Description**: `Service account for Google Sheets integration`
4. Kliknij **Create and Continue**

### 3. Nadaj uprawnienia

1. W sekcji **Grant this service account access to project**:
   - **Role**: `Editor` (lub `Google Sheets API` + `Google Drive API`)
2. Kliknij **Continue** → **Done**

### 4. Utwórz klucz JSON

1. Kliknij na utworzony Service Account
2. Idź do zakładki **Keys**
3. Kliknij **Add Key** → **Create new key**
4. Wybierz **JSON** i kliknij **Create**
5. Pobierz plik JSON

### 5. Skonfiguruj plik credentials

1. Skopiuj pobrany plik JSON do `google_credentials.json` w folderze projektu
2. Upewnij się, że plik ma poprawną strukturę:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

### 6. Udostępnij arkusz Service Account

1. Otwórz swój arkusz Google Sheets
2. Kliknij **Share** (Udostępnij)
3. Dodaj email Service Account (z pliku JSON: `client_email`)
4. Nadaj uprawnienia **Editor**

### 7. Sprawdź ID arkusza

W URL arkusza znajdź ID:
```
https://docs.google.com/spreadsheets/d/1p6bQ3Ck7qMv8M6vobXQcnEjXXdECAoBOlmy2_n9sUPI/edit
```
ID to: `1p6bQ3Ck7qMv8M6vobXQcnEjXXdECAoBOlmy2_n9sUPI`

## 🧪 Test integracji

Uruchom test:
```bash
python google_sheets_integration.py
```

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

## 🔧 Rozwiązywanie problemów

### Błąd: "Brak pliku google_credentials.json"
- Sprawdź czy plik istnieje w folderze projektu
- Sprawdź czy ma poprawną strukturę JSON

### Błąd: "Permission denied"
- Sprawdź czy Service Account ma dostęp do arkusza
- Sprawdź czy arkusz jest udostępniony dla Service Account

### Błąd: "Invalid credentials"
- Sprawdź czy plik JSON jest poprawny
- Sprawdź czy Service Account ma odpowiednie uprawnienia w Google Cloud Console

## 📝 Przykład użycia

```python
from google_sheets_integration import GoogleSheetsIntegration

# Tworzymy integrację
integration = GoogleSheetsIntegration()

# Dane do zapisania
data = {
    "VK_Clips": {
        "platform": "VK Clips",
        "user_name": "Reychel K",
        "total_views": 47,
        "clips_count": 10
    }
}

# Zapisujemy do arkusza
success = integration.save_to_sheets(data)
```




