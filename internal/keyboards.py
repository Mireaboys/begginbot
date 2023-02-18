from telebot import types
from internal.content import bio_questions

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