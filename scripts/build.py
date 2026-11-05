#!/usr/bin/env python3
"""Build and validate the FFXIV Relic Weapon Roadmap Guide site.

Usage:
  python3 scripts/build.py             build site/ from docs/
  python3 scripts/build.py --check     validate only (no writes)

Requires only the Python standard library.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"
LICENSE = ROOT / "LICENSE"
README = ROOT / "README.md"

REQUIRED_COPYRIGHT = "Copyright (c) 2026 Asdale Dynamics, LLC"

# doc filename -> (output html filename, nav title)
PAGES = {
    "index.md": ("index.html", "Home"),
    "primer.md": ("primer.html", "Primer"),
    "roulettes-and-dailies.md": ("roulettes.html", "Roulettes & Dailies"),
    "budget-and-gil.md": ("budget.html", "Time & Gil Ledger"),
    "gadgets-and-tricks.md": ("gadgets.html", "Gadgets & Tricks"),
    "zodiac-arr.md": ("zodiac.html", "ARR \u2014 Zodiac"),
    "anima-hw.md": ("anima.html", "HW \u2014 Anima"),
    "eureka-sb.md": ("eureka.html", "SB \u2014 Eureka"),
    "resistance-shb.md": ("resistance.html", "ShB \u2014 Resistance"),
    "manderville-ew.md": ("manderville.html", "EW \u2014 Manderville"),
    "phantom-dawntrail.md": ("phantom.html", "DT \u2014 Phantom"),
}

ORDER = [
    "index", "primer", "zodiac", "anima", "eureka", "resistance",
    "manderville", "phantom", "roulettes", "budget", "gadgets",
]

SLUG_OF_DOC = {doc: out.split(".")[0] for doc, (out, _) in PAGES.items()}
DOC_OF_NAME = {out: doc for doc, (out, _) in PAGES.items()}


def md_inline(text: str) -> str:
    """Render bold/italic/code/links for one markdown line (no HTML escaping first)."""
    # protect braces? not needed. Escape, then apply patterns on escaped text.
    t = html.escape(text, quote=False)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"_(.+)_", r"<em>\1</em>", t)
    return t


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def md_to_html(md: str, source_name: str) -> str:
    """Small markdown subset: h1-h4, paragraphs, lists (tasks/bullets/numbers), tables."""
    out: list[str] = []
    lines = md.split("\n")
    i = 0
    list_stack: list[str] = []
    last_was_li = False

    def close_list():
        while list_stack:
            out.append("</ul>" if list_stack.pop() == "ul" else "</ol>")

    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            close_list()
            last_was_li = False
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            close_list()
            level = len(m.group(1))
            text = m.group(2)
            return_anchor = ""
            if source_name == "index.html" or level == 1 or level == 2:
                return_anchor = f' id="{slugify(text)}"'
            out.append(f"<h{level}{return_anchor}>{md_inline(text)}</h{level}>")
            i += 1
            continue

        if line.startswith("> "):
            close_list()
            out.append(f"<blockquote><p>{md_inline(line[2:])}</p></blockquote>")
            i += 1
            continue

        # table (markdown pipe table with a separator row)
        if line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(
            r"^\s*\|[\s:\-|]+\|\s*$", lines[i + 1]
        ):
            close_list()
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            out.append('<div class="tablewrap"><table>')
            out.append("<thead><tr>" + "".join(f"<th>{md_inline(c)}</th>" for c in header) + "</tr></thead>")
            out.append("<tbody>")
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                out.append("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in cells) + "</tr>")
                i += 1
            out.append("</tbody></table></div>")
            continue

        # indented continuation of the previous list item (soft-wrapped bullet)
        if re.match(r"^\s{2,}\S", line) and list_stack and not re.match(r"^\s*[-*] ", line) \
                and out[-1].lstrip().startswith("<li"):
            out[-1] = out[-1] + " " + md_inline(line.strip())
            i += 1
            continue

        task = re.match(r"^(\s*)- \[( |x)\] (.*)$", line)
        if task:
            if not list_stack or list_stack[-1] != "ul":
                close_list()
                list_stack.append("ul")
                out.append('<ul class="checklist">')
            checked = ' checked="checked"' if task.group(2) == "x" else ""
            key = f"{source_name.split('.')[0]}:{len(out)}"
            out.append(
                f'<li class="check-item"><input type="checkbox" data-key="{key}"{checked}> '
                f"<span>{md_inline(task.group(3))}</span></li>"
            )
            i += 1
            continue

        bullet = re.match(r"^(\s*)[-*] (.*)$", line)
        if bullet:
            if not list_stack or list_stack[-1] != "ul":
                close_list()
                list_stack.append("ul")
                out.append("<ul>")
            out.append(f"<li>{md_inline(bullet.group(2))}</li>")
            i += 1
            continue

        number = re.match(r"^(\s*)(\d+)\. (.*)$", line)
        if number:
            if not list_stack or list_stack[-1] != "ol":
                close_list()
                list_stack.append("ol")
                out.append("<ol>")
            out.append(f"<li>{md_inline(number.group(3))}</li>")
            i += 1
            continue

        close_list()
        # paragraph: merge soft-wrapped lines
        buf = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#{1,4}\s|\s*[-*] |\s*\d+\. |\s*- \[|> )", lines[i]
        ) and not lines[i].lstrip().startswith("|"):
            buf.append(lines[i].strip())
            i += 1
        out.append(f"<p>{md_inline(' '.join(buf))}</p>")

    close_list()
    return "\n".join(out)


def build_nav(current: str) -> str:
    parts = []
    for name in ORDER:
        page = f"{name}.html"
        _, title = PAGES[DOC_OF_NAME[page]]
        cls = ' class="current"' if name == current else ""
        parts.append(f'<a href="{page}"{cls}>{title}</a>')
    return " ".join(parts)


def page_template(body: str, title: str, current: str, prev_next: tuple[str, str]) -> str:
    prev_name, next_name = prev_next

    def link_html(name: str | None, label: str) -> str:
        if not name:
            return f'<div class="pn {label} pn-hidden"><span>{label}</span><span>&nbsp;</span></div>'
        _, t = PAGES[DOC_OF_NAME[f"{name}.html"]]
        return f'<div class="pn {label}"><span>{label}</span><a href="{name}.html">{t}</a></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} \u2014 FFXIV Relic Weapon Roadmap Guide</title>
<meta name="description" content="A cozy fan-made guide to every Final Fantasy XIV relic weapon journey: steps, time and gil estimates, roulette pairings, and checklists.">
<link rel="stylesheet" href="css/style.css">
</head>
<body>
<header class="site-header">
  <p class="brand"><a href="index.html">FFXIV Relic Weapon Roadmap Guide</a></p>
  <nav class="site-nav">{build_nav(current)}</nav>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="pn-row">
    {link_html(prev_name, "Previous")}
    {link_html(next_name, "Next")}
  </div>
  <p>A fan-made educational guide \u2014 unaffiliated with Square Enix. EST/IST not included; enthusiasm is.</p>
  <p>Copyright (c) 2026 Asdale Dynamics, LLC \u00b7 licensed under the MIT License.</p>
</footer>
<script src="js/checklist.js"></script>
</body>
</html>
"""


def build_site() -> list[Path]:
    """Generate all HTML pages from docs; return list of written files."""
    SITE.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    entries = []
    for name in ORDER:
        doc = next(d for d, (out, _) in PAGES.items() if out == f"{name}.html")
        md = (DOCS / doc).read_text(encoding="utf-8")
        entries.append((doc, md, name))

    for idx, (doc, md, name) in enumerate(entries):
        prev_name = entries[idx - 1][2] if idx > 0 else None
        next_name = entries[idx + 1][2] if idx < len(entries) - 1 else None
        body_html = md_to_html(md, f"{name}.html")
        # make doc-internal .md links point at generated pages
        title_match = re.search(r"^# (.+)$", md, re.MULTILINE)
        title = title_match.group(1) if title_match else dfname_title(doc)
        out_path = SITE / f"{name}.html"
        out_path.write_text(
            page_template(body_html, title, name, (prev_name, next_name)), encoding="utf-8"
        )
        written.append(out_path)

    for shared in ["css/style.css", "js/checklist.js"]:
        src = ROOT / "site-src" / shared
        dst = SITE / shared
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    return written


def dfname_title(doc: str) -> str:
    return doc.replace(".md", "").replace("-", " ").title()


def get_parsing_failures() -> list[str]:
    """Static validations that don't require a build."""
    failures: list[str] = []

    if not LICENSE.exists():
        failures.append("LICENSE file missing")
    elif REQUIRED_COPYRIGHT not in LICENSE.read_text(encoding="utf-8"):
        failures.append(f"LICENSE must contain exactly: {REQUIRED_COPYRIGHT}")

    if not README.exists():
        failures.append("README.md missing")
    else:
        readme = README.read_text(encoding="utf-8")
        if "Asdale Dynamics, LLC" not in readme:
            failures.append("README must credit Asdale Dynamics, LLC")
        for l_url in ("http://", "https://"):
            if l_url in readme:
                break
        else:
            failures.append("README missing at least one documentation URL")

    for doc in PAGES:
        path = DOCS / doc
        if not path.exists():
            failures.append(f"docs/{doc} missing")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.lstrip().startswith("# "):
            failures.append(f"docs/{doc} does not start with an H1 title")
        first_line = text.lstrip().splitlines()[0]
        if first_line.count("# ") > 1:
            failures.append(f"docs/{doc} H1 contains stray markdown")
        if re.search(r"\bTBD\b|\bTODO\b|\bFIXME\b|\[Item\]", text):
            failures.append(f"docs/{doc} contains placeholder text (TODO/TBD/FIXME/[Item])")
        if "Copyright (\u0441)" in text:
            failures.append(f"docs/{doc} uses cyrillic copyright look-alike")
        for i, line in enumerate(text.splitlines(), 1):
            if line.startswith("^") and line.endswith(","):
                failures.append(f"docs/{doc}:{i} suspicious caret line")

        # internal links must resolve to a doc in PAGES
        for link in re.findall(r"\[([^\]]+)\]\(([^)\s]+\.md)\)", text):
            target = link[1].split("#")[0]
            if target and target not in PAGES:
                failures.append(f"docs/{doc} links to unknown doc {target}")

        # expansion docs must have a checklist and key sections
        is_expansion = doc in {
            "zodiac-arr.md", "anima-hw.md", "eureka-sb.md",
            "resistance-shb.md", "manderville-ew.md", "phantom-dawntrail.md",
        }
        if is_expansion:
            n_checks = len(re.findall(r"^- \[( |x)\] ", text, re.MULTILINE))
            if n_checks < 5:
                failures.append(f"docs/{doc} checklist too short ({n_checks} items)")
            for section in ("## The journey", "## Survival checklist", "## Real-life survival notes"):
                if section not in text:
                    failures.append(f"docs/{doc} missing {section!r} section")

    # secret patterns
    for path in list(DOCS.glob("*.md")) + [README, LICENSE]:
        if path.exists():
            t = path.read_text(encoding="utf-8")
            if re.search(r"(sk-[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)", t):
                failures.append(f"{path} appears to contain a secret/API key")

    return failures


def get_build_failures() -> list[str]:
    """Validations that require a fresh build."""
    failures: list[str] = []

    for name in ORDER:
        site_file = SITE / f"{name}.html"
        if not site_file.exists():
            failures.append(f"site/{name}.html was not generated")
            continue
        text = site_file.read_text(encoding="utf-8")
        if "css/style.css" not in text or "js/checklist.js" not in text:
            failures.append(f"site/{name}.html missing asset references")
        if "</body>" not in text:
            failures.append(f"site/{name}.html not closed properly")

    index = SITE / "index.html"
    if index.exists():
        text = index.read_text(encoding="utf-8")
        for name in ORDER:
            if f'href="{name}.html"' not in text and f'href="{name}.html" ' not in text:
                failures.append(f"site/index.html missing link to {name}.html")

    for asset in ["css/style.css", "js/checklist.js"]:
        if not (SITE / asset).exists():
            failures.append(f"site/{asset} missing (expected from site-src/)")

    # every internal md link in docs should exist as generated page
    for doc in PAGES:
        src = (DOCS / doc).read_text(encoding="utf-8")
        for link in re.findall(r"\[([^\]]+)\]\(([^)\s]+\.md)\)", src):
            target = link[1].split("#")[0]
            if target in PAGES:
                out_name = PAGES[target][0].replace(".html", "")
                if not (SITE / f"{out_name}.html").exists():
                    failures.append(f"docs/{doc} links to {target}, but site page missing")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate only, do not write")
    args = parser.parse_args()

    static = get_parsing_failures()
    if static:
        for f in static:
            print(f"FAIL: {f}")
        return 1

    if not args.check:
        build_site()

    build = get_build_failures() if not args.check else []
    # validation-only mode still checks that generated site matches sources if built
    if build:
        for f in build:
            print(f"FAIL: {f}")
        return 1

    if args.check:
        print("Check OK: docs, license, readme, and site sources are consistent.")
    else:
        n = len(ORDER)
        print(f"Build OK: {n} pages written to site/ from docs/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
