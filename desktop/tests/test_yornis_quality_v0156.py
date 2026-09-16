from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESKTOP = ROOT / "desktop"
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))

import yornis_evidence_v0155 as evidence

evidence.install()

import yornis_desktop_v0156 as app
import yornis_quality_ui_v0156 as quality
import yornis_reference_help_v0156 as help_v0156


class QualityUXV0156Tests(unittest.TestCase):
    def test_version_and_reference_catalog(self):
        self.assertTrue(app.APP_VERSION.startswith("0.15.6"))
        self.assertEqual(quality.QUALITY_VERSION, "0.15.6")
        help_v0156.validate_tables()
        self.assertEqual(len(help_v0156.TABLES), 17)

    def test_reference_search_matches_measurements(self):
        airway = next(t for t in help_v0156.TABLES if t["id"] == "via_aerea")
        self.assertTrue(help_v0156._matches(airway, "6 años"))
        self.assertTrue(help_v0156._matches(airway, "McNamara"))
        self.assertFalse(help_v0156._matches(airway, "Steiner SNA"))

    def test_no_universal_c1_c7_cutoff_restored(self):
        import classic_engine as engine
        import yornis_cervical_v0152 as cervical

        row = next(
            m for m in engine.MEASUREMENTS
            if m.analysis == cervical.POSTURE_ANALYSIS and m.name == cervical.POSTURE_MEASUREMENT
        )
        self.assertIsNone(row.lo)
        self.assertIsNone(row.hi)
        self.assertNotIn("35–45", row.norm_text)
        self.assertIn("50.7", row.norm_text)

    def test_website_quality_copy(self):
        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "docs" / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "docs" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("v0.15.6", html)
        self.assertIn("Quality & UX", html)
        self.assertIn("filter-chip", js)
        self.assertIn("focus-visible", css)
        self.assertNotIn("rango orientativo 35°–45°", html)


if __name__ == "__main__":
    unittest.main()
