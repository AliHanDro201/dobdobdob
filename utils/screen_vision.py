# utils/screen_vision.py
"""
Модуль для захвата и анализа скриншотов экрана.
Позволяет ИИ-помощнику "видеть" экран и взаимодействовать с ним.
"""

import os
import logging
import time
import base64
import io
from typing import Dict, List, Tuple, Optional, Union, Any
import json

# Импортируем необходимые библиотеки
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageGrab
    import pytesseract
    import pyautogui
    HAS_GUI = True
except ImportError:
    HAS_GUI = False
    logging.warning("Нет доступа к графическому интерфейсу, используем заглушки для screen_vision")
    from utils.mock_modules import MockPyAutoGUI
    pyautogui = MockPyAutoGUI()

# Настройка логирования
logger = logging.getLogger(__name__)

# Директория для сохранения скриншотов
SCREENSHOTS_DIR = "screenshots"

def ensure_screenshots_dir():
    """Проверяет и создает директорию для скриншотов, если она не существует."""
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)
        logger.info(f"Создана директория для скриншотов: {SCREENSHOTS_DIR}")

def capture_screenshot(region: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
    """
    Захватывает скриншот экрана или указанной области.
    
    Args:
        region: Кортеж (x, y, width, height) для захвата определенной области экрана.
                Если None, захватывается весь экран.
    
    Returns:
        Изображение в формате numpy array или None, если произошла ошибка.
    """
    if not HAS_GUI:
        logger.warning("Нет доступа к графическому интерфейсу, возвращаем заглушку для скриншота")
        # Возвращаем заглушку - пустое изображение 800x600
        return np.zeros((600, 800, 3), dtype=np.uint8)
    
    try:
        ensure_screenshots_dir()
        
        # Захватываем скриншот
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        
        # Конвертируем в numpy array
        screenshot_np = np.array(screenshot)
        
        # Конвертируем из RGB в BGR (для OpenCV)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Сохраняем скриншот для отладки
        timestamp = int(time.time())
        filename = f"{SCREENSHOTS_DIR}/screenshot_{timestamp}.png"
        cv2.imwrite(filename, screenshot_cv)
        logger.info(f"Скриншот сохранен: {filename}")
        
        return screenshot_cv
    except Exception as e:
        logger.error(f"Ошибка при захвате скриншота: {e}")
        return None

def screenshot_to_base64(screenshot: np.ndarray) -> str:
    """
    Конвертирует скриншот в строку base64 для передачи в веб-интерфейс.
    
    Args:
        screenshot: Изображение в формате numpy array.
    
    Returns:
        Строка base64 с изображением.
    """
    try:
        # Конвертируем из BGR в RGB
        screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        
        # Создаем изображение PIL
        pil_img = Image.fromarray(screenshot_rgb)
        
        # Сохраняем в буфер
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        
        # Конвертируем в base64
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return img_str
    except Exception as e:
        logger.error(f"Ошибка при конвертации скриншота в base64: {e}")
        return ""

def extract_text_from_screenshot(screenshot: np.ndarray, region: Optional[Tuple[int, int, int, int]] = None) -> str:
    """
    Извлекает текст из скриншота с помощью OCR.
    
    Args:
        screenshot: Изображение в формате numpy array.
        region: Кортеж (x, y, width, height) для извлечения текста из определенной области.
                Если None, используется весь скриншот.
    
    Returns:
        Извлеченный текст.
    """
    if not HAS_GUI:
        logger.warning("Нет доступа к графическому интерфейсу, возвращаем заглушку для OCR")
        return "Пример текста на экране (заглушка OCR)"
    
    try:
        # Если указана область, вырезаем ее
        if region:
            x, y, w, h = region
            roi = screenshot[y:y+h, x:x+w]
        else:
            roi = screenshot
        
        # Конвертируем в оттенки серого
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Применяем пороговую обработку для улучшения распознавания
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Извлекаем текст
        text = pytesseract.image_to_string(thresh, lang='rus+eng')
        
        return text.strip()
    except Exception as e:
        logger.error(f"Ошибка при извлечении текста из скриншота: {e}")
        return ""

def find_element_by_text(screenshot: np.ndarray, text: str, threshold: float = 0.7) -> Optional[Tuple[int, int, int, int]]:
    """
    Находит элемент на скриншоте по тексту.
    
    Args:
        screenshot: Изображение в формате numpy array.
        text: Текст для поиска.
        threshold: Порог совпадения (0-1).
    
    Returns:
        Кортеж (x, y, width, height) с координатами найденного элемента или None, если элемент не найден.
    """
    if not HAS_GUI:
        logger.warning("Нет доступа к графическому интерфейсу, возвращаем заглушку для поиска элемента")
        return (100, 100, 200, 50)  # Заглушка - координаты элемента
    
    try:
        # Конвертируем в оттенки серого
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Применяем OCR для поиска всех текстовых блоков
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT, lang='rus+eng')
        
        # Ищем совпадения с точным текстом
        exact_matches = []
        partial_matches = []
        
        for i, word in enumerate(data['text']):
            confidence = float(data['conf'][i]) / 100
            if confidence < threshold:
                continue
                
            if text.lower() == word.lower():
                # Точное совпадение
                exact_matches.append((i, confidence))
            elif text.lower() in word.lower():
                # Частичное совпадение
                partial_matches.append((i, confidence))
        
        # Сначала проверяем точные совпадения
        if exact_matches:
            # Берем совпадение с наивысшей уверенностью
            best_match = max(exact_matches, key=lambda x: x[1])
            i = best_match[0]
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            logger.info(f"Найдено точное совпадение для текста '{text}' с уверенностью {best_match[1]:.2f}")
            return (x, y, w, h)
        
        # Если точных совпадений нет, используем частичные
        if partial_matches:
            best_match = max(partial_matches, key=lambda x: x[1])
            i = best_match[0]
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            logger.info(f"Найдено частичное совпадение для текста '{text}' в '{data['text'][i]}' с уверенностью {best_match[1]:.2f}")
            return (x, y, w, h)
        
        logger.warning(f"Текст '{text}' не найден на экране")
        return None
    except Exception as e:
        logger.error(f"Ошибка при поиске элемента по тексту: {e}")
        return None

def find_element_by_image(screenshot: np.ndarray, template_path: str, threshold: float = 0.8) -> Optional[Tuple[int, int, int, int]]:
    """
    Находит элемент на скриншоте по шаблону изображения.
    
    Args:
        screenshot: Изображение в формате numpy array.
        template_path: Путь к файлу шаблона.
        threshold: Порог совпадения (0-1).
    
    Returns:
        Кортеж (x, y, width, height) с координатами найденного элемента или None, если элемент не найден.
    """
    if not HAS_GUI:
        logger.warning("Нет доступа к графическому интерфейсу, возвращаем заглушку для поиска элемента")
        return (100, 100, 200, 50)  # Заглушка - координаты элемента
    
    try:
        # Загружаем шаблон
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            logger.error(f"Не удалось загрузить шаблон: {template_path}")
            return None
        
        # Получаем размеры шаблона
        h, w = template.shape[:2]
        
        # Выполняем сопоставление шаблона
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        
        # Находим позиции, где совпадение превышает порог
        locations = np.where(result >= threshold)
        
        if len(locations[0]) > 0:
            # Берем первое совпадение
            y, x = locations[0][0], locations[1][0]
            return (x, y, w, h)
        
        return None
    except Exception as e:
        logger.error(f"Ошибка при поиске элемента по изображению: {e}")
        return None

def click_element_by_text(text: str, double_click: bool = False) -> bool:
    """
    Находит элемент по тексту и кликает по нему.
    
    Args:
        text: Текст для поиска.
        double_click: Выполнить двойной клик вместо одинарного.
    
    Returns:
        True, если элемент найден и клик выполнен, иначе False.
    """
    if not HAS_GUI:
        logger.warning("Нет доступа к графическому интерфейсу, имитируем клик по элементу")
        return True  # Заглушка - имитация успешного клика
    
    try:
        # Захватываем скриншот
        screenshot = capture_screenshot()
        if screenshot is None:
            return False
        
        # Находим элемент
        element = find_element_by_text(screenshot, text)
        if element is None:
            logger.warning(f"Элемент с текстом '{text}' не найден")
            return False
        
        # Получаем координаты центра элемента
        x, y, w, h = element
        center_x, center_y = x + w // 2, y + h // 2
        
        # Выполняем клик
        if double_click:
            pyautogui.doubleClick(center_x, center_y)
            logger.info(f"Выполнен двойной клик по элементу с текстом '{text}' в позиции ({center_x}, {center_y})")
        else:
            pyautogui.click(center_x, center_y)
            logger.info(f"Выполнен клик по элементу с текстом '{text}' в позиции ({center_x}, {center_y})")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при клике по элементу с текстом '{text}': {e}")
        return False

def type_text(text: str, interval: float = 0.05) -> bool:
    """
    Вводит текст с клавиатуры.
    
    Args:
        text: Текст для ввода.
        interval: Интервал между нажатиями клавиш (в секундах).
    
    Returns:
        True, если ввод выполнен успешно, иначе False.
    """
    if not HAS_GUI:
        logger.warning("Нет доступа к графическому интерфейсу, имитируем ввод текста")
        return True  # Заглушка - имитация успешного ввода
    
    try:
        pyautogui.write(text, interval=interval)
        logger.info(f"Введен текст: '{text}'")
        return True
    except Exception as e:
        logger.error(f"Ошибка при вводе текста: {e}")
        return False

def analyze_screen(region: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, Any]:
    """
    Анализирует экран и возвращает информацию о его содержимом.
    
    Args:
        region: Кортеж (x, y, width, height) для анализа определенной области экрана.
                Если None, анализируется весь экран.
    
    Returns:
        Словарь с информацией о содержимом экрана.
    """
    try:
        # Захватываем скриншот
        screenshot = capture_screenshot(region)
        if screenshot is None:
            return {"error": "Не удалось захватить скриншот"}
        
        # Извлекаем текст
        text = extract_text_from_screenshot(screenshot)
        
        # Конвертируем скриншот в base64
        screenshot_base64 = screenshot_to_base64(screenshot)
        
        # Формируем результат
        result = {
            "timestamp": int(time.time()),
            "text": text,
            "screenshot": screenshot_base64,
            "resolution": (screenshot.shape[1], screenshot.shape[0])
        }
        
        return result
    except Exception as e:
        logger.error(f"Ошибка при анализе экрана: {e}")
        return {"error": str(e)}

def save_screen_analysis(analysis: Dict[str, Any]) -> str:
    """
    Сохраняет результаты анализа экрана в JSON-файл.
    
    Args:
        analysis: Словарь с результатами анализа.
    
    Returns:
        Путь к сохраненному файлу.
    """
    try:
        ensure_screenshots_dir()
        
        # Формируем имя файла
        timestamp = analysis.get("timestamp", int(time.time()))
        filename = f"{SCREENSHOTS_DIR}/analysis_{timestamp}.json"
        
        # Сохраняем анализ без скриншота (чтобы файл не был слишком большим)
        analysis_to_save = analysis.copy()
        if "screenshot" in analysis_to_save:
            del analysis_to_save["screenshot"]
        
        # Сохраняем в файл
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_to_save, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Анализ экрана сохранен: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Ошибка при сохранении анализа экрана: {e}")
        return ""

# Пример использования
if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Тестируем захват и анализ экрана
    analysis = analyze_screen()
    print("\nРезультаты анализа экрана:")
    print(f"Разрешение: {analysis['resolution']}")
    print(f"Текст на экране: {analysis['text'][:200]}...")
    
    # Сохраняем результаты анализа
    save_path = save_screen_analysis(analysis)
    print(f"Результаты сохранены: {save_path}")