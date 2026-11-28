#!/usr/bin/env python3
"""Print recent messages of public Telegram channels as JSON.

Usage: python3 tg_fetch.py [--days N] HANDLE [HANDLE ...]
Reads https://t.me/s/<handle> (public web preview, about 20 messages per page). With --days N it pages
backwards (?before=<id>) until messages are older than N days (max 60 pages per channel).
Channels without a preview return an empty list.
"""
import html, json, re, subprocess, sys, time
from datetime import datetime, timedelta, timezone

def fetch(handle, before=None):
    url = f"https://t.me/s/{handle}" + (f"?before={before}" if before else "")
    out = subprocess.run(
        ["curl", "-sS", "-m", "25", "-L", "-A", "Mozilla/5.0", url],
        capture_output=True, text=True)
    return out.stdout

def strip(s):
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()

def parse(handle, page):
    msgs = []
    for block in re.split(r'(?=<div class="tgme_widget_message_wrap)', page)[1:]:
        text = re.search(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', block, re.S)
        if not text:
            continue
        perma = re.search(r'href="(https://t\.me/[^"]+/\d+)"[^>]*class="tgme_widget_message_date"', block) or \
                re.search(r'class="tgme_widget_message_date"[^>]*href="(https://t\.me/[^"]+/\d+)"', block)
        date = re.search(r'<time[^>]*datetime="([^"]+)"', block)
        links = [html.unescape(u) for u in re.findall(r'<a[^>]+href="(https?://[^"]+)"', text.group(1))]
        msgs.append({"channel": handle, "permalink": perma.group(1) if perma else None,
                     "date": date.group(1) if date else None, "text": strip(text.group(1)), "links": links})
    return msgs

def post_id(m):
    mm = re.search(r"/(\d+)$", m["permalink"] or "")
    return int(mm.group(1)) if mm else None

def collect(handle, days):
    msgs, before = parse(handle, fetch(handle)), None
    if not days:
        return msgs
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    for _ in range(60):
        ids = [i for i in map(post_id, msgs) if i]
        oldest = min(msgs, key=lambda m: m["date"] or "9") if msgs else None
        if not ids or not oldest or not oldest["date"] or datetime.fromisoformat(oldest["date"]) < cutoff:
            break
        before = min(ids)
        page = parse(handle, fetch(handle, before))
        if not page:
            break
        msgs += page
        time.sleep(0.5)
    seen, out = set(), []
    for m in msgs:
        if m["permalink"] not in seen and (not m["date"] or datetime.fromisoformat(m["date"]) >= cutoff):
            seen.add(m["permalink"]); out.append(m)
    return out

if __name__ == "__main__":
    args = sys.argv[1:]
    days = 0
    if args[:1] == ["--days"] and len(args) > 2:
        days, args = int(args[1]), args[2:]
    if not args:
        sys.exit(__doc__)
    print(json.dumps({h: collect(h, days) for h in args}, ensure_ascii=False, indent=1))
