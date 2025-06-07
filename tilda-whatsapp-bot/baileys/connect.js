const { default: makeWASocket, useSingleFileAuthState } = require('@whiskeysockets/baileys');
const fs = require('fs');
const path = require('path');

const id = process.argv[2];
if (!id) {
  console.error('Usage: node connect.js <telegram_id>');
  process.exit(1);
}

const sessionDir = path.join(__dirname, '..', 'sessions', String(id));
if (!fs.existsSync(sessionDir)) fs.mkdirSync(sessionDir, { recursive: true });
const { state, saveState } = useSingleFileAuthState(path.join(sessionDir, 'session.json'));

async function connect() {
  const sock = makeWASocket({ auth: state });
  sock.ev.on('creds.update', saveState);
  sock.ev.on('connection.update', (update) => {
    const { qr, connection } = update;
    if (qr) {
      const qrImage = Buffer.from(qr).toString('base64');
      console.log(qrImage);
    }
    if (connection === 'open') {
      fs.writeFileSync(path.join(sessionDir, 'jid'), sock.user.id);
      process.exit(0);
    }
    if (connection === 'close') {
      process.exit(1);
    }
  });
}

connect();
