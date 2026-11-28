# Sources

The daily run reads this list at the start of every run, covers every active source, and updates it: new sources that work are added with the date and what they are good for; sources that stop working are marked inactive with the date. See "Growing the source list" in `ANALYST_PROMPT.md`.

Fetch Telegram with `python3 tg_fetch.py [--days N] HANDLE ...`.

## Telegram: Iranian military and IRGC (read in full; Persian)
| Handle | What it is | Status |
|---|---|---|
| sepah | Sepah News, IRGC official news | active |
| defapress_ir | Defa Press, armed forces outlet | active |
| seghal_aja | Artesh (army) public relations | active |
| AeroSpaceTalk | Iranian aerospace/defence talk | active, low volume |
| Iranian_Militarism | Iranian military-enthusiast channel (mostly foreign militaries; Iran items useful) | active |
| jangaavaran1390 | Iranian military-enthusiast channel (mostly foreign militaries) | active |
| BisimchiMedia | Pro-regime military/IRGC-aligned channel | active |

## Telegram: Iranian state and semi-official media (keyword filter; Persian)
| Handle | What it is | Status |
|---|---|---|
| farsna | Fars (IRGC-affiliated) | active |
| FarsNewsInt | Fars international desk | active, added 2026-11-28 |
| iribnews | IRIB state broadcaster | active |
| mehrnews | Mehr news agency | active, added 2026-11-28 |
| irna_1313 | IRNA official agency | active, added 2026-11-28 |
| Nournews_ir | Nour News (close to the Supreme National Security Council) | active, added 2026-11-28 |
| Kayhan_online | Kayhan daily | active, added 2026-11-28 |
| PressTV | Press TV (English) | active, added 2026-11-28 |
| JahanTasnim | Tasnim world desk (main `Tasnimnews` has no public preview) | active |
| Tasnimnews_hebrew | Tasnim in Hebrew | active |
| Tasnimnovosti | Tasnim in Russian | active |

## Telegram: opposition and foreign Persian-language media (keyword filter)
| Handle | What it is | Status |
|---|---|---|
| IranintlTV | Iran International | active |
| bbcpersian | BBC Persian | active, added 2026-11-28 |
| radiofarda | Radio Farda (RFE/RL) | active, added 2026-11-28 |
| VahidOnline | Persian news aggregator | active |
| hadshotiran | Hebrew-language Iran news | active |

## Telegram: OSINT and international (keyword filter; transfers to/from Iran, imagery, launches)
| Handle | What it is | Status |
|---|---|---|
| OSINTWarfare | OSINT aggregator, good on Iranian weapons displays and launches | active, added 2026-11-28 |
| CIG_telegram | Conflict monitoring aggregator (Middle East focus) | active, added 2026-11-28 |
| clashreport | Clash Report, wire-style aggregator (relays FT, WSJ, Reuters) | active, added 2026-11-28 |
| BellumActaNews | Conflict aggregator (relays TheWarReporter) | active, added 2026-11-28 |
| OSINTdefender | OSINT aggregator | active, added 2026-11-28 |
| intelslava | Pro-Russian aggregator; check claims | active, added 2026-11-28 |
| Middle_East_Spectator | Middle East aggregator | active, added 2026-11-28 |
| warmonitors | Aggregator | active, added 2026-11-28, low signal |
| rybar | Russian milblogger (Russia-Iran angle) | active, added 2026-11-28 |
| rian_ru | RIA Novosti (Russian state) | active, added 2026-11-28 |
| tass_agency | TASS (Russian state) | active, added 2026-11-28 |
| kyivindependent_official | Kyiv Independent (Ukraine; Iran-Russia transfers) | active, added 2026-11-28 |
| militarysummary | Military Summary | active, added 2026-11-28, low signal |
| tankertrackers | TankerTrackers (Iranian shipping) | active but last post 2026-11-19, added 2026-11-28 |

## Telegram: no public preview or dead (do not retry every run)
Tasnimnews, Partizan_ir, isna_news, Javan_online, Defapress (use defapress_ir), militarnyi, Abu_Ali_Express, sabereenpaltelegram, kurdistan24, alalam_arabia, Intel_Sky, ShipTracker_ru (no messages); manoto_news, mashreghnews, IranObserver0, IranWireFarsi, IranMilitaryNews, AuroraIntel (stale); almayadeen and DDGeopolitics (preview works but no Iran-military value).

## Websites reachable from this environment
| Host | What it is |
|---|---|
| criticalthreats.org | CTP-ISW daily Iran Update (`/analysis/iran-update-<month>-<day>-<year>`) |
| iranintl.com | Iran International (English `/en/` and Persian article IDs) |
| navalnews.com | Naval News |
| news.usni.org | USNI News |
| cna.org | CNA |
| missilethreat.csis.org | CSIS Missile Threat |

## Websites blocked by this environment's network policy (checked 2026-11-28)
Proxy answers "CONNECT tunnel failed, response 403". Do not retry or route around; reach their content when an allowed source quotes them.
hisutton.com, twz.com, reuters.com, apnews.com, defensenews.com, breakingdefense.com, al-monitor.com, amwaj.media, longwarjournal.org, fdd.org, washingtoninstitute.org, timesofisrael.com, jpost.com, ynetnews.com, middleeasteye.net, aljazeera.com, theguardian.com, bbc.com, radiofarda.com, rferl.org, kyivindependent.com, mil.in.ua, militarnyi.com, oryxspioenkop.com, nknews.org, 38north.org, armyrecognition.com, militaryleak.com, janes.com, wsj.com, ft.com, bloomberg.com, economist.com, atlanticcouncil.org, csis.org (main site), globalsecurity.org, defense-update.com, israeldefense.co.il, maariv.co.il, inss.org.il, armscontrolwonk.com, news.google.com. iiss.org and iranwatch.org return 403 from the site itself. understandingwar.org is unreachable (CTP's mirror on criticalthreats.org works).
State-media websites (tasnimnews, farsnews, mehrnews, defapress, kayhan, mashregh) refuse connections: use their Telegram channels.
