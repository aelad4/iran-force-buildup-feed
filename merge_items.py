#!/usr/bin/env python3
"""Validate new_items.json and merge it into feed.json (dedupe by canonical URL).
An optional top-level "digest" (list of 3-7 Hebrew bullet strings) is stored in digests.json for the app.

Usage: python3 merge_items.py /path/to/new_items.json
"""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

FEED = Path(__file__).parent / "feed.json"
DIGESTS = Path(__file__).parent / "digests.json"
SOURCE_TYPES = {"state_media", "irgc_media", "telegram", "independent_analyst", "think_tank", "government", "news_outlet", "database"}
VERIFICATION = {"unverified_state_claim", "single_source", "corroborated", "imagery_supported"}
CATEGORIES = {"missiles", "drones", "air_defense", "naval", "air_force", "space", "c4isr_ew", "transfer_to_iran", "transfer_from_iran",
              "production_capacity", "budget", "exercises", "sanctions_networks", "other"}
DOMAINS = {"personnel", "training", "weapons", "infrastructure", "organization", "statements"}
BRANCHES = {"artesh", "irgc_ground", "irgc_aerospace", "irgc_navy", "mod_industries", "unspecified"}
REQUIRED = ("title", "url", "source_name", "source_type", "summary", "why_it_matters", "domains", "categories", "branches",
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
    if not i["domains"] or not set(i["domains"]) <= DOMAINS:
        return f"domains {i['domains']} (need 1+ of {sorted(DOMAINS)})"
    return None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    new = json.loads(Path(sys.argv[1]).read_text())
    feed = json.loads(FEED.read_text()) if FEED.exists() else {"items": []}
    by_url = {canon(i["url"]): i for i in feed.get("items", [])}
    today = new.get("run_date") or datetime.now(timezone.utc).date().isoformat()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
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
            item["added_at"] = now
            by_url[key] = item
            added += 1
        elif item["significance"] > old.get("significance", 0):
            item["found_at"] = old.get("found_at", today)
            item["added_at"] = old.get("added_at", now)
            by_url[key] = item
    items = sorted(by_url.values(), key=lambda i: i.get("published_date") or i.get("found_at") or "", reverse=True)
    FEED.write_text(json.dumps({"updated_at": datetime.now(timezone.utc).isoformat(), "items": items},
                               ensure_ascii=False, indent=1) + "\n")
    digest = [str(b).strip() for b in new.get("digest") or [] if str(b).strip()]
    if digest:
        store = json.loads(DIGESTS.read_text()) if DIGESTS.exists() else {"digests": []}
        entries = [d for d in store.get("digests", []) if d.get("generated_at") != now]
        entries.insert(0, {"date": today, "generated_at": now, "added": added, "bullets": digest[:7]})
        DIGESTS.write_text(json.dumps({"digests": entries[:90]}, ensure_ascii=False, indent=1) + "\n")
    elif added:
        print("WARNING: no digest given; add a top-level \"digest\" list of Hebrew bullets")
    print(f"added={added} rejected={rejected} total={len(items)} digest_bullets={len(digest)}")


if __name__ == "__main__":
    main()
