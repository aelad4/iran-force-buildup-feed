# Iran Force Buildup OSINT Feed

A scheduled Claude Code task runs daily, researches Iran's military force buildup from public sources,
and pushes new scored items to `feed.json`. `index.html` (GitHub Pages) displays the feed.

- `ANALYST_PROMPT.md` - the instructions the daily task follows
- `SOURCES.md` - the source list (Telegram channels, reachable and blocked websites); the daily task reads it and adds new sources
- `tg_fetch.py` - reads public Telegram channel previews
- `merge_items.py` - validates, dedupes and merges new items into `feed.json`
- `index.html` - the dashboard (filters: buildup axis (personnel, training, weapons, infrastructure, organization, statements), category, branch, source type, verification, significance, date, search)

Item titles, summaries and notes are written in Hebrew; the dashboard is Hebrew (RTL).

Limits: Iranian state-media sites refuse connections from the task's network (Telegram is used instead);
X/Twitter, paywalled Janes and many news and analysis sites are blocked by the environment's network policy (see `SOURCES.md`).
Output is automated analysis of open sources, including state propaganda. `significance` and `verification` are the agent's judgment, not ground truth.
