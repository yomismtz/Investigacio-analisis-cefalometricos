from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from yornis_branding_v0161 import rebrand_python_string_literals
from yornis_paths import migrate_legacy_app_dir


class YornisBrandingAndMigrationTests(unittest.TestCase):
    def test_branding_changes_visible_string_literals_not_identifiers(self):
        source = (
            "class YomCephClassic:\\n"
            "    title = 'YomCeph Desktop'\\n"
            "    logo = 'yomceph_logo.png'\\n"
        )
        updated = rebrand_python_string_literals(source)
        self.assertIn("class YomCephClassic:", updated)
        self.assertIn("'Yornis Desktop'", updated)
        self.assertIn("'yornis_logo.png'", updated)
        compile(updated, "<branding-test>", "exec")

    def test_legacy_directory_moves_and_database_is_renamed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = root / "YomCeph"
            research = legacy / "research"
            research.mkdir(parents=True)
            (legacy / "settings.json").write_text('{"language":"es"}', encoding="utf-8")
            (research / "yomceph_research.sqlite3").write_bytes(b"existing-db")
            result = migrate_legacy_app_dir(legacy, root / "Yornis")
            self.assertTrue(result["moved"])
            self.assertTrue((root / "Yornis" / "settings.json").exists())
            self.assertEqual(
                (root / "Yornis" / "research" / "yornis_research.sqlite3").read_bytes(),
                b"existing-db",
            )
            self.assertFalse((root / "YomCeph").exists())

    def test_merge_does_not_overwrite_existing_yornis_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = root / "YomCeph"
            target = root / "Yornis"
            (legacy / "research").mkdir(parents=True)
            (target / "research").mkdir(parents=True)
            (legacy / "settings.json").write_text("legacy", encoding="utf-8")
            (target / "settings.json").write_text("current", encoding="utf-8")
            (legacy / "research" / "yomceph_research.sqlite3").write_bytes(b"legacy-db")
            result = migrate_legacy_app_dir(legacy, target)
            self.assertFalse(result["moved"])
            self.assertEqual((target / "settings.json").read_text(encoding="utf-8"), "current")
            self.assertEqual(
                (target / "research" / "yornis_research.sqlite3").read_bytes(),
                b"legacy-db",
            )
            self.assertTrue(legacy.exists())


if __name__ == "__main__":
    unittest.main()
