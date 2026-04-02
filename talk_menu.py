from states import STATE_MENU
from storage import user_state
from keyboards import get_menu_keyboard

async def handle_talk_menu(update, context, user_id, text):
    if text == "Расскажи о космосе":
        await update.message.reply_text(
            "Бланета (англ. Blanet) — гипотетический класс экзопланет, "
            "которые могут быть сформированы вокруг сверхмассивной чёрной дыры "
            "в центре галактик."
        )
        return True

    if text == "Скажи шутку":
        await update.message.reply_text("У тебя электрокар. Бросаешь водить?")
        return True

    if text == "Покажи смешную картинку":
        await update.message.reply_photo("https://i.imgur.com/4AiXzf8.jpeg")
        return True

    if text == "Вернуться в меню":
        user_state[user_id] = STATE_MENU
        await update.message.reply_text(
            "Возвращаю тебя в меню!",
            reply_markup=get_menu_keyboard()
        )
        return True

    return False
