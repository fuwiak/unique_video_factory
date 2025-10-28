#!/usr/bin/env python3
"""
Telegram Bot для уникализации видео с интеграцией Yandex Disk
"""

import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
import json
import uuid
import threading
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import websockets
import aiohttp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)
from dotenv import load_dotenv
import yadisk
from video_uniquizer import VideoUniquizer
from google_sheets_integration import GoogleSheetsIntegration
from advanced_social_stats import AdvancedSocialStatsChecker

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
YANDEX_DISK_TOKEN = os.getenv('YANDEX_DISK_TOKEN')
YANDEX_DISK_FOLDER = os.getenv('YANDEX_DISK_FOLDER', 'unique_video_factory')
MAX_VIDEO_SIZE_MB = int(os.getenv('MAX_VIDEO_SIZE_MB', '300'))

# Self-hosted Bot API configuration
# Auto-enable self-hosted API for Railway deployment
USE_SELF_HOSTED_API = os.getenv('USE_SELF_HOSTED_API', 'true').lower() == 'true'  # Default to true for Railway
SELF_HOSTED_API_URL = os.getenv('SELF_HOSTED_API_URL', 'http://localhost:8081').rstrip('/')
SELF_HOSTED_BOT_API_URL = f"{SELF_HOSTED_API_URL}/bot"
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '2000'))  # 2GB for self-hosted

# Auto-detect self-hosted API availability
def check_self_hosted_api():
    """Check if self-hosted Bot API is available"""
    try:
        import requests
        
        # Try multiple endpoints
        endpoints = [
            f"{SELF_HOSTED_API_URL}/health",
            f"{SELF_HOSTED_API_URL}/",
            f"{SELF_HOSTED_API_URL}/bot"
        ]
        
        for endpoint in endpoints:
            try:
                logger.info(f"🔍 Checking self-hosted API at: {endpoint}")
                response = requests.get(endpoint, timeout=5)
                logger.info(f"   Response status: {response.status_code}")
                if response.status_code in [200, 404]:  # 404 is OK for some endpoints
                    return True
            except Exception as e:
                logger.debug(f"   Endpoint {endpoint} failed: {e}")
                continue
        
        return False
    except Exception as e:
        logger.warning(f"⚠️ Self-hosted API check failed: {e}")
        return False

def start_self_hosted_api_server():
    """Start self-hosted Bot API server for Railway deployment"""
    try:
        import subprocess
        import threading
        
        # Check if we have API credentials
        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')
        
        if not api_id or not api_hash:
            logger.warning("⚠️ TELEGRAM_API_ID or TELEGRAM_API_HASH not found, skipping self-hosted API")
            return False
        
        # Check if telegram-bot-api binary exists
        import shutil
        telegram_bot_api_path = shutil.which("telegram-bot-api")
        
        if not telegram_bot_api_path:
            # Try to find it in common locations
            possible_paths = [
                "/usr/local/bin/telegram-bot-api",
                "/usr/bin/telegram-bot-api",
                "./telegram-bot-api",
                "./bot_api_server/telegram-bot-api"
            ]
            
            for path in possible_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    telegram_bot_api_path = path
                    break
            
            if not telegram_bot_api_path:
                logger.warning("⚠️ telegram-bot-api binary not found, skipping self-hosted API")
                return False
        
        # Double check the binary still exists and is executable
        if not (telegram_bot_api_path and os.path.exists(telegram_bot_api_path)):
            logger.error(f"❌ telegram-bot-api binary not found at {telegram_bot_api_path}")
            logger.info("   Install it or run docker-compose up telegram-bot-api before starting the bot.")
            return False
        
        # Test if binary can run (check version)
        try:
            test_result = subprocess.run(
                [telegram_bot_api_path, "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if test_result.returncode != 0:
                logger.warning(f"⚠️ telegram-bot-api binary may not work properly")
                logger.warning(f"   Return code: {test_result.returncode}")
                logger.warning(f"   Stderr: {test_result.stderr}")
        except Exception as e:
            logger.warning(f"⚠️ Could not test telegram-bot-api binary: {e}")

        # Start Bot API server in background
        def run_server():
            try:
                server_args = [
                    telegram_bot_api_path,
                    "--api-id", api_id,
                    "--api-hash", api_hash,
                    "--local",
                    "--http-port", "8081",
                    "--verbosity", "1"
                ]
                
                logger.info("🚀 Starting self-hosted Bot API server...")
                logger.info(f"   Binary: {telegram_bot_api_path}")
                logger.info(f"   API ID: {api_id}")
                logger.info(f"   Args: {' '.join(server_args)}")
                
                # Start server in background with timeout
                process = subprocess.Popen(
                    server_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Wait a bit for server to start
                import time
                time.sleep(2)
                
                # Check if process is still running
                if process.poll() is None:
                    logger.info("✅ Self-hosted Bot API server started successfully")
                    return True
                else:
                    stdout, stderr = process.communicate()
                    logger.error(f"❌ Server failed to start")
                    logger.error(f"   Stdout: {stdout}")
                    logger.error(f"   Stderr: {stderr}")
                    return False
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to start self-hosted API server: {e}")
                logger.error(f"   Stdout: {e.stdout}")
                logger.error(f"   Stderr: {e.stderr}")
            except FileNotFoundError as e:
                logger.error(f"❌ telegram-bot-api binary not found: {e}")
                logger.info("   Ensure the binary is installed and accessible in PATH or /usr/local/bin.")
            except Exception as e:
                logger.error(f"❌ Failed to start self-hosted API server: {e}", exc_info=True)
        
        # Start server in background thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        import time
        time.sleep(3)
        
        # Check if server is running
        if check_self_hosted_api():
            logger.info("✅ Self-hosted Bot API server started successfully")
            return True
        else:
            logger.warning("⚠️ Self-hosted API server failed to start")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error starting self-hosted API server: {e}")
        return False

# Check if we should use self-hosted API
logger.info(f"🔍 Checking self-hosted API configuration:")
logger.info(f"   USE_SELF_HOSTED_API: {USE_SELF_HOSTED_API}")
logger.info(f"   SELF_HOSTED_API_URL: {SELF_HOSTED_API_URL}")
logger.info(f"   MAX_FILE_SIZE_MB: {MAX_FILE_SIZE_MB}")

if USE_SELF_HOSTED_API:
    logger.info("🔍 Self-hosted API is enabled, checking availability...")
    api_available = check_self_hosted_api()
    logger.info(f"   API available: {api_available}")
    
    if not api_available:
        logger.error("❌ Self-hosted Bot API is required but not available!")
        logger.error(f"   Expected to reach: {SELF_HOSTED_API_URL}")
        logger.error("   Please start the self-hosted API service first:")
        logger.error("   - Docker: docker-compose up telegram-bot-api")
        logger.error("   - Native: ./start_self_hosted_api.sh")
        logger.error("   - Systemd: sudo systemctl start telegram-bot-api@API_ID:API_HASH")
        raise RuntimeError("Self-hosted Bot API is required but not available")
    
    # Use self-hosted API
    logger.info("🚀 Using self-hosted Bot API (Railway deployment)")
    ACTUAL_API_URL = SELF_HOSTED_BOT_API_URL
    ACTUAL_MAX_FILE_SIZE = MAX_FILE_SIZE_MB
    logger.info(f"   Using API URL: {ACTUAL_API_URL}")
    logger.info(f"   Max file size: {ACTUAL_MAX_FILE_SIZE}MB")
else:
    logger.info("📱 Using standard Telegram API (20MB limit)")
    ACTUAL_API_URL = "https://api.telegram.org"
    ACTUAL_MAX_FILE_SIZE = 20  # Standard API limit

    logger.info(f"🎯 Final configuration:")
    logger.info(f"   ACTUAL_API_URL: {ACTUAL_API_URL}")
    logger.info(f"   ACTUAL_MAX_FILE_SIZE: {ACTUAL_MAX_FILE_SIZE}MB")
    
    # Verify configuration
    if ACTUAL_MAX_FILE_SIZE > 20:
        logger.info("✅ Self-hosted Bot API configured - files up to 2GB supported")
    else:
        logger.warning("⚠️ Using standard Telegram API - 20MB limit")

# Состояния пользователей
user_states = {}

# Состояния для карт блогеров
blogger_states = {}

# Состояния менеджеров для апрува видео
manager_states = {}

# Очередь видео на аппрув
pending_approvals = {}

# Доступные фильтры Instagram с разными скоростями
INSTAGRAM_FILTERS = {
    'vintage_slow': {
        'name': '📸 Винтажный (медленно)',
        'description': 'Теплые тона, виньетка, зерно, 0.8x скорость',
        'effects': ['social', 'temporal'],
        'params': {'warmth': 0.9, 'vignette': 0.2, 'grain': 0.1, 'speed': 0.8}
    },
    'vintage_normal': {
        'name': '📸 Винтажный (нормально)',
        'description': 'Теплые тона, виньетка, зерно, 1.0x скорость',
        'effects': ['social'],
        'params': {'warmth': 0.9, 'vignette': 0.2, 'grain': 0.1, 'speed': 1.0}
    },
    'vintage_fast': {
        'name': '📸 Винтажный (быстро)',
        'description': 'Теплые тона, виньетка, зерно, 1.2x скорость',
        'effects': ['social', 'temporal'],
        'params': {'warmth': 0.9, 'vignette': 0.2, 'grain': 0.1, 'speed': 1.2}
    },
    'dramatic_slow': {
        'name': '🎭 Драматический (медленно)',
        'description': 'Высокий контраст, тени, блики, 0.8x скорость',
        'effects': ['social', 'temporal'],
        'params': {'contrast': 1.15, 'shadows': 0.8, 'highlights': 1.2, 'speed': 0.8}
    },
    'dramatic_normal': {
        'name': '🎭 Драматический (нормально)',
        'description': 'Высокий контраст, тени, блики, 1.0x скорость',
        'effects': ['social'],
        'params': {'contrast': 1.15, 'shadows': 0.8, 'highlights': 1.2, 'speed': 1.0}
    },
    'dramatic_fast': {
        'name': '🎭 Драматический (быстро)',
        'description': 'Высокий контраст, тени, блики, 1.2x скорость',
        'effects': ['social', 'temporal'],
        'params': {'contrast': 1.15, 'shadows': 0.8, 'highlights': 1.2, 'speed': 1.2}
    },
    'soft_slow': {
        'name': '🌸 Мягкий (медленно)',
        'description': 'Размытие, повышенная яркость, 0.8x скорость',
        'effects': ['social', 'temporal'],
        'params': {'blur': 0.5, 'brightness': 5, 'saturation': 0.9, 'speed': 0.8}
    },
    'soft_normal': {
        'name': '🌸 Мягкий (нормально)',
        'description': 'Размытие, повышенная яркость, 1.0x скорость',
        'effects': ['social'],
        'params': {'blur': 0.5, 'brightness': 5, 'saturation': 0.9, 'speed': 1.0}
    },
    'soft_fast': {
        'name': '🌸 Мягкий (быстро)',
        'description': 'Размытие, повышенная яркость, 1.2x скорость',
        'effects': ['social', 'temporal'],
        'params': {'blur': 0.5, 'brightness': 5, 'saturation': 0.9, 'speed': 1.2}
    },
    'vibrant_slow': {
        'name': '🌈 Яркий (медленно)',
        'description': 'Усиленная насыщенность, четкость, 0.8x скорость',
        'effects': ['social', 'temporal'],
        'params': {'saturation': 1.2, 'vibrance': 1.15, 'clarity': 1.1, 'speed': 0.8}
    },
    'vibrant_normal': {
        'name': '🌈 Яркий (нормально)',
        'description': 'Усиленная насыщенность, четкость, 1.0x скорость',
        'effects': ['social'],
        'params': {'saturation': 1.2, 'vibrance': 1.15, 'clarity': 1.1, 'speed': 1.0}
    },
    'vibrant_fast': {
        'name': '🌈 Яркий (быстро)',
        'description': 'Усиленная насыщенность, четкость, 1.2x скорость',
        'effects': ['social', 'temporal'],
        'params': {'saturation': 1.2, 'vibrance': 1.15, 'clarity': 1.1, 'speed': 1.2}
    }
}


class WebSocketUploadProgress:
    """WebSocket upload progress tracker"""
    
    def __init__(self, user_id: int, filename: str):
        self.user_id = user_id
        self.filename = filename
        self.uploaded_bytes = 0
        self.total_bytes = 0
        self.progress_percent = 0
        self.status = "starting"
        self.start_time = time.time()
        self.websocket_clients = set()
    
    def update_progress(self, uploaded: int, total: int):
        """Update upload progress"""
        self.uploaded_bytes = uploaded
        self.total_bytes = total
        self.progress_percent = (uploaded / total * 100) if total > 0 else 0
        
        # Broadcast progress to WebSocket clients
        self.broadcast_progress()
    
    def set_status(self, status: str):
        """Set upload status"""
        self.status = status
        self.broadcast_progress()
    
    def broadcast_progress(self):
        """Broadcast progress to all connected WebSocket clients"""
        progress_data = {
            "type": "upload_progress",
            "user_id": self.user_id,
            "filename": self.filename,
            "uploaded_bytes": self.uploaded_bytes,
            "total_bytes": self.total_bytes,
            "progress_percent": round(self.progress_percent, 2),
            "status": self.status,
            "elapsed_time": time.time() - self.start_time,
            "speed_mbps": self.calculate_speed()
        }
        
        # Remove disconnected clients
        disconnected = set()
        for client in self.websocket_clients:
            try:
                asyncio.create_task(client.send(json.dumps(progress_data)))
            except:
                disconnected.add(client)
        
        for client in disconnected:
            self.websocket_clients.discard(client)
    
    def calculate_speed(self) -> float:
        """Calculate upload speed in MB/s"""
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            return (self.uploaded_bytes / (1024 * 1024)) / elapsed
        return 0.0
    
    def add_client(self, websocket):
        """Add WebSocket client for progress updates"""
        self.websocket_clients.add(websocket)
    
    def remove_client(self, websocket):
        """Remove WebSocket client"""
        self.websocket_clients.discard(websocket)


class TelegramVideoBot:
    """Основной класс бота для обработки видео"""
    
    def __init__(self):
        self.yandex_disk = None
        if YANDEX_DISK_TOKEN:
            self.yandex_disk = yadisk.YaDisk(token=YANDEX_DISK_TOKEN)
        
        # WebSocket upload tracking
        self.upload_progress = {}  # user_id -> WebSocketUploadProgress
        self.websocket_server = None
        
        # Инициализируем папки на Yandex Disk
        self.init_yandex_folders()
        
        # Создаем папки для временных файлов
        self.temp_dir = Path("temp_videos")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Создаем папку для результатов
        self.results_dir = Path("telegram_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Google Sheets integration
        self.google_sheets = GoogleSheetsIntegration()
        
        # Social stats checker
        self.social_stats_checker = AdvancedSocialStatsChecker()
    
    def init_yandex_folders(self):
        """Инициализация папок на Yandex Disk"""
        try:
            if not self.yandex_disk:
                return
            
            # Создаем базовую папку
            base_folder = "Медиабанк/Команда 1"
            if not self.yandex_disk.exists(base_folder):
                self.yandex_disk.mkdir(base_folder)
                logger.info(f"Создана базовая папка: {base_folder}")
            
            logger.info("Папки Yandex Disk инициализированы")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации папок Yandex Disk: {e}")
    
    async def create_yandex_folders(self, blogger_name, folder_name):
        """Создает структуру папок для блогера на Yandex Disk"""
        try:
            if not self.yandex_disk:
                logger.warning("Yandex Disk не подключен")
                return
            
            base_folder = "Медиабанк/Команда 1"
            blogger_folder = f"{base_folder}/{blogger_name}"
            content_folder = f"{blogger_folder}/{folder_name}"
            
            # Создаем папку блогера, если не существует
            if not self.yandex_disk.exists(blogger_folder):
                self.yandex_disk.mkdir(blogger_folder)
                logger.info(f"Создана папка блогера: {blogger_folder}")
            
            # Создаем папку контента, если не существует
            if not self.yandex_disk.exists(content_folder):
                self.yandex_disk.mkdir(content_folder)
                logger.info(f"Создана папка контента: {content_folder}")
            
            # Создаем папки approved и not_approved
            for status in ["approved", "not_approved"]:
                status_folder = f"{content_folder}/{status}"
                if not self.yandex_disk.exists(status_folder):
                    self.yandex_disk.mkdir(status_folder)
                    logger.info(f"Создана папка {status}: {status_folder}")
            
            logger.info(f"Структура папок создана для {blogger_name}/{folder_name}")
            
        except Exception as e:
            logger.error(f"Ошибка создания папок для {blogger_name}/{folder_name}: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        
        welcome_text = """
🎬 *Бот уникализации видео*

Отправьте мне видео файл, и я создам уникальную версию с фильтрами Instagram!

*Доступные команды:*
/start - Начать работу
/help - Помощь
/filters - Показать доступные фильтры
/status - Статус обработки

*Как использовать:*
1. Отправьте видео файл
2. Выберите количество видео (1, 3, 5, 10)
3. Выберите группу фильтров (разные скорости)
4. Получите обработанные видео с разными эффектами
5. Каждое видео будет с уникальным ID для аппрува
        """
        
        await update.message.reply_text(
            welcome_text, 
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        help_text = """
🆘 *Помощь по использованию бота*

*Поддерживаемые форматы:*
• MP4, AVI, MOV, MKV

*Максимальный размер:*
• {max_size} MB

*Доступные фильтры:*
• 📸 Винтажный - теплые тона
• 🎭 Драматический - высокий контраст  
• 🌸 Мягкий - размытие и яркость
• 🌈 Яркий - усиленная насыщенность
• ⏰ Временной - изменение скорости
• 🎨 Визуальный - цветовые коррекции
• ✨ Все эффекты - комбинация

*Процесс обработки:*
1. Отправьте видео
2. Выберите фильтр
3. Дождитесь обработки
4. Видео отправляется на аппрув
5. Менеджер одобряет/отклоняет
6. Одобренные видео отправляются в чатбот

*Команды для всех:*
• /blogger - создать карту блогера со статистикой

*Команды для менеджеров:*
• /manager - панель менеджера
• /queue - очередь на аппрув
• /approved - одобренные видео
• /approve <ID> - одобрить видео
• /reject <ID> - отклонить видео
• /send_to_chatbot <ID> - отправить в чатбот
        """.format(max_size=MAX_VIDEO_SIZE_MB)
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown'
        )
    
    async def blogger_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /blogger - создать карту блогера со статистикой"""
        user_id = update.effective_user.id
        
        # Инициализируем состояние для создания карты блогера
        blogger_states[user_id] = {
            'status': 'waiting_for_name',
            'blogger_name': None,
            'links': []
        }
        
        await update.message.reply_text(
            "👤 *Создание карты блогера*\n\n"
            "Введите имя блогера (например: Лиза):",
            parse_mode='Markdown'
        )
    
    async def filters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /filters - показать доступные фильтры"""
        filters_text = "🎨 *Доступные фильтры Instagram:*\n\n"
        
        for filter_id, filter_info in INSTAGRAM_FILTERS.items():
            filters_text += f"*{filter_info['name']}*\n"
            filters_text += f"_{filter_info['description']}_\n\n"
        
        await update.message.reply_text(
            filters_text,
            parse_mode='Markdown'
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /status - показать статус"""
        user_id = update.effective_user.id
        
        if user_id in user_states:
            state = user_states[user_id]
            status_text = f"""
📊 *Статус обработки:*

🔄 Текущее состояние: {state.get('status', 'Неизвестно')}
📁 Обрабатываемый файл: {state.get('filename', 'Нет')}
🎨 Выбранный фильтр: {state.get('filter', 'Не выбран')}
⏰ Время начала: {state.get('start_time', 'Неизвестно')}
            """
        else:
            status_text = "📊 *Статус:* Готов к работе"
        
        await update.message.reply_text(
            status_text,
            parse_mode='Markdown'
        )
    
    async def manager_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /manager - панель менеджера"""
        user_id = update.effective_user.id
        
        # Проверяем права менеджера (можно настроить список ID)
        manager_ids = [user_id]  # Добавьте ID менеджеров
        
        if user_id not in manager_ids:
            await update.message.reply_text("❌ У вас нет прав менеджера.")
            return
        
        manager_text = """
👨‍💼 *Панель менеджера*

*Доступные команды:*
/queue - Показать очередь на аппрув
/approved - Показать одобренные видео
/approve <ID> - Одобрить видео
/reject <ID> - Отклонить видео
/send_to_chatbot <ID> - Отправить в чатбот

*Статистика:*
📊 Ожидают аппрува: {pending_count}
✅ Одобрено: {approved_count}
❌ Отклонено: {rejected_count}
        """.format(
            pending_count=len(pending_approvals),
            approved_count=len([v for v in pending_approvals.values() if v.get('status') == 'approved']),
            rejected_count=len([v for v in pending_approvals.values() if v.get('status') == 'rejected'])
        )
        
        await update.message.reply_text(
            manager_text,
            parse_mode='Markdown'
        )
    
    async def queue_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /queue - показать очередь на аппрув"""
        user_id = update.effective_user.id
        
        if not pending_approvals:
            await update.message.reply_text("📋 *Очередь пуста*", parse_mode='Markdown')
            return
        
        queue_text = "📋 *Очередь на аппрув:*\n\n"
        
        for approval_id, video_data in pending_approvals.items():
            if video_data.get('status') == 'pending':
                queue_text += f"🆔 *ID:* {approval_id}\n"
                queue_text += f"👤 *Пользователь:* {video_data.get('user_name', 'Неизвестно')}\n"
                queue_text += f"📁 *Файл:* {video_data.get('filename', 'Неизвестно')}\n"
                queue_text += f"🎨 *Фильтр:* {video_data.get('filter', 'Неизвестно')}\n"
                queue_text += f"⏰ *Время:* {video_data.get('timestamp', 'Неизвестно')}\n\n"
        
        await update.message.reply_text(queue_text, parse_mode='Markdown')
    
    async def approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /approve - одобрить видео"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text("❌ Укажите ID видео для одобрения.\nПример: /approve abc123")
            return
        
        approval_id = context.args[0]
        
        if approval_id not in pending_approvals:
            await update.message.reply_text("❌ Видео с таким ID не найдено.")
            return
        
        video_data = pending_approvals[approval_id]
        video_data['status'] = 'approved'
        video_data['approved_by'] = user_id
        video_data['approved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Перемещаем файл в папку approved
        try:
            await self.move_to_approved_folder(video_data, approval_id)
            await update.message.reply_text(f"✅ Видео {approval_id} одобрено и перемещено в папку approved!")
        except Exception as e:
            logger.error(f"Ошибка перемещения в approved папку: {e}")
            await update.message.reply_text(f"✅ Видео {approval_id} одобрено, но ошибка при перемещении: {str(e)}")
        
        # Уведомляем пользователя
        await context.bot.send_message(
            chat_id=video_data['user_id'],
            text=f"✅ Ваше видео одобрено!\n🆔 ID: {approval_id}\n👨‍💼 Одобрил: {update.effective_user.first_name}"
        )
    
    async def approved_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /approved - показать одобренные видео"""
        user_id = update.effective_user.id
        
        approved_videos = [v for v in pending_approvals.values() if v.get('status') == 'approved']
        
        if not approved_videos:
            await update.message.reply_text("📋 *Нет одобренных видео*", parse_mode='Markdown')
            return
        
        approved_text = "✅ *Одобренные видео:*\n\n"
        
        for video_data in approved_videos:
            approved_text += f"🆔 *ID:* {video_data.get('approval_id', 'Неизвестно')}\n"
            approved_text += f"👤 *Пользователь:* {video_data.get('user_name', 'Неизвестно')}\n"
            approved_text += f"📁 *Файл:* {video_data.get('filename', 'Неизвестно')}\n"
            approved_text += f"🎨 *Фильтр:* {video_data.get('filter', 'Неизвестно')}\n"
            approved_text += f"⏰ *Одобрено:* {video_data.get('approved_at', 'Неизвестно')}\n"
            approved_text += f"👨‍💼 *Одобрил:* {video_data.get('approved_by', 'Неизвестно')}\n\n"
        
        await update.message.reply_text(approved_text, parse_mode='Markdown')
    
    async def reject_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /reject - отклонить видео"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text("❌ Укажите ID видео для отклонения.\nПример: /reject abc123")
            return
        
        approval_id = context.args[0]
        
        if approval_id not in pending_approvals:
            await update.message.reply_text("❌ Видео с таким ID не найдено.")
            return
        
        video_data = pending_approvals[approval_id]
        video_data['status'] = 'rejected'
        video_data['rejected_by'] = user_id
        video_data['rejected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Уведомляем пользователя
        await context.bot.send_message(
            chat_id=video_data['user_id'],
            text=f"❌ Ваше видео отклонено.\n🆔 ID: {approval_id}\n👨‍💼 Отклонил: {update.effective_user.first_name}"
        )
        
        await update.message.reply_text(f"❌ Видео {approval_id} отклонено!")
    
    async def send_to_chatbot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /send_to_chatbot - отправить видео в чатбот с метаданными"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text("❌ Укажите ID видео для отправки в чатбот.\nПример: /send_to_chatbot abc123")
            return
        
        approval_id = context.args[0]
        
        if approval_id not in pending_approvals:
            await update.message.reply_text("❌ Видео с таким ID не найдено.")
            return
        
        video_data = pending_approvals[approval_id]
        
        if video_data['status'] != 'approved':
            await update.message.reply_text("❌ Видео должно быть одобрено перед отправкой в чатбот.")
            return
        
        # Запрашиваем метаданные
        manager_states[user_id] = {
            'status': 'waiting_metadata',
            'approval_id': approval_id,
            'video_data': video_data
        }
        
        await update.message.reply_text(
            f"📝 Введите метаданные для видео {approval_id}:\n\n"
            f"1. Дата публикации (YYYY-MM-DD HH:MM):\n"
            f"2. ID сценария:\n"
            f"3. Описание видео:\n\n"
            f"Отправьте в формате:\n"
            f"<дата>|<ID сценария>|<описание>"
        )
    
    async def handle_user_metadata(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка метаданных от пользователя (ID ролика, имя блогера и папки)"""
        user_id = update.effective_user.id
        
        # Проверяем, создаем ли карту блогера
        if user_id in blogger_states:
            await self.handle_blogger_creation(update, context)
            return
        
        if user_id not in user_states:
            await update.message.reply_text("❌ Сначала отправьте видео.")
            return
        
        text = update.message.text.strip()
        
        # Если еще не ввели ID ролика
        if user_states[user_id]['video_id'] is None:
            user_states[user_id]['video_id'] = text
            await update.message.reply_text(
                f"✅ ID ролика: **{text}**\n\n"
                "👤 **Введите имя блогера:**\n"
                "(например: Нина, Рэйчел, или новое имя)"
            )
            return
        
        # Если еще не ввели имя блогера
        if user_states[user_id]['blogger_name'] is None:
            user_states[user_id]['blogger_name'] = text
            await update.message.reply_text(
                f"✅ Имя блогера: **{text}**\n\n"
                "📁 **Введите название папки:**\n"
                "(например: clips, videos, content)"
            )
            return
        
        # Если еще не ввели название папки
        if user_states[user_id]['folder_name'] is None:
            user_states[user_id]['folder_name'] = text
            
            # Создаем структуру папок на Yandex Disk
            await self.create_yandex_folders(user_states[user_id]['blogger_name'], text)
            
            await update.message.reply_text(
                f"✅ Настройки сохранены:\n"
                f"🆔 ID ролика: **{user_states[user_id]['video_id']}**\n"
                f"👤 Блогер: **{user_states[user_id]['blogger_name']}**\n"
                f"📁 Папка: **{text}**\n"
                f"📂 Создана структура папок на Yandex Disk\n\n"
                "🎬 Теперь выберите количество видео:"
            )
            
            # Создаем клавиатуру для выбора количества видео
            keyboard = []
            for n in [1, 3, 5, 10]:
                keyboard.append([
                    InlineKeyboardButton(
                        f"🎬 {n} видео", 
                        callback_data=f"count_{n}"
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🎬 Сколько видео создать?",
                reply_markup=reply_markup
            )

    async def handle_blogger_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка создания карты блогера"""
        user_id = update.effective_user.id
        text = update.message.text.strip()
        state = blogger_states[user_id]
        
        if state['status'] == 'waiting_for_name':
            # Сохраняем имя блогера
            state['blogger_name'] = text
            state['status'] = 'waiting_for_links'
            
            await update.message.reply_text(
                f"✅ Имя блогера: **{text}**\n\n"
                "🔗 Теперь отправьте ссылки на профили социальных сетей:\n\n"
                "Поддерживаемые платформы:\n"
                "• Instagram\n"
                "• YouTube\n"
                "• TikTok\n"
                "• VK\n"
                "• Likee\n\n"
                "Отправляйте по одной ссылке за раз.\n"
                "Когда закончите, отправьте: **готово**",
                parse_mode='Markdown'
            )
            
        elif state['status'] == 'waiting_for_links':
            if text.lower() == 'готово':
                await self.process_blogger_links(user_id, update)
            else:
                # Проверяем, является ли ссылка валидной
                if self.is_valid_social_link(text):
                    state['links'].append(text)
                    await update.message.reply_text(
                        f"✅ Добавлена ссылка: {text}\n\n"
                        f"Всего ссылок: {len(state['links'])}\n\n"
                        "Отправьте еще ссылку или напишите готово для завершения."
                    )
                else:
                    await update.message.reply_text(
                        "❌ Неверная ссылка. Поддерживаемые платформы:\n"
                        "• Instagram (instagram.com)\n"
                        "• YouTube (youtube.com)\n"
                        "• TikTok (tiktok.com)\n"
                        "• VK (vk.com)\n"
                        "• Likee (likee.video)\n\n"
                        "Попробуйте еще раз или напишите **готово**."
                    )
        
        elif state['status'] == 'waiting_for_vk_id':
            # Sprawdzamy czy to numer ID
            if text.isdigit():
                vk_id = text
                vk_url = state['vk_url']
                platform = state['current_platform']
                
                # Tworzymy nowy URL z numerem ID
                new_vk_url = f"https://vk.com/clips/user?owner={vk_id}"
                
                await update.message.reply_text(
                    f"✅ VK ID: {vk_id}\n"
                    f"🔄 Обрабатываю VK статистику..."
                )
                
                try:
                    # Pobieramy statystyki VK z numerem ID
                    result = self.social_stats_checker.check_vk_stats(new_vk_url)
                    
                    # Dodajemy do wyników
                    stats_results = {platform: result}
                    
                    # Dodajemy dane blogera
                    for platform_name, data in stats_results.items():
                        if 'error' not in data:
                            data['blogger_name'] = state['blogger_name']
                            data['user_name'] = state['blogger_name']
                            data['url'] = new_vk_url
                    
                    # Zapisujemy do Google Sheets
                    await update.message.reply_text("💾 Сохраняю в Google Sheets...")
                    
                    if not self.google_sheets.sheet:
                        await update.message.reply_text(
                            "❌ Google Sheets не настроен.\n"
                            "Проверьте файл google_credentials.json i настройки."
                        )
                        return
                    
                    success = self.google_sheets.save_to_blogger_sheet(state['blogger_name'], stats_results)
                    
                    if success:
                        # Podsumowanie
                        stats_summary = f"📊 **Статистика VK для {state['blogger_name']}:**\n\n"
                        
                        for platform_name, data in stats_results.items():
                            if 'error' not in data:
                                if 'clips' in data:
                                    clips_count = len(data['clips'])
                                    total_views = sum(clip.get('views', 0) for clip in data['clips'])
                                    stats_summary += f"**{platform_name}:**\n"
                                    stats_summary += f"• Clips: {clips_count}\n"
                                    stats_summary += f"• Total views: {total_views}\n\n"
                                else:
                                    stats_summary += f"**{platform_name}:** ❌ No clips found\n\n"
                            else:
                                stats_summary += f"**{platform_name}:** ❌ Error\n\n"
                        
                        await update.message.reply_text(
                            f"✅ **VK карта создана!**\n\n"
                            f"{stats_summary}\n"
                            "📋 Данные сохранены в Google Sheets.",
                            parse_mode='Markdown'
                        )
                    else:
                        await update.message.reply_text(
                            "❌ Ошибка сохранения в Google Sheets.\n"
                            "Проверьте настройки Google Sheets."
                        )
                    
                    # Oчищаем состояние
                    del blogger_states[user_id]
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки VK ID: {e}")
                    await update.message.reply_text(
                        f"❌ Ошибка обработки VK ID: {str(e)}"
                    )
                    # Oчищаем состояние
                    del blogger_states[user_id]
            else:
                await update.message.reply_text(
                    "❌ Неверный формат ID. Введите только цифры.\n"
                    "Пример: 1072165347"
                )

    def is_valid_social_link(self, link: str) -> bool:
        """Проверяет, является ли ссылка валидной социальной сетью"""
        valid_domains = [
            'instagram.com', 'youtube.com', 'tiktok.com', 'vk.com', 'likee.video'
        ]
        link = link.lower().strip()
        return any(domain in link for domain in valid_domains)

    async def process_blogger_links(self, user_id: int, update: Update):
        """Обрабатывает ссылки блогера и создает карту"""
        state = blogger_states[user_id]
        blogger_name = state['blogger_name']
        links = state['links']
        
        if not links:
            await update.message.reply_text(
                "❌ Не добавлено ни одной ссылки.\n"
                "Используйте /blogger для повторного создания карты."
            )
            # Очищаем состояние
            del blogger_states[user_id]
            return
        
        await update.message.reply_text(
            f"🔄 Обрабатываю ссылки для **{blogger_name}**...\n"
            f"Найдено ссылок: {len(links)}",
            parse_mode='Markdown'
        )
        
        try:
            # Группируем ссылки по платформам
            platform_urls = self.group_links_by_platform(links)
            
            # Собираем статистику
            stats_results = {}
            for platform, url in platform_urls.items():
                await update.message.reply_text(f"📊 Собираю статистику {platform}...")
                
                try:
                    if platform.lower() == 'youtube':
                        # Sprawdzamy czy to YouTube Shorts URL
                        if '/shorts/' in url:
                            result = self.social_stats_checker.get_youtube_short_data(url)
                        else:
                            result = self.social_stats_checker.check_youtube_stats(url)
                    elif platform.lower() == 'instagram':
                        result = self.social_stats_checker.check_instagram_stats(url)
                    elif platform.lower() == 'tiktok':
                        result = self.social_stats_checker.check_tiktok_stats(url)
                    elif platform.lower() == 'vk':
                        # Sprawdzamy czy to VK clip URL
                        if '/clips/' in url:
                            result = self.social_stats_checker.extract_vk_clips_views(url)
                        else:
                            # Sprawdzamy czy można wyciągnąć ID z URL
                            vk_id = self.social_stats_checker._extract_vk_user_id(url)
                            if not vk_id or not vk_id.isdigit():
                                # Jeśli nie ma ID, pytamy użytkownika
                                await update.message.reply_text(
                                    f"🔍 Для VK нужен номер ID пользователя.\n"
                                    f"Найдите его в URL профиля: https://vk.com/id123456789\n"
                                    f"Или в параметре owner: https://vk.com/clips/username?owner=123456789\n\n"
                                    f"Введите номер ID для VK:"
                                )
                                
                                # Zmieniamy stan na oczekiwanie VK ID
                                blogger_states[user_id]['status'] = 'waiting_for_vk_id'
                                blogger_states[user_id]['vk_url'] = url
                                blogger_states[user_id]['current_platform'] = platform
                                return
                            
                            result = self.social_stats_checker.check_vk_stats(url)
                    elif platform.lower() == 'likee':
                        result = self.social_stats_checker.check_likee_stats(url)
                    else:
                        continue
                    
                    stats_results[platform] = result
                    
                except Exception as e:
                    logger.error(f"Ошибка сбора статистики для {platform}: {e}")
                    stats_results[platform] = {'platform': platform, 'error': str(e)}
            
            # Добавляем имя блогера и URL к результатам
            for platform, data in stats_results.items():
                if 'error' not in data:
                    data['blogger_name'] = blogger_name
                    data['user_name'] = blogger_name
                    data['url'] = platform_urls.get(platform, '')
            
            # Сохраняем в Google Sheets
            await update.message.reply_text("💾 Сохраняю в Google Sheets...")
            
            # Проверяем состояние Google Sheets
            if not self.google_sheets.sheet:
                await update.message.reply_text(
                    "❌ Google Sheets не настроен.\n"
                    "Проверьте файл google_credentials.json и настройки."
                )
                return
            
            success = self.google_sheets.save_to_blogger_sheet(blogger_name, stats_results)
            
            if success:
                # Подсчитываем общее количество подписчиков
                total_followers = 0
                stats_summary = f"📊 **Статистика для {blogger_name}:**\n\n"
                
                for platform, data in stats_results.items():
                    if 'error' not in data:
                        followers = data.get('followers', 0)
                        if isinstance(followers, (int, float)):
                            total_followers += followers
                        
                        stats_summary += f"**{platform.title()}:**\n"
                        stats_summary += f"• Подписчики: {data.get('followers', 'N/A')}\n"
                        stats_summary += f"• Видео: {data.get('videos', 'N/A')}\n"
                        stats_summary += f"• Просмотры: {data.get('views', 'N/A')}\n\n"
                    else:
                        stats_summary += f"**{platform.title()}:** ❌ Ошибка\n\n"
                
                stats_summary += f"📈 **Общее количество подписчиков: {total_followers}**"
                
                await update.message.reply_text(
                    f"✅ **Карта блогера создана!**\n\n"
                    f"{stats_summary}\n\n"
                    "📋 Данные сохранены в Google Sheets.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "❌ Ошибка сохранения в Google Sheets.\n"
                    "Проверьте настройки Google Sheets."
                )
            
        except Exception as e:
            logger.error(f"Ошибка обработки ссылок блогера: {e}")
            await update.message.reply_text(
                f"❌ Ошибка обработки ссылок: {str(e)}"
            )
        
        finally:
            # Очищаем состояние
            del blogger_states[user_id]

    def group_links_by_platform(self, links: list) -> dict:
        """Группирует ссылки по платформам"""
        platform_urls = {}
        
        for link in links:
            link_lower = link.lower()
            if 'instagram.com' in link_lower:
                platform_urls['Instagram'] = link
            elif 'youtube.com' in link_lower or 'youtu.be' in link_lower:
                platform_urls['YouTube'] = link
            elif 'tiktok.com' in link_lower:
                platform_urls['TikTok'] = link
            elif 'vk.com' in link_lower:
                # Конвертируем VK URL в clips URL
                vk_url = self.convert_vk_to_clips_url(link)
                platform_urls['VK'] = vk_url
            elif 'likee.video' in link_lower:
                platform_urls['Likee'] = link
        
        return platform_urls
    
    def convert_vk_to_clips_url(self, vk_url: str) -> str:
        """Конвертирует VK URL в clips URL"""
        try:
            # Извлекаем username из URL
            # Пример: https://vk.com/lizaaaakorzh -> lizaaaakorzh
            if '/vk.com/' in vk_url:
                username = vk_url.split('/vk.com/')[-1].split('?')[0].split('#')[0]
                return f"https://vk.com/clips/{username}"
            return vk_url
        except Exception as e:
            logger.error(f"Ошибка конвертации VK URL: {e}")
            return vk_url

    async def handle_metadata(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка метаданных от менеджера"""
        user_id = update.effective_user.id
        
        if user_id not in manager_states:
            return
        
        if manager_states[user_id]['status'] != 'waiting_metadata':
            return
        
        try:
            # Парсим метаданные
            metadata_text = update.message.text
            parts = metadata_text.split('|')
            
            if len(parts) != 3:
                await update.message.reply_text(
                    "❌ Неверный формат. Используйте:\n"
                    "<дата>|<ID сценария>|<описание>"
                )
                return
            
            publish_date, scenario_id, description = [part.strip() for part in parts]
            
            # Сохраняем метаданные
            approval_id = manager_states[user_id]['approval_id']
            video_data = pending_approvals[approval_id]
            
            video_data['metadata'] = {
                'publish_date': publish_date,
                'scenario_id': scenario_id,
                'description': description,
                'sent_to_chatbot': True,
                'sent_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Отправляем в чатбот (симуляция)
            await self.send_to_chatbot(video_data, context)
            
            # Перемещаем файл в папку approved
            await self.move_to_approved_folder(video_data, approval_id)
            
            # Очищаем состояние
            del manager_states[user_id]
            
            await update.message.reply_text(
                f"✅ Видео {approval_id} отправлено в чатбот с метаданными:\n"
                f"📅 Дата публикации: {publish_date}\n"
                f"🆔 ID сценария: {scenario_id}\n"
                f"📝 Описание: {description}"
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка обработки метаданных: {str(e)}")
    
    async def send_to_chatbot(self, video_data, context):
        """Отправка видео в чатбот с метаданными"""
        try:
            # Здесь должна быть логика отправки в чатбот
            # Пока что просто логируем
            logger.info(f"Отправка в чатбот: {video_data}")
            
            # В реальной реализации здесь будет API вызов к чатботу
            # с передачей видео и метаданных
            
        except Exception as e:
            logger.error(f"Ошибка отправки в чатбот: {e}")
    
    async def move_to_approved_folder(self, video_data, approval_id):
        """Перемещение файла в папку approved"""
        try:
            if not self.yandex_disk:
                return
            
            # Получаем информацию о блогере и папке
            blogger_name = video_data.get('blogger_name', 'unknown')
            folder_name = video_data.get('folder_name', 'default')
            
            # Создаем путь к папке approved
            base_folder = "Медиабанк/Команда 1"
            blogger_folder = f"{base_folder}/{blogger_name}"
            content_folder = f"{blogger_folder}/{folder_name}"
            approved_folder = f"{content_folder}/approved"
            
            # Создаем папку approved, если не существует
            if not self.yandex_disk.exists(approved_folder):
                self.yandex_disk.mkdir(approved_folder)
                logger.info(f"Создана папка approved: {approved_folder}")
            
            # Создаем подпапку для конкретного видео
            video_folder = f"{approved_folder}/{approval_id}"
            if not self.yandex_disk.exists(video_folder):
                self.yandex_disk.mkdir(video_folder)
                logger.info(f"Создана папка видео: {video_folder}")
            
            # Получаем путь к файлу на Yandex Disk
            source_remote_path = video_data.get('yandex_remote_path')
            logger.info(f"Yandex путь из данных: {source_remote_path}")
            
            # Если путь не найден, ищем файл в новой структуре папок
            if not source_remote_path:
                # Ищем в новой структуре: Медиабанк/Команда 1/Мая/videos/run_timestamp/
                try:
                    # Получаем информацию о блогере и папке
                    blogger_name = video_data.get('blogger_name', 'unknown')
                    folder_name = video_data.get('folder_name', 'default')
                    
                    # Создаем путь к папке контента
                    content_folder = f"{base_folder}/{blogger_name}/{folder_name}"
                    
                    if self.yandex_disk.exists(content_folder):
                        content_contents = list(self.yandex_disk.listdir(content_folder))
                        for run_folder in content_contents:
                            if run_folder['type'] == 'dir' and run_folder['name'].startswith('run_'):
                                run_path = f"{content_folder}/{run_folder['name']}"
                                run_contents = list(self.yandex_disk.listdir(run_path))
                                for file_item in run_contents:
                                    if file_item['name'].endswith('.mp4'):
                                        source_remote_path = f"{run_path}/{file_item['name']}"
                                        logger.info(f"Найден файл в новой структуре: {source_remote_path}")
                                        break
                                if source_remote_path:
                                    break
                except Exception as e:
                    logger.error(f"Ошибка поиска файла в новой структуре: {e}")
                    source_remote_path = None
            
            if source_remote_path:
                # Перемещаем файл с Yandex Disk
                approved_path = f"{video_folder}/video.mp4"
                try:
                    # Сначала копируем файл
                    self.yandex_disk.copy(source_remote_path, approved_path)
                    logger.info(f"Файл скопирован с {source_remote_path} в {approved_path}")
                    
                    # Затем удаляем исходный файл
                    self.yandex_disk.remove(source_remote_path)
                    logger.info(f"Исходный файл удален: {source_remote_path}")
                    
                except Exception as move_error:
                    logger.error(f"Ошибка перемещения файла: {move_error}")
                    # Fallback - загружаем локальный файл
                    source_path = video_data.get('video_path')
                    if source_path and os.path.exists(source_path):
                        self.yandex_disk.upload(source_path, approved_path)
                        logger.info(f"Файл загружен локально: {source_path}")
                    else:
                        logger.error("Локальный файл не найден для fallback")
                        return False
            else:
                # Fallback - загружаем локальный файл
                source_path = video_data.get('video_path')
                logger.info(f"Локальный путь из данных: {source_path}")
                if source_path and os.path.exists(source_path):
                    approved_path = f"{video_folder}/video.mp4"
                    self.yandex_disk.upload(source_path, approved_path)
                    logger.info(f"Файл загружен локально: {source_path}")
                else:
                    logger.error(f"Локальный файл не найден: {source_path}")
                    logger.error(f"Файл существует: {os.path.exists(source_path) if source_path else 'source_path is None'}")
                    return False
            
            # Создаем файл с метаданными
            metadata_content = f"""
ID: {approval_id}
Пользователь: {video_data.get('user_name', 'Неизвестно')}
Фильтр: {video_data.get('filter', 'Неизвестно')}
Дата создания: {video_data.get('timestamp', 'Неизвестно')}
Блогер: {video_data.get('blogger_name', 'Неизвестно')}
Папка: {video_data.get('folder_name', 'Неизвестно')}
ID ролика: {video_data.get('video_id', 'Неизвестно')}
            """.strip()
            
            # Добавляем метаданные от менеджера, если они есть
            if 'metadata' in video_data:
                metadata_content += f"""
Дата публикации: {video_data['metadata']['publish_date']}
ID сценария: {video_data['metadata']['scenario_id']}
Описание: {video_data['metadata']['description']}
Отправлено в чатбот: {video_data['metadata']['sent_at']}
                """.strip()
            
            # Сохраняем метаданные как текстовый файл
            metadata_path = f"{video_folder}/metadata.txt"
            with open("temp_metadata.txt", "w", encoding="utf-8") as f:
                f.write(metadata_content)
            
            self.yandex_disk.upload("temp_metadata.txt", metadata_path)
            
            # Удаляем временный файл
            os.remove("temp_metadata.txt")
            
            # Удаляем локальный файл после успешного перемещения (только если он существует)
            try:
                if source_path and os.path.exists(source_path):
                    os.remove(source_path)
                    logger.info(f"Локальный файл удален: {source_path}")
            except Exception as delete_error:
                logger.warning(f"Не удалось удалить локальный файл: {delete_error}")
            
            logger.info(f"Видео {approval_id} перемещено в approved папку")
            logger.info(f"Финальный путь: {approved_path}")
            logger.info(f"Публичная ссылка: {video_data.get('yandex_public_url', 'Не создана')}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка перемещения в approved папку: {e}")
            return False
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка полученного видео"""
        user_id = update.effective_user.id
        
        # Проверяем разные типы видео
        video = update.message.video
        document = update.message.document
        
        if not video and not document:
            await update.message.reply_text("❌ Пожалуйста, отправьте видео файл.")
            return
        
        # Проверяем, ждем ли мы сжатое видео
        if user_id in user_states and user_states[user_id].get('status') == 'waiting_for_compressed_video':
            # Пользователь отправил сжатое видео
            await update.message.reply_text(
                f"✅ **Сжатое видео получено!**\n\n"
                f"🔄 Проверяю размер и продолжаю обработку..."
            )
            # Сбрасываем статус
            user_states[user_id]['status'] = 'video_received'
        
        # Определяем размер файла и имя
        file_size_mb = 0
        file_name = "video.mp4"
        
        if video:
            file_size_mb = video.file_size / (1024 * 1024) if video.file_size else 0
            file_name = video.file_name or "video.mp4"
            logger.info(f"📹 Video file: {file_name}, size: {video.file_size} bytes ({file_size_mb:.1f} MB)")
        elif document:
            file_size_mb = document.file_size / (1024 * 1024) if document.file_size else 0
            file_name = document.file_name or "video.mp4"
            logger.info(f"📄 Document file: {file_name}, size: {document.file_size} bytes ({file_size_mb:.1f} MB), mime: {document.mime_type}")
        
        # Debug: sprawdzamy czy rozmiar jest prawidłowy
        if file_size_mb == 0:
            logger.warning(f"⚠️ File size is 0 or unknown for {file_name}")
            # Dla plików .MOV może być problem z rozpoznaniem rozmiaru
            if file_name.lower().endswith('.mov'):
                logger.info("🎬 .MOV file detected, allowing processing despite unknown size")
                file_size_mb = 25  # Ustawiamy bezpieczny rozmiar dla .MOV
        
        # Проверяем размер файла с fallbackami
        # Telegram API ma różne limity dla różnych typów plików
        # Dla video limit może być niższy niż 50MB
        # Use actual detected limits
        telegram_video_limit = ACTUAL_MAX_FILE_SIZE
        telegram_document_limit = ACTUAL_MAX_FILE_SIZE
        
        if ACTUAL_MAX_FILE_SIZE > 20:
            logger.info(f"🚀 Self-hosted Bot API enabled - max file size: {ACTUAL_MAX_FILE_SIZE}MB")
        else:
            logger.info(f"📱 Standard Telegram API - max file size: {ACTUAL_MAX_FILE_SIZE}MB")
        
        if file_size_mb > telegram_video_limit and (video or file_name.lower().endswith(('.mp4', '.mov', '.avi'))):
            # Dla video plików limit jest niższy - próbujemy z kompresją lub podziałem
            if file_size_mb <= telegram_video_limit * 3:  # Do 60MB próbujemy skompresować
                logger.info(f"🎬 Video file {file_size_mb:.1f} MB - attempting compression")
                await update.message.reply_text(
                    f"⚠️ **Видео большое для Telegram API** ({file_size_mb:.1f} MB)\n"
                    f"🔄 Попробуем сжать до < {telegram_video_limit}MB..."
                )
            else:
                # Dla bardzo dużych plików - podział na części
                await update.message.reply_text(
                    f"📹 **Очень большое видео** ({file_size_mb:.1f} MB)\n\n"
                    f"💡 **Telegram limit: {telegram_video_limit}MB**\n\n"
                    f"🔄 **Автоматическое решение:**\n"
                    f"• Разделю на части по 30 секунд\n"
                    f"• Обработаю каждую часть отдельно\n"
                    f"• Соединю в финальное видео\n\n"
                    f"⏳ Начинаю обработку..."
                )
                
                # Сохраняем информацию о том, что файл нужно разделить
                user_states[user_id]['needs_splitting'] = True
                user_states[user_id]['original_size'] = file_size_mb
        elif file_size_mb > telegram_document_limit and document and not file_name.lower().endswith(('.mp4', '.mov', '.avi')):
            # Dla dokumentów limit jest wyższy
            await update.message.reply_text(
                f"❌ **Документ слишком большой для Telegram API!**\n\n"
                f"📁 Размер: {file_size_mb:.1f} MB\n"
                f"📁 Имя: {file_name}\n\n"
                f"💡 **Telegram document limit: {telegram_document_limit}MB**\n\n"
                f"🔄 **Решения:**\n"
                f"• Сожмите файл до < {telegram_document_limit}MB\n"
                f"• Используйте онлайн-сжатие\n"
                f"• Разделите на части\n\n"
                f"📱 Попробуйте отправить сжатый файл"
            )
            return
        elif file_size_mb > MAX_VIDEO_SIZE_MB:
            # Fallback 1: Попробуем сжать видео
            if file_size_mb <= MAX_VIDEO_SIZE_MB * 2:  # До 600MB
                await update.message.reply_text(
                    f"⚠️ Файл большой ({file_size_mb:.1f} MB), но попробуем обработать с сжатием.\n"
                    f"📁 Имя файла: {file_name}\n"
                    f"🔄 Начинаю обработку..."
                )
            else:
                await update.message.reply_text(
                    f"❌ Файл слишком большой! ({file_size_mb:.1f} MB)\n"
                    f"📁 Имя файла: {file_name}\n"
                    f"💡 Максимальный размер: {MAX_VIDEO_SIZE_MB} MB\n"
                    f"🔄 Попробуйте сжать видео или отправить файл меньшего размера."
                )
                return
        
        # Сохраняем состояние пользователя
        user_states[user_id] = {
            'status': 'video_received',
            'filename': file_name,
            'file_id': video.file_id if video else document.file_id,
            'file_size': video.file_size if video else document.file_size,
            'start_time': datetime.now().strftime('%H:%M:%S'),
            'blogger_name': None,
            'folder_name': None,
            'video_id': None
        }
        
        # Запрашиваем ID ролика
        await update.message.reply_text(
            f"✅ Видео получено! ({file_size_mb:.1f} MB)\n\n"
            "🆔 **Введите ID ролика:**\n"
            "(например: 001, 002, 123, или любое число)"
        )
    
    async def handle_count_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора количества видео"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if user_id not in user_states:
            await query.edit_message_text("❌ Сессия истекла. Отправьте видео заново.")
            return
        
        if not query.data.startswith('count_'):
            return
        
        count = int(query.data.replace('count_', ''))
        
        # Сохраняем количество видео
        user_states[user_id]['video_count'] = count
        
        # Создаем клавиатуру для выбора фильтров для каждого видео
        keyboard = []
        
        # Группируем фильтры по типам
        filter_groups = {
            'vintage': ['vintage_slow', 'vintage_normal', 'vintage_fast'],
            'dramatic': ['dramatic_slow', 'dramatic_normal', 'dramatic_fast'],
            'soft': ['soft_slow', 'soft_normal', 'soft_fast'],
            'vibrant': ['vibrant_slow', 'vibrant_normal', 'vibrant_fast']
        }
        
        for group_name, filter_ids in filter_groups.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"🎨 {group_name.title()} (разные скорости)", 
                    callback_data=f"group_{group_name}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎬 Создаю {count} видео с разными фильтрами и скоростями\n\n"
            "🎨 Выберите группу фильтров:",
            reply_markup=reply_markup
        )
    
    async def handle_group_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора группы фильтров"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if user_id not in user_states:
            await query.edit_message_text("❌ Сессия истекла. Отправьте видео заново.")
            return
        
        if not query.data.startswith('group_'):
            return
        
        group_name = query.data.replace('group_', '')
        video_count = user_states[user_id].get('video_count', 1)
        
        # Группируем фильтры по типам
        filter_groups = {
            'vintage': ['vintage_slow', 'vintage_normal', 'vintage_fast'],
            'dramatic': ['dramatic_slow', 'dramatic_normal', 'dramatic_fast'],
            'soft': ['soft_slow', 'soft_normal', 'soft_fast'],
            'vibrant': ['vibrant_slow', 'vibrant_normal', 'vibrant_fast']
        }
        
        if group_name not in filter_groups:
            await query.edit_message_text("❌ Неизвестная группа фильтров.")
            return
        
        # Выбираем фильтры для каждого видео
        available_filters = filter_groups[group_name]
        selected_filters = []
        
        for i in range(video_count):
            filter_id = available_filters[i % len(available_filters)]
            selected_filters.append(filter_id)
        
        # Сохраняем выбранные фильтры
        user_states[user_id]['selected_filters'] = selected_filters
        
        # Обновляем состояние
        user_states[user_id].update({
            'status': 'processing',
            'filter_group': group_name
        })
        
        await query.edit_message_text(
            f"🎬 Создаю {video_count} видео с фильтрами {group_name}...\n"
            f"🎨 Фильтры: {', '.join([INSTAGRAM_FILTERS[f]['name'] for f in selected_filters])}\n"
            "⏳ Это может занять несколько минут..."
        )
        
        # Запускаем обработку в фоне
        asyncio.create_task(
            self.process_multiple_videos_parallel(user_id, query, selected_filters, context)
        )
    
    async def process_multiple_videos_parallel(self, user_id: int, query, selected_filters: list, context):
        """Параллельная обработка нескольких видео с разными фильтрами"""
        try:
            # Отправляем уведомление о начале обработки
            await query.edit_message_text(
                "🔄 **НАЧИНАЮ ОБРАБОТКУ ВИДЕО**\n\n"
                "📁 Файл будет сохранен в папке:\n"
                f"`{self.results_dir}/batch_[ID]`\n\n"
                "⏳ Пожалуйста, подождите..."
            )
            
            # Проверяем размер файла ПЕРЕД попыткой get_file()
            file_size_mb = user_states[user_id]['file_size'] / (1024 * 1024)
            logger.info(f"📥 Проверяю размер файла: {user_states[user_id]['filename']}, размер: {file_size_mb:.1f} MB")
            
            # Railway deployment - używamy 2GB limit zamiast 20MB
            railway_limit_mb = 2000  # 2GB limit na Railway
            logger.info(f"📊 Размер файла: {file_size_mb:.1f} MB, лимит Railway: {railway_limit_mb} MB")
            if file_size_mb > railway_limit_mb:  # Jeśli файл больше 2GB, автоматически сжимаем
                logger.info(f"🚨 Файл превышает Railway лимит! Начинаю компрессию...")
                await query.message.edit_text(
                    f"📦 **АВТОМАТИЧЕСКАЯ КОМПРЕССИЯ**\n\n"
                    f"📁 Размер: {file_size_mb:.1f} MB\n"
                    f"📁 Имя: {user_states[user_id]['filename']}\n\n"
                    f"🔄 Сжимаю до < {railway_limit_mb}MB...\n"
                    f"⏳ Пожалуйста, подождите..."
                )
                
                # Показываем инструкции по компрессии (Telegram API не позволяет скачать файлы >20MB)
                await query.message.edit_text(
                    f"📦 **КОМПРЕССИЯ ТРЕБУЕТСЯ**\n\n"
                    f"📁 Размер: {file_size_mb:.1f} MB\n"
                    f"📁 Имя: {user_states[user_id]['filename']}\n\n"
                    f"💡 **Telegram API limit: 20MB**\n"
                    f"🚫 **Не могу скачать файл для автоматической компрессии**\n\n"
                    f"🔄 **Быстрые решения:**\n\n"
                    f"📱 **Мобильные приложения:**\n"
                    f"• Video Compressor (Android)\n"
                    f"• Video Compress (iOS)\n"
                    f"• InShot (Android/iOS)\n\n"
                    f"💻 **Онлайн-сжатие:**\n"
                    f"• https://www.freeconvert.com/video-compressor\n"
                    f"• https://www.clideo.com/compress-video\n"
                    f"• https://www.kapwing.com/tools/compress-video\n\n"
                    f"⚡ **Рекомендуемые настройки:**\n"
                    f"• Качество: 720p или ниже\n"
                    f"• Битрейт: 1-2 Mbps\n"
                    f"• Размер: < 20MB\n\n"
                    f"⏳ Отправьте сжатое видео боту..."
                )
                
                # Очищаем состояние и ждем новый файл
                user_states[user_id]['status'] = 'waiting_for_compressed_video'
                return
            
            # Получаем файл через context только если размер OK
            try:
                logger.info(f"📥 Pobieranie pliku: {user_states[user_id]['filename']}, rozmiar: {user_states[user_id]['file_size']} bytes")
                file = await context.bot.get_file(user_states[user_id]['file_id'])
                logger.info(f"✅ Plik pobrany pomyślnie: {file.file_path}")
            except Exception as e:
                logger.error(f"❌ Błąd pobierania pliku: {e}")
                if "File is too big" in str(e):
                    logger.warning(f"⚠️ File too big for current API (limit: {ACTUAL_MAX_FILE_SIZE}MB)")
                    logger.info(f"   Using API: {ACTUAL_API_URL}")
                    logger.info(f"   File size: {user_states[user_id]['file_size'] / (1024*1024):.1f}MB")
                if "File is too big" in str(e):
                    file_size_mb = user_states[user_id]['file_size'] / (1024*1024)
                    await query.message.edit_text(
                        f"⚠️ **Файл слишком большой для стандартного Telegram API!**\n\n"
                        f"📁 Размер: {file_size_mb:.1f} MB\n"
                        f"📁 Имя: {user_states[user_id]['filename']}\n\n"
                        f"💡 **Стандартный API limit: 20MB**\n\n"
                        f"🔄 **Решения:**\n"
                        f"• **Сожмите видео** до < 20MB и отправьте снова\n"
                        f"• **Используйте self-hosted Bot API** (2GB limit)\n"
                        f"• **Разделите на части**\n\n"
                        f"🔧 **Для Railway deployment:**\n"
                        f"• Настройте self-hosted Bot API\n"
                        f"• Или сожмите файл перед отправкой\n\n"
                        f"📱 **Быстрое решение:**\n"
                        f"Отправьте сжатое видео < 20MB"
                    )
                    return
                else:
                    raise e
            
            # Создаем уникальное имя файла для входного файла
            unique_id = str(uuid.uuid4())[:8]
            input_filename = f"input_{unique_id}.mp4"
            input_path = self.temp_dir / input_filename
            
            # Скачиваем файл
            await file.download_to_drive(input_path)
            
            # Проверяем czy plik potrzebuje podziału
            needs_splitting = user_states[user_id].get('needs_splitting', False)
            if needs_splitting:
                await query.message.edit_text(
                    f"📹 **РАЗДЕЛЕНИЕ БОЛЬШОГО ФАЙЛА**\n\n"
                    f"📁 Размер: {user_states[user_id].get('original_size', 0):.1f} MB\n"
                    f"🔄 Разделяю на части по 30 секунд...\n\n"
                    f"⏳ Пожалуйста, подождите..."
                )
                
                # Разделяем файл на части
                chunks = self.split_video_into_chunks_sync(str(input_path), chunk_duration=30)
                
                if len(chunks) > 1:
                    await query.message.edit_text(
                        f"✅ **ФАЙЛ РАЗДЕЛЕН НА {len(chunks)} ЧАСТЕЙ**\n\n"
                        f"📁 Части: {len(chunks)} x 30 секунд\n"
                        f"🔄 Обрабатываю каждую часть...\n\n"
                        f"⏳ Пожалуйста, подождите..."
                    )
                    
                    # Обрабатываем каждую часть отдельно
                    processed_chunks = []
                    for i, chunk in enumerate(chunks):
                        await query.message.edit_text(
                            f"🎬 **ОБРАБОТКА ЧАСТИ {i+1}/{len(chunks)}**\n\n"
                            f"📁 Файл: {os.path.basename(chunk)}\n"
                            f"🔄 Применяю фильтры...\n\n"
                            f"⏳ Пожалуйста, подождите..."
                        )
                        
                        # Обрабатываем часть
                        uniquizer = VideoUniquizer()
                        processed_chunk = uniquizer.uniquize_video(
                            input_path=chunk,
                            output_path=chunk.replace('.mp4', '_processed.mp4'),
                            effects=selected_filters[0]['effects']  # Используем первый фильтр для всех частей
                        )
                        
                        if processed_chunk:
                            processed_chunks.append(processed_chunk)
                            logger.info(f"✅ Часть {i+1} обработана: {processed_chunk}")
                    
                    # Объединяем обработанные части
                    final_output = str(input_path).replace('.mp4', '_merged.mp4')
                    result_path = self.merge_video_chunks_sync(processed_chunks, final_output)
                    
                    if result_path:
                        # Заменяем input_path на объединенный файл
                        input_path = Path(result_path)
                        logger.info(f"✅ Видео объединено: {result_path}")
                        
                        await query.message.edit_text(
                            f"✅ **ВСЕ ЧАСТИ ОБРАБОТАНЫ И ОБЪЕДИНЕНЫ**\n\n"
                            f"📁 Финальный файл: {os.path.basename(result_path)}\n"
                            f"🔄 Продолжаю обработку с фильтрами...\n\n"
                            f"⏳ Пожалуйста, подождите..."
                        )
                    else:
                        # Если не удалось объединить, используем первую часть
                        input_path = Path(processed_chunks[0]) if processed_chunks else input_path
                        logger.warning("⚠️ Не удалось объединить части, используем первую часть")
                else:
                    logger.warning("⚠️ Не удалось разделить файл, обрабатываем как обычно")
            
            # Создаем папку для результатов
            results_folder = self.results_dir / f"batch_{unique_id}"
            results_folder.mkdir(exist_ok=True)
            
            # Уведомляем о создании папки
            blogger_name = user_states[user_id].get('blogger_name', 'Unknown')
            folder_name = user_states[user_id].get('folder_name', 'default')
            
            await query.edit_message_text(
                f"📁 **ПАПКА СОЗДАНА**\n\n"
                f"👤 Блогер: **{blogger_name}**\n"
                f"📂 Папка: **{folder_name}**\n"
                f"📂 Путь: `{results_folder}`\n"
                f"🎬 Обрабатываю {len(selected_filters)} видео...\n\n"
                "⏳ Начинаю параллельную обработку..."
            )
            
            # Создаем задачи для параллельной обработки
            tasks = []
            video_id = user_states[user_id].get('video_id', 'unknown')
            upload_date = datetime.now().strftime('%Y%m%d')
            
            for i, filter_id in enumerate(selected_filters):
                output_filename = f"{upload_date}_{video_id}_{i+1}.mp4"
                output_path = results_folder / output_filename
                
                task = {
                    'index': i + 1,
                    'filter_id': filter_id,
                    'input_path': str(input_path),
                    'output_path': str(output_path),
                    'filter_info': INSTAGRAM_FILTERS[filter_id],
                    'video_id': video_id,
                    'upload_date': upload_date
                }
                tasks.append(task)
            
            # Обрабатываем видео параллельно
            processed_videos = []
            with ThreadPoolExecutor(max_workers=min(len(tasks), 4)) as executor:
                # Запускаем все задачи
                future_to_task = {
                    executor.submit(self.process_single_video, task): task 
                    for task in tasks
                }
                
                # Отслеживаем прогресс
                completed = 0
                total = len(tasks)
                
                for future in concurrent.futures.as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        if result:
                            processed_videos.append(result)
                            completed += 1
                            logger.info(f"✅ Video {task['index']} processed successfully")
                        else:
                            logger.warning(f"⚠️ Video {task['index']} processing returned None")
                            
                            # Обновляем прогресс в Telegram с информацией о компрессии
                            progress = f"🎬 **ПРОГРЕСС ОБРАБОТКИ**\n\n"
                            progress += f"✅ Обработано: {completed}/{total} видео\n"
                            progress += f"🎨 Фильтр: {task['filter_info']['name']}\n"
                            progress += f"📁 Сохранено в: `{results_folder}`\n"
                            
                            # Добавляем информацию о компрессии если была применена
                            if result.get('compressed', False):
                                progress += f"📦 **Компрессия:** Применена\n"
                            
                            # Добавляем информацию о разделении если было применено
                            if result.get('split', False):
                                progress += f"📹 **Разделение:** {result.get('chunks_count', 0)} частей\n"
                            
                            progress += f"\n⏳ Осталось: {total - completed} видео..."
                            
                            await query.edit_message_text(progress)
                            
                    except Exception as e:
                        logger.error(f"Ошибка обработки видео {task['index']}: {e}")
                        completed += 1
                        
                        # Обновляем прогресс с ошибкой
                        progress = f"🎬 Обработано {completed}/{total} видео...\n"
                        progress += f"❌ Ошибка в видео {task['index']}: {str(e)}"
                        
                        await query.edit_message_text(progress)
            
            # Уведомляем о завершении обработки
            await query.edit_message_text(
                f"🎉 **ОБРАБОТКА ЗАВЕРШЕНА!**\n\n"
                f"✅ Обработано: {len(processed_videos)}/{len(selected_filters)} видео\n"
                f"📁 Все файлы сохранены в папке:\n"
                f"`{results_folder}`\n\n"
                f"📤 Отправляю готовые видео..."
            )
            
            # Отправляем все видео
            for video_data in processed_videos:
                try:
                    await query.message.reply_video(
                        video=open(video_data['path'], 'rb'),
                        caption=f"✅ Видео {video_data['index']}/{len(selected_filters)}\n"
                               f"🎨 Фильтр: {video_data['filter_name']}\n"
                               f"📁 Размер: {os.path.getsize(video_data['path']) / (1024*1024):.1f} MB\n"
                               f"📂 Путь: `{video_data['path']}`"
                               + (f"\n☁️ Yandex Disk: {video_data['yandex_url']}" if video_data.get('yandex_url') else ""),
                        supports_streaming=True
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки видео {video_data['index']}: {e}")
            
            # Очищаем только входной файл, выходные файлы оставляем для загрузки на Yandex Disk
            input_path.unlink(missing_ok=True)
            logger.info("Входной файл удален, выходные файлы сохранены для загрузки на Yandex Disk")
            
            # Обновляем состояние
            user_states[user_id]['status'] = 'completed'
            
            # Загружаем все видео на Yandex Disk перед добавлением в очередь
            for i, video_data in enumerate(processed_videos):
                logger.info(f"🔄 Загружаю видео {i+1} на Yandex Disk: {video_data['path']}")
                
                # Загружаем на Yandex Disk
                yandex_url, yandex_remote_path = await self.upload_to_yandex_disk(
                    video_data['path'], user_id, f"{video_data['filter_id']}_{i+1}"
                )
                
                if yandex_remote_path:
                    video_data['yandex_remote_path'] = yandex_remote_path
                    video_data['yandex_public_url'] = yandex_url
                    logger.info(f"✅ Видео {i+1} загружено на Yandex Disk: {yandex_remote_path}")
                else:
                    logger.error(f"❌ Ошибка загрузки видео {i+1} на Yandex Disk")
            
            # Добавляем все видео в очередь на аппрув
            for i, video_data in enumerate(processed_videos):
                approval_id = str(uuid.uuid4())[:8]
                pending_approvals[approval_id] = {
                    'status': 'pending',
                    'user_id': user_id,
                    'user_name': query.from_user.first_name or 'Пользователь',
                    'filename': user_states[user_id]['filename'],
                    'filter': video_data['filter_name'],
                    'video_path': video_data['path'],
                    'yandex_remote_path': video_data.get('yandex_remote_path'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'approval_id': approval_id,
                    'batch_index': i + 1,
                    'batch_total': len(selected_filters),
                    'blogger_name': user_states[user_id].get('blogger_name', 'unknown'),
                    'folder_name': user_states[user_id].get('folder_name', 'default'),
                    'video_id': user_states[user_id].get('video_id', 'unknown'),
                    'upload_date': video_data.get('upload_date', datetime.now().strftime('%Y%m%d'))
                }
                
                # Логируем для отладки
                logger.info(f"Добавлено видео в очередь: {approval_id}")
                logger.info(f"Локальный путь: {video_data['path']}")
                logger.info(f"Yandex путь: {video_data.get('yandex_remote_path', 'Не загружен')}")
            
            # Создаем клавиатуру для быстрого одобрения/отклонения
            approval_ids = [pending_approvals[aid]['approval_id'] for aid in list(pending_approvals.keys())[-len(processed_videos):]]
            keyboard = []
            
            for approval_id in approval_ids:
                keyboard.append([
                    InlineKeyboardButton(
                        f"✅ Одобрить {approval_id}", 
                        callback_data=f"quick_approve_{approval_id}"
                    ),
                    InlineKeyboardButton(
                        f"❌ Отклонить {approval_id}", 
                        callback_data=f"quick_reject_{approval_id}"
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(
                f"✅ Создано {len(processed_videos)} видео и отправлено на аппрув!\n"
                f"🆔 ID аппрува: {', '.join(approval_ids)}\n\n"
                f"👤 Блогер: **{user_states[user_id]['blogger_name']}**\n"
                f"📁 Папка: **{user_states[user_id]['folder_name']}**\n\n"
                f"⚡ **Быстрое решение:**",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Ошибка параллельной обработки видео: {e}")
            
            # Специальная обработка для "File is too big"
            if "File is too big" in str(e):
                await query.message.reply_text(
                    f"❌ **Файл слишком большой для Telegram API!**\n\n"
                    f"📁 Размер: {user_states[user_id]['file_size'] / (1024*1024):.1f} MB\n"
                    f"💡 **Telegram API limit: 50MB**\n\n"
                    f"🔄 **Решения:**\n"
                    f"• Сожмите видео до < 50MB\n"
                    f"• Используйте онлайн-сжатие\n"
                    f"• Разделите на части\n\n"
                    f"📱 Попробуйте отправить сжатое видео"
                )
            else:
                await query.message.reply_text(
                    text=f"❌ Ошибка обработки: {str(e)}"
                )
            user_states[user_id]['status'] = 'error'
    
    def process_single_video(self, task):
        """Обработка одного видео в отдельном потоке"""
        try:
            logger.info(f"🎬 Начинаю обработку видео {task['index']} с фильтром {task['filter_info']['name']}")
            
            # Проверяем размер файла и решаем как обрабатывать
            file_size_mb = os.path.getsize(task['input_path']) / (1024 * 1024)
            chunks = []  # Инициализируем переменную
            
            if file_size_mb > 50:  # Если файл больше 50MB, разделяем на части
                logger.info(f"📹 Большой файл ({file_size_mb:.1f} MB) - разделяю на части")
                print(f"📹 БОЛЬШОЙ ФАЙЛ: {file_size_mb:.1f} MB - разделение на части")
                
                # Разделяем на части по 30 секунд
                chunks = self.split_video_into_chunks_sync(task['input_path'], chunk_duration=30)
                
                if len(chunks) > 1:
                    # Обрабатываем каждую часть отдельно
                    processed_chunks = []
                    for i, chunk in enumerate(chunks):
                        logger.info(f"🎬 Обрабатываю часть {i+1}/{len(chunks)}")
                        print(f"🎬 ЧАСТЬ {i+1}/{len(chunks)}: {chunk}")
                        
                        # Сжимаем часть если нужно
                        compressed_chunk = self.compress_video_if_needed_sync(chunk)
                        
                        # Обрабатываем часть
                        uniquizer = VideoUniquizer()
                        processed_chunk = uniquizer.uniquize_video(
                            input_path=compressed_chunk,
                            output_path=chunk.replace('.mp4', '_processed.mp4'),
                            effects=task['filter_info']['effects']
                        )
                        
                        if processed_chunk:
                            processed_chunks.append(processed_chunk)
                            logger.info(f"✅ Часть {i+1} обработана: {processed_chunk}")
                            print(f"✅ ЧАСТЬ {i+1} ГОТОВА: {processed_chunk}")
                    
                    # Объединяем обработанные части
                    final_output = task['output_path'].replace('.mp4', '_merged.mp4')
                    result_path = self.merge_video_chunks_sync(processed_chunks, final_output)
                    
                    if result_path:
                        logger.info(f"✅ Видео объединено: {result_path}")
                        print(f"✅ ВИДЕО ОБЪЕДИНЕНО: {result_path}")
                    else:
                        result_path = processed_chunks[0] if processed_chunks else task['output_path']
                else:
                    # Если не удалось разделить, обрабатываем как обычно
                    trimmed_input_path = self.trim_video_if_needed_sync(task['input_path'], max_duration_seconds=60)
                    compressed_input_path = self.compress_video_if_needed_sync(trimmed_input_path)
                    
                    # Progress callback for user updates
                    def progress_callback(message, progress_pct=None):
                        if progress_pct is not None:
                            print(f"📊 [{progress_pct:.1f}%] {message}")
                        else:
                            print(f"📊 {message}")
                    
                    uniquizer = VideoUniquizer(progress_callback=progress_callback)
                    result_path = uniquizer.uniquize_video(
                        input_path=compressed_input_path,
                        output_path=task['output_path'],
                        effects=task['filter_info']['effects']
                    )
            else:
                # Обычная обработка для небольших файлов
                trimmed_input_path = self.trim_video_if_needed_sync(task['input_path'], max_duration_seconds=60)
                compressed_input_path = self.compress_video_if_needed_sync(trimmed_input_path)
                
                # Progress callback for user updates
                def progress_callback(message, progress_pct=None):
                    if progress_pct is not None:
                        print(f"📊 [{progress_pct:.1f}%] {message}")
                    else:
                        print(f"📊 {message}")
                
                uniquizer = VideoUniquizer(progress_callback=progress_callback)
                result_path = uniquizer.uniquize_video(
                    input_path=compressed_input_path,
                    output_path=task['output_path'],
                    effects=task['filter_info']['effects']
                )
            
            # Логируем результат обработки
            logger.info(f"✅ Видео {task['index']} обработано и сохранено в: {result_path}")
            print(f"✅ ВИДЕО {task['index']} ГОТОВО: {result_path}")
            
            # Проверяем что файл действительно создан
            if not result_path or not os.path.exists(result_path):
                logger.error(f"❌ Output file not created: {result_path}")
                return None
            
            # Проверяем размер выходного файла
            output_size = os.path.getsize(result_path)
            
            # Дополнительная walidacja pliku
            if output_size == 0:
                logger.error(f"❌ Output file is empty: {result_path}")
                return None
            
            logger.info(f"📊 Output file size: {output_size} bytes ({output_size/1024/1024:.1f} MB)")
            logger.info(f"✅ Video {task['index']} processed successfully: {result_path} ({output_size / (1024*1024):.1f}MB)")
            
            # Dodatkowe informacje o przetworzonym video
            try:
                from moviepy.editor import VideoFileClip
                output_clip = VideoFileClip(result_path)
                output_duration = output_clip.duration
                output_fps = output_clip.fps
                output_clip.close()
                
                print(f"📹 Output video: {output_duration:.1f}s @ {output_fps}fps")
                logger.info(f"📹 Output video: {output_duration:.1f}s @ {output_fps}fps")
            except Exception as e:
                print(f"⚠️ Could not get output video info: {e}")
                logger.warning(f"⚠️ Could not get output video info: {e}")
            
            return {
                'index': task['index'],
                'path': result_path,
                'filter_name': task['filter_info']['name'],
                'filter_id': task['filter_id'],
                'video_id': task.get('video_id', 'unknown'),
                'upload_date': datetime.now().strftime('%Y%m%d'),
                'compressed': file_size_mb > 20,  # Если файл был больше 20MB
                'split': file_size_mb > 50,  # Если файл был больше 50MB
                'chunks_count': len(chunks) if file_size_mb > 50 else 1
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки видео {task['index']}: {e}")
            logger.error(f"   Task details: {task}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            return None
    
    async def handle_filter_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора фильтра"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if user_id not in user_states:
            await query.edit_message_text("❌ Сессия истекла. Отправьте видео заново.")
            return
        
        if not query.data.startswith('filter_'):
            return
        
        filter_id = query.data.replace('filter_', '')
        if filter_id not in INSTAGRAM_FILTERS:
            await query.edit_message_text("❌ Неизвестный фильтр.")
            return
        
        filter_info = INSTAGRAM_FILTERS[filter_id]
        video_count = user_states[user_id].get('video_count', 1)
        
        # Обновляем состояние
        user_states[user_id].update({
            'status': 'processing',
            'filter': filter_info['name'],
            'filter_id': filter_id
        })
        
        await query.edit_message_text(
            f"🎬 Создаю {video_count} видео с фильтром {filter_info['name']}...\n"
            "⏳ Это может занять несколько минут..."
        )
        
        # Запускаем обработку в фоне
        asyncio.create_task(
            self.process_multiple_videos(user_id, query, filter_id, video_count, context)
        )
    
    async def handle_quick_approval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка быстрого одобрения/отклонения"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        action, approval_id = query.data.split('_', 2)[1], query.data.split('_', 2)[2]
        
        if approval_id not in pending_approvals:
            await query.edit_message_text("❌ Видео не найдено в очереди.")
            return
        
        video_data = pending_approvals[approval_id]
        
        try:
            if action == "approve":
                # Одобряем видео
                logger.info(f"Начинаю одобрение видео {approval_id}")
                success = await self.move_to_approved_folder(video_data, approval_id)
                logger.info(f"Результат одобрения: {success}")
                if not success:
                    await query.edit_message_text(f"❌ Ошибка загрузки файла на Yandex Disk")
                    return
                video_data['status'] = 'approved'
                
                await query.edit_message_text(
                    f"✅ **ВИДЕО ОДОБРЕНО!**\n\n"
                    f"🆔 ID: {approval_id}\n"
                    f"👤 Блогер: {video_data['blogger_name']}\n"
                    f"📁 Папка: {video_data['folder_name']}\n"
                    f"📂 Перемещено в: approved/\n\n"
                    f"🎉 Видео готово к публикации!"
                )
                
                # Уведомляем пользователя
                await context.bot.send_message(
                    chat_id=video_data['user_id'],
                    text=f"🎉 **Ваше видео одобрено!**\n\n"
                         f"🆔 ID: {approval_id}\n"
                         f"👤 Блогер: {video_data['blogger_name']}\n"
                         f"📁 Папка: {video_data['folder_name']}\n"
                         f"✅ Статус: Одобрено"
                )
                
            elif action == "reject":
                # Отклоняем видео
                video_data['status'] = 'rejected'
                
                await query.edit_message_text(
                    f"❌ **ВИДЕО ОТКЛОНЕНО**\n\n"
                    f"🆔 ID: {approval_id}\n"
                    f"👤 Блогер: {video_data['blogger_name']}\n"
                    f"📁 Папка: {video_data['folder_name']}\n"
                    f"📂 Перемещено в: not_approved/\n\n"
                    f"💡 Видео требует доработки"
                )
                
                # Уведомляем пользователя
                await context.bot.send_message(
                    chat_id=video_data['user_id'],
                    text=f"❌ **Видео отклонено**\n\n"
                         f"🆔 ID: {approval_id}\n"
                         f"👤 Блогер: {video_data['blogger_name']}\n"
                         f"📁 Папка: {video_data['folder_name']}\n"
                         f"❌ Статус: Отклонено\n\n"
                         f"💡 Попробуйте другой фильтр или настройки"
                )
            
        except Exception as e:
            logger.error(f"Ошибка быстрого одобрения: {e}")
            await query.edit_message_text(f"❌ Ошибка обработки: {str(e)}")
    
    async def process_multiple_videos(self, user_id: int, query, filter_id: str, video_count: int, context):
        """Обработка нескольких видео"""
        try:
            # Проверяем размер файла ПЕРЕД попыткой get_file()
            file_size_mb = user_states[user_id]['file_size'] / (1024 * 1024)
            logger.info(f"📥 Проверяю размер файла: {user_states[user_id]['filename']}, размер: {file_size_mb:.1f} MB")
            
            # Railway deployment - używamy 2GB limit zamiast 20MB
            railway_limit_mb = 2000  # 2GB limit na Railway
            logger.info(f"📊 Размер файла: {file_size_mb:.1f} MB, лимит Railway: {railway_limit_mb} MB")
            if file_size_mb > railway_limit_mb:  # Jeśli файл больше 2GB, автоматически сжимаем
                logger.info(f"🚨 Файл превышает Railway лимит! Начинаю компрессию...")
                await query.message.edit_text(
                    f"📦 **АВТОМАТИЧЕСКАЯ КОМПРЕССИЯ**\n\n"
                    f"📁 Размер: {file_size_mb:.1f} MB\n"
                    f"📁 Имя: {user_states[user_id]['filename']}\n\n"
                    f"🔄 Сжимаю до < {railway_limit_mb}MB...\n"
                    f"⏳ Пожалуйста, подождите..."
                )
                
                # Показываем инструкции по компрессии (Telegram API не позволяет скачать файлы >20MB)
                await query.message.edit_text(
                    f"📦 **КОМПРЕССИЯ ТРЕБУЕТСЯ**\n\n"
                    f"📁 Размер: {file_size_mb:.1f} MB\n"
                    f"📁 Имя: {user_states[user_id]['filename']}\n\n"
                    f"💡 **Telegram API limit: 20MB**\n"
                    f"🚫 **Не могу скачать файл для автоматической компрессии**\n\n"
                    f"🔄 **Быстрые решения:**\n\n"
                    f"📱 **Мобильные приложения:**\n"
                    f"• Video Compressor (Android)\n"
                    f"• Video Compress (iOS)\n"
                    f"• InShot (Android/iOS)\n\n"
                    f"💻 **Онлайн-сжатие:**\n"
                    f"• https://www.freeconvert.com/video-compressor\n"
                    f"• https://www.clideo.com/compress-video\n"
                    f"• https://www.kapwing.com/tools/compress-video\n\n"
                    f"⚡ **Рекомендуемые настройки:**\n"
                    f"• Качество: 720p или ниже\n"
                    f"• Битрейт: 1-2 Mbps\n"
                    f"• Размер: < 20MB\n\n"
                    f"⏳ Отправьте сжатое видео боту..."
                )
                
                # Очищаем состояние и ждем новый файл
                user_states[user_id]['status'] = 'waiting_for_compressed_video'
                return
            
            # Получаем файл через context только если размер OK
            try:
                logger.info(f"📥 Pobieranie pliku: {user_states[user_id]['filename']}, rozmiar: {user_states[user_id]['file_size']} bytes")
                file = await context.bot.get_file(user_states[user_id]['file_id'])
                logger.info(f"✅ Plik pobrany pomyślnie: {file.file_path}")
            except Exception as e:
                logger.error(f"❌ Błąd pobierania pliku: {e}")
                if "File is too big" in str(e):
                    logger.warning(f"⚠️ File too big for current API (limit: {ACTUAL_MAX_FILE_SIZE}MB)")
                    logger.info(f"   Using API: {ACTUAL_API_URL}")
                    logger.info(f"   File size: {user_states[user_id]['file_size'] / (1024*1024):.1f}MB")
                if "File is too big" in str(e):
                    file_size_mb = user_states[user_id]['file_size'] / (1024*1024)
                    await query.message.edit_text(
                        f"⚠️ **Файл слишком большой для стандартного Telegram API!**\n\n"
                        f"📁 Размер: {file_size_mb:.1f} MB\n"
                        f"📁 Имя: {user_states[user_id]['filename']}\n\n"
                        f"💡 **Стандартный API limit: 20MB**\n\n"
                        f"🔄 **Решения:**\n"
                        f"• **Сожмите видео** до < 20MB и отправьте снова\n"
                        f"• **Используйте self-hosted Bot API** (2GB limit)\n"
                        f"• **Разделите на части**\n\n"
                        f"🔧 **Для Railway deployment:**\n"
                        f"• Настройте self-hosted Bot API\n"
                        f"• Или сожмите файл перед отправкой\n\n"
                        f"📱 **Быстрое решение:**\n"
                        f"Отправьте сжатое видео < 20MB"
                    )
                    return
                else:
                    raise e
            
            # Создаем уникальное имя файла для входного файла
            unique_id = str(uuid.uuid4())[:8]
            input_filename = f"input_{unique_id}.mp4"
            input_path = self.temp_dir / input_filename
            
            # Скачиваем файл
            await file.download_to_drive(input_path)
            
            # Создаем папку для результатов
            results_folder = self.results_dir / f"batch_{unique_id}"
            results_folder.mkdir(exist_ok=True)
            
            # Обрабатываем каждое видео
            processed_videos = []
            for i in range(video_count):
                try:
                    # Создаем уникальное имя для каждого видео
                    output_filename = f"output_{unique_id}_{i+1}.mp4"
                    output_path = results_folder / output_filename
                    
                    # Обрабатываем видео
                    uniquizer = VideoUniquizer()
                    filter_info = INSTAGRAM_FILTERS[filter_id]
                    
                    result_path = uniquizer.uniquize_video(
                        input_path=str(input_path),
                        output_path=str(output_path),
                        effects=filter_info['effects']
                    )
                    
                    # Загружаем на Yandex Disk
                    yandex_url = None
                    yandex_remote_path = None
                    if self.yandex_disk:
                        yandex_url, yandex_remote_path = await self.upload_to_yandex_disk(
                            result_path, user_id, f"{filter_id}_{i+1}"
                        )
                    
                    processed_videos.append({
                        'path': result_path,
                        'yandex_url': yandex_url,
                        'yandex_remote_path': yandex_remote_path,
                        'index': i + 1
                    })
                    
                    # Обновляем прогресс
                    progress = f"🎬 Создано {i+1}/{video_count} видео..."
                    await query.edit_message_text(progress)
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки видео {i+1}: {e}")
                    continue
            
            # Отправляем все видео
            for video_data in processed_videos:
                try:
                    await query.message.reply_video(
                        video=open(video_data['path'], 'rb'),
                        caption=f"✅ Видео {video_data['index']}/{video_count}\n"
                               f"🎨 Фильтр: {filter_info['name']}\n"
                               f"📁 Размер: {os.path.getsize(video_data['path']) / (1024*1024):.1f} MB"
                               + (f"\n☁️ Yandex Disk: {video_data['yandex_url']}" if video_data['yandex_url'] else ""),
                        supports_streaming=True
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки видео {video_data['index']}: {e}")
            
            # Очищаем только входной файл, выходные файлы оставляем для загрузки на Yandex Disk
            input_path.unlink(missing_ok=True)
            logger.info("Входной файл удален, выходные файлы сохранены для загрузки на Yandex Disk")
            
            # Обновляем состояние
            user_states[user_id]['status'] = 'completed'
            
            # Добавляем все видео в очередь на аппрув
            for i, video_data in enumerate(processed_videos):
                approval_id = str(uuid.uuid4())[:8]
                pending_approvals[approval_id] = {
                    'status': 'pending',
                    'user_id': user_id,
                    'user_name': query.from_user.first_name or 'Пользователь',
                    'filename': user_states[user_id]['filename'],
                    'filter': filter_info['name'],
                    'video_path': video_data['path'],
                    'yandex_remote_path': video_data['yandex_remote_path'],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'approval_id': approval_id,
                    'batch_index': i + 1,
                    'batch_total': video_count
                }
            
            await query.message.reply_text(
                f"✅ Создано {len(processed_videos)} видео и отправлено на аппрув!\n"
                f"⏳ Ожидайте одобрения менеджера."
            )
            
        except Exception as e:
            logger.error(f"Ошибка обработки множественных видео: {e}")
            await query.message.reply_text(
                text=f"❌ Ошибка обработки: {str(e)}"
            )
            user_states[user_id]['status'] = 'error'
    
    async def process_video(self, user_id: int, query, filter_id: str, context):
        """Обработка видео в фоне"""
        try:
            # Уведомляем о начале обработки
            filter_info = INSTAGRAM_FILTERS[filter_id]
            await query.edit_message_text(
                f"🔄 **НАЧИНАЮ ОБРАБОТКУ ВИДЕО**\n\n"
                f"🎨 Фильтр: {filter_info['name']}\n"
                f"📁 Файл будет сохранен в папке:\n"
                f"`{self.temp_dir}`\n\n"
                f"⏳ Пожалуйста, подождите..."
            )
            
            # Проверяем размер файла ПЕРЕД попыткой get_file()
            file_size_mb = user_states[user_id]['file_size'] / (1024 * 1024)
            logger.info(f"📥 Проверяю размер файла: {user_states[user_id]['filename']}, размер: {file_size_mb:.1f} MB")
            
            # Railway deployment - używamy 2GB limit zamiast 20MB
            railway_limit_mb = 2000  # 2GB limit na Railway
            logger.info(f"📊 Размер файла: {file_size_mb:.1f} MB, лимит Railway: {railway_limit_mb} MB")
            if file_size_mb > railway_limit_mb:  # Jeśli файл больше 2GB, автоматически сжимаем
                logger.info(f"🚨 Файл превышает Railway лимит! Начинаю компрессию...")
                await query.message.edit_text(
                    f"📦 **АВТОМАТИЧЕСКАЯ КОМПРЕССИЯ**\n\n"
                    f"📁 Размер: {file_size_mb:.1f} MB\n"
                    f"📁 Имя: {user_states[user_id]['filename']}\n\n"
                    f"🔄 Сжимаю до < {railway_limit_mb}MB...\n"
                    f"⏳ Пожалуйста, подождите..."
                )
                
                # Показываем инструкции по компрессии (Telegram API не позволяет скачать файлы >20MB)
                await query.message.edit_text(
                    f"📦 **КОМПРЕССИЯ ТРЕБУЕТСЯ**\n\n"
                    f"📁 Размер: {file_size_mb:.1f} MB\n"
                    f"📁 Имя: {user_states[user_id]['filename']}\n\n"
                    f"💡 **Telegram API limit: 20MB**\n"
                    f"🚫 **Не могу скачать файл для автоматической компрессии**\n\n"
                    f"🔄 **Быстрые решения:**\n\n"
                    f"📱 **Мобильные приложения:**\n"
                    f"• Video Compressor (Android)\n"
                    f"• Video Compress (iOS)\n"
                    f"• InShot (Android/iOS)\n\n"
                    f"💻 **Онлайн-сжатие:**\n"
                    f"• https://www.freeconvert.com/video-compressor\n"
                    f"• https://www.clideo.com/compress-video\n"
                    f"• https://www.kapwing.com/tools/compress-video\n\n"
                    f"⚡ **Рекомендуемые настройки:**\n"
                    f"• Качество: 720p или ниже\n"
                    f"• Битрейт: 1-2 Mbps\n"
                    f"• Размер: < 20MB\n\n"
                    f"⏳ Отправьте сжатое видео боту..."
                )
                
                # Очищаем состояние и ждем новый файл
                user_states[user_id]['status'] = 'waiting_for_compressed_video'
                return
            
            # Получаем файл через context только если размер OK
            try:
                logger.info(f"📥 Pobieranie pliku: {user_states[user_id]['filename']}, rozmiar: {user_states[user_id]['file_size']} bytes")
                file = await context.bot.get_file(user_states[user_id]['file_id'])
                logger.info(f"✅ Plik pobrany pomyślnie: {file.file_path}")
            except Exception as e:
                logger.error(f"❌ Błąd pobierania pliku: {e}")
                if "File is too big" in str(e):
                    logger.warning(f"⚠️ File too big for current API (limit: {ACTUAL_MAX_FILE_SIZE}MB)")
                    logger.info(f"   Using API: {ACTUAL_API_URL}")
                    logger.info(f"   File size: {user_states[user_id]['file_size'] / (1024*1024):.1f}MB")
                if "File is too big" in str(e):
                    file_size_mb = user_states[user_id]['file_size'] / (1024*1024)
                    await query.message.edit_text(
                        f"⚠️ **Файл слишком большой для стандартного Telegram API!**\n\n"
                        f"📁 Размер: {file_size_mb:.1f} MB\n"
                        f"📁 Имя: {user_states[user_id]['filename']}\n\n"
                        f"💡 **Стандартный API limit: 20MB**\n\n"
                        f"🔄 **Решения:**\n"
                        f"• **Сожмите видео** до < 20MB и отправьте снова\n"
                        f"• **Используйте self-hosted Bot API** (2GB limit)\n"
                        f"• **Разделите на части**\n\n"
                        f"🔧 **Для Railway deployment:**\n"
                        f"• Настройте self-hosted Bot API\n"
                        f"• Или сожмите файл перед отправкой\n\n"
                        f"📱 **Быстрое решение:**\n"
                        f"Отправьте сжатое видео < 20MB"
                    )
                    return
                else:
                    raise e
            
            # Создаем имя файла с датой и ID ролика
            video_id = user_states[user_id].get('video_id', 'unknown')
            upload_date = datetime.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4())[:8]
            
            input_filename = f"input_{unique_id}.mp4"
            output_filename = f"{upload_date}_{video_id}.mp4"
            
            input_path = self.temp_dir / input_filename
            output_path = self.temp_dir / output_filename
            
            # Скачиваем файл
            await file.download_to_drive(input_path)
            
            # Уведомляем о начале обработки
            await query.edit_message_text(
                f"🎬 **ОБРАБАТЫВАЮ ВИДЕО**\n\n"
                f"🎨 Фильтр: {filter_info['name']}\n"
                f"📂 Входной файл: `{input_path}`\n"
                f"📂 Выходной файл: `{output_path}`\n\n"
                f"⏳ Обработка может занять несколько минут..."
            )
            
            # Обрабатываем видео
            uniquizer = VideoUniquizer()
            
            result_path = uniquizer.uniquize_video(
                input_path=str(input_path),
                output_path=str(output_path),
                effects=filter_info['effects']
            )
            
            # Уведомляем о завершении обработки
            await query.edit_message_text(
                f"✅ **ОБРАБОТКА ЗАВЕРШЕНА!**\n\n"
                f"🎨 Фильтр: {filter_info['name']}\n"
                f"📁 Файл сохранен в: `{result_path}`\n"
                f"📊 Размер: {os.path.getsize(result_path) / (1024*1024):.1f} MB\n\n"
                f"📤 Отправляю готовое видео..."
            )
            
            # Загружаем на Yandex Disk
            yandex_url = None
            yandex_remote_path = None
            if self.yandex_disk:
                yandex_url, yandex_remote_path = await self.upload_to_yandex_disk(
                    result_path, user_id, filter_id
                )
            
            # Отправляем результат с WebSocket progress
            result_filename = f"processed_{user_id}_{filter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            upload_result = await self.upload_video_with_progress(
                file_path=result_path,
                user_id=user_id,
                context=context,
                filename=result_filename,
                caption=f"✅ **ГОТОВО!**\n\n"
                       f"🎨 Фильтр: {filter_info['name']}\n"
                       f"📁 Размер: {os.path.getsize(result_path) / (1024*1024):.1f} MB\n"
                       f"📂 Локальный путь: `{result_path}`"
                       + (f"\n☁️ Yandex Disk: {yandex_url}" if yandex_url else "")
            )
            
            # Очищаем временные файлы
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
            
            # Обновляем состояние
            user_states[user_id]['status'] = 'completed'
            
            # Добавляем видео в очередь на аппрув
            approval_id = str(uuid.uuid4())[:8]
            pending_approvals[approval_id] = {
                'status': 'pending',
                'user_id': user_id,
                'user_name': query.from_user.first_name or 'Пользователь',
                'filename': user_states[user_id]['filename'],
                'filter': filter_info['name'],
                'video_path': result_path,
                'yandex_remote_path': yandex_remote_path,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'approval_id': approval_id
            }
            
            await query.message.reply_text(
                f"✅ Видео обработано и отправлено на аппрув!\n"
                f"🆔 ID аппрува: {approval_id}\n"
                f"⏳ Ожидайте одобрения менеджера."
            )
            
        except Exception as e:
            logger.error(f"Ошибка обработки видео: {e}")
            await query.message.reply_text(
                text=f"❌ Ошибка обработки: {str(e)}"
            )
            user_states[user_id]['status'] = 'error'
    
    def split_video_into_chunks_sync(self, file_path: str, chunk_duration: int = 30) -> list:
        """Разделяет видео на части для обработки"""
        try:
            import subprocess
            import os
            
            # Проверяем длительность видео
            cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return [file_path]  # Если не можем получить длительность, возвращаем оригинал
            
            duration = float(result.stdout.strip())
            if duration <= chunk_duration:
                return [file_path]  # Если видео короткое, не разделяем
            
            logger.info(f"🔄 Разделяю видео на части: {duration:.1f}s -> {chunk_duration}s части")
            print(f"📹 РАЗДЕЛЕНИЕ ВИДЕО: {duration:.1f}s -> {chunk_duration}s части")
            
            # Создаем папку для частей
            chunks_dir = file_path.replace('.mp4', '_chunks')
            os.makedirs(chunks_dir, exist_ok=True)
            
            chunks = []
            chunk_count = int(duration / chunk_duration) + 1
            
            for i in range(chunk_count):
                start_time = i * chunk_duration
                chunk_path = os.path.join(chunks_dir, f"chunk_{i:02d}.mp4")
                
                cmd = [
                    'ffmpeg', '-i', file_path,
                    '-ss', str(start_time),
                    '-t', str(chunk_duration),
                    '-c', 'copy',  # Копируем без перекодирования
                    '-y',
                    chunk_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(chunk_path):
                    chunks.append(chunk_path)
                    logger.info(f"✅ Часть {i+1}/{chunk_count} создана: {chunk_path}")
                    print(f"✅ ЧАСТЬ {i+1}/{chunk_count}: {chunk_path}")
                else:
                    logger.error(f"❌ Ошибка создания части {i+1}: {result.stderr}")
                    print(f"❌ ОШИБКА ЧАСТИ {i+1}: {result.stderr}")
            
            return chunks if chunks else [file_path]
            
        except Exception as e:
            logger.error(f"❌ Ошибка разделения видео: {e}")
            print(f"❌ ОШИБКА РАЗДЕЛЕНИЯ: {e}")
            return [file_path]
    
    def merge_video_chunks_sync(self, chunks: list, output_path: str) -> str:
        """Объединяет части видео в один файл"""
        try:
            import subprocess
            import os
            
            if len(chunks) <= 1:
                return chunks[0] if chunks else None
            
            logger.info(f"🔄 Объединяю {len(chunks)} частей в один файл")
            print(f"🔗 ОБЪЕДИНЕНИЕ: {len(chunks)} частей -> {output_path}")
            
            # Создаем список файлов для ffmpeg
            concat_file = output_path.replace('.mp4', '_concat.txt')
            with open(concat_file, 'w') as f:
                for chunk in chunks:
                    f.write(f"file '{chunk}'\n")
            
            # Объединяем части
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Видео объединено: {output_path}")
                print(f"✅ ОБЪЕДИНЕНИЕ ЗАВЕРШЕНО: {output_path}")
                
                # Удаляем временные файлы
                os.remove(concat_file)
                for chunk in chunks:
                    if os.path.exists(chunk):
                        os.remove(chunk)
                
                return output_path
            else:
                logger.error(f"❌ Ошибка объединения: {result.stderr}")
                print(f"❌ ОШИБКА ОБЪЕДИНЕНИЯ: {result.stderr}")
                return chunks[0] if chunks else None
                
        except Exception as e:
            logger.error(f"❌ Ошибка объединения видео: {e}")
            print(f"❌ ОШИБКА ОБЪЕДИНЕНИЯ: {e}")
            return chunks[0] if chunks else None
    
    async def compress_video_automatically(self, file_id: str, filename: str, context, user_id: int) -> dict:
        """Автоматически сжимает видео используя альтернативные методы"""
        try:
            import tempfile
            import os
            import requests
            import subprocess
            
            logger.info(f"🔄 Начинаю автоматическую компрессию: {filename}")
            logger.info(f"📁 File ID: {file_id}")
            logger.info(f"👤 User ID: {user_id}")
            
            # Создаем временную папку
            with tempfile.TemporaryDirectory() as temp_dir:
                logger.info(f"📂 Временная папка: {temp_dir}")
                # Метод 1: Пытаемся получить файл через get_file (может не работать для больших файлов)
                try:
                    file = await context.bot.get_file(file_id)
                    temp_input = os.path.join(temp_dir, f"input_{file_id}.mp4")
                    await file.download_to_drive(temp_input)
                    logger.info(f"✅ Файл получен через get_file: {temp_input}")
                except Exception as e:
                    logger.warning(f"⚠️ get_file не удался: {e}")
                    
                    # Метод 2: Прямое скачивание через URL
                    try:
                        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_id}"
                        response = requests.get(file_url, stream=True, timeout=30)
                        
                        if response.status_code == 200:
                            temp_input = os.path.join(temp_dir, f"input_{file_id}.mp4")
                            with open(temp_input, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            logger.info(f"✅ Файл скачан напрямую: {temp_input}")
                        else:
                            logger.error(f"❌ Ошибка скачивания: {response.status_code}")
                            return None
                    except Exception as e2:
                        logger.error(f"❌ Прямое скачивание не удалось: {e2}")
                        return None
                
                # Проверяем размер входного файла
                input_size = os.path.getsize(temp_input)
                input_size_mb = input_size / (1024 * 1024)
                logger.info(f"📁 Размер входного файла: {input_size_mb:.1f} MB")
                
                # Сжимаем файл с агрессивными настройками
                compressed_path = os.path.join(temp_dir, f"compressed_{file_id}.mp4")
                
                # Определяем целевую битрейт на основе размера
                target_bitrate = "500k" if input_size_mb > 50 else "1000k"
                
                cmd = [
                    'ffmpeg', '-i', temp_input,
                    '-c:v', 'libx264',
                    '-crf', '32',  # Очень высокая компрессия
                    '-preset', 'ultrafast',  # Быстрая компрессия
                    '-c:a', 'aac',
                    '-b:a', '64k',  # Низкий битрейт аудио
                    '-vf', 'scale=854:480',  # Масштабируем до 480p
                    '-b:v', target_bitrate,
                    '-maxrate', target_bitrate,
                    '-bufsize', f"{int(target_bitrate.replace('k', '')) * 2}k",
                    '-y',
                    compressed_path
                ]
                
                logger.info(f"🔄 Компрессия с параметрами: {target_bitrate}, 480p")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0 and os.path.exists(compressed_path):
                    compressed_size = os.path.getsize(compressed_path)
                    compressed_size_mb = compressed_size / (1024 * 1024)
                    
                    logger.info(f"✅ Компрессия завершена: {input_size_mb:.1f} MB -> {compressed_size_mb:.1f} MB")
                    
                    # Проверяем размер сжатого файла
                    if compressed_size < 20 * 1024 * 1024:  # < 20MB
                        # Загружаем сжатый файл обратно в Telegram
                        with open(compressed_path, 'rb') as f:
                            message = await context.bot.send_document(
                                chat_id=user_id,
                                document=f,
                                filename=f"compressed_{filename}",
                                caption=f"📦 Автоматически сжатое видео\n📁 Размер: {compressed_size_mb:.1f} MB"
                            )
                        
                        logger.info(f"✅ Сжатый файл загружен: {message.document.file_id}")
                        
                        return {
                            'file_id': message.document.file_id,
                            'file_size': message.document.file_size,
                            'filename': message.document.file_name
                        }
                    else:
                        logger.error(f"❌ Сжатый файл все еще слишком большой: {compressed_size_mb:.1f} MB")
                        return None
                else:
                    logger.error(f"❌ Ошибка компрессии: {result.stderr}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Ошибка автоматической компрессии: {e}")
            return None
    
    async def compress_and_reupload_video(self, file_id: str, filename: str, context, user_id: int) -> dict:
        """Сжимает видео и загружает обратно в Telegram"""
        try:
            import tempfile
            import os
            
            # Создаем временную папку
            with tempfile.TemporaryDirectory() as temp_dir:
                # Пытаемся получить файл через альтернативный метод
                try:
                    # Используем прямой URL для больших файлов
                    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_id}"
                    
                    # Скачиваем файл напрямую
                    import requests
                    response = requests.get(file_url, stream=True)
                    
                    if response.status_code == 200:
                        # Сохраняем во временный файл
                        temp_input = os.path.join(temp_dir, f"input_{file_id}.mp4")
                        with open(temp_input, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        logger.info(f"✅ Файл скачан напрямую: {temp_input}")
                        
                        # Сжимаем файл
                        compressed_path = os.path.join(temp_dir, f"compressed_{file_id}.mp4")
                        
                        cmd = [
                            'ffmpeg', '-i', temp_input,
                            '-c:v', 'libx264',
                            '-crf', '30',  # Высокая компрессия
                            '-preset', 'fast',
                            '-c:a', 'aac',
                            '-b:a', '96k',
                            '-vf', 'scale=1280:720',  # Масштабируем до 720p
                            '-y',
                            compressed_path
                        ]
                        
                        import subprocess
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        
                        if result.returncode == 0 and os.path.exists(compressed_path):
                            compressed_size = os.path.getsize(compressed_path)
                            
                            # Проверяем размер сжатого файла
                            if compressed_size < 20 * 1024 * 1024:  # < 20MB
                                # Загружаем сжатый файл обратно в Telegram
                                with open(compressed_path, 'rb') as f:
                                    # Отправляем как документ
                                    message = await context.bot.send_document(
                                        chat_id=user_id,
                                        document=f,
                                        filename=f"compressed_{filename}",
                                        caption="📦 Сжатое видео для обработки"
                                    )
                                
                                return {
                                    'file_id': message.document.file_id,
                                    'file_size': message.document.file_size,
                                    'filename': message.document.file_name
                                }
                            else:
                                logger.error(f"❌ Сжатый файл все еще слишком большой: {compressed_size / (1024*1024):.1f} MB")
                                return None
                        else:
                            logger.error(f"❌ Ошибка сжатия: {result.stderr}")
                            return None
                    else:
                        logger.error(f"❌ Ошибка скачивания: {response.status_code}")
                        return None
                        
                except Exception as e:
                    logger.error(f"❌ Ошибка прямого скачивания: {e}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Ошибка компрессии и перезагрузки: {e}")
            return None
    
    def trim_video_if_needed_sync(self, file_path: str, max_duration_seconds: int = 60) -> str:
        """Обрезает видео если оно слишком длинное"""
        try:
            import subprocess
            import os
            
            # Проверяем длительность видео
            cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return file_path
            
            duration = float(result.stdout.strip())
            if duration <= max_duration_seconds:
                return file_path
            
            logger.info(f"🔄 Обрезаю видео: {duration:.1f}s -> {max_duration_seconds}s")
            
            # Создаем обрезанный файл
            trimmed_path = file_path.replace('.mp4', '_trimmed.mp4')
            
            cmd = [
                'ffmpeg', '-i', file_path,
                '-t', str(max_duration_seconds),  # Обрезаем до max_duration_seconds
                '-c', 'copy',  # Копируем без перекодирования
                '-y',  # Перезаписать файл
                trimmed_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(trimmed_path):
                trimmed_size_mb = os.path.getsize(trimmed_path) / (1024 * 1024)
                logger.info(f"✅ Видео обрезано: {duration:.1f}s -> {max_duration_seconds}s, размер: {trimmed_size_mb:.1f} MB")
                
                # Удаляем оригинальный файл
                os.remove(file_path)
                return trimmed_path
            else:
                logger.error(f"❌ Ошибка обрезки: {result.stderr}")
                return file_path
                
        except Exception as e:
            logger.error(f"❌ Ошибка обрезки видео: {e}")
            return file_path
    
    def compress_video_if_needed_sync(self, file_path: str, max_size_mb: int = 2000) -> str:
        """Сжимает видео если оно слишком большое (синхронная версия)"""
        try:
            import subprocess
            import os
            
            # Проверяем размер файла
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb <= max_size_mb:
                return file_path
            
            logger.info(f"🔄 Сжимаю видео: {file_size_mb:.1f} MB -> {max_size_mb} MB")
            print(f"📦 КОМПРЕССИЯ: {file_size_mb:.1f} MB -> {max_size_mb} MB")
            
            # Создаем сжатый файл
            compressed_path = file_path.replace('.mp4', '_compressed.mp4')
            
            # Используем ffmpeg для сжатия z lepszymi parametrami dla .MOV
            cmd = [
                'ffmpeg', '-i', file_path,
                '-c:v', 'libx264',
                '-crf', '30',  # Większa kompresja dla .MOV
                '-preset', 'fast',
                '-c:a', 'aac',
                '-b:a', '96k',  # Niższy bitrate audio
                '-vf', 'scale=1280:720',  # Skalowanie do 720p
                '-y',  # Перезаписать файл
                compressed_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(compressed_path):
                compressed_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
                logger.info(f"✅ Видео сжато: {file_size_mb:.1f} MB -> {compressed_size_mb:.1f} MB")
                
                # Удаляем оригинальный файл
                os.remove(file_path)
                return compressed_path
            else:
                logger.error(f"❌ Ошибка сжатия: {result.stderr}")
                return file_path
                
        except Exception as e:
            logger.error(f"❌ Ошибка сжатия видео: {e}")
            return file_path
    
    async def compress_video_if_needed(self, file_path: str, max_size_mb: int = 2000) -> str:
        """Сжимает видео если оно слишком большое"""
        try:
            import subprocess
            import os
            
            # Проверяем размер файла
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb <= max_size_mb:
                return file_path
            
            logger.info(f"🔄 Сжимаю видео: {file_size_mb:.1f} MB -> {max_size_mb} MB")
            print(f"📦 КОМПРЕССИЯ: {file_size_mb:.1f} MB -> {max_size_mb} MB")
            
            # Создаем сжатый файл
            compressed_path = file_path.replace('.mp4', '_compressed.mp4')
            
            # Используем ffmpeg для сжатия z lepszymi parametrami dla .MOV
            cmd = [
                'ffmpeg', '-i', file_path,
                '-c:v', 'libx264',
                '-crf', '30',  # Większa kompresja dla .MOV
                '-preset', 'fast',
                '-c:a', 'aac',
                '-b:a', '96k',  # Niższy bitrate audio
                '-vf', 'scale=1280:720',  # Skalowanie do 720p
                '-y',  # Перезаписать файл
                compressed_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(compressed_path):
                compressed_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
                logger.info(f"✅ Видео сжато: {file_size_mb:.1f} MB -> {compressed_size_mb:.1f} MB")
                
                # Удаляем оригинальный файл
                os.remove(file_path)
                return compressed_path
            else:
                logger.error(f"❌ Ошибка сжатия: {result.stderr}")
                return file_path
                
        except Exception as e:
            logger.error(f"❌ Ошибка сжатия видео: {e}")
            return file_path
    
    async def upload_to_yandex_disk(self, file_path: str, user_id: int, filter_id: str) -> tuple:
        """Загрузка файла на Yandex Disk"""
        try:
            logger.info(f"🚀 Начинаю загрузку файла на Yandex Disk: {file_path}")
            
            # Получаем информацию о блогере и папке
            blogger_name = user_states[user_id].get('blogger_name', f'user_{user_id}')
            folder_name = user_states[user_id].get('folder_name', 'default')
            
            logger.info(f"👤 Блогер: {blogger_name}, 📁 Папка: {folder_name}")
            
            # Создаем структуру папок
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_folder = "Медиабанк/Команда 1"
            blogger_folder = f"{base_folder}/{blogger_name}"
            content_folder = f"{blogger_folder}/{folder_name}"
            remote_folder = f"{content_folder}/run_{timestamp}"
            
            # Создаем папки пошагово
            try:
                # Создаем базовую папку, если не существует
                if not self.yandex_disk.exists(base_folder):
                    self.yandex_disk.mkdir(base_folder)
                    logger.info(f"Создана базовая папка: {base_folder}")
                
                # Создаем папку блогера, если не существует
                if not self.yandex_disk.exists(blogger_folder):
                    self.yandex_disk.mkdir(blogger_folder)
                    logger.info(f"Создана папка блогера: {blogger_folder}")
                
                # Создаем папку контента, если не существует
                if not self.yandex_disk.exists(content_folder):
                    self.yandex_disk.mkdir(content_folder)
                    logger.info(f"Создана папка контента: {content_folder}")
                
                # Создаем папку для конкретного запуска
                if not self.yandex_disk.exists(remote_folder):
                    self.yandex_disk.mkdir(remote_folder)
                    logger.info(f"Создана папка запуска: {remote_folder}")
                
            except Exception as mkdir_error:
                logger.error(f"Ошибка создания папок: {mkdir_error}")
                # Пробуем создать папку заново
                try:
                    self.yandex_disk.mkdir(remote_folder)
                except:
                    pass
            
            # Создаем имя файла с датой и ID ролика
            video_id = user_states[user_id].get('video_id', 'unknown')
            upload_date = datetime.now().strftime('%Y%m%d')
            filename = f"{upload_date}_{video_id}.mp4"
            remote_path = f"{remote_folder}/{filename}"
            
            # Проверяем существование локального файла
            if not os.path.exists(file_path):
                logger.error(f"❌ Локальный файл не существует: {file_path}")
                return None, None
            
            logger.info(f"📁 Локальный файл существует: {file_path}")
            logger.info(f"📁 Размер файла: {os.path.getsize(file_path)} bytes")
            
            # Загружаем файл
            logger.info(f"⬆️ Загружаю файл на Yandex Disk: {remote_path}")
            self.yandex_disk.upload(file_path, remote_path)
            
            # Создаем публичную ссылку
            public_url = self.yandex_disk.get_download_link(remote_path)
            
            logger.info(f"✅ Файл загружен на Yandex Disk: {remote_path}")
            logger.info(f"🔗 Публичная ссылка: {public_url}")
            return public_url, remote_path
            
        except Exception as e:
            logger.error(f"Ошибка загрузки на Yandex Disk: {e}")
            return None, None
    
    async def start_websocket_server(self):
        """Start WebSocket server for upload progress"""
        try:
            # Use port 8082 for WebSocket (8081 is used by self-hosted API)
            websocket_port = 8082
            self.websocket_server = await websockets.serve(
                self.handle_websocket_connection,
                "0.0.0.0", websocket_port
            )
            logger.info(f"🚀 WebSocket server started on port {websocket_port}")
        except Exception as e:
            logger.error(f"❌ Failed to start WebSocket server: {e}")
    
    async def handle_websocket_connection(self, websocket, path):
        """Handle WebSocket connections for progress updates"""
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data.get("type") == "subscribe_progress":
                    user_id = data.get("user_id")
                    if user_id in self.upload_progress:
                        self.upload_progress[user_id].add_client(websocket)
                        logger.info(f"📡 WebSocket client subscribed to user {user_id}")
                
        except websockets.exceptions.ConnectionClosed:
            # Remove client from all progress trackers
            for progress in self.upload_progress.values():
                progress.remove_client(websocket)
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
    
    def compress_mov_file(self, file_path: str, output_path: str) -> str:
        """Compress .MOV files for faster upload"""
        try:
            import subprocess
            
            # Check if file is .MOV and larger than 10MB
            if not file_path.lower().endswith('.mov'):
                return file_path
            
            file_size = os.path.getsize(file_path)
            if file_size < 10 * 1024 * 1024:  # Less than 10MB, no compression needed
                return file_path
            
            logger.info(f"🗜️ Compressing .MOV file: {file_size / (1024*1024):.1f}MB")
            
            # Use FFmpeg to compress .MOV files
            cmd = [
                'ffmpeg', '-i', file_path,
                '-c:v', 'libx264',           # H.264 codec
                '-crf', '28',                # Constant rate factor (lower = better quality)
                '-preset', 'fast',           # Fast encoding
                '-c:a', 'aac',               # AAC audio codec
                '-b:a', '128k',              # Audio bitrate
                '-movflags', '+faststart',   # Optimize for streaming
                '-y',                        # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                compressed_size = os.path.getsize(output_path)
                compression_ratio = (1 - compressed_size / file_size) * 100
                logger.info(f"✅ Compression successful: {compression_ratio:.1f}% size reduction")
                return output_path
            else:
                logger.warning(f"⚠️ Compression failed, using original file: {result.stderr}")
                return file_path
                
        except Exception as e:
            logger.error(f"❌ Compression error: {e}")
            return file_path

    async def upload_video_with_progress(self, file_path: str, user_id: int, context, 
                                      filename: str, caption: str = "") -> dict:
        """Upload video with WebSocket progress tracking and .MOV compression"""
        try:
            # Compress .MOV files for faster upload
            if file_path.lower().endswith('.mov'):
                compressed_path = f"{file_path}_compressed.mp4"
                file_path = self.compress_mov_file(file_path, compressed_path)
                if file_path != compressed_path and os.path.exists(compressed_path):
                    # Use compressed file
                    file_path = compressed_path
            
            file_size = os.path.getsize(file_path)
            
            # Create progress tracker
            progress = WebSocketUploadProgress(user_id, filename)
            self.upload_progress[user_id] = progress
            progress.set_status("preparing")
            
            # Chunked upload for large files
            chunk_size = 1024 * 1024  # 1MB chunks
            uploaded_bytes = 0
            
            progress.set_status("uploading")
            progress.update_progress(0, file_size)
            
            # For files > 50MB, use chunked upload
            if file_size > 50 * 1024 * 1024:
                return await self.chunked_upload(file_path, user_id, context, 
                                              filename, caption, progress)
            
            # For smaller files, use optimized direct upload
            with open(file_path, 'rb') as f:
                # Upload to Telegram with optimized settings
                message = await context.bot.send_document(
                    chat_id=user_id,
                    document=f,
                    filename=filename,
                    caption=caption,
                    # Optimize for speed
                    read_timeout=300,  # 5 minutes timeout
                    write_timeout=300,  # 5 minutes timeout
                    connect_timeout=60,  # 1 minute connection timeout
                    pool_timeout=60  # 1 minute pool timeout
                )
                
                # Update progress to 100% after successful upload
                progress.update_progress(file_size, file_size)
            
            progress.set_status("completed")
            
            # Clean up compressed file if it was created
            if file_path.endswith('_compressed.mp4') and os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                    logger.info(f"🗑️ Cleaned up compressed file: {file_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to clean up compressed file: {e}")
            
            return {
                'file_id': message.document.file_id,
                'file_size': message.document.file_size,
                'filename': message.document.file_name
            }
            
        except Exception as e:
            if user_id in self.upload_progress:
                self.upload_progress[user_id].set_status(f"error: {str(e)}")
            logger.error(f"❌ Upload error: {e}")
            raise
    
    async def chunked_upload(self, file_path: str, user_id: int, context, 
                           filename: str, caption: str, progress: WebSocketUploadProgress) -> dict:
        """Optimized parallel chunked upload for large files"""
        try:
            file_size = os.path.getsize(file_path)
            
            # Optimize chunk size based on file size
            if file_size > 500 * 1024 * 1024:  # > 500MB
                chunk_size = 10 * 1024 * 1024  # 10MB chunks
                max_concurrent = 3  # 3 parallel uploads
            elif file_size > 100 * 1024 * 1024:  # > 100MB
                chunk_size = 8 * 1024 * 1024  # 8MB chunks
                max_concurrent = 4  # 4 parallel uploads
            else:
                chunk_size = 5 * 1024 * 1024  # 5MB chunks
                max_concurrent = 5  # 5 parallel uploads
            
            total_chunks = (file_size + chunk_size - 1) // chunk_size
            progress.set_status("chunked_upload")
            
            # Create temporary chunks
            temp_chunks = []
            with open(file_path, 'rb') as f:
                chunk_num = 0
                while True:
                    chunk_data = f.read(chunk_size)
                    if not chunk_data:
                        break
                    
                    chunk_path = f"temp_chunk_{user_id}_{chunk_num}.tmp"
                    with open(chunk_path, 'wb') as chunk_file:
                        chunk_file.write(chunk_data)
                    temp_chunks.append(chunk_path)
                    chunk_num += 1
            
            # Upload chunks in parallel with semaphore for concurrency control
            semaphore = asyncio.Semaphore(max_concurrent)
            upload_tasks = []
            
            async def upload_chunk(chunk_path: str, chunk_index: int):
                async with semaphore:
                    try:
                        with open(chunk_path, 'rb') as f:
                            message = await context.bot.send_document(
                                chat_id=user_id,
                                document=f,
                                filename=f"{filename}_part{chunk_index + 1}",
                                caption=f"📦 Часть {chunk_index + 1}/{len(temp_chunks)}",
                                # Optimize for speed
                                read_timeout=300,
                                write_timeout=300,
                                connect_timeout=60,
                                pool_timeout=60
                            )
                        
                        # Clean up chunk after upload
                        os.unlink(chunk_path)
                        
                        # Update progress
                        progress.update_progress(
                            (chunk_index + 1) * chunk_size, 
                            file_size
                        )
                        
                        return message
                    except Exception as e:
                        logger.error(f"❌ Chunk {chunk_index + 1} upload error: {e}")
                        # Clean up failed chunk
                        if os.path.exists(chunk_path):
                            os.unlink(chunk_path)
                        raise
            
            # Create upload tasks for all chunks
            for i, chunk_path in enumerate(temp_chunks):
                task = asyncio.create_task(upload_chunk(chunk_path, i))
                upload_tasks.append(task)
            
            # Wait for all uploads to complete
            messages = await asyncio.gather(*upload_tasks, return_exceptions=True)
            
            # Check for any failed uploads
            failed_uploads = [i for i, result in enumerate(messages) if isinstance(result, Exception)]
            if failed_uploads:
                raise Exception(f"Failed to upload chunks: {failed_uploads}")
            
            # Return info about the first chunk (main document)
            first_message = messages[0]
            progress.set_status("completed")
            return {
                'file_id': first_message.document.file_id,
                'file_size': first_message.document.file_size,
                'filename': first_message.document.file_name,
                'chunks': len(temp_chunks)
            }
            
        except Exception as e:
            progress.set_status(f"error: {str(e)}")
            logger.error(f"❌ Chunked upload error: {e}")
            raise


def main():
    """Главная функция запуска бота"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env файле!")
        return
    
    if not YANDEX_DISK_TOKEN:
        print("⚠️ YANDEX_DISK_TOKEN не найден. Загрузка на Yandex Disk отключена.")
    
    # Создаем бота
    bot = TelegramVideoBot()
    
    # Создаем приложение с оптимизацией для Railway
    if ACTUAL_API_URL != "https://api.telegram.org":
        # Use self-hosted Bot API with connection pooling
        application = (Application.builder()
                      .token(TELEGRAM_BOT_TOKEN)
                      .base_url(ACTUAL_API_URL)
                      .connection_pool_size(20)  # Increase connection pool
                      .read_timeout(300)        # 5 minutes read timeout
                      .write_timeout(300)       # 5 minutes write timeout
                      .connect_timeout(60)      # 1 minute connect timeout
                      .pool_timeout(60)         # 1 minute pool timeout
                      .build())
        logger.info(f"🚀 Using self-hosted Bot API: {ACTUAL_API_URL}")
    else:
        # Use standard Telegram API with connection pooling
        application = (Application.builder()
                      .token(TELEGRAM_BOT_TOKEN)
                      .connection_pool_size(20)  # Increase connection pool
                      .read_timeout(300)         # 5 minutes read timeout
                      .write_timeout(300)        # 5 minutes write timeout
                      .connect_timeout(60)       # 1 minute connect timeout
                      .pool_timeout(60)         # 1 minute pool timeout
                      .build())
        logger.info("📱 Using standard Telegram API")
    
    # Оптимизация для Railway deployment - ustawiamy timeout w Application.builder
    # Timeout settings są już wbudowane w python-telegram-bot
    
    # Start WebSocket server for upload progress using post_init
    async def start_websocket(app):
        await bot.start_websocket_server()
    
    application.post_init = start_websocket
    
    # Check if self-hosted Bot API is available (running in separate container)
    if USE_SELF_HOSTED_API:
        logger.info("🔍 Checking if self-hosted Bot API is available...")
        if check_self_hosted_api():
            logger.info("✅ Self-hosted Bot API is available and running")
        else:
            logger.warning("⚠️ Self-hosted Bot API is not available")
            logger.info("   Make sure telegram-bot-api container is running")
            logger.info("   Run: docker-compose up telegram-bot-api")
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("blogger", bot.blogger_command))
    application.add_handler(CommandHandler("filters", bot.filters_command))
    application.add_handler(CommandHandler("status", bot.status_command))
    
    # Обработчики для менеджеров
    application.add_handler(CommandHandler("manager", bot.manager_command))
    application.add_handler(CommandHandler("queue", bot.queue_command))
    application.add_handler(CommandHandler("approve", bot.approve_command))
    application.add_handler(CommandHandler("approved", bot.approved_command))
    application.add_handler(CommandHandler("reject", bot.reject_command))
    application.add_handler(CommandHandler("send_to_chatbot", bot.send_to_chatbot_command))
    
    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.VIDEO, bot.handle_video))
    application.add_handler(MessageHandler(filters.Document.VIDEO, bot.handle_video))
    application.add_handler(MessageHandler(filters.Document.MimeType("video/quicktime"), bot.handle_video))  # .MOV files
    application.add_handler(MessageHandler(filters.Document.MimeType("video/x-msvideo"), bot.handle_video))  # .AVI files
    application.add_handler(MessageHandler(filters.Document.MimeType("video/mp4"), bot.handle_video))       # .MP4 files
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_user_metadata))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_metadata))
    application.add_handler(CallbackQueryHandler(bot.handle_count_selection, pattern="^count_"))
    application.add_handler(CallbackQueryHandler(bot.handle_group_selection, pattern="^group_"))
    application.add_handler(CallbackQueryHandler(bot.handle_filter_selection, pattern="^filter_"))
    application.add_handler(CallbackQueryHandler(bot.handle_quick_approval, pattern="^quick_(approve|reject)_"))
    
    # Запускаем бота
    print("🤖 Запускаем Telegram бота...")
    print("✅ Бот запущен! Нажмите Ctrl+C для остановки.")
    
    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("\n👋 Остановка бота...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


# Health check server for Railway
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "telegram-bot"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    """Start health check server in background"""
    port = int(os.getenv('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

if __name__ == "__main__":
    # Start health server in background thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    main()
