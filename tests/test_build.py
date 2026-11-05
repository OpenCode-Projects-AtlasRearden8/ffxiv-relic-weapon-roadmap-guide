import io
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build as build_mod  # noqa: E402

EXPANSION_DOCS = [
    "zodiac-arr.md", "anima-hw.md", "eureka-sb.md",
    "resistance-shb.md", "manderville-ew.md", "phantom-dawntrail.md",
]


class TestStaticValidation(unittest.TestCase):
    def test_static_checks_pass(self):
        failures = build_mod.get_parsing_failures()
        self.assertEqual([], failures)

    def test_license_copyright_is_exact(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Asdale Dynamics, LLC", text)

    def test_readme_credits_asdale(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Asdale Dynamics, LLC", text)

    def test_no_copygame_claims(self):
        # fan-education guard: docs must never claim to be official
        for doc in build_mod.PAGES:
            text = (ROOT / "docs" / doc).read_text(encoding="utf-8")
            assert "official guide" not in text.lower()


class TestMarkdownConversion(unittest.TestCase):
    def test_headings_bold_checklists_render(self):
        md = "# Title\n\nA **bold** and *soft* line.\n\n- plain\n- [ ] task one\n- [x] done task\n\n1. first\n2. second\n"
        out = build_mod.md_to_html(md, "test.html")
        self.assertIn("<h1", out)
        self.assertIn("<strong>bold</strong>", out)
        self.assertIn("<em>soft</em>", out)
        self.assertIn('type="checkbox"', out)
        self.assertIn('checked="checked"', out)
        self.assertIn("<ol>", out)

    def test_tables_render(self):
        md = "| A | B |\n| --- | --- |\n| 1 | 2 |\n"
        out = build_mod.md_to_html(md, "test.html")
        self.assertIn("<table>", out)
        self.assertIn("<th>A</th>", out)
        self.assertIn("<td>1</td>", out)

    def test_internal_md_links_are_kept_for_resolver(self):
        md = "See [Primer](primer.md) next.\n"
        out = build_mod.md_to_html(md, "test.html")
        self.assertIn('href="primer.md"', out)


class TestSiteBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_mod.build_site()

    def test_all_pages_generated(self):
        for name in build_mod.ORDER:
            self.assertTrue((ROOT / "site" / f"{name}.html").exists(), name)

    def test_index_links_every_page(self):
        text = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        for name in build_mod.ORDER:
            self.assertIn(f'href="{name}.html"', text)

    def test_checklists_present_in_expansion_pages(self):
        for doc in EXPANSION_DOCS:
            name = build_mod.SLUG_OF_DOC[doc]
            text = (ROOT / "site" / f"{name}.html").read_text(encoding="utf-8")
            self.assertIn('class="checklist"', text, doc)
            self.assertIn('data-key="', text, doc)

    def test_assets_copied(self):
        self.assertTrue((ROOT / "site" / "css" / "style.css").exists())
        self.assertTrue((ROOT / "site" / "js" / "checklist.js").exists())

    def test_footer_line_on_every_page(self):
        for name in build_mod.ORDER:
            text = (ROOT / "site" / f"{name}.html").read_text(encoding="utf-8")
            self.assertIn(build_mod.REQUIRED_COPYRIGHT, text)

    def test_previous_next_nav(self):
        text = (ROOT / "site" / "primer.html").read_text(encoding="utf-8")
        self.assertIn('<a href="index.html">', text)
        self.assertIn('<a href="zodiac.html">', text)

    def test_build_failures_empty(self):
        self.assertEqual([], build_mod.get_build_failures())


class TestDocsQuality(unittest.TestCase):
    def test_expansion_docs_have_costs_table(self):
        for doc in EXPANSION_DOCS:
            text = (ROOT / "docs" / doc).read_text(encoding="utf-8")
            assert "## Costs at a glance" in text, doc

    def test_every_doc_links_to_index_or_primer(self):
        for doc in build_mod.PAGES:
            if doc == "index.md":
                continue
            text = (ROOT / "docs" / doc).read_text(encoding="utf-8")
            has_link = bool(re.search(r"\]\((primer|index)\.md\)", text))
            self.assertTrue(has_link, f"{doc} should link primer/index for navigation")


if __name__ == "__main__":
    unittest.main()
