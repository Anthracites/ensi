import json
import os
from telegram import ReplyKeyboardMarkup
import localization


def build_keyboard(section: str):
    """
    Строит клавиатуру для обычных меню из JSON.
    """
    buttons = localization.STR[section]["buttons"]

    keyboard = []
    row = []

    for key, info in buttons.items():
        # Старый формат: просто строка
        if isinstance(info, str):
            label = info
        else:
            label = info.get("label")

        row.append(label)

    # Каждая кнопка — отдельная строка
    keyboard = [[label] for label in row]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_language_keyboard():
    """
    Динамически строит клавиатуру выбора языка
    на основе файлов в папке strings/.
    """
    buttons = []

    # Сканируем папку strings/
    files = os.listdir("strings")

    for filename in files:
        # Ищем файлы вида ensi_xx.json
        if filename.startswith("ensi_") and filename.endswith(".json"):
            lang = filename.replace("ensi_", "").replace(".json", "")

            # Загружаем файл, чтобы взять подпись языка
            path = os.path.join("strings", filename)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Берём поле "language" или код языка
            label = data.get("language", lang)

            # Каждая кнопка — отдельная строка
            buttons.append([label])

    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)
