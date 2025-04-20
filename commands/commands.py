"""
These commands are functions that ChatGPT will use 
if the user requests it. 

So far the user can ask ChatGPT to:
- Open or close an application
- Interact with their spotify by:
    - Playing an album, playlist, or song.
"""

# ************************************************
# * Utilities
# Условный импорт AppOpener (только для Windows)
try:
    import AppOpener
except ImportError:
    AppOpener = None

from dotenv import load_dotenv
import psutil
import webbrowser
import traceback
import requests
import os
import re
import time
import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("assistant.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("commands")

# Импортируем заглушки для GUI-зависимых библиотек
import os
import sys

# Проверяем наличие графического интерфейса
has_display = "DISPLAY" in os.environ and os.environ["DISPLAY"]

# Условные импорты для кроссплатформенности
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

if has_display:
    try:
        from helium import *
        HELIUM_AVAILABLE = True
    except ImportError:
        logger.warning("helium не установлен")
        HELIUM_AVAILABLE = False
else:
    logger.warning("Нет доступа к графическому интерфейсу, helium не будет доступен")
    HELIUM_AVAILABLE = False

try:
    import pytesseract
    import cv2
    import numpy as np
    CV_AVAILABLE = True
except ImportError:
    logger.warning("pytesseract, cv2 или numpy не установлены")
    pytesseract = None
    cv2 = None
    np = None
    CV_AVAILABLE = False

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    logger.warning("pyperclip не установлен")
    pyperclip = None
    PYPERCLIP_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    logger.warning("selenium не установлен")
    SELENIUM_AVAILABLE = False

if has_display:
    try:
        import keyboard
        KEYBOARD_AVAILABLE = True
    except ImportError:
        logger.warning("keyboard не установлен")
        from utils.mock_modules import mock_keyboard as keyboard
        KEYBOARD_AVAILABLE = False
else:
    logger.warning("Нет доступа к графическому интерфейсу, используем заглушку keyboard")
    from utils.mock_modules import mock_keyboard as keyboard
    KEYBOARD_AVAILABLE = False

from utils.tts import stop_audio

# Загрузка переменных окружения
try:
    load_dotenv(dotenv_path='.evn')
    logger.info("Переменные окружения загружены из .evn")
except Exception as e:
    logger.warning(f"Ошибка при загрузке .evn: {e}")
    try:
        load_dotenv(dotenv_path='.env')
        logger.info("Переменные окружения загружены из .env")
    except Exception as e:
        logger.error(f"Ошибка при загрузке .env: {e}")

NEWS_API_KEY = os.getenv("NEWS_API_KEY") 
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


def get_news() -> str:
    """
    Получает последние новости.

    Returns:
    - str: Топ-3 новости.
    """
    if not NEWS_API_KEY:
        return "API ключ для новостей не найден."
    
    url = f"https://newsapi.org/v2/top-headlines?country=ru&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    
    if "articles" not in response:
        return "Ошибка при получении новостей."
    
    news_list = [f"{idx+1}. {article['title']}" for idx, article in enumerate(response["articles"][:3])]
    return "\n".join(news_list)



def get_weather(city: str) -> str:
    """
    Получает текущую погоду из WeatherAPI.

    Parameters:
    - city : str
        - Название города.

    Returns:
    - str: Погода.
    """
    if not WEATHER_API_KEY:
        return "API ключ для погоды не найден."

    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&lang=ru"
    
    try:
        response = requests.get(url).json()
        
        if "error" in response:
            return "Ошибка: " + response["error"]["message"]

        location = response["location"]["name"]
        country = response["location"]["country"]
        condition = response["current"]["condition"]["text"]
        temp_c = response["current"]["temp_c"]
        feels_like = response["current"]["feelslike_c"]
        wind_kph = response["current"]["wind_kph"]
        humidity = response["current"]["humidity"]

        return (f"Погода в {location}, {country}: {condition}, {temp_c}°по цельсю.\n"
                f"Ощущается как {feels_like}°по цельсю. Ветер {wind_kph} километров в час, влажность {humidity}%.")
    
    except Exception as e:
        return f"Ошибка при получении погоды: {str(e)}"

# ************************************************


# * Utility functions
def is_open(app_name: str, include_exe: bool = False) -> bool:
    """
    Confirms if an application is open or not.
    
    Parameters:
    - include_exe : bool (optional)
        - Determines if .exe should be included in the application 
          name to search for.
    Returns:

    """

    if include_exe:
        app_name = str.strip(app_name) + ".exe"


    opened = False
    for i in psutil.process_iter():
        if str.lower(app_name) in str.lower(i.name()):
            opened = True
            break
    
    return opened

# *********************************
# * Commands

# * Open an app
def open_app(name: str) -> str:
    """
    Открывает приложение на компьютере пользователя.

    Parameters:
    - name : str
        - Название приложения
        
    Returns:
    - str: Сообщение о результате операции
    """
    logger.info(f"Попытка открыть приложение: {name}")
    
    # Проверяем, установлен ли AppOpener
    if AppOpener is None:
        # Кроссплатформенная альтернатива
        try:
            if sys.platform == "win32":
                # Windows
                os.startfile(name)
            elif sys.platform == "darwin":
                # macOS
                os.system(f"open {name}")
            else:
                # Linux
                os.system(f"xdg-open {name}")
            
            logger.info(f"Приложение {name} успешно открыто")
            return f"Приложение {name} успешно открыто"
        except Exception as e:
            error = str(e)
            logger.error(f"Ошибка при открытии приложения: {error}")
            return f"Не удалось открыть приложение {name}: {error}"
    else:
        # Используем AppOpener, если доступен
        try:
            logger.info("Используем AppOpener для открытия приложения")
            AppOpener.open(name, match_closest=True, throw_error=True, output=False)
            logger.info(f"Приложение {name} успешно открыто через AppOpener")
            return f"Приложение {name} успешно открыто"
        except Exception as e:
            error = str(e)
            logger.error(f"Ошибка при открытии приложения через AppOpener: {error}")
            return f"Не удалось открыть приложение {name}: {error}"

# * Close an app
def close_app(name: str) -> str:
    """
    Закрывает приложение на компьютере пользователя.

    Parameters:
    - name : str
        - Название приложения
        
    Returns:
    - str: Сообщение о результате операции
    """
    logger.info(f"Попытка закрыть приложение: {name}")
    
    # Проверяем, установлен ли AppOpener
    if AppOpener is None:
        # Кроссплатформенная альтернатива
        try:
            # Ищем процесс по имени
            for proc in psutil.process_iter(['pid', 'name']):
                if name.lower() in proc.info['name'].lower():
                    proc.kill()
                    logger.info(f"Процесс {proc.info['name']} (PID: {proc.info['pid']}) завершен")
                    return f"Приложение {name} успешно закрыто"
            
            logger.warning(f"Процесс {name} не найден")
            return f"Приложение {name} не найдено в списке запущенных процессов"
        except Exception as e:
            error = str(e)
            logger.error(f"Ошибка при закрытии приложения: {error}")
            return f"Не удалось закрыть приложение {name}: {error}"
    else:
        # Используем AppOpener, если доступен
        try:
            logger.info("Используем AppOpener для закрытия приложения")
            AppOpener.close(name, match_closest=True, throw_error=True, output=False)
            logger.info(f"Приложение {name} успешно закрыто через AppOpener")
            return f"Приложение {name} успешно закрыто"
        except Exception as e:
            error = str(e)
            logger.error(f"Ошибка при закрытии приложения через AppOpener: {error}")
            return f"Не удалось закрыть приложение {name}: {error}"


# * Команды для работы с веб-браузером

def search_web(query: str) -> str:
    """
    Открывает браузер и выполняет поиск информации в Google.

    Parameters:
    - query : str
        - Запрос для поиска.

    Returns:
    - str: Сообщение о выполнении поиска.
    """
    """
    Если запрос совпадает с известным сайтом — открывает его напрямую.
    """
    websites = {
        "YouTube": "https://www.youtube.com",
        "Википедия": "https://ru.wikipedia.org",
        "Google": "https://www.google.com",
        "Новости": "https://news.google.com",
        "е-кызмет":"https://eqyzmet.gov.kz/#/main/start"
    }

    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)
    return f"Ищу информацию по запросу: {query}"




def sleep() -> None:
    """
    This function will be passed to ChatGPT. This function will help
    determine if user input should continue to be processed or not.
    """
    return ""




    
def open_ekyzmet():
    """
    Открывает сайт e-Кызмет и автоматически нажимает кнопку 'Вход/Регистрация' с помощью Helium.
    """
    try:
        # Открываем браузер
        browser = start_chrome("https://eqyzmet.gov.kz/#/main/start", headless=False)
        
        # Ожидаем загрузки страницы
        time.sleep(5)
        
        # Находим и нажимаем кнопку 'Вход/Регистрация'
        click("Вход/Регистрация")
        time.sleep(2)
        
        print("Кнопка 'Вход/Регистрация' успешно нажата.")
        return "Сайт e-Кызмет открыт, вход выполнен."

    except Exception as e:
        return f"Ошибка при открытии e-Кызмет: {str(e)}"


def go_back():
    """Возвращает пользователя на предыдущую страницу в браузере."""
    pyautogui.hotkey("alt", "left")  # Работает в любом браузере
    return "Перехожу назад."

def go_forward():
    """Перемещает пользователя вперёд в истории браузера."""
    pyautogui.hotkey("alt", "right")
    return "Перехожу вперёд."

def scroll_up():
    """Прокручивает страницу вверх на 1 экран."""
    pyautogui.press("pageup")
    return "Прокручиваю вверх."

def scroll_down():
    """Прокручивает страницу вниз на 1 экран."""
    pyautogui.press("pagedown")
    return "Прокручиваю вниз."



from .window_manager import click_button
#def click_button(button_text: str):
#    """Нажимает кнопку с указанным текстом в браузере."""
#    pyautogui.press("tab")  # Переключение между элементами
#    pyautogui.press("enter")  # Подтверждение
#    return f"Нажимаю кнопку: {button_text}"



def open_website(url: str):
    """Открывает указанный сайт в браузере."""
    webbrowser.open(url)
    return f"Открываю сайт: {url}"

# Глобальные команды
if keyboard is not None:
    try:
        keyboard.add_hotkey("caps lock", stop_audio)  # Останавливает озвучку даже в свернутом режиме
        logger.info("Горячая клавиша Caps Lock для остановки аудио активирована")
    except Exception as e:
        logger.error(f"Не удалось активировать горячую клавишу Caps Lock: {e}")



































def get_active_tab_index() -> int:
    """
    Определяет текущую активную вкладку по ее позиции.
    Работает с Chrome, Edge и Firefox.
    """
    for i in range(1, 10):  # Проверяем вкладки 1-9
        pyautogui.hotkey('ctrl', str(i))
        time.sleep(0.1)  # Даем браузеру время переключиться
        active_window = pyautogui.getActiveWindowTitle()  # Получаем заголовок активного окна
        if active_window:
            return i
    return 1  # Если не удалось определить, считаем, что активна 1-я вкладка


def switch_tab_by_number(tab_number: int):
    """
    Переключается на вкладку по её номеру (в том числе если вкладок больше 9).
    """
    if tab_number < 1:
        return "❌ Введите корректный номер вкладки (1 или выше)."

    current_tab = get_active_tab_index()  # Определяем текущую вкладку

    if tab_number == current_tab:
        return f"✅ Уже на вкладке №{tab_number}."

    if tab_number <= 9:
        # Если вкладка в пределах 1-9, переключаемся напрямую
        pyautogui.hotkey('ctrl', str(tab_number))
    elif tab_number > current_tab:
        # Если вкладка справа, переключаемся вперёд
        steps = tab_number - current_tab
        for _ in range(steps):
            pyautogui.hotkey('ctrl', 'tab')
            time.sleep(0.2)
    else:
        # Если вкладка слева, переключаемся назад
        steps = current_tab - tab_number
        for _ in range(steps):
            pyautogui.hotkey('ctrl', 'shift', 'tab')
            time.sleep(0.2)

    return f"🔀 Переключаюсь на вкладку №{tab_number}."




def refresh_page():
    """Обновляет текущую страницу в браузере."""
    
    pyautogui.hotkey("ctrl", "r")  # ✅ Горячая клавиша для обновления страницы
    time.sleep(0.5)  # ⏳ Небольшая задержка, чтобы обновление произошло
    return "🔄 Страница обновлена."

def clear_cache():
    """Очищает кэш данной страницы и обновляет её."""
    
    pyautogui.hotkey("ctrl", "shift", "r")  # ✅ Горячая клавиша для обновления с очисткой кэша
    time.sleep(0.5)  # ⏳ Небольшая задержка для выполнения команды
    return "🧹 Кэш страницы очищен и обновлён."

def clear_cache_and_cookies():
    """Очищает cookies, local storage и кэш, затем обновляет страницу."""
    
    # ✅ Открываем DevTools
    pyautogui.hotkey("ctrl", "shift", "i")
    time.sleep(1)

    # ✅ Открываем панель "Приложение"
    pyautogui.hotkey("ctrl", "shift", "p")
    time.sleep(0.5)
    pyautogui.write("Clear site data")  # ✅ Вводим команду очистки
    time.sleep(0.5)
    pyautogui.press("enter")  # ✅ Подтверждаем очистку

    time.sleep(1)  # ⏳ Ожидание завершения очистки

    # ✅ Закрываем DevTools
    pyautogui.hotkey("ctrl", "shift", "i")

    return "🧹 Кэш, cookies и local storage очищены, страница обновлена!"





def play_pause_media():
    """Ставит на паузу любое воспроизведение медиа в системе."""
    pyautogui.press("playpause")  # Работает с YouTube, Spotify, VLC
    return "Понял!"










