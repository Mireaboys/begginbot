## BegginBot

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