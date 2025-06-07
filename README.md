 Tilda WhatsApp Bot

This repository contains a sample implementation of the "Tilda → WhatsApp" integration. The project lives in the `tilda-whatsapp-bot` directory.

## Configuration

Copy `.env.example` to `.env` inside `tilda-whatsapp-bot` and put your Telegram bot token and admin ID there.

## Quick start

On an Ubuntu 24.04 server run the installer:

```bash
cd tilda-whatsapp-bot
sudo bash install.sh
```

The script installs Python 3.11, Node.js 20 and all dependencies, sets up systemd services and configures nginx with HTTPS for the domain **onegin.troxy.tech**. At the end it prints the webhook URL:

```
✅ Ваш веб-хук готов: https://onegin.troxy.tech/send
```

## Usage

1. Start the Telegram bot by sending `/start` to it.
2. Press **«Создать подключение»**. The bot will reply with a QR code that you need to scan with WhatsApp.
3. When WhatsApp confirms the scan press **«QR-код отсканирован»**.
4. Tilda should send forms via POST to `https://onegin.troxy.tech/send`.

Every request is forwarded to WhatsApp and duplicated to the Telegram chat. If the WhatsApp session is not active, the webhook replies with HTTP 403 and the bot notifies the admin.
The bot also sends notifications when the service starts or if there is a problem with the WhatsApp connection.