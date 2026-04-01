from datetime import date
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import TOKEN

# Дата рождения Энси
BIRTHDAY = date(2026, 4, 1)


# Состояния
STATE_WAITING_NAME = "waiting_name"
STATE_MENU = "menu"
STATE_CHAT = "chat"
waiting_for_menu_answer = set()

# Хранилища
user_state = {}
user_name = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_state[user_id] = STATE_WAITING_NAME

    await update.message.reply_text("Привет! Как тебя зовут?")

def get_talk_menu_keyboard():
    keyboard = [
        ["Расскажи о космосе"], ["Скажи шутку"],
        ["Покажи смешную картинку"], ["Вернуться в меню"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_menu_keyboard():
    keyboard = [
        ["Расскажи о себе", "Сколько тебе дней"],
        ["Просто поговорим", "Просто кнопка"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    state = user_state.get(user_id)

    # 1. Ждём имя
    if state == STATE_WAITING_NAME:
        user_name[user_id] = text
        user_state[user_id] = STATE_MENU
        await update.message.reply_text(
            f"Приятно познакомиться, {text}! Что хочешь узнать?",
            reply_markup=get_menu_keyboard()
        )
        return

    # 2. Главное меню
    if state == STATE_MENU:
        if text == "Расскажи о себе":
            await update.message.reply_text(
                "Меня зовут Ensi. (Это сокращение от ensimäinen). Я люблю общаться и узнавать новое."
            )
            return

        if text == "Сколько тебе дней":
            age = (date.today() - BIRTHDAY).days
            await update.message.reply_text(f"Мне сейчас {age} дней.")
            return

        if text == "Просто поговорим":
            user_state[user_id] = STATE_CHAT

            keyboard = [
                ["Расскажи о космосе"],
                ["Скажи шутку"],
                ["Покажи смешную картинку"],
                ["Вернуться в меню"]
            ]
            markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_text(
                "О чём хочешь поговорить?",
                reply_markup=markup
            )
            return

    # 3. Свободный чат
    if state == STATE_CHAT:

        if text == "Расскажи о космосе":
            await update.message.reply_text(
                "Бланета (англ. Blanet) — гипотетический класс экзопланет, "
                "которые могут быть сформированы вокруг сверхмассивной чёрной дыры "
                "в центре галактик."
            )
            return

        if text == "Скажи шутку":
            await update.message.reply_text("У тебя электрокар. Бросаешь водить?")
            return

        if text == "Покажи смешную картинку":
            await update.message.reply_photo(
                photo="https://i.imgur.com/4AiXzf8.jpeg"  # пример
            )
            return

        if text == "Вернуться в меню":
            user_state[user_id] = STATE_MENU
            await update.message.reply_text(
                "Возвращаю тебя в меню!",
                reply_markup=get_menu_keyboard()
            )
            return

        await update.message.reply_text("Выбери вариант из меню.")
        return


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Бот запущен. Можно писать ему в Telegram.")
    app.run_polling()


if __name__ == "__main__":
    main()