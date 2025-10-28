# Railway Environment Variables for Google Sheets

## Wymagane zmienne środowiskowe dla Google Sheets

Aby funkcjonalność blogger cards działała w Railway, musisz ustawić następujące zmienne środowiskowe:

### Google Service Account Credentials

1. **GOOGLE_PROJECT_ID** - ID projektu Google Cloud
2. **GOOGLE_PRIVATE_KEY_ID** - ID klucza prywatnego
3. **GOOGLE_PRIVATE_KEY** - Klucz prywatny (z \\n jako nowe linie)
4. **GOOGLE_CLIENT_EMAIL** - Email konta serwisowego
5. **GOOGLE_CLIENT_ID** - ID klienta

### Jak uzyskać te dane:

1. Przejdź do [Google Cloud Console](https://console.cloud.google.com/)
2. Wybierz swój projekt
3. Przejdź do "IAM & Admin" > "Service Accounts"
4. Kliknij "Create Service Account"
5. Nadaj nazwę (np. "telegram-bot-sheets")
6. Kliknij "Create and Continue"
7. Dodaj role: "Editor" dla Google Sheets
8. Kliknij "Done"
9. Kliknij na utworzone konto serwisowe
10. Przejdź do zakładki "Keys"
11. Kliknij "Add Key" > "Create new key"
12. Wybierz "JSON" i pobierz plik

### Konwersja JSON na zmienne środowiskowe:

Z pobranego pliku JSON skopiuj wartości:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",           // GOOGLE_PROJECT_ID
  "private_key_id": "your-private-key-id",   // GOOGLE_PRIVATE_KEY_ID
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",  // GOOGLE_PRIVATE_KEY
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",  // GOOGLE_CLIENT_EMAIL
  "client_id": "your-client-id"              // GOOGLE_CLIENT_ID
}
```

### Ustawienie w Railway:

1. Przejdź do swojego projektu w Railway
2. Kliknij na "Variables"
3. Dodaj każdą zmienną:

```
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY_ID=your-private-key-id
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n
GOOGLE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=your-client-id
```

### Ważne uwagi:

- **GOOGLE_PRIVATE_KEY** musi mieć `\n` zamiast rzeczywistych nowych linii
- Upewnij się, że konto serwisowe ma dostęp do Google Sheets
- Udostępnij arkusz Google Sheets kontu serwisowemu (email z GOOGLE_CLIENT_EMAIL)

### Testowanie:

Po ustawieniu zmiennych, bot powinien logować:
```
Google Sheets połączone pomyślnie (ze zmiennych środowiskowych)
```

Zamiast błędu:
```
Google Sheets nie jest zainicjalizowane
```

### Alternatywa - plik lokalny:

Jeśli wolisz używać pliku lokalnie, skopiuj `google_credentials.json` do Railway (ale nie commituj go do git).
