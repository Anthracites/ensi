import os
import json

LOCALES_DIR = "strings"

CURRENT_LANG = "ru"
STR = {}


# ---------------------------------------------------------
# Получение списка доступных языков по файлам
# ---------------------------------------------------------
def get_available_languages():
    langs = []
    for filename in os.listdir(LOCALES_DIR):
        if filename.startswith("ensi_") and filename.endswith(".json"):
            lang = filename.replace("ensi_", "").replace(".json", "")
            langs.append(lang)
    return langs


# ---------------------------------------------------------
# Определение языка по подписи (label)
# ---------------------------------------------------------
def resolve_lang_by_label(label: str):
    """
    Ищем язык по подписи "language" внутри каждого JSON-файла.
    Не используем STR, чтобы не зависеть от текущего языка.
    """
    for filename in os.listdir(LOCALES_DIR):
        if filename.startswith("ensi_") and filename.endswith(".json"):
            lang = filename.replace("ensi_", "").replace(".json", "")
            path = os.path.join(LOCALES_DIR, filename)

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("language") == label:
                return lang

    return None


# ---------------------------------------------------------
# Загрузка строк выбранного языка
# ---------------------------------------------------------
def load_strings(lang: str):
    """
    Загружает JSON выбранного языка в STR.
    """
    global STR, CURRENT_LANG

    CURRENT_LANG = lang
    path = os.path.join(LOCALES_DIR, f"ensi_{lang}.json")

    with open(path, "r", encoding="utf-8") as f:
        STR = json.load(f)

    print("Загружены ключи:", STR.keys())


# ---------------------------------------------------------
# Поиск кнопки по тексту
# ---------------------------------------------------------
def resolve_button_key(section: str, text: str):
    """
    Ищет кнопку по тексту в текущем меню.
    """
    buttons = STR[section]["buttons"]

    for key, info in buttons.items():
        if isinstance(info, str):
            label = info
        else:
            label = info.get("label")

        if text == label:
            return key, info

    return None, None


# ---------------------------------------------------------
# Доступ к строкам по пути
# ---------------------------------------------------------
def t(path: str, **kwargs):
    """
    Достаёт строку по пути вида "start_questions.buttons.ask_name".
    """
    parts = path.split(".")
    value = STR

    for p in parts:
        if p not in value:
            print(f"[t] Нет ключа '{p}' в пути '{path}'. Возвращаю заглушку.")
            return f"[missing:{path}]"
        value = value[p]

    # Если это объект кнопки — берём label
    if isinstance(value, dict) and "label" in value:
        value = value["label"]

    if isinstance(value, str):
        try:
            return value.format(**kwargs)
        except KeyError as e:
            print(f"[t] Нет параметра {e} для строки '{path}'")
            return value

    return value
