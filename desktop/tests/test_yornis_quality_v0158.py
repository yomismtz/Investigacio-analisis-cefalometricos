import os
import sys
import unittest

HERE = os.path.dirname(__file__)
DESKTOP = os.path.dirname(HERE)
if DESKTOP not in sys.path:
    sys.path.insert(0, DESKTOP)


class YornisFinalPolishTests(unittest.TestCase):
    def test_versions_and_catalog(self):
        import yornis_quality_ui_v0158 as quality
        import yornis_desktop_v0158 as app
        import yornis_theme
        import yornis_virtual_assistant_v0157 as assistant
        import yornis_reference_help_v0156 as refs
        import classic_engine as engine

        self.assertEqual(quality.QUALITY_VERSION, "0.15.8")
        self.assertTrue(app.APP_VERSION.startswith("0.15.8"))
        self.assertEqual(len(yornis_theme.theme_names()), 8)
        self.assertEqual(set(yornis_theme.theme_names()), set(assistant.BIRD_PROFILES))
        self.assertEqual(len(refs.TABLES), 17)
        self.assertEqual(len(engine.MEASUREMENTS), 102)

    def test_evidence_safeguards_are_preserved(self):
        import yornis_evidence_v0155 as evidence
        evidence.install()
        import classic_engine as engine
        import yornis_cervical_v0152 as cervical

        posture = [m for m in engine.MEASUREMENTS if m.analysis == cervical.POSTURE_ANALYSIS and m.name == cervical.POSTURE_MEASUREMENT]
        self.assertEqual(len(posture), 1)
        self.assertNotIn("35–45", posture[0].norm_text)
        self.assertIsNone(posture[0].lo)
        self.assertIsNone(posture[0].hi)

    def test_assistant_search_still_works(self):
        import yornis_virtual_assistant_v0157 as assistant
        self.assertTrue(any(x.kind == "Tabla" for x in assistant.search_content("Steiner")))
        self.assertTrue(any(x.kind == "Medición" for x in assistant.search_content("Steiner")))
        self.assertTrue(any(x.kind == "Guía" for x in assistant.search_content("landmark")))


if __name__ == "__main__":
    unittest.main()
