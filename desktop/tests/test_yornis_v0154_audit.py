from __future__ import annotations

import json
import math
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Match the application install order before the v0.15.4 replacement layer.
import yornis_ceph_quality_v0153
import research_stability_db_v0141
import yornis_storage_v015
import yornis_import_v015
import yornis_backup_v015
from research_db import ResearchDB

research_stability_db_v0141.install()
yornis_storage_v015.install()
yornis_import_v015.install()
yornis_backup_v015.install()

import yornis_audit_hardening_v0154 as hard
hard.install_global()

import classic_engine as engine
import research_protocol as rp
import yornis_cervical_v0152 as cv
import yornis_alignment_v0152 as al


class AuditHardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = ResearchDB(self.root / "research.sqlite3")
        self.study = self.db.create_study("Audit v0.15.4")

    def tearDown(self):
        self.tmp.cleanup()

    def _save_protocol(self, keys):
        cfg = {"selected_variables": list(keys), "population": "cohorte de prueba"}
        return self.db.save_protocol(self.study, cfg)

    def test_hp_measurements_request_construction_landmarks(self):
        candidates = [v for vs in rp.analysis_catalog().values() for v in vs if str(v.kind).lower().startswith("hp_")]
        self.assertTrue(candidates)
        for v in candidates:
            required = rp.minimum_landmarks([v.key])
            for p in ("S", "N", "Po", "Or"):
                self.assertIn(p, required, (v.key, required))

    def test_latest_results_is_per_outcome_and_manual_history_is_append_only(self):
        cv_key = next(v.key for v in rp.analysis_catalog()[cv.CVM_ANALYSIS])
        pv = self._save_protocol([cv_key])
        cid = self.db.add_case(self.study, "001")
        self.db.case_protocol_version(cid, pv)
        class W: pass
        w = W(); w.case_id = cid; w.db = self.db; w.protocol = {"version": pv}
        hard.save_cvm_v154(w, {"stage": 1, "phase": "Prepuberal", "timing": "t1"}, {"c2": "no"})
        hard.save_cvm_v154(w, {"stage": 2, "phase": "Prepuberal", "timing": "t2"}, {"c2": "si"})
        with self.db.connect() as con:
            rows = con.execute("SELECT value,version FROM results WHERE case_id=? AND analysis=? AND measurement=? ORDER BY id", (cid, cv.CVM_ANALYSIS, cv.CVM_MEASUREMENT)).fetchall()
        self.assertEqual([(r["value"], r["version"]) for r in rows], [(1.0, 1), (2.0, 2)])
        latest = self.db.latest_results(cid, pv)
        current = next(r for r in latest if r["analysis"] == cv.CVM_ANALYSIS)
        self.assertEqual(current["value"], 2.0)

    def test_backup_is_consistent_study_scoped_and_restorable(self):
        other = self.db.create_study("Other study")
        self._save_protocol([])
        self.db.add_case(self.study, "001")
        self.db.add_case(other, "999")
        target = self.root / "backup.zip"
        self.db.backup_study(self.study, target)
        with zipfile.ZipFile(target) as z:
            self.assertIn("manifest.json", z.namelist())
            z.extract("database/yomceph_research.sqlite3", self.root / "unzip")
        snap = self.root / "unzip" / "database" / "yomceph_research.sqlite3"
        con = sqlite3.connect(snap)
        try:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(con.execute("SELECT COUNT(*) FROM studies").fetchone()[0], 1)
            self.assertEqual(con.execute("SELECT id FROM studies").fetchone()[0], self.study)
        finally:
            con.close()
        info = self.db.restore_backup_archive(target, self.root / "restored")
        self.assertEqual(info["integrity"], "ok")
        self.assertTrue(Path(info["database"]).exists())

    def test_json_redacts_legacy_paths_and_source_names(self):
        self._save_protocol([])
        cid = self.db.add_case(self.study, "001")
        self.db.audit(self.study, "legacy", case_id=cid, source_filename="Patient_Name.jpg", target="C:/secret/path/out.csv")
        out = self.root / "bundle.json"
        hard.export_json_v154(self.db, self.study, out)
        text = out.read_text(encoding="utf-8")
        self.assertNotIn("Patient_Name.jpg", text)
        self.assertNotIn("C:/secret/path", text)
        self.assertIn("<redacted>", text)

    def test_spss_declares_variables_and_categorical_labels(self):
        cv_key = next(v.key for v in rp.analysis_catalog()[cv.CVM_ANALYSIS])
        al_key = next(v.key for v in rp.analysis_catalog()[al.ALIGNMENT_ANALYSIS])
        pv = self._save_protocol([cv_key, al_key])
        out = self.root / "study.sps"
        hard.export_spss_v154(self.db, self.study, {"selected_variables": [cv_key, al_key], "version": pv}, out)
        s = out.read_text(encoding="utf-8")
        self.assertIn("/VARIABLES=", s)
        self.assertIn("CS1", s)
        self.assertIn("Lordosis normal", s)
        self.assertIn("(ORDINAL)", s)
        self.assertIn("(NOMINAL)", s)

    def test_all_numeric_measurements_compute_finite_on_nondegenerate_geometry(self):
        names = set()
        for m in engine.MEASUREMENTS:
            names.update(getattr(m, "pts", ()) or ())
        names.update(("S", "N", "Po", "Or", "Me", "Go", "Pg", "A", "B"))
        points = {}
        for i, name in enumerate(sorted(n for n in names if n), 1):
            points[name] = (float(i * 13 + (i % 5) * 2), float(i * i * 0.37 + (i % 7) * 11 + 3))
        failures = []
        for m in engine.MEASUREMENTS:
            try:
                value = engine.compute(m, points, 0.1, "right")
                if not math.isfinite(float(value)):
                    failures.append((m.analysis, m.name, f"non-finite {value}"))
            except Exception as exc:
                failures.append((m.analysis, m.name, repr(exc)))
        self.assertFalse(failures, failures[:12])

    def test_future_timestamps_are_offset_aware(self):
        stamp = hard.now_utc()
        self.assertTrue(stamp.endswith("+00:00"), stamp)


if __name__ == "__main__":
    unittest.main()
