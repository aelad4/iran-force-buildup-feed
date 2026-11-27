#!/usr/bin/env python3
"""Validate new_items.json and merge it into feed.json (dedupe by canonical URL).

Usage: python3 merge_items.py /path/to/new_items.json
"""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

FEED = Path(__file__).parent / "feed.json"
SOURCE_TYPES = {"state_media", "irgc_media", "telegram", "independent_analyst", "think_tank", "government", "news_outlet", "database"}
VERIFICATION = {"unverified_state_claim", "single_source", "corroborated", "imagery_supported"}
CATEGORIES = {"missiles", "drones", "air_defense", "naval", "air_force", "space", "c4isr_ew", "procurement_transfer",
              "production_capacity", "budget", "exercises", "sanctions_networks", "other"}
BRANCHES = {"artesh", "irgc_ground", "irgc_aerospace", "irgc_navy", "mod_industries", "unspecified"}
REQUIRED = ("title", "url", "source_name", "source_type", "summary", "why_it_matters", "categories", "branches",
            "significance", "verification")


def canon(url):
    p = urlsplit(url.strip())
    q = [(k, v) for k, v in parse_qsl(p.query) if not k.startswith(("utm_", "fbclid", "gclid"))]
    return urlunsplit((p.scheme.lower(), p.netloc.lower().removeprefix("www."), p.path.rstrip("/") or "/", urlencode(q), ""))


def problems(i):
    missing = [k for k in REQUIRED if k not in i]
    if missing:
        return f"missing {missing}"
    if not str(i["url"]).startswith(("http://", "https://")):
        return "bad url"
    if not isinstance(i["significance"], int) or not 1 <= i["significance"] <= 5:
        return "significance not 1-5"
    if i["source_type"] not in SOURCE_TYPES:
        return f"source_type {i['source_type']}"
    if i["verification"] not in VERIFICATION:
        return f"verification {i['verification']}"
    if not set(i["categories"]) <= CATEGORIES or not set(i["branches"]) <= BRANCHES:
        return "unknown category/branch"
    return None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    new = json.loads(Path(sys.argv[1]).read_text())
    feed = json.loads(FEED.read_text()) if FEED.exists() else {"items": []}
    by_url = {canon(i["url"]): i for i in feed.get("items", [])}
    today = new.get("run_date") or datetime.now(timezone.utc).date().isoformat()
    added = rejected = 0
    for item in new.get("items", []):
        why = problems(item)
        if why:
            rejected += 1
            print(f"REJECTED {item.get('url', '?')}: {why}")
            continue
        key = canon(item["url"])
        old = by_url.get(key)
        if old is None:
            item["found_at"] = today
            by_url[key] = item
            added += 1
        elif item["significance"] > old.get("significance", 0):
            item["found_at"] = old.get("found_at", today)
            by_url[key] = item
    items = sorted(by_url.values(), key=lambda i: i.get("published_date") or i.get("found_at") or "", reverse=True)
    FEED.write_text(json.dumps({"updated_at": datetime.now(timezone.utc).isoformat(), "items": items},
                               ensure_ascii=False, indent=1) + "\n")
    print(f"added={added} rejected={rejected} total={len(items)}")


if __name__ == "__main__":
    main()
