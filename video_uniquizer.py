import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from moviepy.editor import VideoFileClip, CompositeVideoClip
import random
import os
import time
from typing import Tuple, List, Optional
import json
from tqdm import tqdm
import logging
import subprocess

# VidGear fallback
try:
    from vidgear.gears import WriteGear
    VIDGEAR_AVAILABLE = True
except ImportError:
    VIDGEAR_AVAILABLE = False
    print("⚠️ VidGear not available, using MoviePy only")


class VideoUniquizer:
    """
    Нейронная сеть для уникализации видео через незаметные изменения
    """
    
    def __init__(self, device: str = 'auto', progress_callback=None):
        """
        Инициализация уникализатора видео
        
        Args:
            device: Устройство для обработки ('cpu', 'cuda', 'auto')
            progress_callback: Callback function for progress updates (message, progress_pct)
        """
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        self.progress_callback = progress_callback
        print(f"Используется устройство: {self.device}")
        
        # Параметры для явной уникализации (минимальные но заметные изменения)
        self.speed_range = (0.97, 1.03)  # Изменение скорости на 1-3%
        self.brightness_range = (-10, 10)  # Изменения яркости
        self.contrast_range = (0.92, 1.08)  # Изменения контраста  
        self.saturation_range = (0.92, 1.08)  # Изменения насыщенности
        self.trim_seconds = (0.5, 1.0)  # Обрезка 0.5-1 сек
        
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
        
    def apply_temporal_effects(
        self,
        video_path: str,
        output_path: str,
        speed_factor: float = None,
        trim_amount: float = None,
        trim_start: Optional[float] = None,
        trim_end: Optional[float] = None,
    ) -> str:
        """
        Применяет временные эффекты (скорость, обрезка)
        
        Args:
            video_path: Путь к входному видео
            output_path: Путь к выходному видео
            speed_factor: Конкретный коэффициент скорости (или случайный если None)
            trim_amount: Сколько секунд обрезать с начала и конца (или случайное если None)
        """
        clip = VideoFileClip(video_path)
        
        # Изменение скорости (используем переданный параметр или случайный)
        if speed_factor is None:
            speed_factor = random.uniform(*self.speed_range)
        
        print(f"⚡ Применяю изменение скорости: {speed_factor:.3f}x")
        
        duration = clip.duration
        trim_start_val = 0.0
        trim_end_val = 0.0

        # Обрезка в СЕКУНДАХ (используем переданный параметр или случайный)
        if trim_start is not None or trim_end is not None:
            trim_start_val = max(0.0, trim_start or 0.0)
            trim_end_val = max(0.0, trim_end or 0.0)
        else:
            if trim_amount is None:
                trim_amount = random.uniform(*self.trim_seconds)
            # Гарантируем, что не обрезаем больше 10% длины с каждой стороны
            max_trim = duration * 0.1 if duration else trim_amount
            trim_start_val = min(trim_amount, max_trim)
            trim_end_val = min(trim_amount, max_trim)
        
        # Гарантируем, что итоговая длительность положительная
        if duration:
            max_allowed = max(0.0, duration - 0.1)
            if trim_start_val + trim_end_val > max_allowed:
                excess = (trim_start_val + trim_end_val) - max_allowed
                # Равномерно уменьшаем обрезку с каждой стороны
                trim_start_val = max(0.0, trim_start_val - excess / 2)
                trim_end_val = max(0.0, trim_end_val - excess / 2)
                if trim_start_val + trim_end_val > max_allowed:
                    trim_end_val = max(0.0, max_allowed - trim_start_val)
        
        print(f"✂️ Обрезаю {trim_start_val:.2f}s с начала и {trim_end_val:.2f}s с конца")
        
        # Применяем изменения
        end_time = None
        if duration:
            end_time = max(trim_start_val, duration - trim_end_val)
        processed_clip = clip.subclip(trim_start_val, end_time)
        processed_clip = processed_clip.fx(lambda clip: clip.speedx(speed_factor))
        
        # Сохраняем
        processed_clip.write_videofile(
            output_path, 
            codec='libx264', 
            audio_codec='aac',
            ffmpeg_params=['-preset', 'fast', '-crf', '23', '-threads', '2'],
            verbose=False,
            logger=None
        )
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
            remove_temp=True,
            ffmpeg_params=[
                '-preset', 'fast',  # Быстрая кодировка
                '-crf', '23',       # Качество
                '-maxrate', '2M',   # Максимальный битрейт
                '-bufsize', '4M',   # Размер буфера
                '-threads', '2',    # Количество потоков
                '-movflags', '+faststart'  # Оптимизация для стриминга
            ],
            verbose=False,
            logger=None
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
    
    def _update_progress(self, message: str, progress_pct: float = None):
        """
        Update progress via callback if available
        """
        if self.progress_callback:
            self.progress_callback(message, progress_pct)
        print(f"📊 {message}")
        logging.info(f"📊 {message}")
    
    def apply_social_effects(self, video_path: str, output_path: str, effect_style: str = None, effect_params: dict = None) -> str:
        """
        Применяет естественные эффекты в стиле социальных сетей (с сохранением аудио)
        VidGear first (faster), MoviePy as fallback
        
        Args:
            video_path: Путь к входному видео
            output_path: Путь к выходному видео
            effect_style: Название эффекта ('vintage', 'dramatic', 'soft', 'vibrant') или None для случайного
            effect_params: Параметры эффекта или None для дефолтных
        """
        if VIDGEAR_AVAILABLE:
            try:
                print("🚀 Using VidGear (faster) for video processing...")
                return self._apply_social_effects_vidgear(video_path, output_path, effect_style, effect_params)
            except Exception as e:
                print(f"⚠️ VidGear failed: {e}")
                print("🔄 Trying MoviePy fallback...")
                return self._apply_social_effects_moviepy(video_path, output_path, effect_style, effect_params)
        else:
            print("⚠️ VidGear not available, using MoviePy...")
            return self._apply_social_effects_moviepy(video_path, output_path, effect_style, effect_params)
    
    def _apply_social_effects_moviepy(self, video_path: str, output_path: str, effect_style: str = None, effect_params: dict = None) -> str:
        """
        MoviePy implementation of social effects
        
        Args:
            effect_style: Название эффекта или None для случайного
            effect_params: Параметры эффекта или None для дефолтных
        """
        print("🎬 Using MoviePy for video processing...")
        logging.info("🎬 Starting MoviePy video processing...")
        
        # Загружаем видео с аудио
        clip = VideoFileClip(video_path)
        
        # Получаем информацию о видео
        duration = clip.duration
        fps = clip.fps
        total_frames = int(duration * fps) if fps else 0
        
        print(f"📹 Video info: {clip.w}x{clip.h} @ {fps}fps, {total_frames} frames ({duration:.1f}s)")
        logging.info(f"📹 Video info: {clip.w}x{clip.h} @ {fps}fps, {total_frames} frames ({duration:.1f}s)")
        
        # Выбираем стиль эффекта (используем переданный или случайный)
        if effect_style is None:
            effect_style = random.choice(list(self.social_effects.keys()))
        
        # Используем переданные параметры или дефолтные
        if effect_params is None:
            effect_params = self.social_effects.get(effect_style, self.social_effects['vintage'])
        
        print(f"🎨 Applying effect '{effect_style}': {effect_params}")
        logging.info(f"🎨 Applying effect '{effect_style}': {effect_params}")
        
        # Применяем эффекты к каждому кадру
        def apply_effect(get_frame, t):
            frame = get_frame(t)
            return self._apply_social_frame_effects(frame, effect_style, effect_params)
        
        # Создаем новый клип с эффектами
        processed_clip = clip.fl(apply_effect)
        
        # Progress callback for MoviePy
        def progress_callback(t):
            progress_pct = (t / duration) * 100 if duration > 0 else 0
            if int(progress_pct) % 10 == 0:  # Every 10%
                print(f"📊 MoviePy Progress: {t:.1f}s/{duration:.1f}s ({progress_pct:.1f}%)")
                logging.info(f"📊 MoviePy Progress: {t:.1f}s/{duration:.1f}s ({progress_pct:.1f}%)")
        
        start_time = time.time()
        print("🎬 Starting MoviePy encoding...")
        logging.info("🎬 Starting MoviePy encoding...")
        
        # Сохраняем с аудио
        processed_clip.write_videofile(
            output_path, 
            codec='libx264', 
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            ffmpeg_params=[
                '-preset', 'fast',  # Быстрая кодировка
                '-crf', '23',       # Качество
                '-maxrate', '2M',   # Максимальный битрейт
                '-bufsize', '4M',   # Размер буфера
                '-threads', '2',    # Количество потоков
                '-movflags', '+faststart'  # Оптимизация для стриминга
            ],
            verbose=False,
            logger=None
        )
        
        total_time = time.time() - start_time
        print(f"✅ MoviePy processing completed in {total_time:.1f}s")
        logging.info(f"✅ MoviePy processing completed in {total_time:.1f}s")
        
        # Закрываем клипы
        processed_clip.close()
        clip.close()
        
        return output_path
    
    def _apply_social_effects_vidgear(self, video_path: str, output_path: str, effect_style: str = None, effect_params: dict = None) -> str:
        """
        VidGear implementation for social effects (faster than MoviePy)
        
        Args:
            effect_style: Название эффекта или None для случайного
            effect_params: Параметры эффекта или None для дефолтных
        """
        self._update_progress("🚀 Starting VidGear video processing (faster method)...")
        
        # Открываем видео с помощью OpenCV
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        # Получаем параметры видео
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        self._update_progress(f"📹 Video info: {width}x{height} @ {fps}fps, {total_frames} frames ({duration:.1f}s)")
        
        # Настройки VidGear
        output_params = {
            "-vcodec": "libx264",
            "-preset": "fast",
            "-crf": "23",
            "-maxrate": "2M",
            "-bufsize": "4M",
            "-threads": "2",
            "-movflags": "+faststart"
        }
        
        # Выбираем стиль эффекта (используем переданный или случайный)
        if effect_style is None:
            effect_style = random.choice(list(self.social_effects.keys()))
        
        # Используем переданные параметры или дефолтные
        if effect_params is None:
            effect_params = self.social_effects.get(effect_style, self.social_effects['vintage'])
        
        self._update_progress(f"🎨 Applying effect '{effect_style}': {effect_params}")
        
        # Инициализируем VidGear writer (временный файл без аудио)
        temp_output = output_path + ".tmp.mp4"
        writer = WriteGear(output=temp_output, logging=False, **output_params)
        
        frame_count = 0
        start_time = time.time()
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Применяем эффекты к кадру
                processed_frame = self._apply_social_frame_effects(frame, effect_style, effect_params)
                
                # Записываем кадр
                writer.write(processed_frame)
                
                frame_count += 1
                
                # Progress reporting every 30 frames or every 5%
                progress_interval = max(30, total_frames // 20)  # At least every 5%
                if frame_count % progress_interval == 0 or frame_count == total_frames:
                    progress_pct = (frame_count / total_frames) * 100
                    elapsed_time = time.time() - start_time
                    fps_actual = frame_count / elapsed_time if elapsed_time > 0 else 0
                    eta_seconds = (total_frames - frame_count) / fps_actual if fps_actual > 0 else 0
                    
                    self._update_progress(
                        f"🎬 VidGear Progress: {frame_count}/{total_frames} frames ({progress_pct:.1f}%) | "
                        f"Speed: {fps_actual:.1f} fps | ETA: {eta_seconds:.1f}s",
                        progress_pct
                    )
        
        finally:
            # Закрываем все
            cap.release()
            writer.close()
        
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time if total_time > 0 else 0
        
        self._update_progress(f"✅ VidGear processing completed: {frame_count} frames in {total_time:.1f}s (avg: {avg_fps:.1f} fps)")
        
        # Проверяем что временный файл создан и не пустой
        if not os.path.exists(temp_output) or os.path.getsize(temp_output) == 0:
            raise ValueError("VidGear output file is empty or doesn't exist")
        
        # Микшируем оригинальный аудио-трек обратно
        self._update_progress("🔊 Restoring original audio track...")
        try:
            self._mux_original_audio(temp_output, video_path, output_path)
            os.remove(temp_output)
        except Exception as e:
            # Если не удалось смуксовать аудио, хотя бы вернем видео без аудио
            logging.error(f"⚠️ Failed to restore audio: {e}")
            try:
                os.rename(temp_output, output_path)
            except Exception:
                pass
        
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
    
    def uniquize_video(
        self,
        input_path: str,
        output_path: str,
        effects: List[str] = None,
        params: dict = None,
        postprocess: Optional[dict] = None,
    ) -> str:
        """
        Основной метод для уникализации видео с VidGear fallback
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь для сохранения результата
            effects: Список эффектов для применения
            params: Параметры для эффектов (speed, warmth, contrast и т.д.)
            
        Returns:
            Путь к обработанному видео
        """
        if effects is None:
            effects = ['temporal', 'social']  # Используем социальные эффекты вместо нейросетевых
        
        if params is None:
            params = {}
        params = dict(params)
        postprocess_meta = dict(postprocess) if postprocess else {}
        
        self._update_progress(f"🎬 Starting video uniquization: {input_path}")
        self._update_progress(f"🎨 Effects to apply: {effects}")
        self._update_progress(f"⚙️ Parameters: {params}")
        
        # Получаем информацию о входном видео
        try:
            input_clip = VideoFileClip(input_path)
            input_duration = input_clip.duration
            input_fps = input_clip.fps
            input_frames = int(input_duration * input_fps) if input_fps else 0
            input_clip.close()
            
            self._update_progress(f"📹 Input video: {input_duration:.1f}s @ {input_fps}fps ({input_frames} frames)")
        except Exception as e:
            self._update_progress(f"⚠️ Could not get input video info: {e}")
        
        temp_path = f"temp_{random.randint(1000, 9999)}.mp4"
        current_path = input_path
        start_time = time.time()
        
        try:
            # Применяем эффекты последовательно
            for i, effect in enumerate(effects):
                effect_start = time.time()
                progress_pct = (i / len(effects)) * 100
                self._update_progress(f"🔄 Step {i+1}/{len(effects)}: Applying {effect} effects...", progress_pct)
                
                if effect == 'temporal':
                    self._update_progress("⏱️ Applying temporal effects...")
                    # Извлекаем параметры скорости
                    speed_factor = params.get('speed')
                    if postprocess_meta.get('speed_factor') is not None:
                        speed_factor = postprocess_meta.get('speed_factor')
                    trim_amount = params.get('trim')
                    trim_start_override = postprocess_meta.get('trim_start')
                    trim_end_override = postprocess_meta.get('trim_end')
                    trim_seconds_override = postprocess_meta.get('trim_seconds')
                    if trim_seconds_override is not None:
                        if trim_start_override is None:
                            trim_start_override = trim_seconds_override
                        if trim_end_override is None:
                            trim_end_override = trim_seconds_override
                    self.apply_temporal_effects(
                        current_path,
                        temp_path,
                        speed_factor,
                        trim_amount,
                        trim_start=trim_start_override,
                        trim_end=trim_end_override,
                    )
                elif effect == 'visual':
                    self._update_progress("👁️ Applying visual effects...")
                    self.apply_visual_effects(current_path, temp_path)
                elif effect == 'neural':
                    self._update_progress("🧠 Applying neural effects...")
                    self.apply_neural_effects(current_path, temp_path)
                elif effect == 'social':
                    self._update_progress("📱 Applying social effects...")
                    # Определяем стиль эффекта из параметров
                    effect_style = None
                    effect_params = {}
                    
                    # Определяем стиль по наличию специфичных параметров
                    if 'warmth' in params or 'vignette' in params or 'grain' in params:
                        effect_style = 'vintage'
                    elif 'shadows' in params or 'highlights' in params:
                        effect_style = 'dramatic'
                    elif 'blur' in params:
                        effect_style = 'soft'
                    elif 'vibrance' in params or 'clarity' in params:
                        effect_style = 'vibrant'
                    
                    # Копируем соответствующие параметры
                    for key in ['warmth', 'vignette', 'grain', 'contrast', 'shadows', 'highlights', 
                               'blur', 'brightness', 'saturation', 'vibrance', 'clarity']:
                        if key in params:
                            effect_params[key] = params[key]
                    
                    self.apply_social_effects(current_path, temp_path, effect_style, effect_params if effect_params else None)
                
                effect_time = time.time() - effect_start
                self._update_progress(f"✅ {effect} effects completed in {effect_time:.1f}s")
                
                # Обновляем путь для следующего эффекта
                if i > 0:  # Удаляем предыдущий временный файл
                    os.remove(current_path)
                current_path = temp_path
                
                if i < len(effects) - 1:  # Создаем новый временный файл
                    temp_path = f"temp_{random.randint(1000, 9999)}.mp4"
            
            # Дополнительная пост-обработка через ffmpeg при необходимости
            if postprocess_meta:
                postprocess_for_ffmpeg = dict(postprocess_meta)
                for key in ('trim_seconds', 'trim_start', 'trim_end'):
                    postprocess_for_ffmpeg.pop(key, None)
                if postprocess_for_ffmpeg:
                    try:
                        current_path = self._apply_ffmpeg_postprocess(current_path, postprocess_for_ffmpeg)
                    except Exception as post_err:
                        self._update_progress(f"⚠️ Post-process failed: {post_err}")

            # Переименовываем финальный файл
            os.rename(current_path, output_path)
            total_time = time.time() - start_time
            
            self._update_progress(f"🎉 Video successfully uniquized: {output_path}")
            self._update_progress(f"⏱️ Total processing time: {total_time:.1f}s", 100.0)
            
        except Exception as e:
            print(f"⚠️ MoviePy processing failed: {e}")
            logging.error(f"⚠️ MoviePy processing failed: {e}")
            if VIDGEAR_AVAILABLE:
                print("🔄 Trying VidGear fallback for full video processing...")
                logging.info("🔄 Trying VidGear fallback for full video processing...")
                return self._uniquize_video_vidgear(input_path, output_path, effects)
            else:
                print("❌ No fallback available, re-raising error")
                logging.error("❌ No fallback available, re-raising error")
                # Очищаем временные файлы
                for temp_file in [temp_path, current_path]:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                raise
        
        return output_path
    
    def _uniquize_video_vidgear(self, input_path: str, output_path: str, effects: List[str]) -> str:
        """
        VidGear fallback implementation for full video uniquization
        """
        print("🎬 Using VidGear for full video uniquization...")
        
        # Открываем видео с помощью OpenCV
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {input_path}")
        
        # Получаем параметры видео
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"📹 Video info: {width}x{height} @ {fps}fps, {total_frames} frames")
        
        # Настройки VidGear
        output_params = {
            "-vcodec": "libx264",
            "-preset": "fast",
            "-crf": "23",
            "-maxrate": "2M",
            "-bufsize": "4M",
            "-threads": "2",
            "-movflags": "+faststart"
        }
        
        # Случайно выбираем стиль эффекта
        effect_style = random.choice(list(self.social_effects.keys()))
        effect_params = self.social_effects[effect_style]
        
        print(f"Применяем эффект '{effect_style}': {effect_params}")
        
        # Инициализируем VidGear writer (временный файл без аудио)
        temp_output = output_path + ".tmp.mp4"
        writer = WriteGear(output=temp_output, logging=False, **output_params)
        
        frame_count = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Применяем эффекты к кадру
                processed_frame = self._apply_social_frame_effects(frame, effect_style, effect_params)
                
                # Записываем кадр
                writer.write(processed_frame)
                
                frame_count += 1
                if frame_count % 30 == 0:  # Progress every 30 frames
                    print(f"📊 Processed {frame_count}/{total_frames} frames ({frame_count/total_frames*100:.1f}%)")
        
        finally:
            # Закрываем все
            cap.release()
            writer.close()
        
        print(f"✅ VidGear uniquization completed: {frame_count} frames")
        
        # Проверяем что временный файл создан и не пустой
        if not os.path.exists(temp_output) or os.path.getsize(temp_output) == 0:
            raise ValueError("VidGear output file is empty or doesn't exist")
        
        # Микшируем оригинальный аудио-трек обратно
        print("🔊 Restoring original audio track...")
        logging.info("🔊 Restoring original audio track...")
        try:
            self._mux_original_audio(temp_output, input_path, output_path)
            os.remove(temp_output)
        except Exception as e:
            logging.error(f"⚠️ Failed to restore audio: {e}")
            try:
                os.rename(temp_output, output_path)
            except Exception:
                pass
        
        return output_path

    def _mux_original_audio(self, video_without_audio: str, original_with_audio: str, final_output: str):
        """
        Объединяет обработанное видео (без аудио) с оригинальным аудио-треком.
        Предпочтительно копируем дорожки без перекодирования.
        """
        # Команда ffmpeg: берем видео из первого файла, аудио из второго, обрезаем по минимальной длительности
        cmd = [
            'ffmpeg', '-y',
            '-i', video_without_audio,
            '-i', original_with_audio,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-map', '0:v:0',
            '-map', '1:a:0?',
            '-shortest',
            final_output
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not os.path.exists(final_output):
            # Fallback: если копирование не удалось, перекодируем аудио в AAC
            cmd_fallback = [
                'ffmpeg', '-y',
                '-i', video_without_audio,
                '-i', original_with_audio,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-map', '0:v:0',
                '-map', '1:a:0?',
                '-shortest',
                final_output
            ]
            result2 = subprocess.run(cmd_fallback, capture_output=True, text=True)
            if result2.returncode != 0 or not os.path.exists(final_output):
                raise RuntimeError(f"ffmpeg mux failed: {result.stderr or result2.stderr}")

    def _apply_ffmpeg_postprocess(self, input_path: str, meta: dict) -> str:
        """
        Выполняет дополнительную пост-обработку видео через ffmpeg на основе переданных параметров.

        Args:
            input_path: путь к входному файлу
            meta: словарь с параметрами пост-обработки

        Returns:
            Путь к обработанному файлу (заменяет оригинальный)
        """
        from pathlib import Path

        trim_seconds = float(meta.get('trim_seconds', 0))
        speed_factor = float(meta.get('speed_factor', 1.0))
        crop_factor = float(meta.get('crop_factor', 1.0))
        contrast = float(meta.get('contrast', 1.0))
        saturation = float(meta.get('saturation', 1.0))
        volume = float(meta.get('volume', 1.0))
        video_bitrate = str(meta.get('video_bitrate', '1.4M'))
        maxrate = str(meta.get('maxrate', video_bitrate))
        bufsize = str(meta.get('bufsize', '2.8M'))
        audio_bitrate = str(meta.get('audio_bitrate', '128k'))
        preset = str(meta.get('preset', 'medium'))

        temp_output = str(Path(input_path).with_name(f"{Path(input_path).stem}_post.mp4"))

        # Определяем параметры обрезки
        trim_start = float(meta.get('trim_start', trim_seconds))
        trim_end = float(meta.get('trim_end', 0))
        
        # Получаем длительность для правильной обрезки
        duration = None
        if trim_start > 0 or trim_end > 0:
            probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path]
            try:
                duration = float(subprocess.run(probe_cmd, capture_output=True, text=True).stdout.strip())
            except:
                duration = None
        
        # Собираем фильтры в правильном порядке: обрезка -> скорость -> остальные эффекты
        video_filters = []
        audio_filters = []
        
        # 1. Обрезка (первая операция для синхронизации)
        if trim_start > 0 or trim_end > 0:
            if trim_start > 0:
                trim_video = f"trim=start={trim_start:.3f}"
                if duration and trim_end > 0:
                    end_time = duration - trim_end
                    trim_video += f":end={end_time:.3f}"
                trim_video += ",setpts=PTS-STARTPTS"
                video_filters.append(trim_video)
                
                trim_audio = f"atrim=start={trim_start:.3f}"
                if duration and trim_end > 0:
                    end_time = duration - trim_end
                    trim_audio += f":end={end_time:.3f}"
                trim_audio += ",asetpts=PTS-STARTPTS"
                audio_filters.append(trim_audio)
            elif trim_end > 0 and duration:
                end_time = duration - trim_end
                video_filters.append(f"trim=end={end_time:.3f},setpts=PTS-STARTPTS")
                audio_filters.append(f"atrim=end={end_time:.3f},asetpts=PTS-STARTPTS")
        
        # 2. Изменение скорости (после обрезки)
        if abs(speed_factor - 1.0) > 1e-3:
            video_filters.append(f"setpts=PTS/{speed_factor:.5f}")
            if speed_factor < 0.5 or speed_factor > 2.0:
                raise ValueError("Speed factor for audio must be between 0.5 and 2.0")
            audio_filters.append(f"atempo={speed_factor:.5f}")
        
        # 3. Остальные эффекты (кадрирование, цветокоррекция)
        if crop_factor < 1.0:
            crop_expr = f"crop=iw*{crop_factor:.5f}:ih*{crop_factor:.5f}"
            scale_factor = 1.0 / crop_factor
            scale_expr = (
                f"scale=trunc(iw*{scale_factor:.5f}/2)*2:"
                f"trunc(ih*{scale_factor:.5f}/2)*2"
            )
            video_filters.extend([crop_expr, scale_expr])
        video_filters.append(f"eq=contrast={contrast:.2f}:saturation={saturation:.2f}")
        
        # Громкость для аудио
        if abs(volume - 1.0) > 1e-3:
            audio_filters.append(f"volume={volume:.5f}")
        
        # Собираем filter_complex
        filter_complex_parts = []
        filter_complex_parts.append(f"[0:v]{','.join(video_filters)}[v]")
        if audio_filters:
            filter_complex_parts.append(f"[0:a]{','.join(audio_filters)}[a]")
        filter_complex = ";".join(filter_complex_parts)

        cmd = ['ffmpeg', '-y', '-i', input_path, '-filter_complex', filter_complex, '-map', '[v]'] 

        if audio_filters:
            cmd.extend(['-map', '[a]'])
        else:
            cmd.extend(['-map', '0:a:0?', '-c:a', 'copy'])

        cmd.extend([
            '-c:v', 'libx264',
            '-preset', preset,
            '-b:v', video_bitrate,
            '-maxrate', maxrate,
            '-bufsize', bufsize,
            '-movflags', '+faststart',
            '-async', '1',  # Синхронизация аудио (1 секунда коррекции)
            '-shortest'  # Обрезать по минимальной длительности аудио/видео
        ])

        if audio_filters:
            cmd.extend(['-c:a', 'aac', '-b:a', audio_bitrate])

        cmd.append(temp_output)

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not os.path.exists(temp_output):
            raise RuntimeError(f"ffmpeg post-process failed: {result.stderr}")

        # Заменяем исходный файл новым
        os.remove(input_path)
        os.rename(temp_output, input_path)

        return input_path


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
