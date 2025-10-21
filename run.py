#!/usr/bin/env python3
"""
Простой скрипт для запуска уникализации видео
"""

import os
import sys
from video_uniquizer import VideoUniquizer


def main():
    print("🎬 Нейросетевая уникализация видео")
    print("=" * 50)
    
    # Проверяем аргументы командной строки или просим ввести
    if len(sys.argv) >= 2:
        input_video = sys.argv[1]
        output_video = sys.argv[2] if len(sys.argv) > 2 else "uniquized_" + os.path.basename(input_video)
    else:
        # Интерактивный ввод
        print("Введите путь к видео файлу:")
        input_video = input("> ").strip()
        
        if not input_video:
            print("❌ Не указан файл!")
            return
            
        # Предлагаем имя выходного файла
        base_name = os.path.splitext(os.path.basename(input_video))[0]
        output_video = f"uniquized_{base_name}.mp4"
        print(f"Выходной файл: {output_video}")
    
    # Проверяем существование входного файла
    if not os.path.exists(input_video):
        print(f"❌ Файл {input_video} не найден!")
        return
    
    print(f"📁 Входное видео: {input_video}")
    print(f"📁 Выходное видео: {output_video}")
    print()
    
    try:
        # Создаем уникализатор
        uniquizer = VideoUniquizer()
        
        # Уникализируем видео
        print("🚀 Начинаем обработку...")
        result_path = uniquizer.uniquize_video(
            input_path=input_video,
            output_path=output_video,
            effects=['temporal', 'visual', 'neural']  # Все эффекты
        )
        
        print(f"✅ Видео успешно обработано: {result_path}")
        print(f"📊 Размер файла: {os.path.getsize(result_path) / (1024*1024):.1f} MB")
        
    except Exception as e:
        print(f"❌ Ошибка при обработке: {e}")
        return


if __name__ == "__main__":
    main()
