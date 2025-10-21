#!/usr/bin/env python3
"""
Простой тест уникализации видео
"""

import os
from video_uniquizer import VideoUniquizer

def test_uniquizer():
    print("🎬 Тестирование уникализатора видео")
    print("=" * 40)
    
    # Проверяем наличие видео
    input_video = "vtec_idw_light.mp4"
    if not os.path.exists(input_video):
        print(f"❌ Файл {input_video} не найден!")
        return
    
    print(f"📁 Найден файл: {input_video}")
    print(f"📊 Размер: {os.path.getsize(input_video) / (1024*1024):.1f} MB")
    
    try:
        # Создаем уникализатор
        print("🔧 Создаем уникализатор...")
        uniquizer = VideoUniquizer()
        
        # Тестируем только визуальные эффекты (быстрее)
        print("🎨 Применяем визуальные эффекты...")
        result = uniquizer.apply_visual_effects(
            input_video, 
            "test_output.mp4"
        )
        
        print(f"✅ Тест завершен: {result}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_uniquizer()
