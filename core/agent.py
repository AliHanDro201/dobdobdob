# core/agent.py
import os
import asyncio
import elevenlabs as eleven
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
import json
import threading

from utils.tts import generate_audio
from core.conversation import Conversation
from core.config import prompt, GPT_MODEL, GPT_TEMPERATURE, GPT_MAX_TOKENS, SECOND_OPENAI_API_KEY
from commands.commands_as_json import commands

# Устанавливаем API ключ
try:
    from core.config import OPENAI_API_KEY
    client = OpenAI(api_key=OPENAI_API_KEY)
    if not OPENAI_API_KEY:
        print("ВНИМАНИЕ: API ключ OpenAI не установлен. Функциональность будет ограничена.")
except Exception as e:
    print(f"Ошибка при инициализации OpenAI API: {e}")
    # Создаем заглушку для тестирования
    client = None

# Создаем глобальный пул потоков
executor = ThreadPoolExecutor(max_workers=4)

# Блок для команд
from commands import commands as cmd_functions
from commands.commands_as_json import commands  # это список описаний команд
tools = [{"type": "function", "function": cmd} for cmd in commands]
available_commands = {}
for command in commands:
    command_name = command["name"]
    try:
        # Получаем функцию из модуля cmd_functions по имени
        available_commands[command_name] = getattr(cmd_functions, command_name)
    except AttributeError:
        print(f"Команда {command_name} не найдена в модуле commands.")


        
# Функция для получения голосов ElevenLabs
def get_voices():
    try:
        # Проверяем, что API ключ установлен
        if not os.getenv("ELEVENLABS_API_KEY"):
            print("API ключ ElevenLabs не установлен")
            return []
            
        # Получаем список голосов
        try:
            # Для новых версий elevenlabs
            from elevenlabs.api import Voices
            voices_list = Voices.from_api()
            return voices_list
        except (AttributeError, ImportError):
            # Для старых версий elevenlabs
            try:
                # Пробуем через voices.list()
                voices_list = eleven.voices.list()
                return voices_list
            except AttributeError:
                try:
                    # Пробуем через voices()
                    voices_list = eleven.voices()
                    return voices_list
                except Exception as e:
                    print(f"Ошибка при получении голосов ElevenLabs (старый метод): {e}")
                    return []
    except Exception as e:
        print(f"Ошибка при получении голосов ElevenLabs: {e}")
        return []

VOICE_ID = "XrExE9yKIg1WjnnlVkGX"

try:
    # Получаем голоса только если API ключ установлен
    if os.getenv("ELEVENLABS_API_KEY"):
        voices = get_voices()
        if voices:
            filtered = [voice for voice in voices if getattr(voice, "voice_id", "") == VOICE_ID]
            if filtered:
                main_voice = filtered[0]
            else:
                filtered = [voice for voice in voices if "matilda" in getattr(voice, "name", "").lower()]
                if filtered:
                    main_voice = filtered[0]
                else:
                    main_voice = None
                    print("Не найден подходящий голос, используем None")
        else:
            main_voice = None
            print("Список голосов пуст.")
    else:
        main_voice = None
        print("API ключ ElevenLabs не установлен, голос не будет использоваться")
except Exception as e:
    main_voice = None
    print("Ошибка получения голоса:", e)











async def async_chat_completion(user_text: str) -> dict:
    """
    Один вызов GPT‑4o‑mini + поддержка tool_calls.
    Возвращает словарь {status, gptMessage, …}
    """
    # Для тестирования без API ключа
    if client is None:
        print("OpenAI API не инициализирован, возвращаем тестовый ответ")
        test_response = f"Это тестовый ответ на запрос: {user_text}"
        
        # Запускаем TTS для тестового ответа
        threading.Thread(
            target=lambda: asyncio.run(
                generate_audio(test_response, "audio/message.mp3", "ru-RU-SvetlanaNeural")
            ),
            daemon=True
        ).start()
        
        return {
            "status": 200,
            "gptMessage": test_response,
            "go_to_sleep": False,
            "statusMessage": "Test mode - no API key"
        }
    
    # готовим контекст
    local_conv = Conversation(prompt)
    local_conv.add_message(role="user", content=user_text)

    loop = asyncio.get_running_loop()
    try:
        rsp = await loop.run_in_executor(
            executor,
            lambda: client.chat.completions.create(
                model       = GPT_MODEL,
                messages    = local_conv.get_messages(),
                tools       = tools,          # ← вместо functions
                tool_choice = "auto",
                temperature = GPT_TEMPERATURE,
                max_tokens  = GPT_MAX_TOKENS
            )
        )
    except Exception as e:
        error_msg = f"Ошибка при обращении к OpenAI API: {str(e)}"
        print(error_msg)
        
        # Запускаем TTS для сообщения об ошибке
        threading.Thread(
            target=lambda: asyncio.run(
                generate_audio(error_msg, "audio/message.mp3", "ru-RU-SvetlanaNeural")
            ),
            daemon=True
        ).start()
        
        return {"status": 500, "gptMessage": error_msg, "statusMessage": str(e)}

    # главный ответ
    msg = rsp.choices[0].message          # ChatCompletionMessage object

    # ───────── если GPT вызвал функцию ─────────
    if msg.tool_calls:
        call       = msg.tool_calls[0]
        fn_name    = call.function.name
        fn_args    = json.loads(call.function.arguments or "{}")

        if fn_name in available_commands:
            try:
                result = available_commands[fn_name](**fn_args)
            except Exception as e:
                result = f"Ошибка при выполнении {fn_name}: {e}"
        else:
            result = f"Функция {fn_name} не найдена."

        msg.content = str(result)

    # сохраняем сообщение в истории
    local_conv.add_message(role="assistant", content=msg.content)

    # ───────── пост‑обработка «Открой …» ─────────
    if "{name}" in msg.content:
        app_name   = user_text.replace("Открой", "").strip()
        msg.content = "Открываю " + app_name

    # TTS (только для обычных ответов)
    if "{name}" not in msg.content:
        threading.Thread(
            target=lambda: asyncio.run(
                generate_audio(msg.content, "audio/message.mp3", "ru-RU-SvetlanaNeural")
            ),
            daemon=True
        ).start()

    return {
        "status": 200,
        "gptMessage": msg.content,
        "go_to_sleep": False,
        "statusMessage": "Success"
    }