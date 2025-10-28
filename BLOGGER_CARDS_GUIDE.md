# Blogger Cards - Przewodnik użytkownika

## Opis funkcjonalności

Funkcjonalność **Blogger Cards** pozwala na tworzenie kart blogerów ze statystykami z ich profili społecznościowych. Bot automatycznie zbiera dane z różnych platform i zapisuje je w Google Sheets.

## Jak używać

### 1. Rozpoczęcie tworzenia karty

Wyślij komendę `/blogger` do bota:

```
/blogger
```

### 2. Podanie imienia blogera

Bot poprosi o imię blogera. Wpisz imię, np.:

```
Лиза
```

### 3. Dodawanie linków do profili

Bot poprosi o linki do profili społecznościowych. Dodawaj linki pojedynczo:

```
https://www.instagram.com/raachel_fb?igsh=cm9peTlsOHNsY20x&utm_source=qr
```

```
https://www.tiktok.com/@daniryb_fb?_t=ZS-8zmIVT7JQ5&_r=1
```

```
https://vk.com/raachel_fb
```

```
https://www.youtube.com/@raachel_fb
```

```
https://l.likee.video/p/jSQPBE
```

### 4. Zakończenie

Gdy dodasz wszystkie linki, napisz:

```
готово
```

## Obsługiwane platformy

- **Instagram** (instagram.com)
- **YouTube** (youtube.com, youtu.be)
- **TikTok** (tiktok.com)
- **VK** (vk.com)
- **Likee** (likee.video)

## Zbierane statystyki

Dla każdej platformy bot zbiera:

- **Подписчики** - liczba obserwujących
- **Видео** - liczba opublikowanych filmów
- **Просмотры** - całkowita liczba wyświetleń

## Przykład użycia

```
Użytkownik: /blogger
Bot: 👤 Создание карты блогера

Введите имя блогера (например: Лиза):

Użytkownik: Лиза
Bot: ✅ Имя блогера: **Лиза**

🔗 Теперь отправьте ссылки на профили социальных сетей:

Поддерживаемые платформы:
• Instagram
• YouTube
• TikTok
• VK
• Likee

Отправляйте по одной ссылке за раз.
Когда закончите, отправьте: **готово**

Użytkownik: https://www.instagram.com/raachel_fb?igsh=cm9peTlsOHNsY20x&utm_source=qr
Bot: ✅ Добавлена ссылка: https://www.instagram.com/raachel_fb?igsh=cm9peTlsOHNsY20x&utm_source=qr

Всего ссылок: 1

Отправьте еще ссылку или напишите **готово** для завершения.

Użytkownik: https://www.tiktok.com/@daniryb_fb?_t=ZS-8zmIVT7JQ5&_r=1
Bot: ✅ Добавлена ссылка: https://www.tiktok.com/@daniryb_fb?_t=ZS-8zmIVT7JQ5&_r=1

Всего ссылок: 2

Отправьте еще ссылку или напишите **готово** для завершения.

Użytkownik: готово
Bot: 🔄 Обрабатываю ссылки для **Лиза**...
Найдено ссылок: 2

📊 Собираю статистику Instagram...
📊 Собираю статистику TikTok...
💾 Сохраняю в Google Sheets...

✅ **Карта блогера создана!**

📊 **Статистика для Лиза:**

**Instagram:**
• Подписчики: 1,234
• Видео: 45
• Просмотры: 12,345

**TikTok:**
• Подписчики: 2,345
• Видео: 67
• Просмотры: 23,456

📈 **Общее количество подписчиков: 3,579**

📋 Данные сохранены в Google Sheets.
```

## Zapisywanie danych

Wszystkie dane są automatycznie zapisywane w Google Sheets w następującym formacie:

| Platform | Blogger Name | Followers | Videos | Views | URL |
|----------|--------------|-----------|--------|-------|-----|
| Instagram | Лиза | 1,234 | 45 | 12,345 | https://instagram.com/... |
| TikTok | Лиза | 2,345 | 67 | 23,456 | https://tiktok.com/... |

## Obsługa błędów

- **Nieprawidłowy link**: Bot wyświetli komunikat o błędzie i poprosi o ponowne wprowadzenie
- **Błąd API**: Jeśli nie można pobrać statystyk, bot wyświetli komunikat o błędzie dla danej platformy
- **Błąd Google Sheets**: Bot wyświetli komunikat o błędzie zapisu

## Wymagania

- Skonfigurowane Google Sheets (patrz `GOOGLE_SHEETS_SETUP.md`)
- Skonfigurowane API klucze dla platform społecznościowych (patrz `SOCIAL_MEDIA_STATS_README.md`)

## Komendy

- `/blogger` - rozpocznij tworzenie karty blogera
- `/help` - wyświetl pomoc (zawiera informacje o `/blogger`)
