import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research_db import ResearchDB
from research_protocol import analysis_catalog, minimum_landmarks, shared_landmark_summary


class ResearchSuiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = ResearchDB(Path(self.tmp.name) / "test.sqlite3")
        self.study = self.db.create_study("Prueba", "Investigador", "Institución", "Objetivo")

    def tearDown(self): self.tmp.cleanup()

    def test_protocol_versioning_and_lock(self):
        cat = analysis_catalog()
        self.assertTrue(cat)
        first_analysis = next(iter(cat))
        key = cat[first_analysis][0].key
        cfg = {"selected_variables": [key], "required_landmarks": minimum_landmarks([key])}
        v1 = self.db.save_protocol(self.study, cfg)
        self.assertEqual(v1, 1)
        self.db.lock_protocol(self.study)
        cfg2 = {"selected_variables": [key], "required_landmarks": minimum_landmarks([key]), "custom": {"changed": True}}
        v2 = self.db.save_protocol(self.study, cfg2)
        self.assertEqual(v2, 2)

    def test_exclusion_is_auditable_not_deleted(self):
        cid = self.db.add_case(self.study, "001", sex="F", age=12)
        self.db.exclude_case(cid, "Calidad radiográfica insuficiente", "borrosa")
        row = self.db.case(cid)
        self.assertEqual(row["status"], "excluded")
        self.assertEqual(row["included"], 0)
        self.assertTrue(any(r["event"] == "case_excluded" for r in self.db.audit_rows(self.study)))

    def test_auto_complete_requires_selected_results(self):
        cat = analysis_catalog(); a = next(iter(cat)); v = cat[a][0]
        cfg = {"selected_variables": [v.key], "required_landmarks": list(v.points)}
        version = self.db.save_protocol(self.study, cfg)
        cid = self.db.add_case(self.study, "001")
        points = {p: (float(i * 10 + 1), float(i * 7 + 2)) for i, p in enumerate(v.points)}
        self.db.save_trace(cid, version, points, [{"analysis": v.analysis, "measurement": v.name, "value": 1.0, "unit": v.unit, "reference": "", "interpretation": ""}], [v.name], 0.1)
        self.assertEqual(self.db.case(cid)["status"], "complete")

    def test_landmark_minimization(self):
        cat = analysis_catalog(); keys = []
        for _, variables in list(cat.items())[:3]:
            if variables: keys.append(variables[0].key)
        s = shared_landmark_summary(keys)
        self.assertEqual(s["measurement_count"], len(keys))
        self.assertLessEqual(s["unique_landmark_count"], sum(len(v.points) for vs in cat.values() for v in vs if v.key in keys))


if __name__ == "__main__": unittest.main()
