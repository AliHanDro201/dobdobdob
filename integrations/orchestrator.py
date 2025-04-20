# integrations/orchestrator.py
import logging
import threading
import asyncio
import os
import time
from typing import Dict, Any, Optional

from integrations.browser_chat import send_query_to_chatgpt
from utils.tts import generate_audio, stop_audio

# Настройка логирования
logger = logging.getLogger("orchestrator")

# Директория для аудиофайлов
AUDIO_DIR = "audio"

def ensure_audio_dir():
    """Проверяет и создает директорию для аудиофайлов, если она не существует."""
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)
        logger.info(f"Создана директория для аудиофайлов: {AUDIO_DIR}")

def orchestrate_browser_chat(query: str, enhance: bool = True, headless: bool = True) -> Dict[str, Any]:
    """
    Выполняет запрос к ChatGPT через браузер, получает ответ,
    затем запускает TTS для озвучки и возвращает ответ.
    
    Args:
        query: Запрос пользователя
        enhance: Улучшать ли запрос с помощью prompt_enhancer
        headless: Запускать ли браузер в фоновом режиме
        
    Returns:
        Словарь с результатами запроса
    """
    logger.info(f"Начало оркестрации запроса: {query[:50]}...")
    
    # Останавливаем предыдущее аудио, если оно воспроизводится
    stop_audio()
    
    # Проверяем и создаем директорию для аудиофайлов
    ensure_audio_dir()
    
    # Формируем имя файла для аудио
    timestamp = int(time.time())
    audio_file = f"{AUDIO_DIR}/message_{timestamp}.mp3"
    
    try:
        # Отправляем запрос в ChatGPT через браузер
        logger.info("Отправка запроса в ChatGPT через браузер...")
        answer = send_query_to_chatgpt(query, enhance=enhance, headless=headless)
        
        if answer.startswith("Ошибка:"):
            logger.error(f"Ошибка при получении ответа от ChatGPT: {answer}")
            return {
                "status": 500,
                "message": "Произошла ошибка при обращении к ChatGPT",
                "error": answer,
                "source": "browser_chat"
            }
        
        logger.info(f"Получен ответ от ChatGPT длиной {len(answer)} символов")
        
        # Запускаем TTS в отдельном потоке
        def run_tts():
            try:
                logger.info(f"Запуск генерации аудио для ответа в файл {audio_file}")
                asyncio.run(generate_audio(answer, output_file=audio_file, voice="ru-RU-SvetlanaNeural"))
                logger.info("Аудио успешно сгенерировано")
            except Exception as e:
                logger.error(f"Ошибка при генерации аудио: {e}")
        
        tts_thread = threading.Thread(target=run_tts, daemon=True)
        tts_thread.start()
        
        return {
            "status": 200,
            "message": answer,
            "audio_file": audio_file,
            "source": "browser_chat"
        }
    except Exception as e:
        logger.error(f"Ошибка при оркестрации запроса: {e}")
        return {
            "status": 500,
            "message": f"Произошла ошибка при обработке запроса: {str(e)}",
            "source": "browser_chat"
        }

# Пример вызова:
if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Тестовый запрос
    result = orchestrate_browser_chat("Расскажи о Казахстане", enhance=True, headless=False)
    print("\nРезультат оркестрации:")
    for key, value in result.items():
        if key == "message":
            print(f"{key}: {value[:100]}...")
        else:
            print(f"{key}: {value}")