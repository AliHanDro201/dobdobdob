# integrations/browser_chat.py
import logging
import time
import os
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Импортируем модуль для улучшения промптов
from integrations.prompt_enhancer import enhance_prompt

# Настройка логирования
logger = logging.getLogger("browser_chat")

# URL для ChatGPT
CHATGPT_URL = "https://chat.openai.com/"

def create_chrome_driver(headless=False):
    """
    Создает и настраивает драйвер Chrome.
    
    Args:
        headless: Запускать ли браузер в фоновом режиме
        
    Returns:
        Настроенный экземпляр webdriver.Chrome
    """
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    
    # Добавляем аргументы для поддержки аудио и видео
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    
    # Отключаем уведомления
    chrome_options.add_argument("--disable-notifications")
    
    # Устанавливаем User-Agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        # Пытаемся использовать существующую сессию Chrome
        chrome_options.debugger_address = "127.0.0.1:9222"
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Успешно подключились к существующей сессии Chrome")
        return driver
    except Exception as e:
        logger.warning(f"Не удалось подключиться к существующей сессии Chrome: {e}")
        
        # Если не удалось подключиться к существующей сессии, создаем новую
        try:
            driver = webdriver.Chrome(options=chrome_options)
            logger.info("Создан новый экземпляр Chrome")
            return driver
        except Exception as e:
            logger.error(f"Не удалось создать экземпляр Chrome: {e}")
            raise

def wait_for_chatgpt_ready(driver, timeout=30):
    """
    Ожидает, пока ChatGPT будет готов к вводу запроса.
    
    Args:
        driver: Экземпляр webdriver
        timeout: Время ожидания в секундах
        
    Returns:
        Элемент ввода или None, если не удалось найти
    """
    wait = WebDriverWait(driver, timeout)
    
    try:
        # Пытаемся найти поле ввода
        input_selectors = [
            "textarea[placeholder='Message ChatGPT…']",
            "textarea[placeholder='Send a message']",
            "div#prompt-textarea[contenteditable='true']",
            "div.ProseMirror[contenteditable='true']"
        ]
        
        for selector in input_selectors:
            try:
                input_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                logger.info(f"Найден элемент ввода с селектором: {selector}")
                return input_element
            except TimeoutException:
                logger.debug(f"Не найден элемент с селектором: {selector}")
                continue
        
        # Если не нашли по селекторам, пробуем найти по XPath
        try:
            input_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//textarea[contains(@placeholder, 'Message') or contains(@placeholder, 'Send')]")))
            logger.info("Найден элемент ввода по XPath")
            return input_element
        except TimeoutException:
            logger.debug("Не найден элемент ввода по XPath")
        
        # Если все еще не нашли, проверяем, есть ли кнопка "New chat"
        try:
            new_chat_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'New chat')]")))
            logger.info("Найдена кнопка 'New chat', кликаем по ней")
            new_chat_button.click()
            time.sleep(2)
            
            # Пробуем снова найти поле ввода
            for selector in input_selectors:
                try:
                    input_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    logger.info(f"Найден элемент ввода после клика на 'New chat': {selector}")
                    return input_element
                except TimeoutException:
                    continue
        except TimeoutException:
            logger.debug("Не найдена кнопка 'New chat'")
        
        logger.error("Не удалось найти элемент ввода на странице ChatGPT")
        return None
    except Exception as e:
        logger.error(f"Ошибка при ожидании готовности ChatGPT: {e}")
        return None

def send_query_to_chatgpt(query: str, enhance=True, headless=False, timeout=60) -> str:
    """
    Отправляет запрос в ChatGPT через браузер и возвращает ответ.
    
    Args:
        query: Запрос пользователя
        enhance: Улучшать ли запрос с помощью prompt_enhancer
        headless: Запускать ли браузер в фоновом режиме
        timeout: Максимальное время ожидания ответа в секундах
        
    Returns:
        Ответ от ChatGPT или сообщение об ошибке
    """
    # Улучшаем запрос, если требуется
    if enhance:
        enhanced_query = enhance_prompt(query)
        logger.info(f"Улучшенный запрос: {enhanced_query[:100]}...")
    else:
        enhanced_query = query
        logger.info(f"Запрос без улучшения: {enhanced_query[:100]}...")
    
    driver = None
    try:
        # Создаем драйвер Chrome
        driver = create_chrome_driver(headless=headless)
        
        # Открываем ChatGPT
        logger.info(f"Открываем {CHATGPT_URL}")
        driver.get(CHATGPT_URL)
        
        # Ждем, пока страница загрузится и будет готова к вводу
        input_element = wait_for_chatgpt_ready(driver, timeout=30)
        if not input_element:
            return "Ошибка: Не удалось найти поле ввода на странице ChatGPT"
        
        # Прокручиваем к элементу ввода
        driver.execute_script("arguments[0].scrollIntoView(true);", input_element)
        time.sleep(1)
        
        # Очищаем поле ввода
        input_element.clear()
        
        # Фокусируемся на поле ввода и вводим запрос
        input_element.click()
        input_element.send_keys(enhanced_query)
        logger.info("Запрос введен в поле ввода")
        
        # Отправляем запрос (Enter)
        input_element.send_keys(Keys.RETURN)
        logger.info("Запрос отправлен, ожидаем ответа...")
        
        # Ждем, пока появится ответ
        wait = WebDriverWait(driver, timeout)
        
        # Ожидаем, пока исчезнет индикатор загрузки или появится ответ
        try:
            # Сначала проверяем наличие индикатора загрузки
            loading_indicators = [
                "div.result-streaming",
                "div.result-thinking",
                "div.animate-pulse",
                "button.stop-generating"
            ]
            
            for indicator in loading_indicators:
                try:
                    loading_element = driver.find_element(By.CSS_SELECTOR, indicator)
                    logger.info(f"Найден индикатор загрузки: {indicator}")
                    
                    # Ждем, пока индикатор загрузки исчезнет
                    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, indicator)))
                    logger.info("Индикатор загрузки исчез, ответ готов")
                    break
                except NoSuchElementException:
                    continue
            
            # Даем дополнительное время для полной загрузки ответа
            time.sleep(2)
        except TimeoutException:
            logger.warning("Тайм-аут при ожидании исчезновения индикатора загрузки")
        
        # Пытаемся найти ответ
        response_selectors = [
            "div.markdown",
            "div.prose",
            "div.chat-message-content",
            "div.message-body",
            "div.text-message__content"
        ]
        
        response_text = None
        for selector in response_selectors:
            try:
                # Находим все элементы с ответами
                response_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if response_elements:
                    # Берем последний элемент (самый новый ответ)
                    response_text = response_elements[-1].text
                    logger.info(f"Найден ответ с селектором: {selector}")
                    break
            except Exception as e:
                logger.debug(f"Не удалось найти ответ с селектором {selector}: {e}")
                continue
        
        if not response_text:
            # Если не нашли по селекторам, пробуем найти по XPath
            try:
                # Находим все сообщения
                messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'message') or contains(@class, 'chat-message')]")
                if messages:
                    # Берем последнее сообщение (самый новый ответ)
                    response_text = messages[-1].text
                    logger.info("Найден ответ по XPath")
            except Exception as e:
                logger.debug(f"Не удалось найти ответ по XPath: {e}")
        
        if response_text:
            logger.info(f"Получен ответ длиной {len(response_text)} символов")
            return response_text
        else:
            logger.error("Не удалось найти ответ на странице")
            return "Ошибка: Не удалось найти ответ на странице ChatGPT"
    except Exception as e:
        error_msg = f"Ошибка при взаимодействии с ChatGPT: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return f"Ошибка: {error_msg}"
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Браузер закрыт")
            except Exception as e:
                logger.error(f"Ошибка при закрытии браузера: {e}")

# Пример использования
if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Тестовый запрос
    result = send_query_to_chatgpt("Расскажи о Казахстане", enhance=True, headless=False)
    print("\nОтвет от ChatGPT:")
    print(result)
