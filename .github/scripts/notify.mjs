// Sends a Web Push notification to every subscription in the PUSH_SUBSCRIPTIONS secret
// when feed.json gains items. Subscriptions: one JSON object per line, or a JSON array.
import { execSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import webpush from 'web-push';

const { VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY, PUSH_SUBSCRIPTIONS = '', APP_URL, TEST_MESSAGE, PAYLOAD_FILE } = process.env;
if (!VAPID_PRIVATE_KEY || !PUSH_SUBSCRIPTIONS.trim()) {
  console.log('VAPID_PRIVATE_KEY or PUSH_SUBSCRIPTIONS secret is not set; nothing to send.');
  process.exit(0);
}

function parseSubs(raw) {
  const t = raw.trim();
  if (t.startsWith('[')) return JSON.parse(t);
  return t.split(/\n+/).map(l => l.trim()).filter(Boolean).map(l => JSON.parse(l));
}

const urls = f => new Set((f.items || []).map(i => i.url));
const current = JSON.parse(readFileSync('feed.json', 'utf8'));
let previous = { items: [] };
try { previous = JSON.parse(execSync('git show HEAD~1:feed.json', { encoding: 'utf8', maxBuffer: 64 << 20 })); } catch { /* first commit */ }
const before = urls(previous);
const fresh = (current.items || []).filter(i => !before.has(i.url));

let title, body, url = './#new', tag = 'feed-update';
if (PAYLOAD_FILE) {
  ({ title, body, url = url, tag = tag } = JSON.parse(readFileSync(PAYLOAD_FILE, 'utf8')));
} else if (TEST_MESSAGE) {
  title = 'בדיקת התראות'; body = TEST_MESSAGE;
} else {
  if (!fresh.length) { console.log('No new items in this push; nothing to send.'); process.exit(0); }
  const top = [...fresh].sort((a, b) => (b.significance || 0) - (a.significance || 0));
  const high = fresh.filter(i => (i.significance || 0) >= 3).length;
  title = `${fresh.length} פריטים חדשים בפיד` + (high ? ` (${high} משמעותיים)` : '');
  let bullet = '';
  try { bullet = (JSON.parse(readFileSync('digests.json', 'utf8')).digests || [])[0]?.bullets?.[0] || ''; } catch { /* optional */ }
  body = bullet || top.slice(0, 2).map(i => '• ' + i.title).join('\n');
  if (body.length > 220) body = body.slice(0, 217) + '…';
}

console.log('Notification:', title, '|', body);
webpush.setVapidDetails(APP_URL || 'https://github.com', VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY);
const payload = JSON.stringify({ title, body, url, tag });
let ok = 0, gone = 0, failed = 0;
for (const sub of parseSubs(PUSH_SUBSCRIPTIONS)) {
  try { await webpush.sendNotification(sub, payload, { TTL: 86400, urgency: 'normal' }); ok++; }
  catch (e) {
    if (e.statusCode === 404 || e.statusCode === 410) { gone++; console.log('Expired subscription (remove it from the secret):', sub.endpoint.slice(0, 60)); }
    else { failed++; console.log('Send failed:', e.statusCode, e.body || e.message); }
  }
}
console.log(`sent=${ok} expired=${gone} failed=${failed} new_items=${fresh.length}`);
if (failed && !ok) process.exit(1);
