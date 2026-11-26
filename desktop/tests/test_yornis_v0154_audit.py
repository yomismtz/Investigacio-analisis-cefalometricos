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
import yornis_ceph_quality_v0153 as quality153
import research_stability_db_v0141
import yornis_storage_v015
import yornis_import_v015
import yornis_backup_v015
import research_ui
import yornis_cervical_v0152 as cv
import yornis_alignment_v0152 as al
from research_db import ResearchDB

research_stability_db_v0141.install()
yornis_storage_v015.install()
yornis_import_v015.install()
yornis_backup_v015.install()
# Register the same special Research outcomes as the real application.
cv.install_research(research_ui.ResearchWorkspace)
al.install_research(research_ui.ResearchWorkspace)
quality153.install_research(research_ui.ResearchWorkspace)

import yornis_audit_hardening_v0154 as hard
hard.install_global()
import yornis_calibration_gate_v0164 as calibration_gate
calibration_gate.install_database()

import classic_engine as engine
import research_protocol as rp


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

    def test_calculation_engine_contains_103_numeric_measurements(self):
        self.assertEqual(len(engine.MEASUREMENTS), 106)

    def test_reference_catalog_count_and_fma_norm_are_consistent(self):
        import yornis_reference_help_v0154 as refs
        self.assertEqual(len(refs.TABLES), len({table["id"] for table in refs.TABLES}))
        tweed = next(table for table in refs.TABLES if table["id"] == "tweed")
        fma = next(row for row in tweed["rows"] if row[0] == "FMA")
        self.assertEqual((fma[1], fma[2]), ("25°", "±4°"))
        variable = next(v for v in rp.analysis_catalog()["Tweed"] if v.name == "FMA")
        self.assertTrue(rp.reference_for(variable).startswith("25° ±4°"))
        fmia = next(v for v in rp.analysis_catalog()["Tweed"] if v.name == "FMIA")
        fmia_engine = next(m for m in engine.MEASUREMENTS if m.analysis == "Tweed" and m.name == "FMIA")
        self.assertIsNone(fmia_engine.lo)
        self.assertIsNone(fmia_engine.hi)
        self.assertIn("FMA 21°–29°", rp.reference_for(fmia))

    def test_ricketts_reference_table_matches_calculation_catalog(self):
        import yornis_reference_help_v0154 as refs
        table = next(t for t in refs.TABLES if t["id"] == "ricketts")
        table_names = {row[0] for row in table["rows"]}
        engine_names = {v.name for v in rp.analysis_catalog()["Ricketts"]}
        self.assertEqual(table_names, engine_names)
        lower_angle = next(v for v in rp.analysis_catalog()["Ricketts"] if v.name == "L1 a A-Pg (°)")
        lower_engine = next(m for m in engine.MEASUREMENTS if m.analysis == "Ricketts" and m.name == "L1 a A-Pg (°)")
        self.assertEqual((lower_engine.lo, lower_engine.hi), (18.0, 26.0))
        upper_distance = next(v for v in rp.analysis_catalog()["Ricketts"] if v.name == "U1 a A-Pg")
        upper_engine = next(m for m in engine.MEASUREMENTS if m.analysis == "Ricketts" and m.name == "U1 a A-Pg")
        self.assertIsNone(upper_engine.lo)
        self.assertIsNone(upper_engine.hi)
        convexity = next(v for v in rp.analysis_catalog()["Ricketts"] if v.name == "Convexidad A a N-Pg")
        convexity_engine = next(m for m in engine.MEASUREMENTS if m.analysis == "Ricketts" and m.name == "Convexidad A a N-Pg")
        self.assertIsNone(convexity_engine.lo)
        self.assertIsNone(convexity_engine.hi)
        self.assertIn("ajustar por edad", rp.reference_for(convexity))

    def test_steiner_sn_gogn_angle_uses_the_correct_two_lines_and_is_scale_invariant(self):
        import math

        measurement = next(
            m for m in engine.MEASUREMENTS
            if m.analysis == "Steiner" and "GoGn" in m.name
        )
        self.assertEqual(set(measurement.pts), {"S", "N", "Go", "Gn"})
        self.assertEqual((measurement.lo, measurement.hi), (27.0, 37.0))
        self.assertIn("32° ±5°", measurement.ref)

        # SN is vertical (90° to horizontal); Go-Gn is 58° to horizontal.
        # The smaller inter-plane angle is therefore exactly 32°.
        theta = math.radians(58.0)
        points = {
            "S": (0.0, 0.0),
            "N": (0.0, 100.0),
            "Go": (100.0, 0.0),
            "Gn": (100.0 + 100.0 * math.cos(theta), 100.0 * math.sin(theta)),
        }
        value = engine.compute(measurement, points, None, "right")
        self.assertAlmostEqual(value, 32.0, places=5)

        scaled = {name: (x * 7.0, y * 7.0) for name, (x, y) in points.items()}
        self.assertAlmostEqual(engine.compute(measurement, scaled, None, "right"), 32.0, places=5)

        mirrored = {name: (-x, y) for name, (x, y) in points.items()}
        self.assertAlmostEqual(engine.compute(measurement, mirrored, None, "left"), 32.0, places=5)

    def test_steiner_anb_equals_sna_minus_snb_for_consistent_geometry(self):
        sna = next(m for m in engine.MEASUREMENTS if m.analysis == "Steiner" and m.name == "SNA")
        snb = next(m for m in engine.MEASUREMENTS if m.analysis == "Steiner" and m.name == "SNB")
        anb = next(m for m in engine.MEASUREMENTS if m.analysis == "Steiner" and m.name == "ANB")
        points = {
            "S": (0.0, 0.0),
            "N": (0.0, 100.0),
            "A": (50.0, 0.0),
            "B": (30.0, 0.0),
        }
        a = engine.compute(sna, points, None, "right")
        b = engine.compute(snb, points, None, "right")
        ab = engine.compute(anb, points, None, "right")
        self.assertAlmostEqual(ab, a - b, places=5)

    def test_downs_and_tweed_engine_conventions_are_consistent(self):
        import math
        import classic_engine as ce
        import yornis_measurement_corrections_v0166 as corrections
        corrections.install()

        def measurement(analysis, name):
            return next(m for m in ce.MEASUREMENTS if m.analysis == analysis and m.name == name)

        fma = measurement("Tweed", "FMA")
        fmia = measurement("Tweed", "FMIA")
        self.assertEqual((fma.lo, fma.hi), (21, 29))
        self.assertIsNone(fmia.lo)
        self.assertIsNone(fmia.hi)
        self.assertIn("FMA 21°–29°", fmia.ref)
        impa = measurement("Tweed", "IMPA")
        self.assertIsNone(impa.lo)
        self.assertIsNone(impa.hi)
        self.assertIn("FMA ≤20°", impa.ref)
        self.assertIn("92°–94°", impa.ref)

        l1_occl = measurement("Downs", "L1/plano oclusal")
        angle = math.radians(75.5)
        points = {"L1i": (0.0, 0.0), "L1a": (1.0, 0.0), "OcP": (0.0, 0.0), "OcA": (math.cos(angle), math.sin(angle))}
        self.assertAlmostEqual(ce.compute(l1_occl, points, None), 14.5, places=5)

        convexity = measurement("Downs", "Ángulo de convexidad")
        anterior = {"N": (0.0, 0.0), "A": (1.0, 5.0), "Pg": (0.0, 10.0)}
        posterior = {"N": (0.0, 0.0), "A": (-1.0, 5.0), "Pg": (0.0, 10.0)}
        self.assertGreater(ce.compute(convexity, anterior, None), 0)
        self.assertLess(ce.compute(convexity, posterior, None), 0)

        ab_plane = measurement("Downs", "Plano A-B")
        ab_points = {"N": (0.0, 0.0), "Pg": (0.0, 10.0), "B": (0.0, 5.0), "A": (0.4, 0.0)}
        self.assertAlmostEqual(ce.compute(ab_plane, ab_points, None), -4.57, delta=0.1)
        ab_left = {"N": (0.0, 0.0), "Pg": (0.0, 10.0), "B": (0.0, 5.0), "A": (-0.4, 0.0)}
        self.assertAlmostEqual(ce.compute(ab_plane, ab_left, None, "left"), -4.57, delta=0.1)

    def test_cvm_reference_sequence_matches_published_morphology(self):
        import yornis_reference_help_v0154 as refs
        cvm = next(table for table in refs.TABLES if table["id"] == "cvm")
        rows = {row[0]: row for row in cvm["rows"]}
        self.assertIn("CS2", rows["Concavidad borde inferior C2"][1])
        self.assertIn("CS3", rows["Concavidad borde inferior C3"][1])
        self.assertIn("CS4", rows["Concavidad borde inferior C4"][1])
        self.assertIn("CS4: rectangular horizontal", rows["Forma de cuerpos C3–C4"][1])

    def test_reference_tables_are_counted_and_cervical_claims_are_limited(self):
        import yornis_reference_help_v0154_all as refs
        from pathlib import Path
        self.assertEqual(len(refs.TABLES), 17)
        ui_source = (Path(__file__).resolve().parents[1] / "yornis_reference_help_v0156.py").read_text(encoding="utf-8")
        self.assertIn("import yornis_reference_help_v0154_all as base", ui_source)
        self.assertIn('text=f"{len(TABLES)} tablas', ui_source)
        cervical = next(table for table in refs.TABLES if table["id"] == "alineacion_cervical_c2_c4")
        self.assertIn("No diagnostica patología cervical", cervical["note"])
        self.assertNotIn("vía aérea", " ".join(str(cell) for row in cervical["rows"] for cell in row))

    def test_downs_and_mcnamara_reference_values_match_primary_sources(self):
        import yornis_reference_help_v0154 as refs
        downs = next(table for table in refs.TABLES if table["id"] == "downs")
        downs_rows = {row[0]: row for row in downs["rows"]}
        self.assertEqual(downs_rows["Ángulo de convexidad"][2], "±5.1°")
        self.assertEqual(downs_rows["Plano A-B"][2], "±3.7°")
        self.assertIn("20 sujetos blancos de 12–17 años", downs["note"])
        self.assertIn("L1/plano oclusal", downs_rows)
        self.assertIn("L1/plano mandibular", downs_rows)
        self.assertIn("U1 a A–Pg", downs_rows)
        engine_downs = {m.name for m in engine.MEASUREMENTS if m.analysis == "Downs"}
        self.assertEqual(set(downs_rows), engine_downs)

        mcnamara = next(table for table in refs.TABLES if table["id"] == "mcnamara")
        rows = {row[0]: row for row in mcnamara["rows"]}
        self.assertIn("Mixta: −8 a −6 mm", rows["Pg-Nperp"][1])
        self.assertIn("adulto: −2 a +4 mm", rows["Pg-Nperp"][1])
        self.assertIn("8% de magnificación", mcnamara["note"])
        self.assertIn("♀ 11.3 mm / ♂ 13.5 mm", rows["Faringe inferior"][1])

    def test_steiner_bands_are_not_mislabeled_as_original_standard_deviations(self):
        import yornis_reference_help_v0154 as refs
        from pathlib import Path
        steiner = next(table for table in refs.TABLES if table["id"] == "steiner")
        self.assertIn("sin desviación estándar original", steiner["note"])
        table_names = {row[0] for row in steiner["rows"]}
        engine_names = {v.name for v in rp.analysis_catalog()["Steiner"]}
        self.assertEqual(table_names, engine_names)
        pog_nb_engine = next(m for m in engine.MEASUREMENTS if m.analysis == "Steiner" and m.name == "Pog a NB")
        self.assertIsNone(pog_nb_engine.lo)
        self.assertIsNone(pog_nb_engine.hi)
        self.assertIn("2 mm", rp.reference_for(next(v for v in rp.analysis_catalog()["Steiner"] if v.name == "Pog a NB")))
        ui_source = (Path(__file__).resolve().parents[1] / "yornis_reference_help_v0156.py").read_text(encoding="utf-8")
        self.assertIn('"Referencia", "DE / rango"', ui_source)
        self.assertIn("banda posterior, no DE original", rp.reference_for(
            next(v for v in rp.analysis_catalog()["Steiner"] if v.name == "SNA")
        ))

    def test_ricketts_and_jarabak_static_norms_warn_about_growth_and_size(self):
        import yornis_reference_help_v0154 as refs
        ricketts = next(table for table in refs.TABLES if table["id"] == "ricketts")
        jarabak = next(table for table in refs.TABLES if table["id"] == "bjork_jarabak")
        self.assertIn("ajusta por edad", ricketts["note"])
        self.assertIn("no se automatiza la corrección por edad", ricketts["note"])
        self.assertIn("edad, sexo y tamaño corporal", jarabak["note"])
        self.assertIn("no son umbrales universales", jarabak["note"])

    def test_c1_c7_lordosis_is_descriptive_without_unvalidated_thresholds(self):
        import classic_engine as ce
        import yornis_cervical_v0152 as cervical
        measurement = next(
            m for m in ce.MEASUREMENTS
            if m.analysis == cervical.POSTURE_ANALYSIS and m.name == cervical.POSTURE_MEASUREMENT
        )
        self.assertIsNone(measurement.lo)
        self.assertIsNone(measurement.hi)
        label, explanation = cervical.posture_classification(40.0)
        self.assertIn("descriptivo", label.lower())
        self.assertIn("No se aplica un umbral universal", explanation)
        self.assertNotIn("35–45", cervical.LORDOSIS_REFERENCE)

    def test_cvm_timing_is_described_as_cohort_estimate(self):
        import yornis_cervical_v0152 as cervical
        result = cervical.classify_cvm("no", "no", "no", "trapezoidal", "trapezoidal")
        self.assertIn("cohorte original", result["timing"])
        self.assertIn("no es una predicción individual exacta", result["timing"])
        self.assertIn("no predicen con exactitud", cervical.CVM_REFERENCE)

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

    def test_cvm_and_alignment_outcomes_are_bound_to_the_active_radiograph(self):
        cv_key = next(v.key for v in rp.analysis_catalog()[cv.CVM_ANALYSIS])
        pv = self._save_protocol([cv_key])
        cid = self.db.add_case(self.study, "cervical-image-scope")
        self.db.case_protocol_version(cid, pv)

        class Workspace:
            pass

        workspace = Workspace()
        workspace.case_id = cid
        workspace.db = self.db
        workspace.protocol_version = pv

        cv._save_cvm(
            workspace,
            {"stage": 2, "phase": "Prepuberal", "timing": "cohorte"},
            {"c2": "si", "c3": "no", "c4": "no"},
        )
        al._save_alignment(workspace, al.classify_alignment("Lordosis normal"))
        current = self.db.latest_results(cid, pv)
        self.assertEqual(
            {row["analysis"] for row in current},
            {cv.CVM_ANALYSIS, al.ALIGNMENT_ANALYSIS},
        )

        radiograph = self.root / "cervical-swap.img"
        radiograph.write_bytes(b"first radiograph")
        self.db.attach_image(cid, radiograph, copy_image=False)
        self.assertEqual(self.db.latest_results(cid, pv), [])

        with self.db.connect() as con:
            stale = con.execute(
                "SELECT cvm_stage,alignment_code,image_hash,image_revision "
                "FROM cervical_assessments WHERE case_id=? AND protocol_version=?",
                (cid, pv),
            ).fetchone()
        self.assertIsNone(stale["cvm_stage"])
        self.assertIsNone(stale["alignment_code"])
        self.assertTrue(str(stale["image_hash"]).startswith("historical:"))
        self.assertLess(int(stale["image_revision"]), 0)

        cv._save_cvm(
            workspace,
            {"stage": 3, "phase": "Circumpuberal", "timing": "cohorte"},
            {"c2": "si", "c3": "si", "c4": "no"},
        )
        al._save_alignment(workspace, al.classify_alignment("Rectificación"))
        refreshed = self.db.latest_results(cid, pv)
        by_analysis = {row["analysis"]: row for row in refreshed}
        self.assertEqual(by_analysis[cv.CVM_ANALYSIS]["value"], 3.0)
        self.assertEqual(by_analysis[al.ALIGNMENT_ANALYSIS]["value"], 2.0)

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
        # Regression net: every registered automatic measurement must be callable
        # with a complete, non-degenerate synthetic landmark field.
        names = set()
        for m in engine.MEASUREMENTS:
            names.update(getattr(m, "pts", ()) or ())
        names.update(("S", "N", "Po", "Or", "Me", "Go", "Pg", "A", "B"))
        points = {}
        for i, name in enumerate(sorted(n for n in names if n), 1):
            # Irrational-ish deterministic field avoids coincident/parallel lines.
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
