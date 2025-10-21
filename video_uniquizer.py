import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from moviepy.editor import VideoFileClip, CompositeVideoClip
import random
import os
from typing import Tuple, List, Optional
import json
from tqdm import tqdm


class VideoUniquizer:
    """
    Нейронная сеть для уникализации видео через незаметные изменения
    """
    
    def __init__(self, device: str = 'auto'):
        """
        Инициализация уникализатора видео
        
        Args:
            device: Устройство для обработки ('cpu', 'cuda', 'auto')
        """
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        print(f"Используется устройство: {self.device}")
        
        # Параметры для заметной уникализации
        self.speed_range = (0.95, 1.05)  # Заметное изменение скорости
        self.brightness_range = (-15, 15)  # Заметные изменения яркости
        self.contrast_range = (0.9, 1.1)  # Заметные изменения контраста
        self.saturation_range = (0.9, 1.1)  # Заметные изменения насыщенности
        
        # Эффекты в стиле Instagram (более заметные)
        self.social_effects = {
            'vintage': {'warmth': 0.9, 'vignette': 0.2, 'grain': 0.1},
            'dramatic': {'contrast': 1.15, 'shadows': 0.8, 'highlights': 1.2},
            'soft': {'blur': 0.5, 'brightness': 5, 'saturation': 0.9},
            'vibrant': {'saturation': 1.2, 'vibrance': 1.15, 'clarity': 1.1}
        }
        
        # Дополнительные Instagram фильтры
        self.instagram_filters = {
            'vintage': {'warmth': 0.9, 'vignette': 0.2, 'grain': 0.1},
            'dramatic': {'contrast': 1.15, 'shadows': 0.8, 'highlights': 1.2},
            'soft': {'blur': 0.5, 'brightness': 5, 'saturation': 0.9},
            'vibrant': {'saturation': 1.2, 'vibrance': 1.15, 'clarity': 1.1}
        }
        
    def apply_temporal_effects(self, video_path: str, output_path: str) -> str:
        """
        Применяет временные эффекты (скорость, обрезка)
        """
        clip = VideoFileClip(video_path)
        
        # Случайное изменение скорости
        speed_factor = random.uniform(*self.speed_range)
        new_duration = clip.duration / speed_factor
        
        # Случайная обрезка (убираем 1-5% от начала и конца)
        trim_start = random.uniform(0, clip.duration * 0.05)
        trim_end = random.uniform(0, clip.duration * 0.05)
        
        # Применяем изменения
        processed_clip = clip.subclip(trim_start, clip.duration - trim_end)
        processed_clip = processed_clip.fx(lambda clip: clip.speedx(speed_factor))
        
        # Сохраняем
        processed_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
        processed_clip.close()
        clip.close()
        
        return output_path
    
    def apply_visual_effects(self, video_path: str, output_path: str) -> str:
        """
        Применяет визуальные эффекты (яркость, контраст, насыщенность) с сохранением аудио
        """
        # Загружаем видео с аудио
        clip = VideoFileClip(video_path)
        
        # Случайные параметры для эффектов
        brightness_delta = random.randint(*self.brightness_range)
        contrast_alpha = random.uniform(*self.contrast_range)
        saturation_alpha = random.uniform(*self.saturation_range)
        
        print(f"Применяем эффекты: яркость={brightness_delta}, контраст={contrast_alpha:.2f}, насыщенность={saturation_alpha:.2f}")
        
        # Применяем эффекты к каждому кадру
        def apply_effect(get_frame, t):
            frame = get_frame(t)
            return self._apply_frame_effects(frame, brightness_delta, contrast_alpha, saturation_alpha)
        
        # Создаем новый клип с эффектами
        processed_clip = clip.fl(apply_effect)
        
        # Сохраняем с аудио
        processed_clip.write_videofile(
            output_path, 
            codec='libx264', 
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Закрываем клипы
        processed_clip.close()
        clip.close()
        
        return output_path
    
    def _apply_frame_effects(self, frame: np.ndarray, brightness: int, 
                           contrast: float, saturation: float) -> np.ndarray:
        """
        Применяет эффекты к отдельному кадру
        """
        # Яркость
        frame = cv2.convertScaleAbs(frame, alpha=1, beta=brightness)
        
        # Контраст
        frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=0)
        
        # Насыщенность
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.convertScaleAbs(hsv[:, :, 1], alpha=saturation)
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Случайный шум (очень слабый)
        noise = np.random.normal(0, 1, frame.shape).astype(np.uint8)
        frame = cv2.add(frame, noise)
        
        return frame
    
    def apply_neural_effects(self, video_path: str, output_path: str) -> str:
        """
        Применяет нейросетевые эффекты для уникализации
        """
        cap = cv2.VideoCapture(video_path)
        
        # Получаем параметры видео
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Создаем writer для выходного видео
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        print("Применяем нейросетевые эффекты...")
        
        frame_count = 0
        with tqdm(total=total_frames, desc="Нейросетевая обработка") as pbar:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Применяем нейросетевые эффекты
                processed_frame = self._apply_neural_frame_effects(frame)
                
                out.write(processed_frame)
                frame_count += 1
                pbar.update(1)
        
        cap.release()
        out.release()
        
        return output_path
    
    def _apply_neural_frame_effects(self, frame: np.ndarray) -> np.ndarray:
        """
        Применяет нейросетевые эффекты к кадру
        """
        # Конвертируем в тензор
        frame_tensor = torch.from_numpy(frame).float().permute(2, 0, 1).unsqueeze(0) / 255.0
        frame_tensor = frame_tensor.to(self.device)
        
        # Случайные трансформации
        with torch.no_grad():
            # Случайное изменение гаммы
            gamma = random.uniform(0.9, 1.1)
            frame_tensor = torch.pow(frame_tensor, gamma)
            
            # Случайное изменение цветового баланса
            color_shift = torch.rand(3, 1, 1).to(self.device) * 0.1 - 0.05
            frame_tensor = frame_tensor + color_shift
            frame_tensor = torch.clamp(frame_tensor, 0, 1)
            
            # Случайное размытие (очень слабое)
            if random.random() < 0.3:
                kernel_size = random.choice([3, 5])
                # Создаем ядро для каждого канала отдельно
                blur_kernel = torch.ones(3, 1, kernel_size, kernel_size).to(self.device) / (kernel_size * kernel_size)
                frame_tensor = F.conv2d(frame_tensor, blur_kernel, padding=kernel_size//2, groups=3)
        
        # Конвертируем обратно в numpy
        frame_tensor = frame_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
        frame_tensor = (frame_tensor * 255).astype(np.uint8)
        
        return frame_tensor
    
    def apply_social_effects(self, video_path: str, output_path: str) -> str:
        """
        Применяет естественные эффекты в стиле социальных сетей (с сохранением аудио)
        """
        # Загружаем видео с аудио
        clip = VideoFileClip(video_path)
        
        # Случайно выбираем стиль эффекта
        effect_style = random.choice(list(self.social_effects.keys()))
        effect_params = self.social_effects[effect_style]
        
        print(f"Применяем эффект '{effect_style}': {effect_params}")
        
        # Применяем эффекты к каждому кадру
        def apply_effect(get_frame, t):
            frame = get_frame(t)
            return self._apply_social_frame_effects(frame, effect_style, effect_params)
        
        # Создаем новый клип с эффектами
        processed_clip = clip.fl(apply_effect)
        
        # Сохраняем с аудио
        processed_clip.write_videofile(
            output_path, 
            codec='libx264', 
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Закрываем клипы
        processed_clip.close()
        clip.close()
        
        return output_path
    
    def _apply_social_frame_effects(self, frame: np.ndarray, style: str, params: dict) -> np.ndarray:
        """
        Применяет эффекты социальных сетей к кадру
        """
        if style == 'vintage':
            # Винтажный эффект: теплота, виньетка, зерно
            frame = self._apply_vintage_effect(frame, params)
        elif style == 'dramatic':
            # Драматический эффект: контраст, тени, блики
            frame = self._apply_dramatic_effect(frame, params)
        elif style == 'soft':
            # Мягкий эффект: размытие, яркость
            frame = self._apply_soft_effect(frame, params)
        elif style == 'vibrant':
            # Яркий эффект: насыщенность, вибрация
            frame = self._apply_vibrant_effect(frame, params)
        
        return frame
    
    def _apply_vintage_effect(self, frame: np.ndarray, params: dict) -> np.ndarray:
        """Винтажный эффект как в Instagram"""
        # Создаем копию для изменения
        frame = frame.copy()
        
        # Теплота (сдвиг в сторону оранжевого)
        warmth = params['warmth']
        frame[:, :, 0] = np.clip(frame[:, :, 0] * warmth, 0, 255)  # Увеличиваем красный
        frame[:, :, 2] = np.clip(frame[:, :, 2] * (2 - warmth), 0, 255)  # Уменьшаем синий
        
        # Виньетка (затемнение краев)
        vignette = params['vignette']
        h, w = frame.shape[:2]
        y, x = np.ogrid[:h, :w]
        center_x, center_y = w // 2, h // 2
        mask = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        mask = mask / mask.max()
        vignette_mask = 1 - (mask * vignette)
        frame = frame * vignette_mask[:, :, np.newaxis]
        
        # Зерно (шум)
        grain = params['grain']
        noise = np.random.normal(0, grain * 25, frame.shape)
        frame = np.clip(frame + noise, 0, 255)
        
        return frame.astype(np.uint8)
    
    def _apply_dramatic_effect(self, frame: np.ndarray, params: dict) -> np.ndarray:
        """Драматический эффект как в TikTok"""
        # Создаем копию для изменения
        frame = frame.copy()
        
        # Контраст
        contrast = params['contrast']
        frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=0)
        
        # Тени и блики
        shadows = params['shadows']
        highlights = params['highlights']
        
        # Применяем кривые (упрощенная версия)
        frame = frame.astype(np.float32)
        frame = np.clip(frame * highlights, 0, 255)
        frame = np.clip(frame * shadows, 0, 255)
        
        return frame.astype(np.uint8)
    
    def _apply_soft_effect(self, frame: np.ndarray, params: dict) -> np.ndarray:
        """Мягкий эффект как в YouTube Shorts"""
        # Создаем копию для изменения
        frame = frame.copy()
        
        # Слабое размытие
        blur = params['blur']
        if blur > 0:
            kernel_size = int(blur * 3) * 2 + 1  # Нечетное число
            frame = cv2.GaussianBlur(frame, (kernel_size, kernel_size), blur)
        
        # Яркость
        brightness = params['brightness']
        frame = cv2.convertScaleAbs(frame, alpha=1, beta=brightness)
        
        # Насыщенность
        saturation = params['saturation']
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.convertScaleAbs(hsv[:, :, 1], alpha=saturation)
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return frame
    
    def _apply_vibrant_effect(self, frame: np.ndarray, params: dict) -> np.ndarray:
        """Яркий эффект как в Instagram Stories"""
        # Создаем копию для изменения
        frame = frame.copy()
        
        # Насыщенность
        saturation = params['saturation']
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.convertScaleAbs(hsv[:, :, 1], alpha=saturation)
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Вибрация (усиление цветов)
        vibrance = params['vibrance']
        frame = cv2.convertScaleAbs(frame, alpha=vibrance, beta=0)
        
        # Четкость (усиление краев)
        clarity = params['clarity']
        if clarity > 1.0:
            # Простое усиление краев
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Laplacian(gray, cv2.CV_64F)
            edges = np.clip(edges, 0, 255).astype(np.uint8)
            edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            frame = cv2.addWeighted(frame, 1.0, edges, (clarity - 1.0) * 0.3, 0)
        
        return frame
    
    def uniquize_video(self, input_path: str, output_path: str, 
                      effects: List[str] = None) -> str:
        """
        Основной метод для уникализации видео
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь для сохранения результата
            effects: Список эффектов для применения
            
        Returns:
            Путь к обработанному видео
        """
        if effects is None:
            effects = ['temporal', 'social']  # Используем социальные эффекты вместо нейросетевых
        
        print(f"Уникализация видео: {input_path}")
        print(f"Применяемые эффекты: {effects}")
        
        temp_path = f"temp_{random.randint(1000, 9999)}.mp4"
        current_path = input_path
        
        try:
            # Применяем эффекты последовательно
            for i, effect in enumerate(effects):
                if effect == 'temporal':
                    print("Применяем временные эффекты...")
                    self.apply_temporal_effects(current_path, temp_path)
                elif effect == 'visual':
                    print("Применяем визуальные эффекты...")
                    self.apply_visual_effects(current_path, temp_path)
                elif effect == 'neural':
                    print("Применяем нейросетевые эффекты...")
                    self.apply_neural_effects(current_path, temp_path)
                elif effect == 'social':
                    print("Применяем эффекты социальных сетей...")
                    self.apply_social_effects(current_path, temp_path)
                
                # Обновляем путь для следующего эффекта
                if i > 0:  # Удаляем предыдущий временный файл
                    os.remove(current_path)
                current_path = temp_path
                
                if i < len(effects) - 1:  # Создаем новый временный файл
                    temp_path = f"temp_{random.randint(1000, 9999)}.mp4"
            
            # Переименовываем финальный файл
            os.rename(current_path, output_path)
            print(f"Видео успешно уникализировано: {output_path}")
            
        except Exception as e:
            print(f"Ошибка при обработке видео: {e}")
            # Очищаем временные файлы
            for temp_file in [temp_path, current_path]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            raise
        
        return output_path


def main():
    """
    Пример использования VideoUniquizer
    """
    # Создаем экземпляр уникализатора
    uniquizer = VideoUniquizer()
    
    # Пути к файлам
    input_video = "vtec_idw_light.mp4"  # Замените на ваш файл
    output_video = "uniquized_video.mp4"
    
    # Проверяем существование входного файла
    if not os.path.exists(input_video):
        print(f"Файл {input_video} не найден!")
        print("Поместите ваше видео в папку проекта и переименуйте его в 'input_video.mp4'")
        return
    
    try:
        # Уникализируем видео
        result_path = uniquizer.uniquize_video(
            input_path=input_video,
            output_path=output_video,
            effects=['temporal', 'visual', 'neural']  # Все эффекты
        )
        
        print(f"✅ Видео успешно обработано: {result_path}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()
