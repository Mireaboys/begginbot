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
from internal.asseter import Asseter

load_dotenv()
log = new_logger()

token = os.getenv("BOT_TOKEN")
secret = os.getenv("SECRET")
gpt_url = os.getenv("GPT_URL")
mongo_conn = os.getenv("CONNECTION")

if None in [token, mongo_conn]:
    log.error("Not found envs: BOT_TOKEN, CONNECTION")
    sys.exit(1)
if None in [secret, gpt_url]:
    log.warn("GPT_URL or SECRET: is None")

bot = telebot.TeleBot(token, parse_mode=None)
api = FakeAsyncApi(gpt_url)
store = Store(mongo_conn)
asseter = Asseter()

# Костыль для моментов, где обработки ошибки займет много времени
internal_error = "Internal error"

class Access(custom_filters.SimpleCustomFilter):
    """Проверка на доступ (фильтр)"""
    key='user_have_access'
    @staticmethod
    def check(m: types.Message):
        user = store.get_user(m.from_user.id)
        if user["access"]:
            return True
        bot.send_message(m.chat.id, "У тебя нет доступа к этому модулю, запросить /access")
        return False
    
bot.add_custom_filter(Access())

def message_next(m):
    """Отправка рандомного забавного факта"""
    bot.send_message(
        m.chat.id, 
        content.get_rand_facts(), 
        parse_mode=content.markdown
    )

@bot.message_handler(commands=['admin'])
def handle_message_users(m):
    """Первая страница для Администратора"""
    user = store.get_user(m.from_user.id)
    if not user["admin"]:
        bot.send_message(m.chat.id, "👤 Доступ запрещен")
        return
    users = store.get_users(with_admins=False)
    if not users:
        bot.send_message(m.chat.id, "Пользователи не найдены")
        return
    bot.send_message(m.chat.id, "👨🏼‍💻 Пользователи",reply_markup=kb.get_keyboard_users(users))
    
@bot.message_handler(commands=['access'])
def handle_message_access(m):
    """Запросить доступ и зарегать пользователя"""
    user = store.get_user(m.chat.id)
    if user["access"] == True:
        bot.send_message(m.chat.id, "У тебя уже есть доступ /company")
        return
    bot.send_message(m.chat.id, "👤 Напиши свое ФИО\n/cancel - Отмена")
    bot.register_next_step_handler(m, user_access_step_0)

def user_access_step_0(m):
    if not m.text:
        bot.send_message(m.chat.id, "Ожидается текст")
        return # TODO
    elif m.text == "/cancel":
        bot.send_message(m.chat.id, "Отмена операции")
        return
    user = store.get_user(m.chat.id)
    user["name"] = m.text
    bot.send_message(m.chat.id, "👩🏽‍💼 Теперь своего руководителя и подразделение\n/cancel - Отмена")
    bot.register_next_step_handler(m, user_access_step_1, user)

def user_access_step_1(m, user):
    if not m.text:
        bot.send_message(m.chat.id, "Ожидается текст")
        return # TODO
    elif m.text == "/cancel":
        bot.send_message(m.chat.id, "Отмена операции")
        return
    if not store.admins:
        bot.send_message(m.chat.id, "Не могу найти кому отправить запрос, попробуй позже")
        return
    user["about"] = m.text
    store.update_user(user)
    username = m.from_user.username if m.from_user.username else "noname"
    store.refresh_admins() # TODO
    for a in store.admins:
        bot.send_message(a, f"@{username}\n{user['name']}\n{user['about']}\n\nЗапрашивает доступ", 
                    reply_markup=kb.get_keyboard_access(user, true=True))
    bot.send_message(m.chat.id, "Я отправил сообщение выше, жди ответа. Пока можешь поразвлекать себя /roles")

@bot.message_handler(commands=['init']) # DEV
def handle_message_init(m):
    """FAKE ADMIN"""
    user = store.get_user(m.chat.id, admin=True)
    store.refresh_admins()
    bot.send_message(m.chat.id, str(user))

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
    bot.send_message(
        m.chat.id, 
        "🗄 Проводник", 
        reply_markup=kb.get_keyboard_explorer(asseter.typesdoc),
    )

@bot.message_handler(commands=['roles'])
def handle_message_roles(m):
    message_next(m)
    roles = store.get_roles()
    bot.send_message(
        m.chat.id, 
        content.role_part_0,
        reply_markup=kb.get_keyboard_roles(roles, selected=-1, start=False),
        parse_mode=content.markdown
    )

@bot.message_handler(commands=['Web3000toWeb2'])
def handle_message_web3000(m):
    """CHAT GPT3 OPENAI - фейковая асинхроность в другом потоке"""
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
    """Дальше идет магия колбеков"""
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
                reply_markup=kb.get_keyboard_roles(roles, selected=part),
                parse_mode=content.markdown
            )
        case ["role", "create"]:
            bot.edit_message_text("Создай через БД: TODO", # TODO
                c.from_user.id, c.message.id)
        case ["role", "start", _]:
            part = int(data[-1])
            roles = store.get_roles(full=True)
            if len(roles) <= part:
                bot.edit_message_text("Информация устарела /roles",
                    c.from_user.id, c.message.id, 
                )
            role = roles[part]
            bot.edit_message_text(f"Задача _{role['task']['title']}_\nОписание: {role['task']['description']}",
                c.from_user.id, c.message.id, reply_markup=kb.get_keyboard_role(role), parse_mode=content.markdown
            )
            bot.edit_message_text("В разработке...")
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
        case ["refresh", "users"]:
            users = store.get_users(with_admins=False)
            bot.edit_message_text("👩🏽‍💼 Пользователи",
                c.from_user.id, c.message.id, 
                reply_markup=kb.get_keyboard_users(users))
        case ["users", _, ">"]:
            start_i = int(data[1])
            users = store.get_users(with_admins=False)
            if start_i <= 0: start_i = 0
            bot.edit_message_text("👩‍💻 Пользователи",
                c.from_user.id, c.message.id, 
                reply_markup=kb.get_keyboard_users(users, start_i=start_i))

        case ["user", "id", _]:
            _id = data[-1]
            user = store.get_user_by_id(_id)
            if not user:
                bot.send_message(c.message.chat.id, "Пользователя больше не существует, обновите список")
                return
            keyboard = kb.get_keyboard_access(user, true=not user["access"])
            keyboard.add(types.InlineKeyboardButton(text="↩️", callback_data=f"users_{0}_>"))
            bot.edit_message_text(f"{user['name']}\n{user['about']}", 
                    c.from_user.id, c.message.id, 
                    reply_markup=keyboard)
        case ["photo", ">"]:
            photo = asseter.get_rand_photo()
            if not photo:
                bot.send_message(c.message.chat.id, "Нет фотографий")
                return
            bot.delete_message(c.from_user.id, c.message.id)
            bot.send_photo(c.from_user.id, photo, reply_markup=kb.get_keyboard_photo_navigation())
        case ["doc", "id", _]:
            idx = int(data[-1])
            if idx >= len(asseter.documents):
                bot.send_message(c.message.chat.id, internal_error)
                return
            doc_name = asseter.documents[idx]
            doc = asseter.get_doc_by_name(doc_name)
            if not doc:
                bot.send_message(c.message.chat.id, internal_error)
                return
            bot.send_document(c.message.chat.id, doc)
        case ["typesdoc", "id", _]:
            idx = int(data[-1])
            if idx >= len(asseter.typesdoc):
                bot.send_message(c.message.chat.id, internal_error)
                return
            match asseter.typesdoc[idx]:
                case "Фотографии":
                    photo = asseter.get_rand_photo()
                    if not photo:
                        bot.send_message(c.message.chat.id, "Нет фотографий")
                        return
                    bot.send_photo(c.from_user.id, photo, reply_markup=kb.get_keyboard_photo_navigation())
                case "Документы":
                    if not asseter.documents:
                        bot.send_message(c.message.chat.id, "Нет документов")
                        return
                    asseter.refresh_documents()
                    bot.send_message(
                        c.message.chat.id, 
                        "📁 Документы", 
                        reply_markup=kb.get_keyboard_doc(asseter.documents))

    return
