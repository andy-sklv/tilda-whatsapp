#!/bin/bash
set -e

INSTALL_DIR=/opt/tilda-bot
DOMAIN=onegin.troxy.tech

sudo apt-get update
sudo apt-get install -y curl unzip python3.11-venv nginx

# nvm + node
export NVM_DIR="$HOME/.nvm"
if [ ! -d "$NVM_DIR" ]; then
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
fi
source "$NVM_DIR/nvm.sh"
nvm install 20

# install baileys deps
pushd baileys
npm install
popd

python3 -m venv venv
./venv/bin/pip install -r requirements.txt

sudo mkdir -p "$INSTALL_DIR"
sudo cp -r . "$INSTALL_DIR"
cd "$INSTALL_DIR"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Enter Telegram token:"; read TG; sed -i "s|TG_TOKEN=|TG_TOKEN=$TG|" .env
  echo "Enter Telegram admin id:"; read ID; sed -i "s|TELEGRAM_ADMIN_ID=|TELEGRAM_ADMIN_ID=$ID|" .env
fi

sudo cp systemd/whatsapp-bot.service /etc/systemd/system/
sudo cp systemd/baileys-connect@.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable whatsapp-bot.service
sudo systemctl start whatsapp-bot.service

sudo ln -sf "$INSTALL_DIR"/nginx/tilda-whatsapp.conf /etc/nginx/sites-available/tilda-whatsapp.conf
sudo ln -sf /etc/nginx/sites-available/tilda-whatsapp.conf /etc/nginx/sites-enabled/tilda-whatsapp.conf
sudo nginx -t && sudo systemctl reload nginx

sudo certbot --nginx -d "$DOMAIN" || true

echo "Ваш веб-хук готов: https://$DOMAIN/send"
