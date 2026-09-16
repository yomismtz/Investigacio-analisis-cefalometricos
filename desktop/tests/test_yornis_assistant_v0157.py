from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
DESKTOP = HERE.parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))

import yornis_theme
import yornis_virtual_assistant_v0157 as assistant
import yornis_desktop_v0157 as app


class BirdAssistantV0157Tests(unittest.TestCase):
    def test_all_palettes_have_distinct_assistant_profiles(self):
        self.assertEqual(set(yornis_theme.theme_names()), set(assistant.BIRD_PROFILES))
        signatures = {assistant.avatar_signature(name) for name in yornis_theme.theme_names()}
        self.assertEqual(len(signatures), len(yornis_theme.theme_names()))

    def test_internal_search_finds_guides_tables_and_measurements(self):
        steiner = assistant.search_content("Steiner")
        self.assertTrue(any(item.kind == "Tabla" for item in steiner))
        self.assertTrue(any(item.kind == "Medición" for item in steiner))
        landmarks = assistant.search_content("landmark")
        self.assertTrue(any(item.kind == "Guía" for item in landmarks))

    def test_reference_catalog_and_measurement_index_are_complete(self):
        index = assistant.build_search_index()
        self.assertEqual(sum(1 for x in index if x.kind == "Tabla"), 17)
        self.assertGreaterEqual(sum(1 for x in index if x.kind == "Medición"), 102)
        self.assertGreaterEqual(sum(1 for x in index if x.kind == "Guía"), 12)

    def test_version_and_theme_integrity(self):
        self.assertTrue(app.APP_VERSION.startswith("0.15.7"))
        self.assertEqual(assistant.ASSISTANT_VERSION, "0.15.7")
        self.assertEqual(len(yornis_theme.theme_names()), 8)

    def test_c1_c7_universal_cutoff_is_not_reintroduced(self):
        index = assistant.search_content("lordosis cervical c1 c7")
        text = " ".join(item.text for item in index)
        self.assertIn("No usa 35–45° como corte universal automático", text)


if __name__ == "__main__":
    unittest.main()
