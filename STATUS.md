# STATUS — ffxiv-relic-weapon-roadmap-guide

Last updated: 2026-11-05

## What was built

A cozy, fan-made educational manual for all six FFXIV relic weapon journeys, published as
markdown docs plus a static HTML site with browser-saved checklists.

- **`docs/` — 11 markdown guides** (verified against current wiki/patch data, ~7.5x era):
  - `primer.md` — shared mechanics, house rules, which line to start
  - Six expansion lines: `zodiac-arr.md` (Zodiac, 8 stages), `anima-hw.md` (Anima, 8
    stages), `eureka-sb.md` (Eureka/Physeos, full zone route), `resistance-shb.md`
    (Resistance → Blade's, Bozja/Zadnor), `manderville-ew.md` (4 Poetics-only stages),
    `phantom-dawntrail.md` (Phantom, patches 7.25–7.55 incl. the final 7.55 upgrades)
  - `roulettes-and-dailies.md` — per-step pairing with roulettes/tomestones/collectibles
  - `budget-and-gil.md` — time + gil ledger table across all six lines
  - `gadgets-and-tricks.md` — trackers, light-bonus windows, in-game tricks, habits
- **`site/` — static HTML site**: 11 pages generated from docs by `scripts/build.py`
  (pure-stdlib markdown subset → HTML), shared CSS/JS, prev/next nav, legal footer on
  every page, and interactive survival checklists persisted in localStorage (no network
  calls, works from `file://` as well as any static server).
- **`site-src/`** — the hand-written CSS/JS that the build copies into `site/`.
- **`scripts/build.py`** — builds site pages from docs; `--check` mode validates docs,
  LICENSE, README, and generated output without writing.
- **`tests/test_build.py`** — 16 unittest cases (pure stdlib `unittest`).
- **`README.md`** — overview, distinctness statement (not a comeback guide, not gear
  planning), build/test instructions, attribution.
- **`LICENSE`** — MIT, with the exact line `Copyright (c) 2026 Asdale Dynamics, LLC`.

## How to run it

```bash
python3 scripts/build.py                    # regenerate site/ from docs/
python3 scripts/build.py --check            # validate without writing
python3 -m unittest discover -s tests       # run the test suite
python3 -m http.server 8000 --directory site   # then open http://localhost:8000
```

No dependencies beyond Python 3.9+ standard library. Opening `site/index.html` directly
also works; checklists save per page-title in your browser.

## Verification results (2026-11-05)

- `python3 scripts/build.py` → `Build OK: 11 pages written to site/ from docs/.`
- `python3 scripts/build.py --check` → `Check OK`
- `python3 -m unittest discover -s tests` → `Ran 16 tests ... OK`
- HTTP smoke test: all 11 pages + `css/style.css` + `js/checklist.js` serve with HTTP 200
  via `python3 -m http.server` (verified with curl).
- Static validations confirmed: every doc has an H1; each expansion doc contains
  journey / costs / checklist / survival sections and links back to primer/index;
  internal doc links all resolve; no TODO/TBD/FIXME placeholders; no secret patterns
  (`sk-`, AWS keys, private-key blocks); LICENSE carries the exact required copyright
  line; README credits Asdale Dynamics, LLC.
- Facts spot-verified against ffxiv.consolegameswiki.com and current guides during
  writing: Zodiac stage requirements, Anima tome/seal totals, Resistance memory stages,
  Manderville 6,000-Poetics structure, Eureka crystal route, Phantom 7.25–7.55 steps
  (including the 1,200 crystal paste, Phantom Dispellers, and the one-time Knowledge
  Crystal).

## Known gaps / honest limits

- **Numbers drift.** Time/gil figures are calibrated ballparks for patch ~7.5x; Square
  Enix keeps softening old relic requirements, so totals may improve between now and
  whenever you read this. Every expansion doc says to verify big purchases in game.
- **Job-specific quirks are out of scope.** PLD shield steps, per-quest crafted weapon
  pieces, and weapon-piece/MB price specifics are mentioned generically; Universalis is
  the recommended live-price check rather than shipping prices in docs.
- **No images.** The site is deliberately asset-free (no copied game content); glamour
  appreciation needs a browser tab for weapon previews.
- **Markdown subset only.** The custom builder supports headings, paragraphs, nested
  wrap-around list items, task/bullet/numbered lists, tables, blockquotes, bold/italic/
  code/links — that's every construct used in docs, but not full CommonMark.
- **Checklist state is per browser.** localStorage keys are page-based and domain-less
  (works on file://), but there is no cross-device sync — by design, personal data
  never leaves the browser.
- **Eureka estimates are the widest range** (30–50h) because zone activity depends on
  community train timing, which varies by server/data center.
