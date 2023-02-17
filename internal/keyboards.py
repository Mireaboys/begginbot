from telebot import types
from internal.content import bio_questions

def get_keyboard_bio(skip=0):
    keyboard = types.InlineKeyboardMarkup()
    for i, part in  enumerate(bio_questions):
        if skip == i+1: continue
        keyboard.add(types.InlineKeyboardButton(text=part, callback_data=f"bio_part_{i+1}"))
    return keyboard