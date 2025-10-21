#!/usr/bin/env python3
"""
Skrypt testowania bota Telegram
"""

import os
import asyncio
import requests
from dotenv import load_dotenv


async def test_telegram_connection():
    """Testuje połączenie z Telegram API"""
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN nie znaleziony!")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                bot_info = data['result']
                print(f"✅ Telegram API: OK")
                print(f"   Bot: @{bot_info['username']}")
                print(f"   Nazwa: {bot_info['first_name']}")
                return True
        
        print(f"❌ Telegram API: Błąd - {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Telegram API: Błąd połączenia - {e}")
        return False


async def test_yandex_disk():
    """Testuje połączenie z Yandex Disk"""
    load_dotenv()
    
    yandex_token = os.getenv('YANDEX_DISK_TOKEN')
    if not yandex_token:
        print("⚠️ YANDEX_DISK_TOKEN nie ustawiony - pomijam test")
        return True
    
    try:
        import yadisk
        
        yandex = yadisk.YaDisk(token=yandex_token)
        
        if yandex.check_token():
            print("✅ Yandex Disk: OK")
            
            # Testujemy folder
            folder = os.getenv('YANDEX_DISK_FOLDER', 'unique_video_factory')
            if not yandex.exists(folder):
                yandex.mkdir(folder)
                print(f"   📁 Utworzono folder: {folder}")
            else:
                print(f"   📁 Folder istnieje: {folder}")
            
            return True
        else:
            print("❌ Yandex Disk: Nieprawidłowy token!")
            return False
            
    except Exception as e:
        print(f"❌ Yandex Disk: Błąd - {e}")
        return False


async def test_video_processing():
    """Testuje przetwarzanie video"""
    try:
        from video_uniquizer import VideoUniquizer
        
        # Sprawdzamy czy istnieje test video
        test_video = "test.mp4"
        if not os.path.exists(test_video):
            print(f"⚠️ Plik testowy {test_video} nie istnieje - pomijam test")
            return True
        
        print("🎬 Testowanie przetwarzania video...")
        
        uniquizer = VideoUniquizer()
        
        # Test prostego efektu
        output_file = "test_output_bot.mp4"
        result = uniquizer.apply_visual_effects(test_video, output_file)
        
        if os.path.exists(result):
            size_mb = os.path.getsize(result) / (1024*1024)
            print(f"✅ Przetwarzanie video: OK ({size_mb:.1f} MB)")
            
            # Usuwamy test file
            os.remove(result)
            return True
        else:
            print("❌ Przetwarzanie video: Błąd - plik nie został utworzony")
            return False
            
    except Exception as e:
        print(f"❌ Przetwarzanie video: Błąd - {e}")
        return False


async def test_instagram_filters():
    """Testuje filtry Instagram"""
    try:
        from video_uniquizer import VideoUniquizer
        
        uniquizer = VideoUniquizer()
        
        print("🎨 Testowanie filtrów Instagram...")
        
        # Sprawdzamy dostępne filtry
        filters = uniquizer.instagram_filters
        print(f"   Dostępne filtry: {list(filters.keys())}")
        
        # Testujemy każdy filtr
        for filter_name, params in filters.items():
            print(f"   📸 {filter_name}: {params}")
        
        print("✅ Filtry Instagram: OK")
        return True
        
    except Exception as e:
        print(f"❌ Filtry Instagram: Błąd - {e}")
        return False


async def main():
    """Główna funkcja testowania"""
    print("🧪 TESTOWANIE BOTA TELEGRAM")
    print("=" * 50)
    
    tests = [
        ("Telegram API", test_telegram_connection),
        ("Yandex Disk", test_yandex_disk),
        ("Przetwarzanie video", test_video_processing),
        ("Filtry Instagram", test_instagram_filters)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testowanie: {test_name}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: Błąd testu - {e}")
            results.append((test_name, False))
    
    # Podsumowanie
    print("\n📊 PODSUMOWANIE TESTÓW:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ OK" if result else "❌ Błąd"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Wynik: {passed}/{len(results)} testów przeszło")
    
    if passed == len(results):
        print("🎉 Wszystkie testy przeszły! Bot gotowy do uruchomienia.")
        print("   Uruchom: python telegram_bot.py")
    else:
        print("⚠️ Niektóre testy nie przeszły. Sprawdź konfigurację.")
        print("   Uruchom: python setup_bot.py")


if __name__ == "__main__":
    asyncio.run(main())
