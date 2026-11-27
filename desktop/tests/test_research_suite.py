import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research_db import ResearchDB
from research_protocol import analysis_catalog, compute_selected, minimum_landmarks, requires_calibration, shared_landmark_summary


class ResearchSuiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = ResearchDB(Path(self.tmp.name) / "test.sqlite3")
        self.study = self.db.create_study("Prueba", "Investigador", "Institución", "Objetivo")

    def tearDown(self): self.tmp.cleanup()

    def test_research_drag_rejects_landmarks_outside_radiograph(self):
        from types import SimpleNamespace
        from research_ui import ResearchWorkspace

        class FakeCanvas:
            def canvasx(self, value): return value
            def canvasy(self, value): return value

        class FakeStatus:
            def __init__(self): self.last = None
            def config(self, **kwargs): self.last = kwargs.get("text")

        fake = SimpleNamespace(
            dragging="S",
            image=SimpleNamespace(width=100, height=80),
            canvas=FakeCanvas(),
            canvas_to_image=lambda x, y: (x, y),
            points={"S": (25.0, 30.0)},
            status=FakeStatus(),
            T=lambda es, en: es,
            redraw=lambda: None,
        )
        ResearchWorkspace.canvas_drag(fake, SimpleNamespace(x=120, y=40))
        self.assertEqual(fake.points["S"], (25.0, 30.0))
        self.assertIn("dentro", fake.status.last)

        ResearchWorkspace.canvas_drag(fake, SimpleNamespace(x=60, y=40))
        self.assertEqual(fake.points["S"], (60.0, 40.0))

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
        image = Path(self.tmp.name) / "001.png"
        image.write_bytes(b"synthetic lateral radiograph")
        cid = self.db.add_case(self.study, "001", image_path=str(image), copy_image=False)
        points = {p: (float(i * 10 + 1), float(i * 7 + 2)) for i, p in enumerate(v.points)}
        self.db.save_trace(cid, version, points, [{"analysis": v.analysis, "measurement": v.name, "value": 1.0, "unit": v.unit, "reference": "", "interpretation": ""}], [v.name], 0.1)
        self.assertEqual(self.db.case(cid)["status"], "complete")

    def test_replacing_radiograph_resets_calibration_and_invalidates_old_trace(self):
        first = Path(self.tmp.name) / "first.png"
        second = Path(self.tmp.name) / "second.png"
        first.write_bytes(b"first radiograph")
        second.write_bytes(b"replacement radiograph")
        cid = self.db.add_case(self.study, "001", image_path=str(first), copy_image=False)
        cat = analysis_catalog()
        analysis = next(iter(cat))
        variable = cat[analysis][0]
        version = self.db.save_protocol(
            self.study,
            {"selected_variables": [variable.key], "required_landmarks": list(variable.points)},
        )
        points = {name: (float(i + 1), float(i + 2)) for i, name in enumerate(variable.points)}
        self.db.update_case_calibration(cid, 0.25)
        self.db.save_trace(
            cid,
            version,
            points,
            [{"analysis": variable.analysis, "measurement": variable.name, "value": 1.0, "unit": variable.unit, "reference": "", "interpretation": ""}],
            [variable.name],
            0.25,
        )
        self.assertIsNotNone(self.db.case(cid)["case_mm_per_px"])
        self.assertTrue(self.db.latest_landmarks(cid, version))

        self.db.attach_image(cid, str(second), copy_image=False)

        self.assertIsNone(self.db.case(cid)["case_mm_per_px"])
        self.assertEqual(self.db.latest_landmarks(cid, version), {})
        self.assertEqual(self.db.latest_results(cid, version), [])
        with self.db.connect() as con:
            archived = con.execute(
                "SELECT image_hash,image_revision FROM results WHERE case_id=?",
                (cid,),
            ).fetchall()
            self.assertEqual(len(archived), 1)
            self.assertTrue(str(archived[0]["image_hash"]).startswith("historical:"))
            self.assertLess(int(archived[0]["image_revision"]), 0)
        # The old image's measurements remain in history, but are no longer
        # considered current for the replacement image.
        with self.db.connect() as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM landmarks WHERE case_id=?", (cid,)).fetchone()[0], len(points))
            self.assertEqual(con.execute("SELECT COUNT(*) FROM results WHERE case_id=?", (cid,)).fetchone()[0], 1)
        events = self.db.audit_rows(self.study)
        self.assertTrue(any(row["event"] == "image_attached" for row in events))

    def test_only_linear_protocols_require_calibration(self):
        variables = [v for group in analysis_catalog().values() for v in group]
        linear = next(
            (v for v in variables if v.unit.strip().lower() in {"mm", "cm"}
             or "distance" in v.kind.lower() or "lineal" in v.kind.lower()),
            None,
        )
        angular = next(
            (v for v in variables if v.unit.strip().lower() in {"°", "deg", "degree", "degrees"}
             or "angle" in v.kind.lower() or "angular" in v.kind.lower()),
            None,
        )
        self.assertIsNotNone(linear, "El catálogo debe contener al menos una variable lineal")
        self.assertIsNotNone(angular, "El catálogo debe contener al menos una variable angular")
        self.assertFalse(requires_calibration([angular.key]))
        self.assertTrue(requires_calibration([linear.key]))
        self.assertTrue(requires_calibration([angular.key, linear.key]))

    def test_angular_measurements_calculate_without_scale_but_linear_do_not(self):
        variables = [v for group in analysis_catalog().values() for v in group]
        linear = next(
            v for v in variables if v.unit.strip().lower() in {"mm", "cm"}
            or "distance" in v.kind.lower() or "lineal" in v.kind.lower()
        )
        angular = next(
            v for v in variables if v.unit.strip().lower() in {"°", "deg", "degree", "degrees"}
            or "angle" in v.kind.lower() or "angular" in v.kind.lower()
        )
        keys = [angular.key, linear.key]
        required = minimum_landmarks(keys)
        points = {name: (float(i * 13 + 7), float(i * 9 + 3)) for i, name in enumerate(required)}
        angle_result = compute_selected([angular.key], points, None)[0]
        linear_result = compute_selected([linear.key], points, None)[0]
        self.assertIsNotNone(angle_result["value"], angle_result["interpretation"])
        self.assertIsNone(linear_result["value"])
        self.assertIn("calibración", linear_result["interpretation"].lower())

    def test_invalid_calibration_values_are_rejected(self):
        cid = self.db.add_case(self.study, "bad-calibration")
        for value in (0, -0.25, float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.db.update_case_calibration(cid, value)
                with self.assertRaises(ValueError):
                    self.db.save_trace(cid, 1, {}, [], [], value)
        self.assertIsNone(self.db.case(cid)["case_mm_per_px"])

    def test_non_finite_results_are_sanitized_and_never_complete_a_case(self):
        image = Path(self.tmp.name) / "finite-check.png"
        image.write_bytes(b"radiograph fixture")
        cid = self.db.add_case(self.study, "finite-check", image_path=str(image), copy_image=False)
        variable = next(v for group in analysis_catalog().values() for v in group)
        version = self.db.save_protocol(
            self.study,
            {"selected_variables": [variable.key], "required_landmarks": list(variable.points)},
        )
        points = {name: (float(i * 13 + 7), float(i * i * 11 + 3)) for i, name in enumerate(variable.points)}
        self.db.save_trace(
            cid, version, points,
            [{"analysis": variable.analysis, "measurement": variable.name, "value": float("nan"),
              "unit": variable.unit, "reference": "", "interpretation": "test"}],
            [variable.name], 0.25,
        )
        saved = self.db.latest_results(cid, version)
        self.assertEqual(len(saved), 1)
        self.assertIsNone(saved[0]["value"])
        self.assertNotEqual(self.db.case(cid)["status"], "complete")

    def test_landmark_minimization(self):
        cat = analysis_catalog(); keys = []
        for _, variables in list(cat.items())[:3]:
            if variables: keys.append(variables[0].key)
        s = shared_landmark_summary(keys)
        self.assertEqual(s["measurement_count"], len(keys))
        self.assertLessEqual(s["unique_landmark_count"], sum(len(v.points) for vs in cat.values() for v in vs if v.key in keys))


if __name__ == "__main__": unittest.main()
