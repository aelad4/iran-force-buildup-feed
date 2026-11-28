// Service worker: offline app shell, fresh data when online, Web Push notifications.
const CACHE = 'ifb-v1';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png',
  './icons/apple-touch-icon.png', './icons/favicon-64.png'];
const DATA = /\/(feed|digests)\.json$/;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  const url = new URL(req.url);
  // Data and the page itself: network first, so the feed is always fresh when online.
  if (DATA.test(url.pathname) || req.mode === 'navigate') {
    e.respondWith(fetch(req, {cache: 'no-store'}).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(DATA.test(url.pathname) ? url.pathname : './', copy)); }
      return res;
    }).catch(() => caches.match(DATA.test(url.pathname) ? url.pathname : './').then(r => r || caches.match('./index.html'))));
    return;
  }
  e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return res;
  })));
});

self.addEventListener('push', e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (_) { d = {body: e.data && e.data.text()}; }
  const title = d.title || 'פיד התעצמות צבאית של איראן';
  e.waitUntil(self.registration.showNotification(title, {
    body: d.body || 'יש עדכון חדש בפיד',
    icon: 'icons/icon-192.png', badge: 'icons/favicon-64.png',
    tag: d.tag || 'feed-update', renotify: true, lang: 'he', dir: 'rtl',
    data: {url: d.url || './#new'}
  }));
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  const target = new URL(e.notification.data && e.notification.data.url || './#new', self.registration.scope).href;
  e.waitUntil(self.clients.matchAll({type: 'window', includeUncontrolled: true}).then(list => {
    for (const c of list) { if (c.url.startsWith(self.registration.scope)) { c.navigate(target); return c.focus(); } }
    return self.clients.openWindow(target);
  }));
});
