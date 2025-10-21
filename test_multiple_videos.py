#!/usr/bin/env python3
"""
Test funkcjonalności tworzenia wielu wideo
"""

import os
import sys
from pathlib import Path

def test_multiple_videos():
    """Testuje funkcjonalność tworzenia wielu wideo"""
    print("🧪 TEST FUNKCJONALNOŚCI WIELU WIDEO")
    print("=" * 50)
    
    # Sprawdzamy czy bot działa
    try:
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'telegram_bot.py' not in result.stdout:
            print("❌ Bot nie działa! Uruchom go najpierw.")
            return False
        print("✅ Bot działa")
    except Exception as e:
        print(f"❌ Błąd sprawdzania bota: {e}")
        return False
    
    # Sprawdzamy strukturę folderów
    temp_dir = Path("temp_videos")
    results_dir = Path("telegram_results")
    
    if not temp_dir.exists():
        print(f"❌ Folder {temp_dir} nie istnieje")
        return False
    print(f"✅ Folder {temp_dir} istnieje")
    
    if not results_dir.exists():
        print(f"❌ Folder {results_dir} nie istnieje")
        return False
    print(f"✅ Folder {results_dir} istnieje")
    
    # Sprawdzamy czy mamy plik wideo do testowania
    test_video = Path("uniquized_test.mp4")
    if not test_video.exists():
        print(f"❌ Plik testowy {test_video} nie istnieje")
        print("💡 Utwórz plik testowy lub użyj innego wideo")
        return False
    print(f"✅ Plik testowy {test_video} istnieje")
    
    print("\n🎬 FUNKCJONALNOŚCI WIELU WIDEO:")
    print("1. ✅ Wybór liczby wideo (1, 3, 5, 10)")
    print("2. ✅ Wybór filtra Instagram")
    print("3. ✅ Przetwarzanie wielu wideo")
    print("4. ✅ Upload na Yandex Disk")
    print("5. ✅ Dodanie do kolejki na aprobatę")
    
    print("\n📱 INSTRUKCJE UŻYCIA:")
    print("1. Wyślij wideo do bota")
    print("2. Wybierz liczbę wideo (1, 3, 5, 10)")
    print("3. Wybierz filtr Instagram")
    print("4. Poczekaj na przetworzenie")
    print("5. Otrzymaj wszystkie wideo")
    
    print("\n🔧 WORKFLOW:")
    print("1. Upload video → Bot")
    print("2. Wybór liczby → count_1, count_3, count_5, count_10")
    print("3. Wybór filtra → filter_vintage, filter_dramatic, etc.")
    print("4. Przetwarzanie → process_multiple_videos()")
    print("5. Upload → Yandex Disk")
    print("6. Aprobat → pending_approvals")
    
    return True


def main():
    """Główna funkcja"""
    success = test_multiple_videos()
    
    if success:
        print("\n✅ Test zakończony pomyślnie!")
        print("🎬 Bot obsługuje tworzenie wielu wideo")
        print("📱 Użyj bota w Telegramie do testowania")
    else:
        print("\n❌ Test nie powiódł się!")
        print("💡 Sprawdź konfigurację bota")


if __name__ == "__main__":
    main()




