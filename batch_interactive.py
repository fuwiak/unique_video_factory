#!/usr/bin/env python3
"""
Интерактивный скрипт для пакетной генерации видео
"""

import os
import asyncio
from batch_generator import BatchVideoGenerator


def get_video_files():
    """Найти все видео файлы в текущей директории"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    video_files = []
    
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in video_extensions):
            video_files.append(file)
    
    return sorted(video_files)


def choose_video():
    """Позволить пользователю выбрать видео файл"""
    video_files = get_video_files()
    
    if not video_files:
        print("❌ Видео файлы не найдены в текущей директории!")
        print("Поддерживаемые форматы: .mp4, .avi, .mov, .mkv, .wmv, .flv")
        return None
    
    print("📁 Найденные видео файлы:")
    for i, file in enumerate(video_files, 1):
        size_mb = os.path.getsize(file) / (1024*1024)
        print(f"   {i}. {file} ({size_mb:.1f} MB)")
    
    print(f"   {len(video_files) + 1}. Ввести свой путь")
    print()
    
    while True:
        try:
            choice = input("Выберите файл (номер): ").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(video_files):
                    return video_files[choice_num - 1]
                elif choice_num == len(video_files) + 1:
                    custom_path = input("Введите путь к файлу: ").strip()
                    if os.path.exists(custom_path):
                        return custom_path
                    else:
                        print("❌ Файл не существует!")
                        continue
                else:
                    print("❌ Неверный номер!")
                    continue
            else:
                print("❌ Введите номер!")
                continue
                
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            continue


def get_generation_params():
    """Получить параметры генерации"""
    print("\n⚙️ Параметры генерации:")
    
    # Количество версий
    while True:
        try:
            n_versions = input("Количество версий (по умолчанию 3): ").strip()
            if not n_versions:
                n_versions = 3
            else:
                n_versions = int(n_versions)
            
            if n_versions > 0:
                break
            else:
                print("❌ Количество должно быть больше 0!")
        except ValueError:
            print("❌ Введите число!")
    
    # Имя запуска
    run_name = input("Имя запуска (оставить пустым для автогенерации): ").strip()
    if not run_name:
        run_name = None
    
    return n_versions, run_name


def choose_generation_method():
    """Выбрать метод генерации"""
    print("\n🚀 Выберите метод генерации:")
    print("1. Асинхронная (async/await) - быстрая, но может быть нестабильной")
    print("2. Параллельная (multiprocessing) - стабильная, но медленнее")
    print("3. Последовательная - самая стабильная, но медленная")
    
    while True:
        try:
            choice = input("Выберите метод (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return choice
            else:
                print("❌ Выберите 1, 2 или 3!")
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            return None


async def main_async():
    """Основная асинхронная функция"""
    print("🎬 ПАКЕТНАЯ ГЕНЕРАЦИЯ ВИДЕО")
    print("=" * 50)
    
    try:
        # Выбираем видео
        input_video = choose_video()
        if not input_video:
            return
        
        print(f"\n📁 Выбранный файл: {input_video}")
        size_mb = os.path.getsize(input_video) / (1024*1024)
        print(f"📊 Размер: {size_mb:.1f} MB")
        
        # Получаем параметры
        n_versions, run_name = get_generation_params()
        
        # Выбираем метод
        method = choose_generation_method()
        if not method:
            return
        
        print(f"\n📋 Параметры:")
        print(f"   Файл: {input_video}")
        print(f"   Версий: {n_versions}")
        print(f"   Запуск: {run_name or 'автогенерация'}")
        print(f"   Метод: {['асинхронная', 'параллельная', 'последовательная'][int(method)-1]}")
        
        # Подтверждение
        confirm = input("\nПродолжить? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes', 'да', 'д']:
            print("❌ Отменено!")
            return
        
        print(f"\n🚀 Начинаем генерацию {n_versions} версий...")
        
        # Создаем генератор
        generator = BatchVideoGenerator()
        
        # Запускаем генерацию
        if method == "1":
            # Асинхронная
            result = await generator.generate_batch_async(
                input_video, n_versions, run_name
            )
        elif method == "2":
            # Параллельная
            result = generator.generate_batch_parallel(
                input_video, n_versions, run_name
            )
        else:
            # Последовательная
            result = generator.generate_batch_sequential(
                input_video, n_versions, run_name
            )
        
        print(f"\n🎉 ГЕНЕРАЦИЯ ЗАВЕРШЕНА!")
        print(f"📁 Папка: {result['run_dir']}")
        print(f"✅ Успешно: {result['successful']}/{result['total_versions']}")
        
        # Показываем список файлов
        run_dir = result['run_dir']
        print(f"\n📁 Созданные файлы:")
        for i in range(1, n_versions + 1):
            version_dir = f"{run_dir}/versions/version_{i:03d}"
            if os.path.exists(version_dir):
                files = os.listdir(version_dir)
                video_files = [f for f in files if f.endswith('.mp4')]
                if video_files:
                    file_path = f"{version_dir}/{video_files[0]}"
                    size_mb = os.path.getsize(file_path) / (1024*1024)
                    print(f"   • Версия {i}: {size_mb:.1f} MB")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Главная функция"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
