from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

from config import TOKEN

# Состояния, которые нужны только ДО входа в меню
from states import (
    STATE_WAITING_NAME,
    STATE_LANGUAGE
)

# Хранилище
from storage import user_state, user_name, user_lang

import localization
from localization import (
    load_strings,
    t,
    resolve_lang_by_label,
    resolve_button_key
)

# Клавиатуры
from keyboards import (
    build_keyboard,
    get_language_keyboard
)

from datetime import date
ENSI_BIRTHDATE = date(2026, 4, 1)

# -----------------------------
# /start → выбор языка
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_state[user_id] = STATE_LANGUAGE

    await update.message.reply_text(
        "👉 🌍💬",
        reply_markup=get_language_keyboard()
    )


# -----------------------------
# Универсальный обработчик меню
# -----------------------------
async def handle_menu(update, user_id, text, section):
    key, info = resolve_button_key(section, text)

    # Если кнопка не найдена
    if not key:
        error_text = localization.STR.get("error_massage", "I don't understand.")
        await update.message.reply_text(error_text)
        return

    # -----------------------------
    # Кнопка-ОТВЕТ
    # -----------------------------
    if info["type"] == "answer":
        answer = localization.STR[section]["answers"].get(key)

        # Если ответ — строка
        if isinstance(answer, str):
            if key == "age":
                days = (date.today() - ENSI_BIRTHDATE).days
                answer = answer.format(days=days)
            # Если строка выглядит как путь к картинке
            if answer.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                await update.message.reply_photo(
                    photo=open(answer, "rb"),
                    reply_markup=build_keyboard(section)
                )
                return

            # Обычный текстовый ответ
            await update.message.reply_text(
                answer,
                reply_markup=build_keyboard(section)
            )
            return

        # Если ответ — объект (на будущее)
        if isinstance(answer, dict):
            text = answer.get("text")
            image = answer.get("image")

            if text:
                await update.message.reply_text(
                    text,
                    reply_markup=build_keyboard(section)
                )

            if image:
                await update.message.reply_photo(
                    photo=open(image, "rb")
                )

            return

    # -----------------------------
    # Кнопка-ПЕРЕХОД
    # -----------------------------
    if info["type"] == "state":
        next_state = info["next_state"]

        # 🔥 ОСОБЫЙ СЛУЧАЙ: переход к выбору языка
        if next_state == "language_menu":
            user_state[user_id] = STATE_LANGUAGE
            await update.message.reply_text(
                "👉 🌍💬",
                reply_markup=get_language_keyboard()
            )
            return

        # Обычный переход в меню
        user_state[user_id] = next_state
        choose_text = localization.STR.get("choose_an_option", "Please choose an option:")

        await update.message.reply_text(
            choose_text,
            reply_markup=build_keyboard(next_state)
        )
        return


# -----------------------------
# Основной обработчик
# -----------------------------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    state = user_state.get(user_id)

    if state == STATE_LANGUAGE:
        lang = resolve_lang_by_label(text)

        if lang:
            user_lang[user_id] = lang
            load_strings(lang)

            # Если имя уже есть — сразу в главное меню
            if user_name.get(user_id):
                user_state[user_id] = "main_menu"
                await update.message.reply_text(
                    t("choose_an_option"),
                    reply_markup=build_keyboard("main_menu")
                )
                return

            # Если имени нет — спрашиваем
            user_state[user_id] = STATE_WAITING_NAME
            await update.message.reply_text(
                t("start_questions.buttons.ask_name"),
                reply_markup=ReplyKeyboardRemove()
            )
            return

        await update.message.reply_text(
            "👉 🌍💬",
            reply_markup=get_language_keyboard()
        )
        user_state[user_id] = STATE_LANGUAGE
        return

    # LANGUAGE SELECTION (return from menu)
    if state == "language_menu":
        await update.message.reply_text(
            "👉 🌍💬",
            reply_markup=get_language_keyboard()
        )
        user_state[user_id] = STATE_LANGUAGE
        return

    # -----------------------------
    # USER ENTERS NAME
    # -----------------------------
    if state == STATE_WAITING_NAME:
        user_name[user_id] = text
        user_state[user_id] = "main_menu"

        await update.message.reply_text(
            t("start_questions.answers.ask_name", name=text),
            reply_markup=build_keyboard("main_menu")
        )
        return

    # -----------------------------
    # ВСЕ ОСТАЛЬНЫЕ СОСТОЯНИЯ — ЭТО МЕНЮ
    # -----------------------------
    if isinstance(state, str):
        await handle_menu(update, user_id, text, state)
        return

# -----------------------------
# MAIN
# -----------------------------
def main():
    print("Создаю приложение...")
    load_strings("ru")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Бот запущен. Жду сообщения...")
    app.run_polling()


if __name__ == "__main__":
    main()
