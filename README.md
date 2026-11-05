# FFXIV Relic Weapon Roadmap Guide

*A cozy, plain-English manual for the six relic weapon journeys in Final Fantasy XIV —
what each one actually takes, how long it takes, what it costs, and how to finish one
with your real life still intact.*

Written in the "explain it like a friend would" spirit of **Asdale Dynamics, LLC**:
step by step, never condescending, with checklists you can actually tick off.

## How this is different (and what it is not)

- **It is not a comeback guide.** It assumes you already play (or have played) FFXIV and
  know what a roulette is. There is a separate, more general *FFXIV casual comeback
  guide* for wide-angle "returning after a break" questions; this one is strictly about
  the six relic weapon journeys.
- **It is not a gear-planning guide.** No BiS spreadsheets, no stat sim advice — relic
  weapons are collection/glamour projects, and this guide treats them that way.
- **It is not a walkthrough of quest text.** It covers what each cross-expansion line
  takes: requirements, currency math, roulettes to pair, and habits that keep the
  journey humane.

## What's inside

| Doc | What it covers |
| --- | --- |
| [`docs/primer.md`](docs/primer.md) | Start here — how relic journeys work, and which line to pick |
| [`docs/roulettes-and-dailies.md`](docs/roulettes-and-dailies.md) | Pairing every relic step with roulettes, tomestones, and collectibles |
| [`docs/budget-and-gil.md`](docs/budget-and-gil.md) | Time and million-gil estimates for all six lines |
| [`docs/gadgets-and-tricks.md`](docs/gadgets-and-tricks.md) | Hidden tricks, timers, and community tools that shorten the grind |
| [`docs/zodiac-arr.md`](docs/zodiac-arr.md) | ARR — Zodiac Weapons (the classic, longest line) |
| [`docs/anima-hw.md`](docs/anima-hw.md) | Heavensward — Anima Weapons (aura weapons, tomestone-friendly) |
| [`docs/eureka-sb.md`](docs/eureka-sb.md) | Stormblood — Eureka Weapons (field zone island adventure) |
| [`docs/resistance-shb.md`](docs/resistance-shb.md) | Shadowbringers — Resistance Weapons (story-forward, modern) |
| [`docs/manderville-ew.md`](docs/manderville-ew.md) | Endwalker — Manderville Weapons (the quick, funny, Poetics-only line) |
| [`docs/phantom-dawntrail.md`](docs/phantom-dawntrail.md) | Dawntrail — Phantom Weapons (the Occult Crescent tour) |

## The static site

`site/` is a zero-dependency static HTML version of the guide with **interactive,
browser-saved checklists** (localStorage; nothing leaves your machine; no scripts fetch
anything). Serve it however you like:

```bash
python3 scripts/build.py    # regenerate site/ from docs/
python3 -m http.server 8000 --directory site   # then open http://localhost:8000
```

Or open `site/index.html` straight from disk — the checklists work either way.

## Build & test

Everything uses only the Python standard library (3.9+):

```bash
python3 scripts/build.py          # build/refresh the site
python3 scripts/build.py --check  # validate docs, LICENSE, README without writing
python3 -m unittest discover -s tests -v   # run the test suite
```

The checks enforce: every doc has a real H1, expansion docs contain journey/costs/
checklist/survival sections, internal links resolve to real pages, no placeholder text,
no secrets, the exact LICENSE copyright line, and README attribution.

## A note on numbers

Time and gil figures are honest ballparks for a steady, casual-friendly playstyle, based
on the state of the game around patch 7.5x (Phantom relic line complete since 7.55).
Square Enix softens requirements over time, so treat every number as a starting point and
verify big spends in game.

## Legal tea

This is a fan-made educational guide. Nothing here is copied from the game or its
clients, no official assets are used, and it is unaffiliated with Square Enix.
Trademarks belong to their owners. Relic grinds are entertainment, not medical,
financial, or romantic advice — as your healer, I prescribe snacks and a session cap.

MIT licensed. Copyright (c) 2026 Asdale Dynamics, LLC — see [`LICENSE`](LICENSE).
