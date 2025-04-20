import asyncio
import json
import logging
import traceback
import os
from typing import Dict, Any, Optional

from core.agent import async_chat_completion
from integrations.orchestrator import orchestrate_browser_chat
from core.config import USE_BROWSER_FOR_ALL_REQUESTS

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("assistant.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("gpt_service")

# Определяем, использовать ли браузер для всех запросов
# По умолчанию используем браузер для всех запросов, если не указано иное
USE_BROWSER = os.environ.get("USE_BROWSER_FOR_ALL_REQUESTS", "1").lower() in ("1", "true", "yes")

def handle_user_input(user_text: str) -> str:
    """
    Обрабатывает пользовательский ввод и определяет, нужно ли использовать
    браузерный чат или обычный GPT.
    
    Args:
        user_text: Текст от пользователя
        
    Returns:
        Строка с ответом в формате JSON
    """
    try:
        # Проверяем наличие явного триггера для браузерного чата
        trigger = "обратись к gpt"
        if user_text.lower().startswith(trigger):
            query = user_text[len(trigger):].strip()
            if query:
                logger.info(f"Обнаружен явный триггер, запрос для браузерного чата: {query}")
                return process_browser_chat(query)
            else:
                logger.warning("Не указан текст запроса после 'обратись к gpt'.")
                return json.dumps({
                    "status": 400, 
                    "gptMessage": "Пожалуйста, укажите запрос после 'обратись к gpt'."
                })
        else:
            # Если нет явного триггера, но настроено использование браузера для всех запросов
            if USE_BROWSER:
                logger.info(f"Используем браузер для запроса: {user_text[:50]}...")
                return process_browser_chat(user_text)
            else:
                # Используем прямой API-вызов
                logger.info(f"Используем API для запроса: {user_text[:50]}...")
                return generate_gpt_response(user_text)
    except Exception as e:
        logger.error(f"Неожиданная ошибка в handle_user_input: {e}")
        logger.error(traceback.format_exc())
        return json.dumps({
            "status": 500, 
            "gptMessage": "Произошла неожиданная ошибка при обработке запроса."
        })

def process_browser_chat(query: str) -> str:
    """
    Обрабатывает запрос через браузерный чат.
    
    Args:
        query: Текст запроса
        
    Returns:
        Строка с ответом в формате JSON
    """
    try:
        # Вызываем оркестратор для обработки запроса через браузер
        result = orchestrate_browser_chat(query, enhance=True, headless=True)
        
        if result["status"] == 200:
            logger.info("Результат оркестрации: успешно")
            return json.dumps({
                "status": 200, 
                "gptMessage": result["message"],
                "source": "browser_chat"
            })
        else:
            logger.error(f"Ошибка при оркестрации браузера: {result.get('error', 'Неизвестная ошибка')}")
            return json.dumps({
                "status": result["status"], 
                "gptMessage": f"Произошла ошибка при обращении к браузеру: {result.get('message', 'Неизвестная ошибка')}"
            })
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса через браузер: {e}")
        logger.error(traceback.format_exc())
        return json.dumps({
            "status": 500, 
            "gptMessage": f"Произошла ошибка при обращении к браузеру: {str(e)}"
        })

def generate_gpt_response(text: str) -> str:
    """
    Генерирует ответ от GPT на основе пользовательского ввода через API.
    
    Args:
        text: Текст запроса
        
    Returns:
        Строка с ответом в формате JSON
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(async_chat_completion(text))
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Ошибка в generate_gpt_response: {e}")
        logger.error(traceback.format_exc())
        return json.dumps({
            "status": 500, 
            "gptMessage": f"Извините, произошла ошибка при обработке вашего запроса: {str(e)}"
        })
    finally:
        loop.close()
