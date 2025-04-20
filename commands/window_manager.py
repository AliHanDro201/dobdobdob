import os
import json
import time
import logging
from typing import Optional, Tuple, Dict

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("assistant.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("window_manager")

# Проверяем наличие графического интерфейса
has_display = "DISPLAY" in os.environ and os.environ["DISPLAY"]

# Условные импорты для кроссплатформенности
try:
    import cv2
    import numpy as np
    import pytesseract
    CV_AVAILABLE = True
except ImportError:
    logger.warning("cv2, numpy или pytesseract не установлены")
    CV_AVAILABLE = False

# Импорт pyautogui с учетом наличия графического интерфейса
if has_display:
    try:
        import pyautogui
        PYAUTOGUI_AVAILABLE = True
    except ImportError:
        logger.warning("pyautogui не установлен")
        from utils.mock_modules import mock_pyautogui as pyautogui
        PYAUTOGUI_AVAILABLE = False
else:
    logger.warning("Нет доступа к графическому интерфейсу, используем заглушку pyautogui")
    from utils.mock_modules import mock_pyautogui as pyautogui
    PYAUTOGUI_AVAILABLE = False

# Импорт pywinctl с учетом наличия графического интерфейса
if has_display:
    try:
        import pywinctl as gw
        PYWINCTL_AVAILABLE = True
    except ImportError:
        logger.warning("pywinctl не установлен")
        PYWINCTL_AVAILABLE = False
        
        # Создаем заглушку для gw.getActiveWindow()
        class MockWindow:
            def __init__(self):
                self.title = "Mock Window"
                self.left = 0
                self.top = 0
                self.width = 100
                self.height = 100
                
        class MockGW:
            def getActiveWindow(self):
                return MockWindow()
                
        gw = MockGW()
else:
    logger.warning("Нет доступа к графическому интерфейсу, создаем заглушку для pywinctl")
    PYWINCTL_AVAILABLE = False
    
    # Создаем заглушку для gw.getActiveWindow()
    class MockWindow:
        def __init__(self):
            self.title = "Mock Window"
            self.left = 0
            self.top = 0
            self.width = 100
            self.height = 100
            
    class MockGW:
        def getActiveWindow(self):
            return MockWindow()
            
    gw = MockGW()

# Путь для хранения кэша интерфейсов
CACHE_DIR = "interface_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def sanitize_filename(filename: str) -> str:
    """
    Убирает неподдерживаемые символы из имени файла.
    """
    return "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in filename)

def get_active_window_screenshot() -> Optional[str]:
    """
    Делает скриншот активного окна и сохраняет его.
    
    Returns:
        Путь к сохраненному скриншоту или None в случае ошибки
    """
    # Проверяем доступность необходимых библиотек
    if not all([PYAUTOGUI_AVAILABLE, PYWINCTL_AVAILABLE]):
        logger.error("Не все необходимые библиотеки установлены для функции get_active_window_screenshot")
        return None
    
    try:
        # Создаем директорию для кэша, если она не существует
        os.makedirs(CACHE_DIR, exist_ok=True)
        
        active_window = gw.getActiveWindow()
        if not active_window:
            logger.warning("Не удалось получить активное окно")
            
            # Альтернативный вариант - скриншот всего экрана
            try:
                screenshot_path = os.path.join(CACHE_DIR, f"fullscreen_{int(time.time())}.png")
                img = pyautogui.screenshot()
                img.save(screenshot_path)
                logger.info(f"Сделан скриншот всего экрана: {screenshot_path}")
                return screenshot_path
            except Exception as e:
                logger.error(f"Ошибка при создании скриншота всего экрана: {e}")
                return None

        # Фильтруем имя файла, убирая неподдерживаемые символы
        window_title = sanitize_filename(active_window.title)
        
        screenshot_path = os.path.join(CACHE_DIR, f"{window_title}_{int(time.time())}.png")

        logger.info(f"Делаем скриншот окна: {window_title}")

        # Проверяем размеры окна
        if active_window.width == 0 or active_window.height == 0:
            logger.error("Окно имеет нулевые размеры")
            return None

        # Делаем скриншот
        try:
            img = pyautogui.screenshot(region=(
                active_window.left,
                active_window.top,
                active_window.width,
                active_window.height
            ))
        except Exception as e:
            logger.error(f"Ошибка при создании скриншота окна: {e}")
            
            # Пробуем сделать скриншот всего экрана
            try:
                screenshot_path = os.path.join(CACHE_DIR, f"fullscreen_{int(time.time())}.png")
                img = pyautogui.screenshot()
                img.save(screenshot_path)
                logger.info(f"Сделан скриншот всего экрана: {screenshot_path}")
                return screenshot_path
            except Exception as e2:
                logger.error(f"Ошибка при создании скриншота всего экрана: {e2}")
                return None

        # Сохраняем скриншот
        try:
            img.save(screenshot_path)
        except Exception as e:
            logger.error(f"Ошибка при сохранении скриншота: {e}")
            return None

        # Проверяем, создался ли файл
        if not os.path.exists(screenshot_path):
            logger.error(f"Файл {screenshot_path} не создан")
            return None

        logger.info(f"Скриншот сохранен: {screenshot_path}")
        return screenshot_path

    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании скриншота: {e}")
        return None

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    logger.warning("PIL не установлена")
    PIL_AVAILABLE = False

def extract_text_elements(image_path: str) -> Dict[str, Tuple[int, int]]:
    """
    Распознает текст на скриншоте и возвращает координаты каждого элемента.
    
    Args:
        image_path: Путь к изображению для анализа
        
    Returns:
        Словарь с текстовыми элементами и их координатами
    """
    # Проверяем доступность необходимых библиотек
    if not all([CV_AVAILABLE, PIL_AVAILABLE]):
        logger.error("Не все необходимые библиотеки установлены для функции extract_text_elements")
        return {}
    
    try:
        # Проверяем, существует ли файл
        if not os.path.exists(image_path):
            logger.error(f"Файл {image_path} не найден")
            return {}

        # Проверяем размер файла
        if os.path.getsize(image_path) == 0:
            logger.error(f"Файл {image_path} пуст")
            return {}

        logger.info(f"Анализируем изображение: {image_path}")

        # Открываем изображение через PIL (устраняет проблемы с cv2)
        try:
            img = Image.open(image_path).convert("RGB")
        except Exception as e:
            logger.error(f"Ошибка при открытии изображения: {e}")
            return {}

        # Конвертируем в OpenCV для обработки
        try:
            img_cv = np.array(img)
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            logger.error(f"Ошибка при конвертации изображения: {e}")
            return {}

        # Используем pytesseract для распознавания текста
        try:
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        except Exception as e:
            logger.error(f"Ошибка при распознавании текста: {e}")
            return {}

        elements = {}
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if text:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                elements[text] = (x + w//2, y + h//2)

        logger.info(f"Найдено {len(elements)} элементов интерфейса")
        return elements

    except Exception as e:
        logger.error(f"Неожиданная ошибка при извлечении текста: {e}")
        return {}

def save_interface_cache(window_title: str, elements: Dict[str, Tuple[int, int]]):
    """
    Сохраняет данные интерфейса в JSON-файл для кэширования.
    """
    cache_path = os.path.join(CACHE_DIR, f"{window_title}.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(elements, f, ensure_ascii=False, indent=4)

def load_interface_cache(window_title: str) -> Optional[Dict[str, Tuple[int, int]]]:
    """
    Загружает данные интерфейса из кэша, если они существуют.
    """
    cache_path = os.path.join(CACHE_DIR, f"{window_title}.json")
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None





import string
import re

def normalize_text(text: str) -> str:
    """
    Убирает из текста кавычки, пунктуацию в начале/конце
    и приводит к нижнему регистру.
    """
    # Удаляем распространённые типы кавычек
    for ch in ["‘", "’", "“", "”", "'", "\"", "«", "»"]:
        text = text.replace(ch, "")

    # Можно убрать и всю пунктуацию, но аккуратно:
    # text = text.translate(str.maketrans('', '', string.punctuation))

    # Для точечной очистки от :, . в начале/конце можно использовать регулярку:
    text = text.strip(string.punctuation + " ")

    return text.lower()










def click_button(button_text: str) -> str:
    """
    Находит и нажимает кнопку с указанным текстом,
    каждый раз делая новый скриншот (без использования кэша).
    
    Args:
        button_text: Текст кнопки, которую нужно нажать
        
    Returns:
        Сообщение о результате операции
    """
    # Проверяем доступность необходимых библиотек
    if not all([CV_AVAILABLE, PYAUTOGUI_AVAILABLE, PYWINCTL_AVAILABLE]):
        logger.error("Не все необходимые библиотеки установлены для функции click_button")
        return "Не удалось выполнить операцию: отсутствуют необходимые библиотеки"
    
    try:
        from PIL import Image
    except ImportError:
        logger.error("Библиотека PIL не установлена")
        return "Не удалось выполнить операцию: отсутствует библиотека PIL"

    try:
        # Проверяем активное окно
        if not PYWINCTL_AVAILABLE:
            return "Не удалось определить активное окно: библиотека pywinctl не установлена"
            
        active_window = gw.getActiveWindow()
        if not active_window:
            logger.warning("Не удалось определить активное окно")
            return "Не удалось определить активное окно"

        # 1. Делаем скриншот активного окна
        screenshot_path = get_active_window_screenshot()
        if not screenshot_path:
            logger.error("Не удалось сделать скриншот окна")
            return "Ошибка: не удалось сделать скриншот окна"

        # 2. Открываем скриншот
        img = Image.open(screenshot_path)
        img_cv = np.array(img)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)

        # 3. С помощью pytesseract распознаём слова
        data = pytesseract.image_to_data(img_cv, lang="rus+eng", output_type=pytesseract.Output.DICT)
        elements = {}
        n_boxes = len(data['level'])
        for i in range(n_boxes):
            raw_word = data['text'][i].strip()
            if raw_word:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                cx, cy = x + w // 2, y + h // 2
                # Используем функцию normalize_text, чтобы убрать кавычки и т.д.
                norm_word = normalize_text(raw_word)
                if norm_word:
                    elements[norm_word] = (cx, cy)

        logger.info(f"Найденные (нормализованные) слова: {', '.join(elements.keys())}")

        # 4. Сопоставляем нужное слово
        search_key = normalize_text(button_text)
        if search_key in elements:
            x, y = elements[search_key]
            pyautogui.click(x, y)
            logger.info(f"Нажата кнопка '{button_text}' по координатам ({x}, {y})")
            return f"✅ Нажал кнопку '{button_text}'"
        
        # 5. Если точное совпадение не найдено, ищем частичное
        for key, (x, y) in elements.items():
            if search_key in key or key in search_key:
                pyautogui.click(x, y)
                logger.info(f"Нажата кнопка '{key}' (частичное совпадение с '{button_text}') по координатам ({x}, {y})")
                return f"✅ Нажал кнопку '{key}' (похожа на '{button_text}')"

        logger.warning(f"Кнопка '{button_text}' не найдена")
        return f"❌ Кнопка '{button_text}' не найдена. Убедитесь, что она видна на экране"
        
    except Exception as e:
        logger.error(f"Ошибка при нажатии кнопки: {e}")
        return f"Произошла ошибка при нажатии кнопки: {str(e)}"

