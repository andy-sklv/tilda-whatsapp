# Tilda WhatsApp Bot

This repository contains a sample implementation of the "Tilda → WhatsApp" integration. The project lives in the `tilda-whatsapp-bot` directory.

## Configuration

Edit `tilda-whatsapp-bot/bot.py` and set your Telegram bot token and admin ID in the constants `TG_TOKEN` and `ADMIN_ID` at the top of the file.

## Quick start

On an Ubuntu 24.04 server run the installer:

```bash
cd tilda-whatsapp-bot
sudo bash install.sh
```

The script installs Python 3.11, Node.js 20 and all dependencies, sets up systemd services and configures nginx with HTTPS for the domain **onegin.troxy.ru**. At the end it prints the webhook URL:

```
✅ Ваш веб-хук готов: https://onegin.troxy.ru/send
```

## Usage

1. Start the Telegram bot by sending `/start` to it.
2. Choose **«Создать подключение»** and scan the QR code from WhatsApp.
3. After scanning press **«QR-код отсканирован»**.
4. Tilda should send forms via POST to `https://onegin.troxy.ru/send`.

Every request is forwarded to WhatsApp and duplicated to the Telegram chat. The first request from Tilda is used for verification and always returns `ok`.
The bot also sends notifications when the service starts or if there is a problem with the WhatsApp connection.