from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yornis_reference_help_v0154_all as refs


class ReferenceHelpTests(unittest.TestCase):
    def test_reference_tables_are_structurally_complete(self):
        refs.validate_tables()
        self.assertEqual(len(refs.TABLES), 17)
        ids = [t["id"] for t in refs.TABLES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(sum(len(t["rows"]) for t in refs.TABLES), 110)
        for table in refs.TABLES:
            self.assertTrue(table["source"])
            self.assertTrue(table["title"])
            for row in table["rows"]:
                self.assertEqual(len(row), 6)

    def test_expected_reference_sets_are_present(self):
        ids = {t["id"] for t in refs.TABLES}
        expected = {
            "steiner", "downs", "tweed", "ricketts", "bjork_jarabak", "wits",
            "mcnamara", "holdaway", "burstone_cogs", "legan_burstone",
            "sassouni", "cvm", "alineacion_cervical_c2_c4",
            "powell", "via_aerea", "craneo_cervical", "lordosis_c1_c7",
        }
        self.assertEqual(ids, expected)

    def test_last_four_tables_have_clinical_context(self):
        by_id = {t["id"]: t for t in refs.TABLES}
        for table_id in ("powell", "via_aerea", "craneo_cervical", "lordosis_c1_c7"):
            table = by_id[table_id]
            self.assertGreaterEqual(len(table["rows"]), 4)
            self.assertTrue(table["source"])


if __name__ == "__main__":
    unittest.main()
