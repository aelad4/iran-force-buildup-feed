#!/usr/bin/env python3
"""Print recent messages of public Telegram channels as JSON.

Usage: python3 tg_fetch.py HANDLE [HANDLE ...]
Reads https://t.me/s/<handle> (public web preview). Channels without a preview return an empty list.
"""
import html, json, re, subprocess, sys

def fetch(handle):
    out = subprocess.run(
        ["curl", "-sS", "-m", "25", "-L", "-A", "Mozilla/5.0", f"https://t.me/s/{handle}"],
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    result = {h: parse(h, fetch(h)) for h in sys.argv[1:]}
    print(json.dumps(result, ensure_ascii=False, indent=1))
