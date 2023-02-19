## BEGGIN BOT BASE
[DEMO](https://t.me/beggin_hack_bot) _Запроси доступы прямо через бота_
### Что успели сделать
* Знакомство с историей бота
* Регистрация\Авторизация
* Имитация проводника по ресурсам (Портал-лайк)
* Описание ролей
* Подготовка для быстрого развертывания проекта
* Интеграция OpenAI - команда /Web3000toWeb2 

### Основной стек технологий
* Python3
* MongoDB
* Docker
* Go*
* OpenAI*

### Install via Docker
```bash
git clone <this-repo>
cd <this-repo>
docker build -t begginbot:latest .
cp .env.bak .env # And edit this
docker run -d -e BOT_TOKEN=<YOUR_TOKEN> begginbot:latest
```

### Install via Docker-Compose (with mongodb)
```bash
git clone <this-repo>
cd <this-repo>
export MONGO_USERNAME=<USER> # ex. for Linux
export MONGO_PASSWORD=<PASS> # ex. for Linux
cp .env.bak .env # And edit this
docker-compose up -d
```

### Run on LinuxOS/Windows/MacOS
```bash
git clone <this-repo>
cd <this-repo>
python3 -m venv venv
source venv/bin/activate # Linux/Mac - bash/zsh
.\venv\Scripts\Activate.ps1 # Windows - PS
pip install -r deps.txt
cp .env.bak .env # And edit this
python main.py
```

### Разработчики
* Никольский Роман Fullstack Developer https://t.me/rombintu
* Виберг Даниил Product Manager & Marketing Specialist https://t.me/User_DK
* Голубенко Елизавета Product Manager & Designer https://t.me/golubenkolisa
* Никольский Антон Junior Analyst & Writer