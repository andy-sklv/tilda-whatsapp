const { default: makeWASocket, useSingleFileAuthState } = require('@whiskeysockets/baileys');
const fs = require('fs');
const path = require('path');

const id = process.argv[2];
if (!id) {
  console.error('Usage: node send.js <telegram_id>');
  process.exit(1);
}

const sessionDir = path.join(__dirname, '..', 'sessions', String(id));
const jidPath = path.join(sessionDir, 'jid');
if (!fs.existsSync(jidPath)) {
  console.error('jid file not found');
  process.exit(1);
}
const jid = fs.readFileSync(jidPath, 'utf8').trim();
const { state, saveState } = useSingleFileAuthState(path.join(sessionDir, 'session.json'));

let text = '';
process.stdin.on('data', chunk => text += chunk.toString());
process.stdin.on('end', async () => {
  const sock = makeWASocket({ auth: state });
  sock.ev.on('creds.update', saveState);
  await sock.waitForConnectionUpdate(u => u?.connection === 'open');
  await sock.sendMessage(jid, { text });
  setTimeout(() => process.exit(0), 1000);
});
