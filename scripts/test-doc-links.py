#!/usr/bin/env python3
"""Relative Markdown links and docs/ paths named in code and config must exist."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
DOC_PATH = re.compile(r"\bdocs/[A-Za-z0-9_./-]+\.md\b")


class DocumentationLinks(unittest.TestCase):
    def test_markdown_links_resolve(self):
        for page in [ROOT / "AGENTS.md", ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]:
            for target in LINK.findall(page.read_text(encoding="utf-8")):
                if re.match(r"[a-z]+:", target) or target.startswith("#"):
                    continue
                with self.subTest(page=page.relative_to(ROOT).as_posix(), target=target):
                    self.assertTrue((page.parent / target.split("#")[0]).exists())

    def test_docs_paths_named_by_code_and_config_exist(self):
        files = [*(ROOT / "src").rglob("*.[ch]*"), *(ROOT / "scripts").glob("*.py"), *(ROOT / "config").iterdir(),
                 ROOT / "AGENTS.md"]
        for path in files:
            if not path.is_file():
                continue
            for name in set(DOC_PATH.findall(path.read_text(encoding="utf-8", errors="replace"))):
                with self.subTest(file=path.relative_to(ROOT).as_posix(), doc=name):
                    self.assertTrue((ROOT / name).exists())


if __name__ == "__main__":
    unittest.main()
