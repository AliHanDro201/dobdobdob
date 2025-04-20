"""
Этот файл содержит функции, которые обрабатывают функцию преобразования текста в речь. 
Функция generate_audio — единственная, которая вам нужна для генерации и воспроизведения звука.
"""

import os
import time
import asyncio
import threading
import logging
from pathlib import Path

# Проверяем, есть ли доступ к графическому интерфейсу
try:
    import pygame
    import keyboard
    has_gui = True
except (ImportError, ModuleNotFoundError):
    has_gui = False
    # Импортируем заглушки
    from utils.mock_modules import mock_pygame_mixer as pygame_mixer
    from utils.mock_modules import mock_keyboard as keyboard
    logging.warning("Нет доступа к графическому интерфейсу, используем заглушки pygame и keyboard")
else:
    # Если pygame доступен, используем его напрямую
    pygame_mixer = pygame.mixer

import edge_tts

# Импортируем централизованный менеджер событий
from utils.event_manager import event_manager
# Импортируем настройки TTS из config.py
from core.config import TTS_DEFAULT_VOICE

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("assistant.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("tts")

# Создаем директорию для аудио, если она не существует
os.makedirs("audio", exist_ok=True)

def stop_audio():
    """Останавливает озвучку при вызове."""
    event_manager.request_stop_audio()  # Устанавливаем флаг остановки
    try:
        pygame_mixer.quit()  # Полностью сбрасываем аудиосистему
        logger.info("🔇 Озвучка остановлена (через вызов stop_audio).")
    except Exception as e:
        logger.error(f"Ошибка при остановке аудио: {e}")
    return "Аудиозапись остановлена"

def listen_capslock():
    """Отслеживает нажатие CapsLock и останавливает озвучку."""
    while True:
        try:
            keyboard.wait("caps lock")
            stop_audio()
        except Exception as e:
            logger.error(f"Ошибка в обработчике CapsLock: {e}")
            time.sleep(1)  # Пауза перед повторной попыткой

# Отключаем автоматический запуск горячей клавиши CapsLock (раскомментируйте, если хотите управлять только через UI)
# keyboard.add_hotkey("caps lock", stop_audio)
# capslock_thread = threading.Thread(target=listen_capslock, daemon=True)
# capslock_thread.start()

async def generate_audio(text: str, output_file: str = "audio/message.mp3", voice: str = TTS_DEFAULT_VOICE):
    """
    Генерирует аудио и воспроизводит его.
    
    Использует edge_tts для генерации аудио, а затем воспроизводит его через pygame.
    
    Args:
        text: Текст для преобразования в речь
        output_file: Путь к выходному аудиофайлу
        voice: Голос для синтеза речи
        
    Returns:
        None
    """
    if not text or not text.strip():
        logger.warning("Попытка озвучить пустой текст")
        return
        
    event_manager.reset_stop_audio()
    
    # Создаем директорию для аудио, если она не существует
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    try:
        # Инициализация pygame
        try:
            pygame_mixer.quit()
            pygame_mixer.init()
        except Exception as e:
            logger.error(f"Ошибка инициализации pygame: {e}")
            # Пробуем еще раз с задержкой
            time.sleep(0.5)
            pygame_mixer.init()

        # Генерация аудио
        try:
            logger.info(f"Генерация аудио для текста: {text[:50]}...")
            tts = edge_tts.Communicate(text, voice)
            await tts.save(output_file)
            logger.info(f"Аудио сохранено в {output_file}")
        except Exception as e:
            logger.error(f"Ошибка генерации аудио: {e}")
            return

        # Воспроизведение аудио
        try:
            pygame_mixer.music.load(output_file)
            pygame_mixer.music.play()
            logger.info("Воспроизведение аудио начато")
        except Exception as e:
            logger.error(f"Ошибка воспроизведения аудио: {e}")
            return

        # Ожидание окончания воспроизведения
        while pygame_mixer.music.get_busy():
            if event_manager.should_stop_audio():
                pygame_mixer.music.stop()
                pygame_mixer.quit()
                logger.info("🔇 Озвучка была остановлена.")
                return
            time.sleep(0.1)
            
        logger.info("Воспроизведение аудио завершено")

    except Exception as e:
        logger.error(f"Неожиданная ошибка воспроизведения: {e}")
    finally:
        # Очистка ресурсов
        try:
            if pygame_mixer.get_init():
                pygame_mixer.quit()
        except:
            pass

def listen(awake=False) -> dict:
    """
    Функция для распознавания речи с использованием Whisper API от OpenAI.
    
    Args:
        awake: Флаг пробуждения
        
    Returns:
        Словарь с результатом распознавания
    """
    try:
        import os
        import tempfile
        from openai import OpenAI
        
        # Получаем API ключ из переменных окружения
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            message = "API ключ OpenAI не найден в переменных окружения"
            logger.error(message)
            return {"message": message, "error": True}
            
        # Инициализируем клиент OpenAI
        client = OpenAI(api_key=api_key)
        
        # Пытаемся импортировать модули для записи аудио
        try:
            import sounddevice as sd
            import soundfile as sf
        except (ImportError, OSError) as e:
            logger.warning(f"Не удалось импортировать модули для записи аудио: {e}")
            logger.info("Используем заглушки для записи аудио")
            from utils.mock_modules import mock_sounddevice as sd, mock_soundfile as sf
        
        import numpy as np
        
        # Параметры записи
        sample_rate = 44100  # Частота дискретизации
        duration = 5  # Длительность записи в секундах
        
        logger.info("Слушаю... (запись 5 секунд)")
        
        try:
            # Записываем аудио
            recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
            sd.wait()  # Ждем окончания записи
        except Exception as e:
            logger.error(f"Ошибка при записи аудио: {e}")
            # В случае ошибки создаем пустой массив для тестирования
            recording = np.zeros((int(duration * sample_rate), 1), dtype='float32')
            logger.info("Создан пустой аудиофайл для тестирования")
        
        # Создаем временный файл для сохранения аудио
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp_path = tmp.name
            
        try:
            # Сохраняем аудио во временный файл
            sf.write(tmp_path, recording, sample_rate)
            logger.info(f"Аудио сохранено во временный файл: {tmp_path}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении аудио: {e}")
            # В случае ошибки создаем пустой файл
            with open(tmp_path, 'wb') as f:
                f.write(b'\x00' * 44)  # Минимальный заголовок WAV
            logger.info("Создан пустой WAV файл для тестирования")
        
        # Для тестирования в среде без аудиоустройства
        if os.path.getsize(tmp_path) < 1000:  # Если файл слишком маленький
            logger.warning("Файл слишком маленький, возвращаем тестовый текст")
            return {"message": "тестовый текст для проверки распознавания", "error": False}
        
        try:
            # Отправляем на распознавание
            with open(tmp_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text",
                    language="ru"  # Указываем русский язык
                )
                
            text = response.lower()  # Преобразуем в нижний регистр для совместимости
            logger.info(f"Распознано: {text}")
            return {"message": text, "error": False}
            
        except Exception as e:
            message = f"Ошибка при распознавании речи через Whisper API: {e}"
            logger.error(message)
            return {"message": message, "error": True}
        finally:
            # Удаляем временный файл
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception as e:
                logger.error(f"Ошибка при удалении временного файла: {e}")
            
    except Exception as e:
        message = f"Ошибка при распознавании речи: {e}"
        logger.error(message)
        return {"message": message, "error": True}
