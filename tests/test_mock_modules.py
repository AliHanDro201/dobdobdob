"""
Тесты для модуля mock_modules.py
"""

import os
import sys
import unittest

# Добавляем корневую директорию проекта в путь
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.mock_modules import (
    mock_pyautogui, mock_keyboard, mock_helium, 
    mock_pygame_mixer, mock_sounddevice, mock_soundfile
)


class TestMockModules(unittest.TestCase):
    """Тесты для заглушек модулей"""
    
    def test_mock_pyautogui(self):
        """Тест заглушки PyAutoGUI"""
        # Проверяем, что методы не вызывают ошибок
        mock_pyautogui.click(x=100, y=100)
        mock_pyautogui.rightClick(x=100, y=100)
        mock_pyautogui.doubleClick(x=100, y=100)
        mock_pyautogui.moveTo(x=100, y=100)
        mock_pyautogui.moveRel(xOffset=10, yOffset=10)
        mock_pyautogui.dragTo(x=100, y=100)
        mock_pyautogui.dragRel(xOffset=10, yOffset=10)
        mock_pyautogui.scroll(clicks=5)
        mock_pyautogui.hscroll(clicks=5)
        mock_pyautogui.vscroll(clicks=5)
        mock_pyautogui.press('a')
        mock_pyautogui.keyDown('a')
        mock_pyautogui.keyUp('a')
        mock_pyautogui.typewrite('test')
        mock_pyautogui.write('test')
        mock_pyautogui.hotkey('ctrl', 'c')
        
        # Проверяем, что screenshot возвращает изображение
        img = mock_pyautogui.screenshot()
        self.assertEqual(img.size, (100, 100))
        
        # Проверяем, что методы поиска возвращают None
        self.assertIsNone(mock_pyautogui.locateOnScreen('test.png'))
        self.assertIsNone(mock_pyautogui.locateCenterOnScreen('test.png'))
        
        # Проверяем, что getActiveWindowTitle возвращает строку
        self.assertEqual(mock_pyautogui.getActiveWindowTitle(), "Mock Window Title")
    
    def test_mock_keyboard(self):
        """Тест заглушки keyboard"""
        # Проверяем, что методы не вызывают ошибок
        callback = lambda: None
        hotkey_id = mock_keyboard.add_hotkey('ctrl+c', callback)
        mock_keyboard.remove_hotkey(hotkey_id)
        self.assertFalse(mock_keyboard.is_pressed('a'))
        mock_keyboard.press('a')
        mock_keyboard.release('a')
        mock_keyboard.write('test')
    
    def test_mock_helium(self):
        """Тест заглушки Helium"""
        # Проверяем, что методы не вызывают ошибок
        mock_helium.start_chrome(url='http://example.com')
        mock_helium.go_to('http://example.com')
        mock_helium.click('button')
        mock_helium.write('test', into='input')
        mock_helium.press('Enter')
        self.assertTrue(mock_helium.wait_until(lambda: True))
        self.assertEqual(mock_helium.find_all('button'), [])
        mock_helium.scroll_down()
        mock_helium.scroll_up()
    
    def test_mock_pygame_mixer(self):
        """Тест заглушки pygame.mixer"""
        # Проверяем, что методы не вызывают ошибок
        self.assertEqual(mock_pygame_mixer.init(), 1)
        mock_pygame_mixer.quit()
        self.assertTrue(mock_pygame_mixer.get_init())
        mock_pygame_mixer.stop()
        
        # Проверяем методы music
        mock_pygame_mixer.music.load('test.mp3')
        mock_pygame_mixer.music.play()
        self.assertTrue(mock_pygame_mixer.music.get_busy())
        mock_pygame_mixer.music.pause()
        mock_pygame_mixer.music.unpause()
        mock_pygame_mixer.music.stop()
        self.assertFalse(mock_pygame_mixer.music.get_busy())
        mock_pygame_mixer.music.fadeout(1000)
        mock_pygame_mixer.music.set_volume(0.5)
        self.assertEqual(mock_pygame_mixer.music.get_volume(), 1.0)
        mock_pygame_mixer.music.set_pos(10)
        self.assertEqual(mock_pygame_mixer.music.get_pos(), 0)
        
        # Проверяем Sound
        sound = mock_pygame_mixer.Sound('test.mp3')
        channel = sound.play()
        self.assertTrue(channel.get_busy())
        sound.stop()
        sound.fadeout(1000)
        sound.set_volume(0.5)
        self.assertEqual(sound.get_volume(), 1.0)
        self.assertEqual(sound.get_length(), 1.0)
        self.assertEqual(sound.get_num_channels(), 1)
        
        # Проверяем Channel
        channel.play(sound)
        channel.stop()
        channel.pause()
        channel.unpause()
        channel.fadeout(1000)
        channel.set_volume(0.5)
        self.assertEqual(channel.get_volume(), 1.0)
    
    def test_mock_sounddevice(self):
        """Тест заглушки sounddevice"""
        # Проверяем, что методы не вызывают ошибок
        recording = mock_sounddevice.rec(44100, samplerate=44100, channels=1)
        self.assertEqual(recording.shape, (44100, 1))
        mock_sounddevice.wait()
        mock_sounddevice.play(recording, samplerate=44100)
        mock_sounddevice.stop()
        
        # Проверяем, что get_status возвращает словарь
        status = mock_sounddevice.get_status()
        self.assertIsInstance(status, dict)
        self.assertFalse(status['input'])
        self.assertFalse(status['output'])
        
        # Проверяем, что query_devices возвращает словарь
        devices = mock_sounddevice.query_devices()
        self.assertIsInstance(devices, dict)
        self.assertEqual(devices['name'], 'Mock Audio Device')
    
    def test_mock_soundfile(self):
        """Тест заглушки soundfile"""
        # Проверяем, что методы не вызывают ошибок
        import numpy as np
        data = np.zeros((1000, 1), dtype='float32')
        mock_soundfile.write('test.wav', data, 44100)
        
        # Проверяем, что read возвращает данные и частоту дискретизации
        read_data, samplerate = mock_soundfile.read('test.wav')
        self.assertEqual(read_data.shape, (1000, 1))
        self.assertEqual(samplerate, 44100)


if __name__ == '__main__':
    unittest.main()