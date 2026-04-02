from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

from config import TOKEN
from states import STATE_WAITING_NAME, STATE_MENU, STATE_CHAT
from storage import user_state, user_name
from main_menu import get_menu_keyboard, handle_main_menu
from talk_menu import handle_talk_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_state[user_id] = STATE_WAITING_NAME
    await update.message.reply_text("Привет! Как тебя зовут?")


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
        handled = await handle_main_menu(update, context, user_id, text)
        if handled:
            return

    # 3. Подменю «Просто поговорим»
    if state == STATE_CHAT:
        handled = await handle_talk_menu(update, context, user_id, text)
        if handled:
            return

        await update.message.reply_text("Выбери вариант из меню.")
        return


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Бот запущен.")
    app.run_polling()


if __name__ == "__main__":
    main()
