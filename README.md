 Tilda WhatsApp Bot

This repository contains a sample implementation of the "Tilda → WhatsApp" integration. The project lives in the `tilda-whatsapp-bot` directory.

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