#!/usr/bin/env python3
"""
Система пакетной генерации видео с параллельной обработкой
"""

import os
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import List, Dict, Tuple
import json
from video_uniquizer import VideoUniquizer
from vidgear.gears import WriteGear
import cv2
import numpy as np


class BatchVideoGenerator:
    """
    Система пакетной генерации видео с организацией по папкам
    """
    
    def __init__(self, base_output_dir: str = "generated_videos"):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        
        # Создаем структуру папок как в MLflow
        self.runs_dir = self.base_output_dir / "runs"
        self.runs_dir.mkdir(exist_ok=True)
        
        print(f"📁 Базовая директория: {self.base_output_dir}")
    
    def create_run_folder(self, run_name: str = None) -> Path:
        """
        Создает папку для нового запуска (как в MLflow)
        """
        if run_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            run_name = f"run_{timestamp}"
        
        run_dir = self.runs_dir / run_name
        run_dir.mkdir(exist_ok=True)
        
        # Создаем подпапки для разных версий
        (run_dir / "versions").mkdir(exist_ok=True)
        (run_dir / "metadata").mkdir(exist_ok=True)
        
        print(f"📁 Создана папка запуска: {run_dir}")
        return run_dir
    
    def generate_single_version(self, input_video: str, run_dir: Path, 
                              version_id: int, effects: List[str]) -> Dict:
        """
        Генерирует одну версию видео
        """
        try:
            # Создаем папку для версии
            version_dir = run_dir / "versions" / f"version_{version_id:03d}"
            version_dir.mkdir(exist_ok=True)
            
            # Имя выходного файла
            output_file = version_dir / f"uniquized_v{version_id:03d}.mp4"
            
            print(f"🎬 Генерируем версию {version_id}: {effects}")
            
            # Создаем уникализатор
            uniquizer = VideoUniquizer()
            
            # Обрабатываем видео
            result_path = uniquizer.uniquize_video(
                input_path=input_video,
                output_path=str(output_file),
                effects=effects
            )
            
            # Собираем метаданные
            metadata = {
                "version_id": version_id,
                "effects": effects,
                "input_file": input_video,
                "output_file": str(result_path),
                "file_size_mb": os.path.getsize(result_path) / (1024*1024),
                "generated_at": datetime.now().isoformat(),
                "status": "success"
            }
            
            # Сохраняем метаданные
            metadata_file = version_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Версия {version_id} готова: {result_path}")
            return metadata
            
        except Exception as e:
            error_metadata = {
                "version_id": version_id,
                "effects": effects,
                "error": str(e),
                "generated_at": datetime.now().isoformat(),
                "status": "error"
            }
            print(f"❌ Ошибка в версии {version_id}: {e}")
            return error_metadata
    
    async def generate_batch_async(self, input_video: str, n_versions: int = 3, 
                                 run_name: str = None) -> Dict:
        """
        Асинхронная генерация пакета видео
        """
        print(f"🚀 Начинаем пакетную генерацию {n_versions} версий")
        
        # Создаем папку для запуска
        run_dir = self.create_run_folder(run_name)
        
        # Список возможных эффектов
        effect_combinations = [
            ['temporal'],
            ['social'],
            ['visual'],
            ['temporal', 'social'],
            ['temporal', 'visual'],
            ['social', 'visual'],
            ['temporal', 'social', 'visual']
        ]
        
        # Создаем задачи для параллельного выполнения
        tasks = []
        for i in range(n_versions):
            # Случайно выбираем комбинацию эффектов
            effects = effect_combinations[i % len(effect_combinations)]
            
            # Создаем задачу
            task = asyncio.create_task(
                self._generate_version_async(input_video, run_dir, i+1, effects)
            )
            tasks.append(task)
        
        # Ждем завершения всех задач
        print(f"⏳ Обрабатываем {len(tasks)} версий параллельно...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Собираем результаты
        successful = [r for r in results if isinstance(r, dict) and r.get('status') == 'success']
        failed = [r for r in results if isinstance(r, dict) and r.get('status') == 'error']
        
        # Создаем сводку запуска
        run_summary = {
            "run_name": run_name or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "input_video": input_video,
            "total_versions": n_versions,
            "successful": len(successful),
            "failed": len(failed),
            "run_dir": str(run_dir),
            "generated_at": datetime.now().isoformat(),
            "results": results
        }
        
        # Сохраняем сводку
        summary_file = run_dir / "metadata" / "run_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(run_summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 ПАКЕТНАЯ ГЕНЕРАЦИЯ ЗАВЕРШЕНА!")
        print(f"📁 Папка запуска: {run_dir}")
        print(f"✅ Успешно: {len(successful)}/{n_versions}")
        print(f"❌ Ошибок: {len(failed)}")
        
        return run_summary
    
    async def _generate_version_async(self, input_video: str, run_dir: Path, 
                                    version_id: int, effects: List[str]) -> Dict:
        """
        Асинхронная генерация одной версии
        """
        # Запускаем в отдельном потоке
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                self.generate_single_version,
                input_video, run_dir, version_id, effects
            )
        return result
    
    def generate_batch_parallel(self, input_video: str, n_versions: int = 3, 
                              run_name: str = None) -> Dict:
        """
        Параллельная генерация с использованием multiprocessing
        """
        print(f"🚀 Начинаем параллельную генерацию {n_versions} версий")
        
        # Создаем папку для запуска
        run_dir = self.create_run_folder(run_name)
        
        # Список возможных эффектов
        effect_combinations = [
            ['temporal'],
            ['social'], 
            ['visual'],
            ['temporal', 'social'],
            ['temporal', 'visual'],
            ['social', 'visual'],
            ['temporal', 'social', 'visual']
        ]
        
        # Подготавливаем аргументы для каждого процесса
        tasks = []
        for i in range(n_versions):
            effects = effect_combinations[i % len(effect_combinations)]
            tasks.append((input_video, run_dir, i+1, effects))
        
        # Запускаем параллельную обработку
        print(f"⏳ Обрабатываем {len(tasks)} версий параллельно...")
        
        with ProcessPoolExecutor(max_workers=min(n_versions, 4)) as executor:
            futures = [
                executor.submit(self.generate_single_version, *task) 
                for task in tasks
            ]
            
            results = []
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    error_result = {
                        "error": str(e),
                        "status": "error",
                        "generated_at": datetime.now().isoformat()
                    }
                    results.append(error_result)
        
        # Собираем результаты
        successful = [r for r in results if r.get('status') == 'success']
        failed = [r for r in results if r.get('status') == 'error']
        
        # Создаем сводку запуска
        run_summary = {
            "run_name": run_name or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "input_video": input_video,
            "total_versions": n_versions,
            "successful": len(successful),
            "failed": len(failed),
            "run_dir": str(run_dir),
            "generated_at": datetime.now().isoformat(),
            "results": results
        }
        
        # Сохраняем сводку
        summary_file = run_dir / "metadata" / "run_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(run_summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 ПАРАЛЛЕЛЬНАЯ ГЕНЕРАЦИЯ ЗАВЕРШЕНА!")
        print(f"📁 Папка запуска: {run_dir}")
        print(f"✅ Успешно: {len(successful)}/{n_versions}")
        print(f"❌ Ошибок: {len(failed)}")
        
        return run_summary
    
    def generate_batch_sequential(self, input_video: str, n_versions: int = 3, 
                                run_name: str = None) -> Dict:
        """
        Последовательная генерация (самая стабильная)
        """
        print(f"🚀 Начинаем последовательную генерацию {n_versions} версий")
        
        # Создаем папку для запуска
        run_dir = self.create_run_folder(run_name)
        
        # Список возможных эффектов
        effect_combinations = [
            ['temporal'],
            ['social'], 
            ['visual'],
            ['temporal', 'social'],
            ['temporal', 'visual'],
            ['social', 'visual'],
            ['temporal', 'social', 'visual']
        ]
        
        results = []
        print(f"⏳ Обрабатываем {n_versions} версий последовательно...")
        
        for i in range(n_versions):
            effects = effect_combinations[i % len(effect_combinations)]
            print(f"\n📝 Версия {i+1}/{n_versions}: {effects}")
            
            try:
                result = self.generate_single_version(
                    input_video, run_dir, i+1, effects
                )
                results.append(result)
            except Exception as e:
                error_result = {
                    "version_id": i+1,
                    "effects": effects,
                    "error": str(e),
                    "status": "error",
                    "generated_at": datetime.now().isoformat()
                }
                results.append(error_result)
                print(f"❌ Ошибка в версии {i+1}: {e}")
        
        # Собираем результаты
        successful = [r for r in results if r.get('status') == 'success']
        failed = [r for r in results if r.get('status') == 'error']
        
        # Создаем сводку запуска
        run_summary = {
            "run_name": run_name or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "input_video": input_video,
            "total_versions": n_versions,
            "successful": len(successful),
            "failed": len(failed),
            "run_dir": str(run_dir),
            "generated_at": datetime.now().isoformat(),
            "results": results
        }
        
        # Сохраняем сводку
        summary_file = run_dir / "metadata" / "run_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(run_summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 ПОСЛЕДОВАТЕЛЬНАЯ ГЕНЕРАЦИЯ ЗАВЕРШЕНА!")
        print(f"📁 Папка запуска: {run_dir}")
        print(f"✅ Успешно: {len(successful)}/{n_versions}")
        print(f"❌ Ошибок: {len(failed)}")
        
        return run_summary
    
    def list_runs(self) -> List[Dict]:
        """
        Показывает список всех запусков
        """
        runs = []
        for run_dir in self.runs_dir.iterdir():
            if run_dir.is_dir():
                summary_file = run_dir / "metadata" / "run_summary.json"
                if summary_file.exists():
                    with open(summary_file, 'r', encoding='utf-8') as f:
                        run_info = json.load(f)
                    runs.append(run_info)
        
        return sorted(runs, key=lambda x: x['generated_at'], reverse=True)
    
    def get_run_info(self, run_name: str) -> Dict:
        """
        Получает информацию о конкретном запуске
        """
        run_dir = self.runs_dir / run_name
        summary_file = run_dir / "metadata" / "run_summary.json"
        
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}


def main():
    """
    Пример использования BatchVideoGenerator
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python batch_generator.py <видео_файл> [количество_версий] [имя_запуска]")
        print("Пример: python batch_generator.py test.mp4 5 my_experiment")
        return
    
    input_video = sys.argv[1]
    n_versions = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    run_name = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(input_video):
        print(f"❌ Файл {input_video} не найден!")
        return
    
    # Создаем генератор
    generator = BatchVideoGenerator()
    
    # Выбираем метод генерации
    print("Выберите метод генерации:")
    print("1. Асинхронная (async/await)")
    print("2. Параллельная (multiprocessing)")
    
    choice = input("Введите номер (1-2): ").strip()
    
    try:
        if choice == "1":
            # Асинхронная генерация
            result = asyncio.run(generator.generate_batch_async(
                input_video, n_versions, run_name
            ))
        else:
            # Параллельная генерация
            result = generator.generate_batch_parallel(
                input_video, n_versions, run_name
            )
        
        print(f"\n📊 Результат:")
        print(f"   Папка: {result['run_dir']}")
        print(f"   Успешно: {result['successful']}/{result['total_versions']}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
