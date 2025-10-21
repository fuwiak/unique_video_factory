#!/usr/bin/env python3
"""
Быстрый просмотр результатов генерации
"""

import os
import json
from pathlib import Path


def show_quick_summary():
    """Быстрый обзор всех запусков"""
    base_dir = Path("generated_videos/runs")
    
    if not base_dir.exists():
        print("❌ Папка generated_videos не найдена!")
        return
    
    print("📊 БЫСТРЫЙ ОБЗОР РЕЗУЛЬТАТОВ")
    print("=" * 50)
    
    runs = []
    for run_dir in base_dir.iterdir():
        if run_dir.is_dir():
            summary_file = run_dir / "metadata" / "run_summary.json"
            if summary_file.exists():
                with open(summary_file, 'r', encoding='utf-8') as f:
                    run_info = json.load(f)
                runs.append(run_info)
    
    if not runs:
        print("❌ Запуски не найдены!")
        return
    
    # Сортируем по времени
    runs.sort(key=lambda x: x['generated_at'], reverse=True)
    
    print(f"📁 Найдено запусков: {len(runs)}")
    print()
    
    for i, run in enumerate(runs, 1):
        print(f"{i}. {run['run_name']}")
        print(f"   📹 Видео: {os.path.basename(run['input_video'])}")
        print(f"   📊 Версий: {run['successful']}/{run['total_versions']}")
        print(f"   📁 Папка: {run['run_dir']}")
        
        # Показываем размеры файлов
        run_path = Path(run['run_dir'])
        if run_path.exists():
            total_size = 0
            video_count = 0
            for version_dir in (run_path / "versions").iterdir():
                if version_dir.is_dir():
                    for video_file in version_dir.glob("*.mp4"):
                        total_size += video_file.stat().st_size
                        video_count += 1
            
            if video_count > 0:
                total_mb = total_size / (1024*1024)
                print(f"   💾 Размер: {total_mb:.1f} MB ({video_count} файлов)")
        
        print()


def show_run_files(run_name: str):
    """Показать файлы конкретного запуска"""
    run_path = Path(f"generated_videos/runs/{run_name}")
    
    if not run_path.exists():
        print(f"❌ Запуск '{run_name}' не найден!")
        return
    
    print(f"📁 ФАЙЛЫ ЗАПУСКА: {run_name}")
    print("=" * 50)
    
    versions_dir = run_path / "versions"
    if not versions_dir.exists():
        print("❌ Папка versions не найдена!")
        return
    
    total_size = 0
    for version_dir in sorted(versions_dir.iterdir()):
        if version_dir.is_dir():
            version_name = version_dir.name
            video_files = list(version_dir.glob("*.mp4"))
            
            if video_files:
                video_file = video_files[0]
                size_mb = video_file.stat().st_size / (1024*1024)
                total_size += video_file.stat().st_size
                
                print(f"   • {version_name}: {video_file.name} ({size_mb:.1f} MB)")
                
                # Показываем метаданные
                metadata_file = version_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    effects = metadata.get('effects', [])
                    print(f"     Эффекты: {', '.join(effects)}")
    
    if total_size > 0:
        total_mb = total_size / (1024*1024)
        print(f"\n💾 Общий размер: {total_mb:.1f} MB")


def main():
    """Главная функция"""
    import sys
    
    if len(sys.argv) > 1:
        # Показать файлы конкретного запуска
        run_name = sys.argv[1]
        show_run_files(run_name)
    else:
        # Показать общий обзор
        show_quick_summary()


if __name__ == "__main__":
    main()
