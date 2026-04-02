from datetime import date
from states import STATE_MENU, STATE_CHAT
from storage import user_state
from keyboards import get_menu_keyboard, get_talk_menu_keyboard

BIRTHDAY = date(2026, 4, 1)

async def handle_main_menu(update, context, user_id, text):
    if text == "Расскажи о себе":
        await update.message.reply_text(
            "Меня зовут Ensi. (Это сокращение от ensimäinen). "
            "Я люблю общаться и узнавать новое."
        )
        return True

    if text == "Сколько тебе дней":
        age = (date.today() - BIRTHDAY).days
        await update.message.reply_text(f"Мне сейчас {age} дней.")
        return True

    if text == "Просто поговорим":
        user_state[user_id] = STATE_CHAT
        await update.message.reply_text(
            "О чём хочешь поговорить?",
            reply_markup=get_talk_menu_keyboard()
        )
        return True

    return False
