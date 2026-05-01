import threading
from aiohttp import web
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

from config import TOKEN

from states import (
    STATE_WAITING_NAME,
    STATE_LANGUAGE,
)

from storage import user_state, user_name, user_lang

from localization import (
    load_strings,
    t,
    resolve_lang_by_label,
)

from keyboards import (
    build_keyboard,
    get_language_keyboard
)

from main_menu import MainMenu


menu = MainMenu()

ASK_NAME_ON_START = False
ASK_LANGUAGE_ON_START = False


# -----------------------------
# /start
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not ASK_LANGUAGE_ON_START:
        DEFAULT_LANGUAGE = "en"
        user_lang[user_id] = DEFAULT_LANGUAGE
        load_strings(DEFAULT_LANGUAGE)

        if user_name.get(user_id):
            user_state[user_id] = "main_menu"
            await update.message.reply_text(
                t("choose_an_option"),
                reply_markup=build_keyboard("main_menu")
            )
            return

        if not ASK_NAME_ON_START:
            user_state[user_id] = "main_menu"
            await update.message.reply_text(
                t("choose_an_option"),
                reply_markup=build_keyboard("main_menu")
            )
            return

        user_state[user_id] = STATE_WAITING_NAME
        await update.message.reply_text(
            t("start_questions.buttons.ask_name"),
            reply_markup=ReplyKeyboardRemove()
        )
        return

    if user_id not in user_state:
        user_state[user_id] = "main_menu"

    state = user_state[user_id]

    user_state[user_id] = STATE_LANGUAGE
    await update.message.reply_text(
        "👉 🌍💬",
        reply_markup=get_language_keyboard()
    )


# -----------------------------
# Основной обработчик
# -----------------------------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    from localization import STR, CURRENT_LANG, load_strings
    # --- Если язык не выбран, ставим язык по умолчанию и состояние main_menu ---
    if user_id not in user_lang:
        user_lang[user_id] = "en"
        load_strings("en")
        user_state[user_id] = "main_menu"

    lang = user_lang.get(user_id, "en")

    if not STR or CURRENT_LANG != lang:
        load_strings(lang)

    text = update.message.text.strip()
    state = user_state.get(user_id, "main_menu")

    # 1. Обработка выбора языка
    if state == STATE_LANGUAGE:
        lang = resolve_lang_by_label(text)

        if lang:
            user_lang[user_id] = lang
            load_strings(lang)

            if user_name.get(user_id) or not ASK_NAME_ON_START:
                user_state[user_id] = "main_menu"
                await update.message.reply_text(
                    t("choose_an_option"),
                    reply_markup=build_keyboard("main_menu")
                )
                return

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
        return

    # 2. Обработка ввода имени
    if state == STATE_WAITING_NAME:
        user_name[user_id] = text
        user_state[user_id] = "main_menu"

        await update.message.reply_text(
            t("start_questions.answers.ask_name", name=text),
            reply_markup=build_keyboard("main_menu")
        )
        return

    # 3. Всё остальное — меню
    await menu.handle(update, user_id, text, state)


# --- ВСТАВЛЯЕМ HTTP-СЕРВЕР СЮДА ---
async def health(request):
    return web.Response(text="OK")

def run_web():
    app = web.Application()
    app.router.add_get("/", health)
    web.run_app(app, port=8080)

threading.Thread(target=run_web, daemon=True).start()
# --- КОНЕЦ ВСТАВКИ ---

def main():
    print("Создаю приложение...")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Бот запущен. Жду сообщения...")
    app.run_polling()


if __name__ == "__main__":
    main()

