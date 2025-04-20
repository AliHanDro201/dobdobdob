"""
Тесты для модуля commands.py
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Добавляем корневую директорию проекта в путь
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import commands.commands as commands_module


class TestCommandsModule(unittest.TestCase):
    """Тесты для модуля commands"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        pass
    
    def test_commands_module_initialization(self):
        """Тест инициализации модуля commands"""
        # Проверяем, что модуль был импортирован
        self.assertIsNotNone(commands_module)
    
    def test_open_app(self):
        """Тест функции open_app"""
        # Проверяем, что функция существует
        self.assertTrue(hasattr(commands_module, 'open_app'))
        
        # Вызываем функцию с заглушкой subprocess.Popen
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_popen.return_value = mock_process
            
            # Вызываем функцию
            try:
                result = commands_module.open_app({"name": "calculator"})
                # Если функция не вызвала исключение, тест пройден
                self.assertTrue(True)
            except Exception as e:
                # Если функция вызвала исключение, тест не пройден
                self.fail(f"open_app вызвала исключение: {e}")
    
    def test_close_app(self):
        """Тест функции close_app"""
        # Проверяем, что функция существует
        self.assertTrue(hasattr(commands_module, 'close_app'))
        
        # Вызываем функцию
        try:
            result = commands_module.close_app({"name": "calculator"})
            # Если функция не вызвала исключение, тест пройден
            self.assertTrue(True)
        except Exception as e:
            # Если функция вызвала исключение, тест не пройден
            self.fail(f"close_app вызвала исключение: {e}")


if __name__ == '__main__':
    unittest.main()