from telegram import ReplyKeyboardMarkup

def get_menu_keyboard():
    keyboard = [
        ["Расскажи о себе", "Сколько тебе дней"],
        ["Просто поговорим", "Просто кнопка"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_talk_menu_keyboard():
    keyboard = [
        ["Расскажи о космосе"],
        ["Скажи шутку"],
        ["Покажи смешную картинку"],
        ["Вернуться в меню"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)