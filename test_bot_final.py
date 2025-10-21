#!/usr/bin/env python3
"""
Finalny test bota Telegram
"""

import os
import requests
import time
from dotenv import load_dotenv


def test_bot_status():
    """Testuje status bota"""
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN nie znaleziony!")
        return False
    
    try:
        # Testujemy API
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                bot_info = data['result']
                print(f"✅ Bot działa!")
                print(f"   Nazwa: {bot_info['first_name']}")
                print(f"   Username: @{bot_info['username']}")
                print(f"   ID: {bot_info['id']}")
                return True
        
        print(f"❌ Błąd API: {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return False


def test_yandex_status():
    """Testuje status Yandex Disk"""
    load_dotenv()
    
    yandex_token = os.getenv('YANDEX_DISK_TOKEN')
    if not yandex_token:
        print("⚠️ YANDEX_DISK_TOKEN nie ustawiony")
        return True
    
    try:
        import yadisk
        yandex = yadisk.YaDisk(token=yandex_token)
        
        if yandex.check_token():
            print("✅ Yandex Disk działa!")
            return True
        else:
            print("❌ Yandex Disk nie działa!")
            return False
            
    except Exception as e:
        print(f"❌ Błąd Yandex Disk: {e}")
        return False


def main():
    """Główna funkcja testowania"""
    print("🧪 FINALNY TEST BOTA TELEGRAM")
    print("=" * 40)
    
    # Test bota
    bot_ok = test_bot_status()
    
    # Test Yandex
    yandex_ok = test_yandex_status()
    
    print("\n📊 WYNIKI:")
    print(f"   Telegram Bot: {'✅ OK' if bot_ok else '❌ Błąd'}")
    print(f"   Yandex Disk: {'✅ OK' if yandex_ok else '❌ Błąd'}")
    
    if bot_ok and yandex_ok:
        print("\n🎉 WSZYSTKO DZIAŁA!")
        print("✅ Bot jest gotowy do użycia")
        print("📱 Znajdź bota: @unique_video_factory_bot")
        print("🎬 Wyślij video i wybierz filtr!")
    else:
        print("\n❌ Niektóre testy nie przeszły")
        print("💡 Sprawdź konfigurację")


if __name__ == "__main__":
    main()




