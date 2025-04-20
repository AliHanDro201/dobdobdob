import eel
import os
import time
import logging
import traceback
import sys
import json

import elevenlabs as eleven
import webbrowser
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from utils.tts import stop_audio as tts_stop_audio
from core.gpt_service import generate_gpt_response, handle_user_input
from core.config import SECOND_OPENAI_API_KEY, ELEVENLABS_API_KEY
import tempfile
import base64

from openai import OpenAI

# Импортируем обработчики команд для работы с экраном
from commands.screen_commands_handler import screen_command_handlers

# ✅ Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# ✅ Создание необходимых директорий
os.makedirs("audio", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# ✅ Загрузка переменных окружения
try:
    load_dotenv(dotenv_path=".evn")  # Намеренно используем .evn как указано в требованиях
    logger.info("Переменные окружения загружены из .evn")
except Exception as e:
    logger.warning(f"Ошибка при загрузке .evn: {e}")
    logger.info("Попытка загрузить из .env")
    try:
        load_dotenv(dotenv_path=".env")
        logger.info("Переменные окружения загружены из .env")
    except Exception as e:
        logger.error(f"Ошибка при загрузке .env: {e}")

# ✅ Инициализация API ключей
try:
    if SECOND_OPENAI_API_KEY:
        client = OpenAI(api_key=SECOND_OPENAI_API_KEY)
        logger.info("OpenAI API инициализирован")
    else:
        logger.warning("OpenAI API ключ не найден, функциональность будет ограничена")
        # Создаем заглушку для тестирования
        client = None
    
    if ELEVENLABS_API_KEY:
        # В новой версии библиотеки ElevenLabs API ключ передается при создании клиента
        # или через переменную окружения ELEVEN_API_KEY
        os.environ["ELEVEN_API_KEY"] = ELEVENLABS_API_KEY
        logger.info("ElevenLabs API инициализирован")
    else:
        logger.warning("ElevenLabs API ключ не найден, будет использоваться edge-tts")
except Exception as e:
    logger.error(f"Ошибка при инициализации API: {e}")
    logger.error(traceback.format_exc())
    # Создаем заглушку для тестирования
    client = None

# ✅ Глобальные переменные
executor = ThreadPoolExecutor(max_workers=1)
isRecognizing = False

# ✅ Функция для обработки аудио
@eel.expose
def transcribe_audio(b64_audio: str) -> str:
    """
    Преобразует аудио в текст с помощью Whisper API.
    
    Args:
        b64_audio: Аудио в формате base64
        
    Returns:
        Распознанный текст
    """
    if not b64_audio:
        logger.warning("Получен пустой аудио-файл")
        return ""
        
    # Для тестирования без API ключа
    if client is None:
        logger.warning("OpenAI API не инициализирован, возвращаем тестовый текст")
        return "Тестовый текст для демонстрации работы без API ключа"
        
    try:
        # Декодируем base64 в бинарные данные
        data = base64.b64decode(b64_audio)
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        
        logger.info(f"Аудио сохранено во временный файл: {tmp_path}")
        
        # Отправляем на распознавание
        try:
            with open(tmp_path, "rb") as audio_file:
                rsp = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            logger.info(f"Распознан текст: {rsp[:50]}...")
            return rsp
        except Exception as e:
            logger.error(f"Ошибка при распознавании речи: {e}")
            logger.error(traceback.format_exc())
            return "Не удалось распознать речь. Пожалуйста, попробуйте еще раз."
        
    except Exception as e:
        logger.error(f"Ошибка в transcribe_audio: {e}")
        logger.error(traceback.format_exc())
        return "Произошла ошибка при обработке аудио."
    finally:
        # Удаляем временный файл
        try:
            if 'tmp_path' in locals():
                os.unlink(tmp_path)
        except:
            pass

# ✅ Eel интерфейсные функции
@eel.expose
def stop_audio_ui():
    """
    Останавливает воспроизведение аудио по запросу из UI.
    
    Returns:
        Сообщение о результате операции
    """
    try:
        logger.info("Остановка аудио по запросу из UI")
        return tts_stop_audio()
    except Exception as e:
        logger.error(f"Ошибка при остановке аудио: {e}")
        return "Ошибка при остановке аудио"

@eel.expose
def process_input(text: str) -> str:
    """
    Обрабатывает пользовательский ввод и возвращает ответ.
    
    Args:
        text: Текст от пользователя
        
    Returns:
        Ответ в формате JSON
    """
    try:
        if not text or not text.strip():
            logger.warning("Получен пустой запрос")
            return json.dumps({
                "status": 400, 
                "gptMessage": "Пожалуйста, введите запрос."
            })
            
        logger.info(f"Обработка запроса: {text[:50]}...")
        response = handle_user_input(text)
        logger.info(f"Получен ответ от обработчика")
        return response
    except Exception as e:
        logger.error(f"Ошибка в process_input: {e}")
        logger.error(traceback.format_exc())
        return json.dumps({
            "status": 500, 
            "gptMessage": "Произошла ошибка при обработке запроса."
        })

@eel.expose
def execute_screen_command(command_name: str, params: dict) -> str:
    """
    Выполняет команду для работы с экраном.
    
    Args:
        command_name: Название команды
        params: Параметры команды
        
    Returns:
        Результат выполнения команды в формате JSON
    """
    try:
        logger.info(f"Выполнение команды для работы с экраном: {command_name}")
        
        if command_name not in screen_command_handlers:
            logger.error(f"Неизвестная команда: {command_name}")
            return json.dumps({
                "status": "error",
                "message": f"Неизвестная команда: {command_name}"
            })
        
        # Выполняем команду
        handler = screen_command_handlers[command_name]
        result = handler(params)
        
        logger.info(f"Результат выполнения команды {command_name}: {result['status']}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Ошибка при выполнении команды {command_name}: {e}")
        logger.error(traceback.format_exc())
        return json.dumps({
            "status": "error",
            "message": f"Произошла ошибка при выполнении команды: {str(e)}"
        })

# ✅ Парсинг аргументов командной строки
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Голосовой ИИ-помощник')
    parser.add_argument('--port', type=int, default=8000, help='Порт для веб-интерфейса')
    parser.add_argument('--host', type=str, default='localhost', help='Хост для веб-интерфейса')
    parser.add_argument('--mode', type=str, default=None, help='Режим запуска браузера')
    parser.add_argument('--no-browser', action='store_true', help='Не открывать браузер автоматически')
    return parser.parse_args()

# ✅ Основной запуск Eel
def main():
    """
    Основная функция запуска приложения.
    """
    try:
        # Парсим аргументы командной строки
        args = parse_args()
        
        # Инициализация Eel
        eel.init('ui')
        logger.info("Eel инициализирован")
        
        # Запуск веб-интерфейса
        try:
            eel.start('main.html', mode=args.mode, host=args.host, port=args.port, block=False)
            logger.info(f"Веб-интерфейс запущен на http://{args.host}:{args.port}/main.html")
        except Exception as e:
            logger.error(f"Ошибка при запуске веб-интерфейса: {e}")
            logger.error(traceback.format_exc())
            sys.exit(1)
        
        # Пауза для загрузки интерфейса
        time.sleep(2)
        
        # Инициализация состояния ассистента
        try:
            eel.muteAssistant()
            logger.info("🎙️ muteAssistant вызван из Python — ассистент молчит")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось вызвать muteAssistant: {e}")
        
        # Открытие браузера (если не указан флаг --no-browser)
        if not args.no_browser:
            try:
                webbrowser.open(f"http://{args.host}:{args.port}/main.html")
                logger.info("Браузер открыт")
            except Exception as e:
                logger.warning(f"Не удалось автоматически открыть браузер: {e}")
                logger.info(f"Пожалуйста, откройте http://{args.host}:{args.port}/main.html вручную")
        else:
            logger.info("Автоматическое открытие браузера отключено")
            logger.info(f"Веб-интерфейс доступен по адресу: http://{args.host}:{args.port}/main.html")
        
        # Поддержка процесса
        try:
            while True:
                eel.sleep(1.0)  # Используем eel.sleep вместо time.sleep для лучшей интеграции
        except KeyboardInterrupt:
            logger.info("⛔ Приложение остановлено пользователем")
        except Exception as e:
            logger.error(f"Неожиданная ошибка в основном цикле: {e}")
            logger.error(traceback.format_exc())
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске приложения: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()