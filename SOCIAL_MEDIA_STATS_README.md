# 📊 Social Media Stats Checker

Ulepszony system do sprawdzania statystyk na platformach społecznościowych z użyciem oficjalnych API i bibliotek.

## 🚀 Funkcje

- **Instagram**: Używa `instaloader` do pobierania danych profilu
- **TikTok**: Używa `TikTokApi` do pobierania statystyk
- **YouTube**: Używa YouTube Data API v3 (wymaga API key)
- **VK**: Używa VK API (wymaga token) z fallback do scraping
- **Likee**: Używa scraping (brak oficjalnego API)

## 📦 Instalacja

```bash
# Aktywuj virtual environment
source .venv/bin/activate

# Zainstaluj biblioteki
pip install instaloader TikTokApi vk-api requests
```

## 🔧 Konfiguracja

### 1. YouTube Data API v3

1. Idź do [Google Cloud Console](https://console.developers.google.com/)
2. Utwórz projekt lub wybierz istniejący
3. Włącz YouTube Data API v3
4. Utwórz klucz API
5. Dodaj do `.env`:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key_here
   ```

### 2. VK API

1. Idź do [VK Apps](https://vk.com/apps?act=manage)
2. Utwórz aplikację
3. Uzyskaj access token
4. Dodaj do `.env`:
   ```
   VK_TOKEN=your_vk_token_here
   ```

### 3. Instagram

Nie wymaga API key - używa `instaloader`.

### 4. TikTok

Nie wymaga API key - używa `TikTokApi`.

### 5. Likee

Nie wymaga API key - używa scraping.

## 🎯 Użycie

### Podstawowe użycie

```python
from enhanced_social_stats import EnhancedSocialStatsChecker

# Tworzymy checker
checker = EnhancedSocialStatsChecker()

# Sprawdzamy Instagram
result = checker.check_instagram_stats("https://www.instagram.com/username")
print(result)

# Sprawdzamy TikTok
result = checker.check_tiktok_stats("https://www.tiktok.com/@username")
print(result)

# Sprawdzamy wszystkie platformy
urls = {
    'Instagram': 'https://www.instagram.com/username',
    'YouTube': 'https://www.youtube.com/@username',
    'TikTok': 'https://www.tiktok.com/@username',
    'VK': 'https://vk.com/username',
    'Likee': 'https://l.likee.video/p/username'
}

results = checker.check_all_platforms(urls)
```

### Uruchomienie skryptu

```bash
# Uruchom główny skrypt
python enhanced_social_stats.py

# Uruchom test
python test_enhanced_social.py

# Sprawdź konfigurację
python social_media_config.py
```

## 📊 Przykładowe wyniki

### Instagram
```json
{
  "platform": "Instagram",
  "username": "raachel_fb",
  "followers": 5,
  "following": 6,
  "posts": 62,
  "is_verified": false,
  "is_private": false,
  "biography": "Рэйчел — Амбассадор настроения...",
  "method": "instaloader"
}
```

### TikTok
```json
{
  "platform": "TikTok",
  "username": "daniryb_fb",
  "followers": 0,
  "following": 0,
  "posts": 0,
  "likes": 0,
  "is_verified": false,
  "method": "TikTokApi"
}
```

### YouTube (z API key)
```json
{
  "platform": "YouTube",
  "channel_id": "UC...",
  "title": "Channel Name",
  "subscribers": 1000,
  "videos": 50,
  "views": 100000,
  "is_verified": false,
  "method": "YouTube Data API"
}
```

## 🔧 Rozwiązywanie problemów

### TikTokApi błędy
- TikTokApi może wymagać dodatkowej konfiguracji
- W przypadku błędów, system automatycznie przełącza się na scraping

### Instagram rate limiting
- `instaloader` może być ograniczony przez Instagram
- System automatycznie obsługuje błędy

### YouTube API limits
- YouTube API ma limity dzienne
- Bez API key, YouTube jest niedostępny

### VK API
- Bez token, system używa scraping
- Scraping może być mniej dokładny

## 📝 Pliki

- `enhanced_social_stats.py` - Główny skrypt
- `test_enhanced_social.py` - Test skrypt
- `social_media_config.py` - Konfiguracja API keys
- `requirements.txt` - Zależności

## 🚀 Przykłady użycia

### Sprawdzenie pojedynczej platformy
```python
checker = EnhancedSocialStatsChecker()
result = checker.check_instagram_stats("https://www.instagram.com/username")
```

### Sprawdzenie wszystkich platform
```python
urls = {
    'Instagram': 'https://www.instagram.com/username',
    'TikTok': 'https://www.tiktok.com/@username'
}
results = checker.check_all_platforms(urls)
```

### Zapis do JSON
```python
import json

results = checker.check_all_platforms(urls)
with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

## ⚠️ Uwagi

- Niektóre platformy mogą blokować automatyczne zapytania
- API keys są wymagane dla YouTube i VK (opcjonalne)
- System automatycznie obsługuje błędy i fallback
- Wyniki są zapisywane do plików JSON z timestamp

## 🔄 Aktualizacje

- **v1.0**: Podstawowa funkcjonalność
- **v1.1**: Dodano TikTokApi i instaloader
- **v1.2**: Dodano fallback mechanisms
- **v1.3**: Dodano VK API support




