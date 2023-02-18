from telebot import types
from internal.content import bio_questions

users_on_page = 5

def get_keyboard_bio(skip=0):
    keyboard = types.InlineKeyboardMarkup()
    for i, part in  enumerate(bio_questions):
        if skip == i+1: continue
        keyboard.add(types.InlineKeyboardButton(text=part, callback_data=f"bio_part_{i+1}"))
    return keyboard

def get_keyboard_role(roles, selected=0, start=True):
    keyboard = types.InlineKeyboardMarkup()
    if not roles:
        keyboard.add(types.InlineKeyboardButton(text="Роли не найдены. Добавить", callback_data=f"role_create"))
        return keyboard
    for i, role in enumerate(roles):
        if i == selected: continue
        keyboard.add(types.InlineKeyboardButton(text=role["title"].title(), callback_data=f"role_part_{i}"))
    if start:
        keyboard.add(types.InlineKeyboardButton(text="Подтвердить выбор", callback_data=f"role_start_{selected}"))
    return keyboard

def get_keyboard_access(user, true=True):
    keyboard = types.InlineKeyboardMarkup()
    if true:
        keyboard.add(types.InlineKeyboardButton(
            text="Разрешить ✅", callback_data=f"{user['uuid']}_access_true"))
    else:
        keyboard.add(types.InlineKeyboardButton(
            text="Исключить ❌", callback_data=f"{user['uuid']}_access_false"))
    return keyboard

def get_keyboard_users(users, start_i=0):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    btn_refresh = types.InlineKeyboardButton(text="🔄", callback_data=f"refresh_users")
    btn_next_r = types.InlineKeyboardButton(text="➡️", callback_data=f"users_{start_i+users_on_page}_>")
    btn_next_l = types.InlineKeyboardButton(text="⬅️", callback_data=f"users_{start_i-users_on_page}_>")
    for i in range(start_i, start_i + users_on_page):
        if i == len(users): break
        if users[i]["name"] == "": continue
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"{users[i]['name']}", 
                callback_data=f"user_id_{users[i]['_id']}"))

    if start_i == 0 and start_i + users_on_page >= len(users):
        keyboard.add(btn_refresh)
    elif start_i + users_on_page >= len(users): 
        keyboard.add(btn_next_l, btn_refresh)
    elif start_i == 0: 
        keyboard.add(btn_refresh, btn_next_r)
    else: 
        keyboard.add(btn_next_l, btn_refresh, btn_next_r,)
    return keyboard