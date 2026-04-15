from datetime import date
from states import STATE_MENU, STATE_CHAT
from storage import user_state
from keyboards import build_keyboard

BIRTHDAY = date(2026, 4, 1)
from states import (
    STATE_LANGUAGE,
    STATE_WAITING_NAME,
    STATE_SUBSCRIBE,
    STATE_UNSUBSCRIBE
)

from storage import user_state, user_name, user_lang
from localization import t, resolve_button_key, load_strings, STR
from keyboards import build_keyboard, get_language_keyboard
from subscriptions import (
    get_user_subscriptions,
    subscribe_user,
    unsubscribe_user,
    load_groups
)


class MainMenu:

    def __init__(self):
        # Таблица обработчиков состояний
        self.state_handlers = {
            STATE_LANGUAGE: self.handle_language,
            STATE_WAITING_NAME: self.handle_name,
            STATE_SUBSCRIBE: self.handle_subscribe,
            STATE_UNSUBSCRIBE: self.handle_unsubscribe
        }


    # -----------------------------
    # ГЛАВНЫЙ РОУТЕР
    # -----------------------------
    async def handle(self, update, user_id, text, state):
        handler = self.state_handlers.get(state)

        if handler:
            return await handler(update, user_id, text)

        # Если состояние — это меню
        return await self.handle_menu(update, user_id, text, state)


    # -----------------------------
    # ОБРАБОТКА МЕНЮ
    # -----------------------------
    async def handle_menu(self, update, user_id, text, section):
        key, info = resolve_button_key(section, text)

        if not key:
            await update.message.reply_text(STR.get("error_massage"))
            return

        if info["type"] == "answer":
            return await self.handle_answer(update, user_id, key, section)

        if info["type"] == "state":
            return await self.handle_state(update, user_id, info)


    # -----------------------------
    # ANSWER BUTTONS
    # -----------------------------
    async def handle_answer(self, update, user_id, key, section):

        # список подписок
        if key == "list":
            return await self.show_subscriptions(update, user_id)
        a = str(key)
        answer = t("main_menu.answers."+ a)
        await update.message.reply_text(answer, reply_markup=build_keyboard(section))


    # -----------------------------
    # STATE BUTTONS
    # -----------------------------
    async def handle_state(self, update, user_id, info):
        next_state = info["next_state"]

        if next_state == "language_menu":
            user_state[user_id] = STATE_LANGUAGE
            await update.message.reply_text("👉 🌍💬", reply_markup=get_language_keyboard())
            return

        if next_state == STATE_SUBSCRIBE:
            user_state[user_id] = STATE_SUBSCRIBE
            await update.message.reply_text(
                t("subscribe.answers.request_subscribe"),
                reply_markup=build_keyboard("subscribe")
            )
            return

        if next_state == STATE_UNSUBSCRIBE:
            return await self.enter_unsubscribe(update, user_id)

        # обычный переход
        user_state[user_id] = next_state
        await update.message.reply_text(
            t("choose_an_option"),
            reply_markup=build_keyboard(next_state)
        )


    # -----------------------------
    # СОСТОЯНИЕ: ВВОД ИМЕНИ
    # -----------------------------
    async def handle_name(self, update, user_id, text):
        user_name[user_id] = text
        user_state[user_id] = "main_menu"

        await update.message.reply_text(
            t("start_questions.answers.ask_name", name=text),
            reply_markup=build_keyboard("main_menu")
        )


    # -----------------------------
    # СОСТОЯНИЕ: ВЫБОР ЯЗЫКА
    # -----------------------------
    async def handle_language(self, update, user_id, text):
        lang = resolve_button_key("language_menu", text)[0]

        if lang:
            user_lang[user_id] = lang
            load_strings(lang)
            user_state[user_id] = "main_menu"
            await update.message.reply_text(
                t("choose_an_option"),
                reply_markup=build_keyboard("main_menu")
            )
            return

        await update.message.reply_text("👉 🌍💬", reply_markup=get_language_keyboard())


    # -----------------------------
    # СОСТОЯНИЕ: ПОДПИСКА
    # -----------------------------
    async def handle_subscribe(self, update, user_id, text):
        user_input = text
        if user_input == t("subscribe.buttons.cancel"):
            user_state[user_id] = "main_menu"
            await update.message.reply_text(t("choose_an_option"), reply_markup=build_keyboard("main_menu"))
            return
        else:
            result = subscribe_user(user_id, user_input)
            if result == "exists":
                await update.message.reply_text(t("subscribe.answers.error_subscribe_duble_request", name = user_input))
                return
            if result == "group_not_found":
                await update.message.reply_text(t("subscribe.answers.error_subscribe"))
                return
        await update.message.reply_text(t("subscribe.answers.confirm_subscribe", name = user_input))
        user_state[user_id] = STATE_SUBSCRIBE


    # -----------------------------
    # СОСТОЯНИЕ: ОТПИСКА
    # -----------------------------
    async def handle_unsubscribe(self, update, user_id, text):
        user_input = text
        if user_input == t("subscribe.buttons.cancel"):
            user_state[user_id] = "main_menu"
            await update.message.reply_text(t("choose_an_option"), reply_markup=build_keyboard("main_menu"))
            return
        else:
            try:
                index = int(text) - 1
            except:
                await update.message.reply_text("Введите номер.")
                return

            subs = get_user_subscriptions(user_id)

            if index < 0 or index >= len(subs):
                await update.message.reply_text("Неверный номер.")
                return

            group_name = subs[index]["group"]
            unsubscribe_user(user_id, group_name)

            await update.message.reply_text(f"Вы отписаны от {group_name}.")
            user_state[user_id] = STATE_UNSUBSCRIBE


    # -----------------------------
    # ПОКАЗ СПИСКА ПОДПИСОК
    # -----------------------------
    async def show_subscriptions(self, update, user_id):
        subs = get_user_subscriptions(user_id)
        groups = load_groups()

        if not subs:
            await update.message.reply_text(t("no_subscriptions"))
            return

        msg = t("main_menu.answers.list") + "\n\n"

        for i, s in enumerate(subs, start=1):
            g = next((g for g in groups if g["name"] == s["group"]), None)
            if g:
                msg += f"{i}. {g['title']} ({g['name']})\n{g['description']}\n\n"
            else:
                msg += f"{i}. {s['group']}\n\n"

        await update.message.reply_text(msg)


    # -----------------------------
    # ВХОД В МЕНЮ ОТПИСКИ
    # -----------------------------
    async def enter_unsubscribe(self, update, user_id):
        subs = get_user_subscriptions(user_id)
        groups = load_groups()

        if not subs:
            await update.message.reply_text(t("no_subscriptions"))
            user_state[user_id] = "main_menu"
            return

        msg = "Ваши подписки:\n\n"
        for i, s in enumerate(subs, start=1):
            g = next((g for g in groups if g["name"] == s["group"]), None)
            msg += f"{i}. {g['title']} ({g['name']})\n"

        msg += "\nВведите номер группы для отписки."
        user_state[user_id] = STATE_UNSUBSCRIBE

        await update.message.reply_text(msg, reply_markup=build_keyboard("unsubscribe"))
