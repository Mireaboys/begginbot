# local imports
import os, sys

# external imports
import telebot
from telebot import types
from dotenv import load_dotenv

# internal imports
from internal import content
from internal import keyboards as kb
from internal.logger import new_logger

load_dotenv()
log = new_logger()

token = os.getenv("BOT_TOKEN")


if None in [token]:
    log.error("Not found envs")
    sys.exit(1)

bot = telebot.TeleBot(token, parse_mode=None)

def message_next(m):
    bot.send_message(
        m.chat.id, 
        content.get_rand_facts(), 
        parse_mode=content.markdown
    )

@bot.message_handler(commands=['start', 'help'])
def handle_message_start(m):
    bot.send_message(
        m.chat.id, 
        content.bio[0], 
        reply_markup=kb.get_keyboard_bio(),
        parse_mode=content.markdown
    )

@bot.callback_query_handler(func=lambda c: c.data)
def callback_bot(c: types.CallbackQuery):
    data = c.data.split("_")
    match data:
        case ["bio", "part", _]:
            part = int(data[-1])
            if part == 1:
                bot.send_message(c.from_user.id, 
                    content.pretty_achiev(content.read_bio), parse_mode=content.markdownV2)
                # bot.send_message(c.from_user.id, content.uwee)
            bot.edit_message_text(content.bio[part],
                c.from_user.id, c.message.id, 
                reply_markup=kb.get_keyboard_bio(part),
                parse_mode=content.markdown
            )
    return
