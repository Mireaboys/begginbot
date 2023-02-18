# local imports
import os, sys

# external imports
import telebot
from telebot import types, custom_filters
from dotenv import load_dotenv

# internal imports
from internal import content
from internal import keyboards as kb
from internal.logger import new_logger
from internal.api import FakeAsyncApi
from internal.store import Store

load_dotenv()
log = new_logger()

token = os.getenv("BOT_TOKEN")
secret = os.getenv("SECRET")
mongo_conn = os.getenv("CONNECTION")
gpt_url = os.getenv("GPT_URL")

if None in [token, secret, gpt_url, mongo_conn]:
    log.error("Not found envs")
    sys.exit(1)

bot = telebot.TeleBot(token, parse_mode=None)
api = FakeAsyncApi(gpt_url)
store = Store(mongo_conn)

def message_next(m):
    bot.send_message(
        m.chat.id, 
        content.get_rand_facts(), 
        parse_mode=content.markdown
    )

@bot.message_handler(commands=['init'])
def handle_message_access(m):
    user = store.get_user(m.chat.id, admin=True)
    store.admins.append(user["uuid"])
    bot.send_message(m.chat.id, str(user))

class Access(custom_filters.SimpleCustomFilter):
    key='user_have_access'
    @staticmethod
    def check(m: types.Message):
        user = store.get_user(m.from_user.id)
        if user["access"]:
            return True
        bot.send_message(m.chat.id, "У тебя нет доступа к этому модулю, запросить /access")
        return False

bot.add_custom_filter(Access())

@bot.message_handler(commands=['access'])
def handle_message_access(m):
    bot.send_message(m.chat.id, "Напиши свое ФИО")
    bot.register_next_step_handler(m, user_access_step_0)

def user_access_step_0(m):
    if not m.text:
        return # TODO
    user = store.get_user(m.chat.id)
    user["name"] = m.text
    bot.send_message(m.chat.id, "Теперь своего руководителя и подразделение")
    bot.register_next_step_handler(m, user_access_step_1, user)

def user_access_step_1(m, user):
    if not m.text:
        return # TODO
    if not store.admins:
        bot.send_message(m.chat.id, "Не могу найти кому отправить запрос, попробуй позже")
        return
    user["about"] = m.text
    store.update_user(user)
    for a in store.admins:
        bot.send_message(a, f"@{m.from_user.username}\n{user['name']}\n*{user['about']}*\n_Запрашивает доступ_", 
                    reply_markup=kb.get_keyboard_access(user, true=True), parse_mode=content.markdown)
    bot.send_message(m.chat.id, "Я отправил сообщение выше, жди ответа. Пока можешь поразвлекать себя /roles")

@bot.message_handler(commands=['start', 'help'])
def handle_message_start(m):
    bot.send_message(
        m.chat.id, 
        content.bio[0], 
        reply_markup=kb.get_keyboard_bio(),
        parse_mode=content.markdown
    )

@bot.message_handler(commands=['company'], user_have_access=True)
def handle_message_company(m):
    message_next(m)
    # bot.send_message(
    #     m.chat.id, 
    #     content.bio[0], 
    #     reply_markup=kb.get_keyboard_bio(),
    #     parse_mode=content.markdown
    # )
    bot.send_message(
        m.chat.id, 
        "TODO"
    )

@bot.message_handler(commands=['roles'])
def handle_message_roles(m):
    message_next(m)
    roles = store.get_roles()
    bot.send_message(
        m.chat.id, 
        content.role_part_0,
        reply_markup=kb.get_keyboard_role(roles, selected=-1, start=False),
        parse_mode=content.markdown
    )

@bot.message_handler(commands=['Web3000toWeb2'])
def handle_message_web3000(m):
    bot.send_message(
        m.chat.id, 
        content.user_request
    )
    bot.register_next_step_handler(m, web3000)

def web3000(m):
    req = m.text
    if not req:
        bot.send_message(m.chat.id, content.require_text)
        return
    api.post(data={"text": m.text, "uuid": str(m.chat.id), "secret": secret})
    bot.send_message(m.chat.id, "Обработка сообщения займет какое то время, если все получится, я пришлю ответ")

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
        case ["role", "part", _]:
            part = int(data[-1])
            roles = store.get_roles()
            if len(roles) <= part:
                bot.edit_message_text("Информация устарела /roles",
                    c.from_user.id, c.message.id, 
                )
            role = roles[part]
            bot.edit_message_text(f'\t*{role["title"].title()}* - ' + role["about"] +\
                    "\n\nАктивные способности:\n\t\t" + '\n\t\t'.join(role["skills"]["active"]) +\
                    "\n\nПассивные способности:\n\t\t" + '\n\t\t'.join(role["skills"]["passive"]),
                c.from_user.id, c.message.id, 
                reply_markup=kb.get_keyboard_role(roles, selected=part),
                parse_mode=content.markdown
            )
        case ["role", "create"]:
            bot.edit_message_text("Создай через БД: TODO", # TODO
                c.from_user.id, c.message.id)
        case [_, "access", _]:
            uuid = int(data[0])
            action = data[-1]
            if action == "true":
                store.access(uuid, access=True)
                bot.send_message(uuid, "Доступ разрешен ✅ /company")
                bot.edit_message_reply_markup(c.message.chat.id, c.message.id, 
                        reply_markup=kb.get_keyboard_access({"uuid": uuid}, False))
            else:
                store.access(uuid, access=False)
                bot.send_message(uuid, "Доступ сброшен ❌")
                bot.edit_message_reply_markup(c.message.chat.id, c.message.id, 
                        reply_markup=kb.get_keyboard_access({"uuid": uuid}, True))
    return
