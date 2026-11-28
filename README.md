# Iran Force Buildup OSINT Feed

A scheduled Claude Code task runs daily, researches Iran's military force buildup from public sources,
and pushes new scored items to `feed.json`. `index.html` (GitHub Pages) displays the feed.

- `ANALYST_PROMPT.md` - the instructions the daily task follows
- `tg_fetch.py` - reads public Telegram channel previews
- `merge_items.py` - validates, dedupes and merges new items into `feed.json`
- `index.html` - the dashboard (filters: category, branch, source type, verification, significance, date, search)

Item titles, summaries and notes are written in Hebrew; the dashboard is Hebrew (RTL).

Limits: Iranian state-media sites refuse connections from the task's network (Telegram is used instead);
X/Twitter and paywalled Janes are not reachable; IISS, ISW and Iran Watch may return 403.
Output is automated analysis of open sources, including state propaganda. `significance` and `verification` are the agent's judgment, not ground truth.
