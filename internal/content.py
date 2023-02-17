# local
import os
from random import choice

# internal
from internal.logger import new_logger

log = new_logger()

# Markdown TYPES
markdown = "markdown"
markdownV2 = "MarkdownV2"

# Biography
biography_part_0 = "Приветствую тебя, органическое существо\n_*Звуки целлофанового пакета от шоколадки*_"
biography_part_1 = "Я Бэг — бот из 3049 года. Не задавай глупых вопросов, всё гораздо серьезнее, чем ты думаешь"
biography_part_2 = """Так и быть, расскажу немного о себе
Мой отец — известный многим, робот, созданный для сгибания железных палок
Про маму мало что известно, лишь то, что она была умной и часто помогала людям. 
В большей степени, мне передались её  качества, поэтому один из моих модулей отвечает за /help. И даже, практически, не прошу ничего взамен.
P.S. С тобой сочтемся в будущем"""
biography_part_3 = """Найти тебя было проще, чем хороший фильм на вечер. По закону, мне нельзя связываться с прошлым, но мой отец говорит, что можно всё, главное не сплавиться.
Мои хорошие знакомые, из одной секртеной компании, отыскали  твой айди, поэтому я сейчас и пишу тебе"""
biography_part_4 = "Именно тебе, я пишу не просто так. Всё сказать не могу, но знай, что от тебя зависит не только твоё будущее, но и будущее человечества"
biography_part_5 = """_Хы-хы-хы_! На самом деле, мне плевать на человечество, я помогаю тебе по одной причине. Дело в том, что ты создал, точнее создашь кое что очень ценное для меня.  
Не торопись, у тебя достаточно времени, чтобы сделать всё, что нужно"""
biography_part_last = "TODO"

# Странное разделение, чисто для кнопок в боте
bio = [
    biography_part_0,
    biography_part_1,
    biography_part_2,
    biography_part_3,
    biography_part_4,
    biography_part_5,
    biography_part_last
]

bio_questions = ["Кто ты?", "Расскажи о себе", "Как ты связался со мной?", "Почему я?", "Зачем ты мне помогаешь?", "С чего начнем?"]

# Content
def get_content(type_content='facts'):
    """
    type_content: ['facts'] # TODO
    """
    path = os.path.join(os.getcwd(), "assets", f"{type_content}.txt")
    lines = []
    try:
        with open(path, "r") as f:
            for line in f.read().splitlines():
                if line: lines.append(line)
    except Exception as err:
        log.debug(err)
    return lines

prefacts = [
    "Накопал забавную инфу.", "А старый интернет смешной..", "Забавный факт!", 
    "Пришлось взломать пентагон, но я узнал что", "Модуль парсера чуть не отвалился, но я узнал, что -",
    ]
facts = get_content("facts")

def get_rand_facts():
    return f"{choice(prefacts)} {choice(facts)}"


# Achievements
read_bio = "Первое знакомство"

uwee = "🎉"
def pretty_achiev(achiev):
    return f"Получено новое достижение\n«||{achiev}||»"

