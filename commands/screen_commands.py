# commands/screen_commands.py
"""
Модуль с командами для работы с экраном.
Позволяет ИИ-помощнику взаимодействовать с элементами интерфейса.
"""

import logging
import os
import time
from typing import Dict, List, Tuple, Optional, Union, Any

from utils.screen_vision import (
    capture_screenshot,
    extract_text_from_screenshot,
    find_element_by_text,
    click_element_by_text,
    type_text,
    analyze_screen
)

# Настройка логирования
logger = logging.getLogger(__name__)

def take_screenshot(region: Optional[str] = None) -> Dict[str, Any]:
    """
    Делает скриншот экрана или указанной области.
    
    Args:
        region: Строка с координатами области в формате "x,y,width,height".
                Если None, делается скриншот всего экрана.
    
    Returns:
        Словарь с результатом операции.
    """
    try:
        # Парсим координаты области, если они указаны
        region_tuple = None
        if region:
            try:
                x, y, w, h = map(int, region.split(','))
                region_tuple = (x, y, w, h)
            except ValueError:
                return {
                    "status": "error",
                    "message": f"Неверный формат области: {region}. Используйте формат 'x,y,width,height'."
                }
        
        # Делаем скриншот
        screenshot = capture_screenshot(region_tuple)
        if screenshot is None:
            return {
                "status": "error",
                "message": "Не удалось сделать скриншот."
            }
        
        # Анализируем экран
        analysis = analyze_screen(region_tuple)
        
        return {
            "status": "success",
            "message": "Скриншот успешно сделан.",
            "text": analysis.get("text", ""),
            "timestamp": analysis.get("timestamp", int(time.time())),
            "resolution": analysis.get("resolution", (0, 0))
        }
    except Exception as e:
        logger.error(f"Ошибка при создании скриншота: {e}")
        return {
            "status": "error",
            "message": f"Произошла ошибка: {str(e)}"
        }

def read_screen_text(region: Optional[str] = None) -> Dict[str, Any]:
    """
    Считывает текст с экрана или указанной области.
    
    Args:
        region: Строка с координатами области в формате "x,y,width,height".
                Если None, считывается текст со всего экрана.
    
    Returns:
        Словарь с результатом операции.
    """
    try:
        # Парсим координаты области, если они указаны
        region_tuple = None
        if region:
            try:
                x, y, w, h = map(int, region.split(','))
                region_tuple = (x, y, w, h)
            except ValueError:
                return {
                    "status": "error",
                    "message": f"Неверный формат области: {region}. Используйте формат 'x,y,width,height'."
                }
        
        # Делаем скриншот
        screenshot = capture_screenshot(region_tuple)
        if screenshot is None:
            return {
                "status": "error",
                "message": "Не удалось сделать скриншот."
            }
        
        # Извлекаем текст
        text = extract_text_from_screenshot(screenshot, region_tuple)
        
        return {
            "status": "success",
            "message": "Текст успешно считан.",
            "text": text
        }
    except Exception as e:
        logger.error(f"Ошибка при считывании текста с экрана: {e}")
        return {
            "status": "error",
            "message": f"Произошла ошибка: {str(e)}"
        }

def click_on_text(text: str, double_click: bool = False) -> Dict[str, Any]:
    """
    Находит текст на экране и кликает по нему.
    
    Args:
        text: Текст для поиска.
        double_click: Выполнить двойной клик вместо одинарного.
    
    Returns:
        Словарь с результатом операции.
    """
    try:
        # Выполняем клик
        result = click_element_by_text(text, double_click)
        
        if result:
            return {
                "status": "success",
                "message": f"{'Двойной клик' if double_click else 'Клик'} по тексту '{text}' выполнен успешно."
            }
        else:
            return {
                "status": "error",
                "message": f"Не удалось найти текст '{text}' на экране."
            }
    except Exception as e:
        logger.error(f"Ошибка при клике по тексту '{text}': {e}")
        return {
            "status": "error",
            "message": f"Произошла ошибка: {str(e)}"
        }

def input_text(text: str, interval: float = 0.05) -> Dict[str, Any]:
    """
    Вводит текст с клавиатуры.
    
    Args:
        text: Текст для ввода.
        interval: Интервал между нажатиями клавиш (в секундах).
    
    Returns:
        Словарь с результатом операции.
    """
    try:
        # Вводим текст
        result = type_text(text, interval)
        
        if result:
            return {
                "status": "success",
                "message": f"Текст '{text}' успешно введен."
            }
        else:
            return {
                "status": "error",
                "message": "Не удалось ввести текст."
            }
    except Exception as e:
        logger.error(f"Ошибка при вводе текста '{text}': {e}")
        return {
            "status": "error",
            "message": f"Произошла ошибка: {str(e)}"
        }

def find_and_click_then_type(text: str, input_text: str, interval: float = 0.05) -> Dict[str, Any]:
    """
    Находит текст на экране, кликает по нему и вводит текст.
    
    Args:
        text: Текст для поиска и клика.
        input_text: Текст для ввода после клика.
        interval: Интервал между нажатиями клавиш (в секундах).
    
    Returns:
        Словарь с результатом операции.
    """
    try:
        # Выполняем клик
        click_result = click_element_by_text(text)
        
        if not click_result:
            return {
                "status": "error",
                "message": f"Не удалось найти текст '{text}' на экране."
            }
        
        # Даем время для фокусировки поля ввода
        time.sleep(0.5)
        
        # Вводим текст
        type_result = type_text(input_text, interval)
        
        if type_result:
            return {
                "status": "success",
                "message": f"Клик по тексту '{text}' и ввод текста '{input_text}' выполнены успешно."
            }
        else:
            return {
                "status": "error",
                "message": f"Клик по тексту '{text}' выполнен успешно, но не удалось ввести текст."
            }
    except Exception as e:
        logger.error(f"Ошибка при клике по тексту '{text}' и вводе текста '{input_text}': {e}")
        return {
            "status": "error",
            "message": f"Произошла ошибка: {str(e)}"
        }

# Функция для поиска полей ввода текста
def find_text_field(field_name: str, double_click: bool = False) -> Dict[str, Any]:
    """
    Находит поле для ввода текста на экране и кликает по нему.
    
    Args:
        field_name: Название или подсказка поля для ввода.
        double_click: Выполнить двойной клик вместо одинарного.
    
    Returns:
        Словарь с результатом операции.
    """
    try:
        # Делаем скриншот
        screenshot = capture_screenshot()
        if screenshot is None:
            return {
                "status": "error",
                "message": "Не удалось сделать скриншот."
            }
        
        # Список возможных меток для полей ввода
        field_labels = [
            field_name,
            f"{field_name}:",
            f"Введите {field_name}",
            f"Ваш {field_name}",
            f"Enter {field_name}",
            f"Your {field_name}"
        ]
        
        # Ищем поле по меткам
        for label in field_labels:
            element = find_element_by_text(screenshot, label)
            if element:
                # Нашли метку поля, кликаем немного правее и ниже (где обычно находится поле ввода)
                x, y, w, h = element
                # Смещаемся вправо от метки и немного вниз
                click_x = x + w + 20
                click_y = y + h // 2
                
                # Выполняем клик
                if double_click:
                    pyautogui.doubleClick(click_x, click_y)
                    logger.info(f"Выполнен двойной клик по полю ввода '{field_name}' в позиции ({click_x}, {click_y})")
                else:
                    pyautogui.click(click_x, click_y)
                    logger.info(f"Выполнен клик по полю ввода '{field_name}' в позиции ({click_x}, {click_y})")
                
                return {
                    "status": "success",
                    "message": f"Поле ввода '{field_name}' найдено и выбрано."
                }
        
        # Если не нашли по меткам, пробуем найти по placeholder или подсказкам внутри полей
        placeholders = [
            field_name,
            f"Введите {field_name}",
            f"Search",
            f"Поиск",
            f"Email",
            f"Пароль",
            f"Логин",
            f"Username",
            f"Password"
        ]
        
        for placeholder in placeholders:
            if field_name.lower() in placeholder.lower() or placeholder.lower() in field_name.lower():
                element = find_element_by_text(screenshot, placeholder)
                if element:
                    # Нашли placeholder, кликаем прямо по нему
                    x, y, w, h = element
                    click_x = x + w // 2
                    click_y = y + h // 2
                    
                    # Выполняем клик
                    if double_click:
                        pyautogui.doubleClick(click_x, click_y)
                        logger.info(f"Выполнен двойной клик по полю с placeholder '{placeholder}' в позиции ({click_x}, {click_y})")
                    else:
                        pyautogui.click(click_x, click_y)
                        logger.info(f"Выполнен клик по полю с placeholder '{placeholder}' в позиции ({click_x}, {click_y})")
                    
                    return {
                        "status": "success",
                        "message": f"Поле ввода с placeholder '{placeholder}' найдено и выбрано."
                    }
        
        return {
            "status": "error",
            "message": f"Не удалось найти поле ввода '{field_name}' на экране."
        }
    except Exception as e:
        logger.error(f"Ошибка при поиске поля ввода '{field_name}': {e}")
        return {
            "status": "error",
            "message": f"Произошла ошибка: {str(e)}"
        }

# Словарь с командами для экспорта
screen_commands = {
    "take_screenshot": take_screenshot,
    "read_screen_text": read_screen_text,
    "click_on_text": click_on_text,
    "input_text": input_text,
    "find_and_click_then_type": find_and_click_then_type,
    "find_text_field": find_text_field
}

# Пример использования
if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Тестируем команды
    print("\nТест команды take_screenshot:")
    print(take_screenshot())
    
    print("\nТест команды read_screen_text:")
    print(read_screen_text())
    
    print("\nТест команды click_on_text:")
    print(click_on_text("Пример"))
    
    print("\nТест команды input_text:")
    print(input_text("Тестовый текст"))
    
    print("\nТест команды find_and_click_then_type:")
    print(find_and_click_then_type("Поиск", "Тестовый запрос"))