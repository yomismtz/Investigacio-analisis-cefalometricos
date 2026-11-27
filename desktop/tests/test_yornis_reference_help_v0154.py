from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yornis_reference_help_v0154_all as refs
import yornis_evidence_v0155 as evidence

evidence.install()


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

    def test_extra_reference_tables_do_not_overstate_airway_or_cervical_norms(self):
        by_id = {t["id"]: t for t in refs.TABLES}

        airway = {row[0]: row for row in by_id["via_aerea"]["rows"]}
        self.assertIn("7.500 mm", airway["McNamara superior · 6 años"][1])
        self.assertIn("17 mm", airway["McNamara superior · referencia histórica de la app"][1])
        self.assertIn("se calculan dentro del análisis McNamara", by_id["via_aerea"]["note"])
        self.assertIn("no diagnostica obstrucción ni apnea", by_id["via_aerea"]["note"])

        cranio = {row[0]: row for row in by_id["craneo_cervical"]["rows"]}
        self.assertIn("101.72°", cranio["SN-OPT · control pediátrico 9–16 años"][1])
        self.assertIn("120 varones daneses", by_id["craneo_cervical"]["source"])
        self.assertIn("no como normalidad universal", by_id["craneo_cervical"]["note"])

        lordosis = {row[0]: row for row in by_id["lordosis_c1_c7"]["rows"]}
        self.assertIn("50.7°", lordosis["C1–C7 · 6–19 años · ambos sexos"][1])
        self.assertIn("No se aplica un umbral universal", by_id["lordosis_c1_c7"]["note"])
        self.assertNotIn("40° ±5°", by_id["lordosis_c1_c7"]["source"])

    def test_reference_source_has_no_duplicate_dictionary_keys(self):
        import ast
        source_path = Path(__file__).resolve().parents[1] / "yornis_reference_help_v0154_all.py"
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        duplicates = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            keys = [key.value for key in node.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)]
            repeated = sorted({key for key in keys if keys.count(key) > 1})
            if repeated:
                duplicates.append((getattr(node, "lineno", 0), repeated))
        self.assertFalse(duplicates, f"Duplicate dictionary keys silently overwrite reference data: {duplicates}")

    def test_cvm_reference_table_uses_baccetti_concavity_sequence(self):
        cvm = next(table for table in refs.TABLES if table["id"] == "cvm")
        rows = {row[0]: row for row in cvm["rows"]}
        self.assertIn("desde CS2", rows["Concavidad borde inferior C2"][1])
        self.assertIn("desde CS3", rows["Concavidad borde inferior C3"][1])
        self.assertIn("desde CS4", rows["Concavidad borde inferior C4"][1])

    def test_last_four_tables_have_clinical_context(self):
        by_id = {t["id"]: t for t in refs.TABLES}
        for table_id in ("powell", "via_aerea", "craneo_cervical", "lordosis_c1_c7"):
            table = by_id[table_id]
            self.assertGreaterEqual(len(table["rows"]), 4)
            self.assertTrue(table["source"])
        self.assertIn("no criterios diagnósticos", by_id["powell"]["note"])
        self.assertIn("no son límites universales", by_id["legan_burstone"]["note"])
        self.assertIn("no existe un módulo de cálculo Legan–Burstone", by_id["legan_burstone"]["note"])
        self.assertIn("U6-NF, L6-MP y B-Pg", by_id["burstone_cogs"]["note"])
        self.assertIn("se calculan dentro del análisis McNamara", by_id["via_aerea"]["note"])


if __name__ == "__main__":
    unittest.main()
