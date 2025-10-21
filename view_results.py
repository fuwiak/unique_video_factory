#!/usr/bin/env python3
"""
Скрипт для просмотра результатов пакетной генерации
"""

import os
import json
from pathlib import Path
from batch_generator import BatchVideoGenerator


def show_runs_list():
    """Показать список всех запусков"""
    generator = BatchVideoGenerator()
    runs = generator.list_runs()
    
    if not runs:
        print("❌ Запуски не найдены!")
        return
    
    print("📋 СПИСОК ЗАПУСКОВ")
    print("=" * 60)
    
    for i, run in enumerate(runs, 1):
        print(f"{i}. {run['run_name']}")
        print(f"   📁 Папка: {run['run_dir']}")
        print(f"   📹 Видео: {run['input_video']}")
        print(f"   📊 Версий: {run['successful']}/{run['total_versions']}")
        print(f"   🕒 Время: {run['generated_at']}")
        print()


def show_run_details(run_name: str):
    """Показать детали конкретного запуска"""
    generator = BatchVideoGenerator()
    run_info = generator.get_run_info(run_name)
    
    if not run_info:
        print(f"❌ Запуск '{run_name}' не найден!")
        return
    
    print(f"📊 ДЕТАЛИ ЗАПУСКА: {run_name}")
    print("=" * 60)
    print(f"📁 Папка: {run_info['run_dir']}")
    print(f"📹 Входное видео: {run_info['input_video']}")
    print(f"📊 Всего версий: {run_info['total_versions']}")
    print(f"✅ Успешно: {run_info['successful']}")
    print(f"❌ Ошибок: {run_info['failed']}")
    print(f"🕒 Время: {run_info['generated_at']}")
    print()
    
    # Показываем детали каждой версии
    print("📝 ВЕРСИИ:")
    for i, result in enumerate(run_info['results'], 1):
        if result.get('status') == 'success':
            print(f"   ✅ Версия {i}: {result['effects']} ({result['file_size_mb']:.1f} MB)")
        else:
            print(f"   ❌ Версия {i}: ОШИБКА - {result.get('error', 'Неизвестная ошибка')}")
    
    print()
    
    # Показываем файлы
    run_dir = Path(run_info['run_dir'])
    if run_dir.exists():
        print("📁 ФАЙЛЫ:")
        versions_dir = run_dir / "versions"
        if versions_dir.exists():
            for version_dir in sorted(versions_dir.iterdir()):
                if version_dir.is_dir():
                    version_name = version_dir.name
                    video_files = list(version_dir.glob("*.mp4"))
                    if video_files:
                        video_file = video_files[0]
                        size_mb = video_file.stat().st_size / (1024*1024)
                        print(f"   • {version_name}: {video_file.name} ({size_mb:.1f} MB)")


def show_run_files(run_name: str):
    """Показать файлы конкретного запуска"""
    generator = BatchVideoGenerator()
    run_info = generator.get_run_info(run_name)
    
    if not run_info:
        print(f"❌ Запуск '{run_name}' не найден!")
        return
    
    run_dir = Path(run_info['run_dir'])
    if not run_dir.exists():
        print(f"❌ Папка запуска не существует: {run_dir}")
        return
    
    print(f"📁 ФАЙЛЫ ЗАПУСКА: {run_name}")
    print("=" * 60)
    
    # Показываем структуру папок
    def show_tree(path: Path, prefix="", max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return
        
        items = sorted(path.iterdir())
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir() and current_depth < max_depth - 1:
                next_prefix = prefix + ("    " if is_last else "│   ")
                show_tree(item, next_prefix, max_depth, current_depth + 1)
    
    show_tree(run_dir)


def main():
    """Главная функция"""
    print("📊 ПРОСМОТР РЕЗУЛЬТАТОВ ГЕНЕРАЦИИ")
    print("=" * 50)
    
    while True:
        print("\nВыберите действие:")
        print("1. Показать список запусков")
        print("2. Показать детали запуска")
        print("3. Показать файлы запуска")
        print("4. Выход")
        
        choice = input("\nВведите номер (1-4): ").strip()
        
        if choice == "1":
            show_runs_list()
            
        elif choice == "2":
            run_name = input("Введите имя запуска: ").strip()
            if run_name:
                show_run_details(run_name)
            
        elif choice == "3":
            run_name = input("Введите имя запуска: ").strip()
            if run_name:
                show_run_files(run_name)
            
        elif choice == "4":
            print("👋 До свидания!")
            break
            
        else:
            print("❌ Неверный выбор!")


if __name__ == "__main__":
    main()
