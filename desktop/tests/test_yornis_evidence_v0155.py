from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import classic_engine as engine
import yornis_cervical_v0152 as cervical
import yornis_evidence_v0155 as evidence


def table(table_id: str) -> dict:
    return next(t for t in evidence.reference_help.TABLES if t["id"] == table_id)


class EvidenceAgeSexV0155Tests(unittest.TestCase):
    def test_c1_c7_no_longer_uses_universal_35_45_cutoff(self):
        evidence.install()
        measurement = next(
            m for m in engine.MEASUREMENTS
            if getattr(m, "analysis", "") == cervical.POSTURE_ANALYSIS
            and getattr(m, "name", "") == cervical.POSTURE_MEASUREMENT
        )
        ref = getattr(measurement, "norm_text", "")
        self.assertIn("50.7", ref)
        self.assertIn("45.6", ref)
        self.assertNotIn("35–45", ref)
        self.assertIsNone(getattr(measurement, "lo", None))
        self.assertIsNone(getattr(measurement, "hi", None))

    def test_posture_interpretation_is_descriptive_not_universal_normality(self):
        label, note = cervical.posture_classification(40.0)
        self.assertIn("descriptivo", label.lower())
        self.assertNotIn("normal", label.lower())
        self.assertNotIn("hiperlordosis", label.lower())
        self.assertIn("no límites de normalidad", note)
        negative, _ = cervical.posture_classification(-5.0)
        self.assertIn("invertida", negative.lower())

    def test_lordosis_table_contains_only_published_age_groups(self):
        rows = table("lordosis_c1_c7")["rows"]
        labels = {r[0] for r in rows}
        self.assertIn("C1–C7 · 4–5 años", labels)
        self.assertIn("C1–C7 · 6–19 años · ambos sexos", labels)
        self.assertIn("C1–C7 · 20–50 años · ambos sexos", labels)
        self.assertNotIn("C1–C7 · 7 años", labels)
        self.assertTrue(any("Sin referencia compatible" in r[1] for r in rows))

    def test_airway_uses_exact_published_6_8_10_12_groups(self):
        rows = table("via_aerea")["rows"]
        by_label = {r[0]: r for r in rows}
        self.assertEqual(by_label["McNamara superior · 6 años"][1:3], ("7.500 mm", "±1.827 mm"))
        self.assertEqual(by_label["McNamara superior · 12 años"][1:3], ("11.416 mm", "±2.261 mm"))
        self.assertEqual(by_label["McNamara inferior · 10 años"][1:3], ("11.556 mm", "±2.549 mm"))
        self.assertFalse(any("· 7 años" in r[0] for r in rows))
        self.assertFalse(any("· 9 años" in r[0] for r in rows))
        self.assertFalse(any("· 11 años" in r[0] for r in rows))

    def test_airway_sex_differences_are_not_presented_as_significant(self):
        t = table("via_aerea")
        self.assertIn("no hubo diferencias significativas por sexo", t["note"].lower())

    def test_craniocervical_context_prevents_wrong_extrapolation(self):
        t = table("craneo_cervical")
        self.assertIn("22–30", t["source"])
        text = " ".join(" ".join(row) for row in t["rows"])
        self.assertIn("101.72°", text)
        self.assertIn("106.59°", text)
        self.assertIn("No extrapolar a niños o mujeres", text)

    def test_all_reference_tables_still_validate(self):
        evidence.reference_help.validate_tables()
        self.assertEqual(len(evidence.reference_help.TABLES), 17)


if __name__ == "__main__":
    unittest.main()
