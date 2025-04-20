# commands/screen_commands_handler.py
"""
Обработчик команд для работы с экраном.
Связывает команды из commands_as_json.py с функциями из screen_commands.py.
"""

import logging
from typing import Dict, Any

from commands.screen_commands import (
    take_screenshot,
    read_screen_text,
    click_on_text,
    input_text,
    find_and_click_then_type,
    find_text_field
)

# Настройка логирования
logger = logging.getLogger(__name__)

def handle_take_screenshot_vision(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обработчик команды take_screenshot_vision.
    
    Args:
        params: Параметры команды.
    
    Returns:
        Результат выполнения команды.
    """
    region = params.get("region")
    return take_screenshot(region)

def handle_read_screen_text(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обработчик команды read_screen_text.
    
    Args:
        params: Параметры команды.
    
    Returns:
        Результат выполнения команды.
    """
    region = params.get("region")
    return read_screen_text(region)

def handle_click_on_text(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обработчик команды click_on_text.
    
    Args:
        params: Параметры команды.
    
    Returns:
        Результат выполнения команды.
    """
    text = params.get("text")
    double_click = params.get("double_click", False)
    
    if not text:
        return {
            "status": "error",
            "message": "Не указан текст для поиска."
        }
    
    return click_on_text(text, double_click)

def handle_input_text_vision(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обработчик команды input_text_vision.
    
    Args:
        params: Параметры команды.
    
    Returns:
        Результат выполнения команды.
    """
    text = params.get("text")
    interval = params.get("interval", 0.05)
    
    if not text:
        return {
            "status": "error",
            "message": "Не указан текст для ввода."
        }
    
    return input_text(text, interval)

def handle_find_and_click_then_type(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обработчик команды find_and_click_then_type.
    
    Args:
        params: Параметры команды.
    
    Returns:
        Результат выполнения команды.
    """
    text = params.get("text")
    input_text_value = params.get("input_text")
    interval = params.get("interval", 0.05)
    
    if not text:
        return {
            "status": "error",
            "message": "Не указан текст для поиска."
        }
    
    if not input_text_value:
        return {
            "status": "error",
            "message": "Не указан текст для ввода."
        }
    
    return find_and_click_then_type(text, input_text_value, interval)

def handle_find_text_field(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обработчик команды find_text_field.
    
    Args:
        params: Параметры команды.
    
    Returns:
        Результат выполнения команды.
    """
    field_name = params.get("field_name")
    double_click = params.get("double_click", False)
    
    if not field_name:
        return {
            "status": "error",
            "message": "Не указано название поля для поиска."
        }
    
    return find_text_field(field_name, double_click)

# Словарь с обработчиками команд
screen_command_handlers = {
    "take_screenshot_vision": handle_take_screenshot_vision,
    "read_screen_text": handle_read_screen_text,
    "click_on_text": handle_click_on_text,
    "input_text_vision": handle_input_text_vision,
    "find_and_click_then_type": handle_find_and_click_then_type,
    "find_text_field": handle_find_text_field
}