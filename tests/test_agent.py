"""
Тесты для модуля agent.py
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Добавляем корневую директорию проекта в путь
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import core.agent as agent


class TestAgent(unittest.TestCase):
    """Тесты для класса Agent"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Устанавливаем тестовый API ключ
        os.environ["OPENAI_API_KEY"] = "sk-test-key"
        os.environ["ELEVENLABS_API_KEY"] = "test-key"
    
    def test_agent_initialization(self):
        """Тест инициализации модуля agent"""
        # Проверяем, что модуль был импортирован
        self.assertIsNotNone(agent)
        
        # Проверяем, что client существует (может быть None в тестовом режиме)
        self.assertTrue(hasattr(agent, 'client'))
    
    @patch('core.agent.client')
    def test_get_voices(self, mock_client):
        """Тест получения голосов ElevenLabs"""
        # Настраиваем мок
        mock_client.voices.list.return_value = MagicMock()
        
        # Вызываем функцию
        try:
            voices = agent.get_voices()
            # Если функция не вызвала исключение, тест пройден
            self.assertTrue(True)
        except Exception as e:
            # Если функция вызвала исключение, тест не пройден
            self.fail(f"get_voices вызвала исключение: {e}")
    
    def test_get_commands(self):
        """Тест получения команд"""
        # Вызываем функцию
        commands = agent.commands
        
        # Проверяем, что команды были получены
        self.assertIsNotNone(commands)
        # Команды могут быть в виде списка или словаря
        self.assertTrue(isinstance(commands, dict) or isinstance(commands, list))


if __name__ == '__main__':
    unittest.main()