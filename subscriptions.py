import json
import os

GROUPS_FILE = "groups.json"            # список всех доступных групп
USER_GROUPS_FILE = "users_groups.json" # подписки пользователей


# ============================================================
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def ensure_file(path, default_data):
    """Создаёт файл, если его нет."""
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)


# ============================================================
#  ГРУППЫ (groups.json)
# ============================================================

def load_groups():
    ensure_file(GROUPS_FILE, {"groups": []})

    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("groups", [])


def group_exists(group_name):
    return any(g["name"] == group_name for g in load_groups())


# ============================================================
#  ПОДПИСКИ ПОЛЬЗОВАТЕЛЕЙ (users_groups.json)
# ============================================================

def load_user_subscriptions():
    ensure_file(USER_GROUPS_FILE, {"subscriptions": {}})

    with open(USER_GROUPS_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("subscriptions", {})


def save_user_subscriptions(data):
    with open(USER_GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump({"subscriptions": data}, f, ensure_ascii=False, indent=2)


def get_user_subscriptions(user_id):
    data = load_user_subscriptions()
    return data.get(str(user_id), [])


def user_has_group(user_id, group_name):
    subs = get_user_subscriptions(user_id)
    return any(s["group"] == group_name for s in subs)


def subscribe_user(user_id, group_name, sensitivity="average"):
    """Подписывает пользователя и сохраняет в JSON."""

    # Проверка существования группы
    if not group_exists(group_name):
        return "group_not_found"

    data = load_user_subscriptions()
    user_key = str(user_id)

    if user_key not in data:
        data[user_key] = []

    # Уже подписан?
    if any(s["group"] == group_name for s in data[user_key]):
        return "exists"

    # Добавляем
    data[user_key].append({
        "group": group_name,
        "sensitivity": sensitivity
    })

    save_user_subscriptions(data)
    return "added"


def unsubscribe_user(user_id, group_name):
    """Удаляет подписку пользователя из JSON."""
    data = load_user_subscriptions()
    user_key = str(user_id)

    if user_key not in data:
        return "not_found"

    before = len(data[user_key])
    data[user_key] = [s for s in data[user_key] if s["group"] != group_name]

    if len(data[user_key]) == before:
        return "not_found"

    save_user_subscriptions(data)
    return "removed"
