import json
import logging
import os
import subprocess
from pathlib import Path
from urllib.parse import unquote_plus

from dotenv import load_dotenv

from flask import Flask, request, abort
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()
TG_TOKEN = os.getenv("TG_TOKEN")
ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))
DATA_FILE = Path(__file__).resolve().parent / 'db.json'
SESSIONS_DIR = Path(__file__).resolve().parent / 'sessions'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_to_whatsapp(telegram_id: int, text: str) -> bool:
    """Send message via Baileys. Returns True on success."""
    try:
        subprocess.run(
            ["node", "baileys/send.js", str(telegram_id)],
            input=text.encode(), check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to send via WhatsApp: %s", e)
        return False


class SessionStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.touch(exist_ok=True)
        if not self.path.read_text().strip():
            self.path.write_text('[]')

    def load(self):
        return json.loads(self.path.read_text())

    def save(self, data):
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def get(self, telegram_id):
        for row in self.load():
            if row.get('telegram_id') == telegram_id:
                return row
        return None

    def set_status(self, telegram_id, status):
        data = self.load()
        for row in data:
            if row.get('telegram_id') == telegram_id:
                row['status'] = status
                break
        else:
            data.append({'telegram_id': telegram_id,
                         'company': '',
                         'session_path': str(SESSIONS_DIR/str(telegram_id)),
                         'status': status})
        self.save(data)


store = SessionStore(DATA_FILE)
app = Flask(__name__)
telegram_app = None


def restricted(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user and update.effective_user.id != ADMIN_ID:
            return
        return await func(update, context)
    return wrapper


def build_keyboard():
    return ReplyKeyboardMarkup([
        ["Создать подключение"],
        ["QR-код отсканирован"],
        ["Статус подключения"],
        ["Отключить"],
        ["О боте"],
    ], resize_keyboard=True)


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать", reply_markup=build_keyboard())


@restricted
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "О боте":
        await update.message.reply_text("Bot by Andrei Sokolov @andysklv")
    elif text == "Создать подключение":
        proc = subprocess.Popen([
            "node", "baileys/connect.js", str(ADMIN_ID)
        ], stdout=subprocess.PIPE, text=True)
        qr_b64 = proc.stdout.readline().strip()
        store.set_status(ADMIN_ID, 'waiting_qr')
        if qr_b64:
            await update.message.reply_photo(qr_b64)
        else:
            await update.message.reply_text("Не удалось сгенерировать QR")
    elif text == "QR-код отсканирован":
        store.set_status(ADMIN_ID, 'connected')
        await update.message.reply_text("Сессия активна")
    elif text == "Статус подключения":
        session = store.get(ADMIN_ID)
        status = session['status'] if session else 'idle'
        await update.message.reply_text(status)
    elif text == "Отключить":
        session_path = SESSIONS_DIR/str(ADMIN_ID)
        if session_path.exists():
            for f in session_path.glob('*'):
                f.unlink()
            session_path.rmdir()
        store.set_status(ADMIN_ID, 'idle')
        await update.message.reply_text("Сессия удалена")


def run_bot():
    global telegram_app
    telegram_app = Application.builder().token(TG_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    return telegram_app


@app.post('/send')
def send():
    user_id = request.form.get('user_id', type=int)
    if not user_id:
        abort(403)
    session = store.get(user_id)
    if not session or session['status'] != 'connected':
        if telegram_app:
            telegram_app.bot.send_message(chat_id=ADMIN_ID, text='Проблема с подключением к WhatsApp')
        abort(403)

    lines = []
    for key, value in request.form.items():
        value = unquote_plus(value)
        if key == 'Date':
            key = 'Дата выезда из гостиницы'
        lines.append(f"{key}: {value}")
    referer = request.headers.get('Referer')
    if referer:
        lines.append(f"Referer: {referer}")
    text = '\n'.join(lines)

    logger.info("Send to WhatsApp: %s", text)
    ok = send_to_whatsapp(user_id, text)
    if telegram_app:
        telegram_app.bot.send_message(chat_id=ADMIN_ID, text=text)
        if not ok:
            telegram_app.bot.send_message(chat_id=ADMIN_ID, text='Проблема с подключением к WhatsApp')
    if ok:
        return 'ok'
    abort(500)


from threading import Thread


def main():
    application = run_bot()

    def run_flask():
        app.run(host='127.0.0.1', port=8000)

    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    try:
        application.bot.send_message(chat_id=ADMIN_ID, text='Сервис запущен')
    except Exception as e:
        logger.warning("Failed to notify startup: %s", e)

    application.run_polling()


if __name__ == '__main__':
    main()

