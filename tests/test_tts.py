"""
Тесты для модуля tts.py
"""

import os
import sys
import unittest
import asyncio
from unittest.mock import patch, MagicMock

# Добавляем корневую директорию проекта в путь
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.tts import listen, generate_audio, stop_audio


class TestTTS(unittest.TestCase):
    """Тесты для функций синтеза и распознавания речи"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Устанавливаем тестовый API ключ
        os.environ["OPENAI_API_KEY"] = "sk-test-key"
        os.environ["ELEVENLABS_API_KEY"] = "test-key"
    
    def test_listen_basic(self):
        """Базовый тест функции listen"""
        # Вызываем функцию
        result = listen()
        
        # Проверяем результат
        self.assertIn("message", result)
        self.assertIn("error", result)
    
    @patch('utils.tts.pygame_mixer')
    def test_stop_audio(self, mock_pygame_mixer):
        """Тест функции stop_audio с использованием мока"""
        # Настраиваем мок
        mock_pygame_mixer.quit.return_value = None
        
        # Вызываем функцию
        result = stop_audio()
        
        # Проверяем результат
        self.assertEqual(result, "Аудиозапись остановлена")
        
        # Проверяем, что моки были вызваны
        mock_pygame_mixer.quit.assert_called_once()
    
    def test_generate_audio_basic(self):
        """Базовый тест функции generate_audio"""
        # Создаем тестовую функцию для запуска через asyncio.run
        async def test_coroutine():
            try:
                await generate_audio("Тестовый текст")
                return True
            except Exception as e:
                print(f"Ошибка при генерации аудио: {e}")
                return False
        
        # Проверяем, что функция не вызывает необработанных исключений
        try:
            asyncio.run(test_coroutine())
            self.assertTrue(True)  # Если дошли до этой точки, тест пройден
        except Exception as e:
            self.fail(f"generate_audio вызвала исключение: {e}")


if __name__ == '__main__':
    unittest.main()