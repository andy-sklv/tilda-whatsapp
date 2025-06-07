#!/bin/bash
set -e

INSTALL_DIR=/opt/tilda-bot
DOMAIN=onegin.troxy.tech

# Обновление пакетов и установка зависимостей
sudo apt-get update
sudo apt-get install -y curl unzip software-properties-common nginx

# Установка Python 3.11 + venv
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev

# pip, если не установлен
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11

# Установка certbot (esli nuzhen HTTPS)
sudo apt-get install -y certbot python3-certbot-nginx

# Установка nvm и Node.js 20
export NVM_DIR="$HOME/.nvm"
if [ ! -d "$NVM_DIR" ]; then
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
fi
export NVM_DIR="$HOME/.nvm"
source "$NVM_DIR/nvm.sh"
nvm install 20
nvm use 20

# Установка зависимостей в папке baileys
pushd baileys
npm install
popd

# Создание виртуального окружения и установка Python-зависимостей
python3.11 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Копирование проекта
sudo mkdir -p "$INSTALL_DIR"
sudo cp -r . "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Создание .env, если не существует
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Enter Telegram token:"; read TG
  sed -i "s|TG_TOKEN=|TG_TOKEN=$TG|" .env
  echo "Enter Telegram admin id:"; read ID
  sed -i "s|TELEGRAM_ADMIN_ID=|TELEGRAM_ADMIN_ID=$ID|" .env
fi


# Настройка systemd
sudo cp systemd/whatsapp-bot.service /etc/systemd/system/
sudo cp systemd/baileys-connect@.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable whatsapp-bot.service
sudo systemctl start whatsapp-bot.service

# Настройка Nginx
sudo ln -sf "$INSTALL_DIR"/nginx/tilda-whatsapp.conf /etc/nginx/sites-available/tilda-whatsapp.conf
sudo ln -sf /etc/nginx/sites-available/tilda-whatsapp.conf /etc/nginx/sites-enabled/tilda-whatsapp.conf
sudo nginx -t && sudo systemctl reload nginx

# Выпуск SSL сертификата
sudo certbot --nginx -d "$DOMAIN" || true

echo "✅ Ваш веб-хук готов: https://$DOMAIN/send"
