# Zapisywanie na Yandex Disk z Quick Mode

## 📋 Przegląd

Dodano możliwość zapisania wygenerowanego video na Yandex Disk bezpośrednio z Quick Mode (szybkiego trybu). Wcześniej Quick Mode nie oferował tej opcji - video było tylko wysyłane do użytkownika bez możliwości archiwizacji.

## ✨ Co się zmieniło?

### PRZED
```
Quick Mode:
1. Upload video
2. Wybór filtru  
3. Przetwarzanie
4. Wysłanie video
5. ❌ KONIEC (brak opcji zapisu)
```

### PO
```
Quick Mode:
1. Upload video
2. Wybór filtru
3. Przetwarzanie  
4. Wysłanie video
5. ✅ WYBÓR: Zapisać na Yandex Disk LUB Zakończyć
   → Jeśli zapis: metadane → upload → link
```

## 🎯 Workflow użytkownika

### Scenariusz 1: Zapisywanie na Yandex Disk

1. **Upload video i wybór filtru**
   - Użytkownik wysyła video
   - Wybiera "⚡ Быстрый фильтр"
   - Wybiera jeden z 12 filtrów

2. **Przetwarzanie i wysłanie**
   - Bot przetwarza video z wybranym filtrem
   - Wysyła gotowe video do użytkownika

3. **✨ NOWY KROK: Wybór dalszych działań**
   ```
   📋 Что делать дальше?
   
   • Записать на Yandex Disk с метаданными
   • Или завершить (временные файлы будут удалены)
   
   [💾 Записать на Yandex Disk] [✅ Готово (удалить временные файлы)]
   ```

4. **Jeśli wybrano zapisanie:**
   
   a. **ID ролика:**
   ```
   🆔 Введите ID ролика:
   (например: 001, 002, 123)
   ```
   
   b. **Имя блогера:**
   ```
   👤 Введите имя блогера:
   (например: Нина, Рэйчел, или новое имя)
   ```
   
   c. **Название папки:**
   ```
   📁 Введите название папки:
   (например: clips, videos, content)
   ```

5. **Upload i potwierdzenie:**
   ```
   ✅ Сохранено на Yandex Disk!
   
   📁 Путь: Медиабанк/Команда 1/Nina/clips/videos/20251029_001_quick.mp4
   🎨 Фильтр: Bright & Warm
   🆔 ID: 001
   👤 Блогер: Nina
   📂 Папка: clips
   🔗 Ссылка: https://disk.yandex.ru/i/xxx...
   ```

### Scenariusz 2: Pominięcie zapisu

1. **Po otrzymaniu video**
   - Użytkownik wybiera "✅ Готово"

2. **Potwierdzenie:**
   ```
   ✅ Готово!
   
   Временные файлы удалены.
   
   Отправьте новое видео для обработки.
   ```

## 🔧 Implementacja techniczna

### Zmiany w `telegram_bot.py`

#### 1. Zapisywanie danych po przetworzeniu
```python
# W process_quick_filter po wysłaniu video:
user_states[user_id]['quick_result'] = {
    'result_path': str(result_path),
    'input_path': str(input_path),
    'filter_name': filter_info['name'],
    'filter_id': filter_id,
    'file_size_mb': file_size_mb
}
```

#### 2. Przyciski wyboru
```python
keyboard = [
    [InlineKeyboardButton("💾 Записать на Yandex Disk", 
                         callback_data=f"save_yandex_{filter_id}")],
    [InlineKeyboardButton("✅ Готово (удалить временные файлы)", 
                         callback_data="quick_done")]
]
```

#### 3. Nowe handlery

**`handle_save_to_yandex`**
- Sprawdza czy `quick_result` istnieje w `user_states`
- Ustawia `status = 'saving_to_yandex'`
- Inicjuje zbieranie metadanych

**`handle_quick_done`**
- Usuwa pliki tymczasowe
- Czyści `quick_result` z `user_states`
- Wyświetla komunikat zakończenia

**`save_quick_result_to_yandex`**
- Pobiera dane z `quick_result`
- Tworzy strukturę folderów na Yandex Disk
- Uploaduje plik
- Tworzy publiczny link
- Usuwa pliki tymczasowe
- Wyświetla potwierdzenie

#### 4. Aktualizacja `handle_user_metadata`
```python
# Obsługa zarówno 'advanced' jak i 'saving_to_yandex'
mode = user_states[user_id].get('mode')
status = user_states[user_id].get('status')

if mode != 'advanced' and status != 'saving_to_yandex':
    return  # Ignoruj tekst w quick mode

# Po zebraniu wszystkich metadanych:
if status == 'saving_to_yandex':
    # Quick mode - zapisz na Yandex Disk
    await self.save_quick_result_to_yandex(update, user_id)
else:
    # Advanced mode - kontynuuj workflow
    # ... (wybór liczby video itp)
```

#### 5. Rejestracja callback handlers
```python
application.add_handler(CallbackQueryHandler(
    bot.handle_save_to_yandex, 
    pattern="^save_yandex_"
))
application.add_handler(CallbackQueryHandler(
    bot.handle_quick_done, 
    pattern="^quick_done$"
))
```

### Struktura plików na Yandex Disk

```
Медиабанк/
└── Команда 1/
    └── {Blogger Name}/
        └── {Folder Name}/
            └── videos/
                └── {YYYYMMDD}_{ID}_quick.mp4
```

Przykład:
```
Медиабанк/Команда 1/Nina/clips/videos/20251029_001_quick.mp4
```

## 📊 Callback Patterns

| Pattern | Handler | Opis |
|---------|---------|------|
| `save_yandex_{filter_id}` | `handle_save_to_yandex` | Zapisanie na Yandex Disk |
| `quick_done` | `handle_quick_done` | Zakończenie bez zapisu |

## 🧪 Testy

Plik: `test_yandex_save_quick.py`

Testuje:
- ✅ Workflow Quick Mode → Yandex Disk
- ✅ Workflow Quick Mode → Zakończenie bez zapisu
- ✅ Zbieranie metadanych
- ✅ Upload na Yandex Disk
- ✅ Tworzenie publicznego linku
- ✅ Usuwanie plików tymczasowych

## 🎁 Korzyści

1. **Elastyczność**
   - Użytkownik sam decyduje czy zapisać video
   - Nie wymusza zbierania metadanych jeśli nie są potrzebne

2. **Szybkość**
   - Quick Mode nadal szybki (jedno video, jeden filtr)
   - Opcja zapisu jest dodatkiem, nie utrudnieniem

3. **Archiwizacja**
   - Możliwość zapisania video na Yandex Disk
   - Publiczny link do udostępniania
   - Zorganizowana struktura folderów

4. **Zgodność**
   - Nie zmienia istniejącego Advanced Mode
   - Zachowuje wszystkie poprzednie funkcjonalności
   - Dodaje nową opcję bez breaking changes

## 🚀 Użycie

### Przykład 1: Szybkie przetworzenie i pobranie
```
Użytkownik → Upload video
Bot → Tryb? [Quick/Advanced]
Użytkownik → Quick
Bot → Filtr? [12 opcji]
Użytkownik → Bright & Warm
Bot → [przetwarza] → [wysyła video]
Bot → Zapisać na YD? [Tak/Nie]
Użytkownik → Nie, gotowe
Bot → Pliki usunięte ✅
```

### Przykład 2: Przetworzenie i archiwizacja
```
Użytkownik → Upload video
Bot → Tryb? [Quick/Advanced]
Użytkownik → Quick
Bot → Filtr? [12 opcji]
Użytkownik → Cinematic
Bot → [przetwarza] → [wysyła video]
Bot → Zapisać na YD? [Tak/Nie]
Użytkownik → Tak
Bot → ID ролика?
Użytkownik → 042
Bot → Имя блогера?
Użytkownik → Rachel
Bot → Название папки?
Użytkownik → videos
Bot → [uploaduje] → Zapisane! 🔗 Link: ...
```

## 📝 Notatki

- **Format nazwy pliku:** `{YYYYMMDD}_{ID}_quick.mp4`
- Suffix `_quick` odróżnia pliki z Quick Mode od Advanced Mode
- Pliki tymczasowe są zawsze usuwane (niezależnie od wyboru)
- Jeśli Yandex Disk nie jest skonfigurowany, wyświetla się ostrzeżenie
- Publiczny link jest tworzony automatycznie (jeśli możliwe)

## 🔄 Przyszłe ulepszenia

Możliwe rozszerzenia:
1. Opcja zapisu bez metadanych (domyślna nazwa pliku)
2. Wybór lokalizacji zapisu (różne foldery)
3. Batch processing w Quick Mode (wiele video naraz)
4. Podgląd przed zapisem
5. Edycja metadanych po zapisie

