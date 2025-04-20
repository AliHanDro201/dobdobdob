"""
Модуль с заглушками для библиотек, которые требуют графический интерфейс.
Используется для тестирования в средах без GUI.
"""

import logging

logger = logging.getLogger("mock_modules")

class MockPyAutoGUI:
    """Заглушка для PyAutoGUI"""
    
    def __init__(self):
        logger.info("Инициализирована заглушка PyAutoGUI")
    
    def click(self, x=None, y=None, clicks=1, interval=0.0, button='left', duration=0.0, tween=None):
        logger.info(f"Имитация клика мыши: x={x}, y={y}, button={button}")
        return None
    
    def rightClick(self, x=None, y=None, duration=0.0, tween=None):
        logger.info(f"Имитация правого клика мыши: x={x}, y={y}")
        return None
    
    def doubleClick(self, x=None, y=None, interval=0.0, button='left', duration=0.0, tween=None):
        logger.info(f"Имитация двойного клика мыши: x={x}, y={y}, button={button}")
        return None
    
    def moveTo(self, x=None, y=None, duration=0.0, tween=None):
        logger.info(f"Имитация перемещения мыши: x={x}, y={y}")
        return None
    
    def moveRel(self, xOffset=0, yOffset=0, duration=0.0, tween=None):
        logger.info(f"Имитация относительного перемещения мыши: xOffset={xOffset}, yOffset={yOffset}")
        return None
    
    def dragTo(self, x, y, duration=0.0, button='left', tween=None):
        logger.info(f"Имитация перетаскивания мыши: x={x}, y={y}, button={button}")
        return None
    
    def dragRel(self, xOffset, yOffset, duration=0.0, button='left', tween=None):
        logger.info(f"Имитация относительного перетаскивания мыши: xOffset={xOffset}, yOffset={yOffset}, button={button}")
        return None
    
    def scroll(self, clicks, x=None, y=None):
        logger.info(f"Имитация прокрутки: clicks={clicks}, x={x}, y={y}")
        return None
    
    def hscroll(self, clicks, x=None, y=None):
        logger.info(f"Имитация горизонтальной прокрутки: clicks={clicks}, x={x}, y={y}")
        return None
    
    def vscroll(self, clicks, x=None, y=None):
        logger.info(f"Имитация вертикальной прокрутки: clicks={clicks}, x={x}, y={y}")
        return None
    
    def press(self, keys, presses=1, interval=0.0):
        logger.info(f"Имитация нажатия клавиш: keys={keys}, presses={presses}")
        return None
    
    def keyDown(self, key):
        logger.info(f"Имитация нажатия клавиши: key={key}")
        return None
    
    def keyUp(self, key):
        logger.info(f"Имитация отпускания клавиши: key={key}")
        return None
    
    def typewrite(self, message, interval=0.0):
        logger.info(f"Имитация ввода текста: message={message}")
        return None
    
    def write(self, message, interval=0.0):
        logger.info(f"Имитация ввода текста: message={message}")
        return None
    
    def hotkey(self, *args, **kwargs):
        logger.info(f"Имитация нажатия горячих клавиш: args={args}, kwargs={kwargs}")
        return None
    
    def screenshot(self, region=None):
        from PIL import Image
        import numpy as np
        
        logger.info(f"Имитация скриншота: region={region}")
        
        # Создаем пустое изображение 100x100 пикселей
        width, height = 100, 100
        if region:
            left, top, width, height = region
        
        # Создаем черное изображение
        img = Image.new('RGB', (width, height), color='black')
        return img
    
    def locateOnScreen(self, image, **kwargs):
        logger.info(f"Имитация поиска изображения на экране: image={image}")
        return None
    
    def locateCenterOnScreen(self, image, **kwargs):
        logger.info(f"Имитация поиска центра изображения на экране: image={image}")
        return None
    
    def getActiveWindowTitle(self):
        logger.info("Имитация получения заголовка активного окна")
        return "Mock Window Title"

class MockKeyboard:
    """Заглушка для keyboard"""
    
    def __init__(self):
        logger.info("Инициализирована заглушка keyboard")
        self._hotkeys = {}
    
    def add_hotkey(self, hotkey, callback, args=(), suppress=False, timeout=1, trigger_on_release=False):
        logger.info(f"Имитация добавления горячей клавиши: hotkey={hotkey}")
        self._hotkeys[hotkey] = callback
        return lambda: None
    
    def remove_hotkey(self, hotkey_or_callback):
        logger.info(f"Имитация удаления горячей клавиши: hotkey_or_callback={hotkey_or_callback}")
        return None
    
    def is_pressed(self, key):
        logger.info(f"Имитация проверки нажатия клавиши: key={key}")
        return False
    
    def press(self, key):
        logger.info(f"Имитация нажатия клавиши: key={key}")
        return None
    
    def release(self, key):
        logger.info(f"Имитация отпускания клавиши: key={key}")
        return None
    
    def write(self, text, delay=0.0):
        logger.info(f"Имитация ввода текста: text={text}")
        return None

class MockHelium:
    """Заглушка для Helium"""
    
    def __init__(self):
        logger.info("Инициализирована заглушка Helium")
    
    def start_chrome(self, url=None, headless=False):
        logger.info(f"Имитация запуска Chrome: url={url}, headless={headless}")
        return None
    
    def go_to(self, url):
        logger.info(f"Имитация перехода по URL: url={url}")
        return None
    
    def click(self, element):
        logger.info(f"Имитация клика по элементу: element={element}")
        return None
    
    def write(self, text, into=None):
        logger.info(f"Имитация ввода текста: text={text}, into={into}")
        return None
    
    def press(self, key):
        logger.info(f"Имитация нажатия клавиши: key={key}")
        return None
    
    def wait_until(self, condition, timeout_secs=10):
        logger.info(f"Имитация ожидания условия: timeout_secs={timeout_secs}")
        return True
    
    def find_all(self, element_type):
        logger.info(f"Имитация поиска всех элементов: element_type={element_type}")
        return []
    
    def scroll_down(self, num_pixels=100):
        logger.info(f"Имитация прокрутки вниз: num_pixels={num_pixels}")
        return None
    
    def scroll_up(self, num_pixels=100):
        logger.info(f"Имитация прокрутки вверх: num_pixels={num_pixels}")
        return None

class MockPygame:
    """Заглушка для pygame.mixer"""
    
    class MockMixer:
        """Заглушка для pygame.mixer"""
        
        def __init__(self):
            logger.info("Инициализирована заглушка pygame.mixer")
            self.music = self.MockMusic()
            self.Sound = self.MockSound
        
        def init(self, *args, **kwargs):
            logger.info(f"Имитация инициализации pygame.mixer: args={args}, kwargs={kwargs}")
            return 1
            
        def quit(self):
            logger.info("Имитация завершения pygame.mixer")
            return None
            
        def get_init(self):
            logger.info("Имитация проверки инициализации pygame.mixer")
            return True
            
        def stop(self):
            logger.info("Имитация остановки всех звуков")
            return None
            
        class MockMusic:
            """Заглушка для pygame.mixer.music"""
            
            def __init__(self):
                logger.info("Инициализирована заглушка pygame.mixer.music")
                self._playing = False
                self._paused = False
                
            def load(self, filename, *args, **kwargs):
                logger.info(f"Имитация загрузки музыки: filename={filename}")
                return None
                
            def play(self, loops=0, start=0.0, fade_ms=0):
                logger.info(f"Имитация воспроизведения музыки: loops={loops}, start={start}, fade_ms={fade_ms}")
                self._playing = True
                self._paused = False
                return None
                
            def stop(self):
                logger.info("Имитация остановки музыки")
                self._playing = False
                self._paused = False
                return None
                
            def pause(self):
                logger.info("Имитация паузы музыки")
                self._paused = True
                return None
                
            def unpause(self):
                logger.info("Имитация снятия с паузы музыки")
                self._paused = False
                return None
                
            def fadeout(self, time):
                logger.info(f"Имитация затухания музыки: time={time}")
                self._playing = False
                return None
                
            def set_volume(self, volume):
                logger.info(f"Имитация установки громкости музыки: volume={volume}")
                return None
                
            def get_volume(self):
                logger.info("Имитация получения громкости музыки")
                return 1.0
                
            def get_busy(self):
                logger.info("Имитация проверки воспроизведения музыки")
                return self._playing and not self._paused
                
            def set_pos(self, pos):
                logger.info(f"Имитация установки позиции музыки: pos={pos}")
                return None
                
            def get_pos(self):
                logger.info("Имитация получения позиции музыки")
                return 0
                
        class MockSound:
            """Заглушка для pygame.mixer.Sound"""
            
            def __init__(self, file=None, buffer=None):
                logger.info(f"Инициализирована заглушка pygame.mixer.Sound: file={file}")
                self._playing = False
                
            def play(self, loops=0, maxtime=0, fade_ms=0):
                logger.info(f"Имитация воспроизведения звука: loops={loops}, maxtime={maxtime}, fade_ms={fade_ms}")
                self._playing = True
                return self.MockChannel()
                
            def stop(self):
                logger.info("Имитация остановки звука")
                self._playing = False
                return None
                
            def fadeout(self, time):
                logger.info(f"Имитация затухания звука: time={time}")
                self._playing = False
                return None
                
            def set_volume(self, volume):
                logger.info(f"Имитация установки громкости звука: volume={volume}")
                return None
                
            def get_volume(self):
                logger.info("Имитация получения громкости звука")
                return 1.0
                
            def get_length(self):
                logger.info("Имитация получения длительности звука")
                return 1.0
                
            def get_num_channels(self):
                logger.info("Имитация получения количества каналов звука")
                return 1
                
            class MockChannel:
                """Заглушка для pygame.mixer.Channel"""
                
                def __init__(self):
                    logger.info("Инициализирована заглушка pygame.mixer.Channel")
                    self._playing = True
                    
                def play(self, sound, loops=0, maxtime=0, fade_ms=0):
                    logger.info(f"Имитация воспроизведения звука на канале: loops={loops}, maxtime={maxtime}, fade_ms={fade_ms}")
                    self._playing = True
                    return None
                    
                def stop(self):
                    logger.info("Имитация остановки звука на канале")
                    self._playing = False
                    return None
                    
                def pause(self):
                    logger.info("Имитация паузы звука на канале")
                    return None
                    
                def unpause(self):
                    logger.info("Имитация снятия с паузы звука на канале")
                    return None
                    
                def fadeout(self, time):
                    logger.info(f"Имитация затухания звука на канале: time={time}")
                    self._playing = False
                    return None
                    
                def set_volume(self, volume):
                    logger.info(f"Имитация установки громкости звука на канале: volume={volume}")
                    return None
                    
                def get_volume(self):
                    logger.info("Имитация получения громкости звука на канале")
                    return 1.0
                    
                def get_busy(self):
                    logger.info("Имитация проверки воспроизведения звука на канале")
                    return self._playing

class MockSoundDevice:
    """Заглушка для sounddevice"""
    
    def __init__(self):
        logger.info("Инициализирована заглушка sounddevice")
    
    def rec(self, frames, samplerate=44100, channels=1, dtype='float32', **kwargs):
        """Имитация записи аудио"""
        logger.info(f"Имитация записи аудио: frames={frames}, samplerate={samplerate}, channels={channels}")
        import numpy as np
        # Создаем массив с тишиной
        return np.zeros((frames, channels), dtype=dtype)
    
    def wait(self):
        """Имитация ожидания окончания записи"""
        logger.info("Имитация ожидания окончания записи")
        return None
    
    def play(self, data, samplerate=44100, **kwargs):
        """Имитация воспроизведения аудио"""
        logger.info(f"Имитация воспроизведения аудио: samplerate={samplerate}")
        return None
    
    def stop(self):
        """Имитация остановки воспроизведения/записи"""
        logger.info("Имитация остановки воспроизведения/записи")
        return None
    
    def get_status(self):
        """Имитация получения статуса"""
        logger.info("Имитация получения статуса sounddevice")
        return {'input': False, 'output': False, 'hostapi': 0, 'device': 0}
    
    def query_devices(self, device=None, kind=None):
        """Имитация запроса устройств"""
        logger.info(f"Имитация запроса устройств: device={device}, kind={kind}")
        return {'name': 'Mock Audio Device', 'hostapi': 0, 'max_input_channels': 2, 'max_output_channels': 2, 
                'default_samplerate': 44100, 'default_low_input_latency': 0.01, 'default_low_output_latency': 0.01,
                'default_high_input_latency': 0.1, 'default_high_output_latency': 0.1}

class MockSoundFile:
    """Заглушка для soundfile"""
    
    def __init__(self):
        logger.info("Инициализирована заглушка soundfile")
    
    def write(self, file, data, samplerate, **kwargs):
        """Имитация записи аудио в файл"""
        logger.info(f"Имитация записи аудио в файл: file={file}, samplerate={samplerate}")
        # Создаем пустой файл
        with open(file, 'wb') as f:
            f.write(b'\x00' * 44)  # Минимальный заголовок WAV
        return None
    
    def read(self, file, **kwargs):
        """Имитация чтения аудио из файла"""
        logger.info(f"Имитация чтения аудио из файла: file={file}")
        import numpy as np
        # Возвращаем пустой массив и частоту дискретизации
        return np.zeros((1000, 1), dtype='float32'), 44100

class MockCV2:
    """Заглушка для OpenCV (cv2)."""
    
    IMREAD_COLOR = 1
    COLOR_RGB2BGR = 4
    COLOR_BGR2RGB = 4
    COLOR_BGR2GRAY = 6
    THRESH_BINARY_INV = 1
    TM_CCOEFF_NORMED = 5
    
    @staticmethod
    def imread(path, flags=None):
        """Имитация чтения изображения."""
        logger.info(f"Имитация чтения изображения: {path}")
        # Возвращаем пустое изображение 100x100
        import numpy as np
        return np.zeros((100, 100, 3), dtype=np.uint8)
    
    @staticmethod
    def imwrite(path, img):
        """Имитация записи изображения."""
        logger.info(f"Имитация записи изображения: {path}")
        # Создаем пустой файл
        with open(path, 'wb') as f:
            f.write(b'MOCK_IMAGE_DATA')
        return True
    
    @staticmethod
    def cvtColor(img, code):
        """Имитация конвертации цветового пространства."""
        logger.info(f"Имитация конвертации цветового пространства: {code}")
        return img
    
    @staticmethod
    def threshold(img, thresh, maxval, type):
        """Имитация пороговой обработки."""
        logger.info(f"Имитация пороговой обработки: thresh={thresh}, maxval={maxval}, type={type}")
        return True, img
    
    @staticmethod
    def matchTemplate(img, template, method):
        """Имитация сопоставления шаблона."""
        logger.info(f"Имитация сопоставления шаблона: method={method}")
        # Возвращаем массив с одним совпадением
        import numpy as np
        result = np.zeros((img.shape[0] - template.shape[0] + 1, img.shape[1] - template.shape[1] + 1))
        result[10, 10] = 0.9  # Имитация совпадения
        return result

class MockPyTesseract:
    """Заглушка для pytesseract."""
    
    class Output:
        DICT = 'dict'
    
    @staticmethod
    def image_to_string(img, lang=None):
        """Имитация распознавания текста."""
        logger.info(f"Имитация распознавания текста: lang={lang}")
        return "Пример текста на экране (заглушка OCR)"
    
    @staticmethod
    def image_to_data(img, output_type=None, lang=None):
        """Имитация распознавания данных."""
        logger.info(f"Имитация распознавания данных: output_type={output_type}, lang={lang}")
        # Возвращаем словарь с данными
        return {
            'text': ['Пример', 'текста', 'на', 'экране'],
            'conf': [90, 85, 95, 80],
            'left': [10, 100, 200, 300],
            'top': [10, 10, 10, 10],
            'width': [80, 80, 80, 80],
            'height': [30, 30, 30, 30]
        }

# Создаем экземпляры заглушек
mock_pyautogui = MockPyAutoGUI()
mock_keyboard = MockKeyboard()
mock_helium = MockHelium()
mock_pygame = MockPygame()
mock_pygame_mixer = mock_pygame.MockMixer()
mock_sounddevice = MockSoundDevice()
mock_soundfile = MockSoundFile()
mock_cv2 = MockCV2()
mock_pytesseract = MockPyTesseract()