#!/usr/bin/env python3
"""
Демонстрация всех эффектов социальных сетей
"""

import os
from video_uniquizer import VideoUniquizer

def demo_all_social_effects():
    print("🎬 ДЕМОНСТРАЦИЯ ЭФФЕКТОВ СОЦИАЛЬНЫХ СЕТЕЙ")
    print("=" * 60)
    
    input_video = "vtec_idw_light.mp4"
    
    if not os.path.exists(input_video):
        print(f"❌ Файл {input_video} не найден!")
        return
    
    print(f"📁 Входное видео: {input_video}")
    print(f"📊 Размер: {os.path.getsize(input_video) / (1024*1024):.1f} MB")
    print()
    
    try:
        # Создаем уникализатор
        uniquizer = VideoUniquizer()
        
        # Список всех эффектов
        effects = ['vintage', 'dramatic', 'soft', 'vibrant']
        effect_names = {
            'vintage': '📸 Винтажный (Instagram)',
            'dramatic': '🎭 Драматический (TikTok)', 
            'soft': '🌸 Мягкий (YouTube Shorts)',
            'vibrant': '🌈 Яркий (Instagram Stories)'
        }
        
        print("🚀 Создаем видео с разными эффектами...")
        print()
        
        for effect in effects:
            output_video = f"social_{effect}.mp4"
            print(f"🎨 {effect_names[effect]}")
            print(f"   Обрабатываем...")
            
            # Применяем только социальные эффекты
            result = uniquizer.apply_social_effects(input_video, output_video)
            
            if os.path.exists(result):
                size_mb = os.path.getsize(result) / (1024*1024)
                print(f"   ✅ Готово: {result} ({size_mb:.1f} MB)")
            else:
                print(f"   ❌ Ошибка создания файла")
            print()
        
        print("🎉 ВСЕ ЭФФЕКТЫ СОЗДАНЫ!")
        print()
        print("📁 Созданные файлы:")
        for effect in effects:
            filename = f"social_{effect}.mp4"
            if os.path.exists(filename):
                size_mb = os.path.getsize(filename) / (1024*1024)
                print(f"   • {filename} - {size_mb:.1f} MB")
        
        print()
        print("🎯 Описание эффектов:")
        print("   📸 Винтажный: Теплые тона, виньетка, зерно")
        print("   🎭 Драматический: Высокий контраст, тени, блики")
        print("   🌸 Мягкий: Размытие, повышенная яркость")
        print("   🌈 Яркий: Усиленная насыщенность, четкость")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_all_social_effects()
