from __future__ import annotations

import sys
import unittest
from pathlib import Path

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))

from yornis_branding_v0161 import calibration_dialog_copy, rebrand_classic_source
import research_db


class YornisBrandingCalibrationTests(unittest.TestCase):
    def test_classic_source_rebrands_literals_but_keeps_python_class_identifier(self):
        source = '''
class YomCephClassic:
    pass
brand = "YOMCEPH"
title = "YomCeph Desktop"
calibration = "Calibrar mm"
icon = "yomceph_logo.png"
'''
        updated = rebrand_classic_source(source)
        self.assertIn("class YomCephClassic:", updated)
        self.assertIn('"YORNIS"', updated)
        self.assertIn('"Yornis Desktop"', updated)
        self.assertIn('"Calibrar radiografía"', updated)
        self.assertIn('"yornis_logo.png"', updated)
        self.assertNotIn('"YOMCEPH"', updated)
        self.assertNotIn('"YomCeph Desktop"', updated)

    def test_calibration_dialog_explains_known_distance_and_two_clicks(self):
        title, prompt = calibration_dialog_copy(
            "Calibrar mm",
            "Distancia real entre puntos",
        )
        self.assertEqual(title, "Calibrar radiografía · Yornis")
        self.assertIn("MILÍMETROS REALES", prompt)
        self.assertIn("primer extremo", prompt)
        self.assertIn("segundo extremo", prompt)
        self.assertIn("25 mm", prompt)

    def test_research_storage_uses_yornis_identity(self):
        self.assertEqual(research_db.APP_DIR.name, "Yornis")
        self.assertEqual(research_db.DB_PATH.name, "yornis_research.sqlite3")

    def test_brand_rewrite_does_not_change_the_legacy_class_name(self):
        source = "class YomCephClassic: pass\\nlabel = 'YOMCEPH'"
        updated = rebrand_classic_source(source)
        self.assertIn("class YomCephClassic", updated)
        self.assertIn("'YORNIS'", updated)


if __name__ == "__main__":
    unittest.main()
