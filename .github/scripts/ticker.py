#!/usr/bin/env python3
"""Breaking-news ticker: pull the latest page of each configured Telegram channel, keep keyword matches
from the last N hours, and write ticker.json (raw, unvetted). Also writes push_payload.json when there
are new alert matches and the minimum interval since the last alert has passed.

Usage: python3 .github/scripts/ticker.py PREVIOUS_TICKER_JSON OUTPUT_DIR
"""
import json, re, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tg_fetch import fetch, parse  # noqa: E402

cfg = json.loads((ROOT / "ticker_config.json").read_text())
prev_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
try:
    prev = json.loads(prev_path.read_text())
except Exception:
    prev = {}
now = datetime.now(timezone.utc)
cutoff = now - timedelta(hours=cfg.get("window_hours", 48))
match, alert = re.compile(cfg["match"], re.I), re.compile(cfg["alert"], re.I)

items = {i["permalink"]: i for i in prev.get("items", []) if i.get("date") and datetime.fromisoformat(i["date"]) >= cutoff}
new, failed = [], []
for handle, opts in cfg["channels"].items():
    try:
        msgs = parse(handle, fetch(handle))
    except Exception as e:  # one bad channel must not stop the run
        failed.append(handle); print(f"{handle}: {e}"); continue
    if not msgs:
        failed.append(handle)
    req = re.compile(opts["require"], re.I) if opts.get("require") else None
    for m in msgs:
        if not m.get("permalink") or not m.get("date") or m["permalink"] in items:
            continue
        if datetime.fromisoformat(m["date"]) < cutoff:
            continue
        t = m["text"]
        hits = sorted({h.group(0) for h in match.finditer(t)})
        if not hits or (req and not req.search(t)):
            continue
        entry = {"permalink": m["permalink"], "channel": handle, "date": m["date"], "first_seen": now.isoformat(timespec="seconds"),
                 "text": t[:1500], "matched": hits[:8], "alert": bool(alert.search(t))}
        items[m["permalink"]] = entry; new.append(entry)
    time.sleep(0.4)

ordered = sorted(items.values(), key=lambda i: i["date"], reverse=True)[: cfg.get("max_items", 400)]
pending = prev.get("pending_alerts", 0) + sum(1 for e in new if e["alert"])
last_alert = prev.get("last_alert_at")
out = {"updated_at": now.isoformat(timespec="seconds"), "items": ordered, "failed_channels": failed,
       "last_alert_at": last_alert, "pending_alerts": pending}

interval = timedelta(minutes=cfg.get("alert_min_interval_minutes", 60))
if pending and (not last_alert or now - datetime.fromisoformat(last_alert) >= interval):
    first = next((e for e in new if e["alert"]), None) or next((i for i in ordered if i["alert"]), None)
    snippet = re.sub(r"\s+", " ", first["text"]).strip()[:140] if first else ""
    payload = {"title": f"מבזק: {pending} התאמות חשובות בטלגרם", "body": (f"{first['channel']}: {snippet}" if first else ""),
               "url": "./#ticker", "tag": "ticker"}
    (out_dir / "push_payload.json").write_text(json.dumps(payload, ensure_ascii=False))
    out["last_alert_at"], out["pending_alerts"] = now.isoformat(timespec="seconds"), 0

changed = [i["permalink"] for i in ordered] != [i["permalink"] for i in prev.get("items", [])] or out["pending_alerts"] != prev.get("pending_alerts", 0) or out["last_alert_at"] != last_alert
(out_dir / "ticker.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
(out_dir / "changed").write_text("1" if changed else "0")
print(f"new={len(new)} alerts_pending={pending} kept={len(ordered)} failed={failed} changed={changed}")
