"""Checks that the documentation stays in step with the code."""

import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = (ROOT / "src", ROOT / "map_editor" / "src")


class DocumentationTest(unittest.TestCase):
    def test_every_module_has_a_docstring(self):
        missing = [
            str(path.relative_to(ROOT))
            for package in PACKAGES
            for path in sorted(package.rglob("*.py"))
            if not ast.get_docstring(ast.parse(path.read_text(encoding="utf-8")))
        ]
        self.assertEqual(missing, [], "start these modules with a docstring that says their role")

    def test_links_between_the_documents_exist(self):
        for document in (*ROOT.glob("*.md"), *(ROOT / "docs").glob("*.md"), ROOT / "map_editor" / "README.md"):
            for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", document.read_text(encoding="utf-8")):
                if "://" in target or target.startswith("mailto:"):
                    continue
                with self.subTest(document=document.name, link=target):
                    self.assertTrue((document.parent / target).exists(), f"{target} does not exist")


if __name__ == "__main__":
    unittest.main()
