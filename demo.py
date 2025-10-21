#!/usr/bin/env python3
"""
Демонстрация нейросетевой уникализации видео
"""

import os
from video_uniquizer import VideoUniquizer

def demo():
    print("🎬 ДЕМОНСТРАЦИЯ НЕЙРОСЕТЕВОЙ УНИКАЛИЗАЦИИ ВИДЕО")
    print("=" * 60)
    
    input_video = "vtec_idw_light.mp4"
    output_video = "uniquized_demo.mp4"
    
    if not os.path.exists(input_video):
        print(f"❌ Файл {input_video} не найден!")
        return
    
    print(f"📁 Входное видео: {input_video}")
    print(f"📊 Размер: {os.path.getsize(input_video) / (1024*1024):.1f} MB")
    print()
    
    try:
        # Создаем уникализатор
        print("🔧 Инициализация нейросетевого уникализатора...")
        uniquizer = VideoUniquizer()
        print()
        
        # Применяем все эффекты
        print("🚀 Начинаем естественную уникализацию...")
        print("   • Временные эффекты (минимальные изменения скорости)")
        print("   • Эффекты социальных сетей (Instagram, TikTok, YouTube)")
        print("   • Естественные фильтры и коррекции")
        print()
        
        result = uniquizer.uniquize_video(
            input_path=input_video,
            output_path=output_video,
            effects=['temporal', 'social']
        )
        
        print()
        print("✅ УНИКАЛИЗАЦИЯ ЗАВЕРШЕНА!")
        print(f"📁 Результат: {result}")
        print(f"📊 Размер: {os.path.getsize(result) / (1024*1024):.1f} MB")
        print()
        print("🎯 Применённые эффекты:")
        print("   • Минимальные изменения скорости (0.98x - 1.02x)")
        print("   • Естественная обрезка (1-2% от краев)")
        print("   • Фильтры социальных сетей:")
        print("     - Винтажный (Instagram)")
        print("     - Драматический (TikTok)")
        print("     - Мягкий (YouTube Shorts)")
        print("     - Яркий (Instagram Stories)")
        print("   • Естественные цветовые коррекции")
        print()
        print("🎉 Видео успешно уникализировано!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo()
