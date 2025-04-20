# Модуль компьютерного зрения для ИИ-помощника

## Описание

Модуль компьютерного зрения позволяет ИИ-помощнику "видеть" экран и взаимодействовать с ним. Он предоставляет следующие возможности:

1. Захват скриншотов экрана
2. Распознавание текста на экране с помощью OCR
3. Поиск элементов интерфейса по тексту
4. Клик по элементам интерфейса
5. Ввод текста в поля ввода
6. Интеллектуальный поиск полей ввода

## Архитектура

Модуль компьютерного зрения состоит из следующих компонентов:

1. **utils/screen_vision.py** - основной модуль для работы со скриншотами и распознавания текста
   - Функции для захвата скриншотов
   - Функции для распознавания текста
   - Функции для поиска элементов интерфейса
   - Функции для взаимодействия с элементами интерфейса

2. **commands/screen_commands.py** - модуль с командами для работы с экраном
   - Функции для выполнения команд, связанных с компьютерным зрением
   - Обработка ошибок и форматирование результатов

3. **commands/screen_commands_handler.py** - обработчик команд для работы с экраном
   - Связывает команды из commands_as_json.py с функциями из screen_commands.py

4. **ui/js/screen_vision.js** - JavaScript-модуль для работы с функциями компьютерного зрения
   - Функции для вызова Python-функций через Eel
   - Обработка результатов и ошибок

## Использование

### Python API

```python
from utils.screen_vision import (
    capture_screenshot,
    extract_text_from_screenshot,
    find_element_by_text,
    click_element_by_text,
    type_text,
    analyze_screen
)

# Захват скриншота
screenshot = capture_screenshot()

# Распознавание текста
text = extract_text_from_screenshot(screenshot)

# Поиск элемента по тексту
element = find_element_by_text(screenshot, "Кнопка")

# Клик по элементу
click_element_by_text("Кнопка")

# Ввод текста
type_text("Привет, мир!")

# Анализ экрана
analysis = analyze_screen()
```

### JavaScript API

```javascript
// Захват скриншота
const screenshot = await window.screenVision.takeScreenshot();

// Распознавание текста
const textResult = await window.screenVision.readScreenText();

// Клик по тексту
const clickResult = await window.screenVision.clickOnText("Кнопка");

// Ввод текста
const inputResult = await window.screenVision.inputText("Привет, мир!");

// Поиск текста, клик и ввод
const findAndTypeResult = await window.screenVision.findAndClickThenType("Поиск", "Запрос");
```

## Команды для GPT

В файле commands_as_json.py добавлены следующие команды для работы с экраном:

1. **take_screenshot_vision** - делает скриншот экрана и анализирует его содержимое
2. **read_screen_text** - считывает текст с экрана с помощью OCR
3. **click_on_text** - находит указанный текст на экране и кликает по нему
4. **input_text_vision** - вводит указанный текст с клавиатуры
5. **find_and_click_then_type** - находит указанный текст на экране, кликает по нему и вводит новый текст
6. **find_text_field** - находит поле для ввода текста на экране и кликает по нему

## Требования

Для работы модуля компьютерного зрения требуются следующие библиотеки:

1. OpenCV (cv2) - для обработки изображений
2. Pytesseract - для распознавания текста
3. PyAutoGUI - для взаимодействия с интерфейсом
4. PIL (Pillow) - для работы с изображениями

## Ограничения

1. Для работы модуля требуется графический интерфейс. В среде без GUI используются заглушки.
2. Точность распознавания текста зависит от качества изображения и шрифта.
3. Поиск элементов по тексту может быть ненадежным, если текст плохо виден или имеет нестандартный шрифт.

## Примеры использования

### Пример 1: Поиск и клик по кнопке

```python
# Python
result = click_on_text("Войти")
```

```javascript
// JavaScript
const result = await window.screenVision.clickOnText("Войти");
```

### Пример 2: Заполнение формы

```python
# Python
find_and_click_then_type("Логин", "user@example.com")
find_and_click_then_type("Пароль", "password123")
click_on_text("Войти")
```

```javascript
// JavaScript
await window.screenVision.findAndClickThenType("Логин", "user@example.com");
await window.screenVision.findAndClickThenType("Пароль", "password123");
await window.screenVision.clickOnText("Войти");
```

### Пример 3: Анализ содержимого экрана

```python
# Python
analysis = analyze_screen()
print(f"Текст на экране: {analysis['text']}")
```

```javascript
// JavaScript
const screenshot = await window.screenVision.takeScreenshot();
console.log(`Текст на экране: ${screenshot.text}`);
```

### Пример 4: Интеллектуальный поиск полей ввода

```python
# Python
# Находим поле для ввода email
find_text_field("Email")
# Вводим текст
type_text("user@example.com")

# Находим поле для ввода пароля
find_text_field("Пароль")
# Вводим текст
type_text("password123")
```

```javascript
// JavaScript
// Находим поле для ввода email и кликаем по нему
await window.screenVision.findTextField("Email");
// Вводим текст
await window.screenVision.inputText("user@example.com");

// Находим поле для ввода пароля и кликаем по нему
await window.screenVision.findTextField("Пароль");
// Вводим текст
await window.screenVision.inputText("password123");
```

## Алгоритм поиска полей ввода

Функция `find_text_field` использует следующий алгоритм для поиска полей ввода:

1. **Поиск по меткам** - ищет текстовые метки, соответствующие названию поля (например, "Email:", "Введите Email")
2. **Смещение от метки** - если метка найдена, кликает правее и немного ниже (где обычно находится поле ввода)
3. **Поиск по placeholder** - если метка не найдена, ищет текст внутри полей ввода (placeholder)
4. **Приоритизация точных совпадений** - сначала ищет точные совпадения, затем частичные

## Улучшенный алгоритм распознавания текста

Функция `find_element_by_text` теперь использует улучшенный алгоритм:

1. **Приоритизация точных совпадений** - сначала ищет точные совпадения текста
2. **Учет уверенности распознавания** - выбирает совпадение с наивысшей уверенностью
3. **Частичные совпадения** - если точных совпадений нет, использует частичные