/**
 * Модуль для работы с функциями компьютерного зрения.
 * Позволяет ИИ-помощнику "видеть" экран и взаимодействовать с ним.
 */

// Функция для выполнения команды для работы с экраном
async function executeScreenCommand(commandName, params) {
    try {
        console.log(`Выполнение команды ${commandName} с параметрами:`, params);
        
        // Вызываем Python-функцию через Eel
        const resultJson = await eel.execute_screen_command(commandName, params)();
        const result = JSON.parse(resultJson);
        
        console.log(`Результат выполнения команды ${commandName}:`, result);
        return result;
    } catch (error) {
        console.error(`Ошибка при выполнении команды ${commandName}:`, error);
        return {
            status: "error",
            message: `Произошла ошибка при выполнении команды: ${error.message || error}`
        };
    }
}

// Функция для захвата скриншота
async function takeScreenshot(region = null) {
    return await executeScreenCommand("take_screenshot_vision", { region });
}

// Функция для считывания текста с экрана
async function readScreenText(region = null) {
    return await executeScreenCommand("read_screen_text", { region });
}

// Функция для клика по тексту
async function clickOnText(text, doubleClick = false) {
    return await executeScreenCommand("click_on_text", { text, double_click: doubleClick });
}

// Функция для ввода текста
async function inputText(text, interval = 0.05) {
    return await executeScreenCommand("input_text_vision", { text, interval });
}

// Функция для поиска текста, клика по нему и ввода нового текста
async function findAndClickThenType(text, inputText, interval = 0.05) {
    return await executeScreenCommand("find_and_click_then_type", { text, input_text: inputText, interval });
}

// Функция для поиска поля ввода текста
async function findTextField(fieldName, doubleClick = false) {
    return await executeScreenCommand("find_text_field", { field_name: fieldName, double_click: doubleClick });
}

// Экспортируем функции
window.screenVision = {
    takeScreenshot,
    readScreenText,
    clickOnText,
    inputText,
    findAndClickThenType,
    findTextField
};

console.log("Модуль screen_vision.js загружен");