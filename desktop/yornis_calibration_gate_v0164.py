from __future__ import annotations

"""Image-specific calibration guard: require mm/px only for selected linear measures."""

import math

from research_db import ResearchDB


def _walk_canvases(widget):
    """Find the classic image canvas without depending on its private attribute name."""
    try:
        from tkinter import Canvas
    except Exception:
        Canvas = ()
    try:
        children = widget.winfo_children()
    except Exception:
        children = []
    for child in children:
        if Canvas and isinstance(child, Canvas):
            yield child
        yield from _walk_canvases(child)


def _set_classic_canvas_state(app, state: str) -> None:
    for canvas in _walk_canvases(app):
        try:
            canvas.configure(state=state)
        except Exception:
            pass


def _positive_finite(value) -> bool:
    """Accept only a real, finite, strictly positive calibration value."""
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return False
    return math.isfinite(number) and number > 0


def _has_two_distinct_calibration_points(app) -> bool:
    """Require two finite 2D endpoints separated by a meaningful pixel distance."""
    points = getattr(app, "calibration_points", None)
    if not isinstance(points, (list, tuple)) or len(points) < 2:
        return False
    try:
        x1, y1 = float(points[0][0]), float(points[0][1])
        x2, y2 = float(points[1][0]), float(points[1][1])
    except (TypeError, ValueError, IndexError, OverflowError):
        return False
    values = (x1, y1, x2, y2)
    if not all(math.isfinite(value) for value in values):
        return False
    return math.hypot(x2 - x1, y2 - y1) > 1e-9


def _has_valid_scale(app) -> bool:
    return _positive_finite(getattr(app, "mm_per_px", None))


def _calibration_mode_enabled(app) -> bool:
    """Support both the normalized and legacy classic-mode attribute names."""
    return bool(getattr(app, "calibration_mode", False) or getattr(app, "calib_mode", False))


def _set_calibration_mode(app, enabled: bool) -> None:
    for attribute in ("calibration_mode", "calib_mode"):
        if hasattr(app, attribute):
            setattr(app, attribute, bool(enabled))


def _requires_calibration(app) -> bool:
    """Require mm/px only when the exact individual selection contains linear measures."""
    mapping = getattr(app, "individual_measurements", None)
    if not isinstance(mapping, dict) or not mapping:
        # Unknown/legacy selections fail closed: never mistake pixels for mm.
        return True
    selected = {
        (str(analysis), str(name))
        for analysis, names in mapping.items()
        for name in (names or [])
    }
    if not selected:
        return True
    try:
        import yornis_measurement_corrections_v0166 as corrections
        corrections.install()
        import classic_engine
        measurements = [
            m for m in classic_engine.MEASUREMENTS
            if (str(m.analysis), str(m.name)) in selected
        ]
    except Exception:
        return True
    # CVM and C2-C4 visual alignment are qualitative outcomes, not mm measures.
    qualitative_special = set()
    try:
        import yornis_cervical_v0152 as cervical
        qualitative_special.add((cervical.CVM_ANALYSIS, "Estadio CVM registrado"))
        qualitative_special.add((cervical.CVM_ANALYSIS, cervical.CVM_MEASUREMENT))
        qualitative_special.add((cervical.POSTURE_ANALYSIS, cervical.POSTURE_MEASUREMENT))
    except Exception:
        pass
    try:
        import yornis_alignment_v0152 as alignment
        qualitative_special.add((alignment.ALIGNMENT_ANALYSIS, alignment.ALIGNMENT_MEASUREMENT))
    except Exception:
        pass
    matched = {(str(m.analysis), str(m.name)) for m in measurements}
    unresolved = selected - matched - qualitative_special
    # If any selected label cannot be resolved, retain the safe calibration gate.
    if unresolved:
        return True
    for m in measurements:
        unit = str(getattr(m, "unit", "") or "").lower().replace(" ", "")
        kind = str(getattr(m, "kind", "") or "").lower()
        if unit in {"mm", "cm"} or any(
            term in kind for term in ("distance", "lineal", "linear", "length")
        ):
            return True
    return False


def install_individual(classic_class) -> None:
    """Require a fresh accepted calibration only when the selected measurements are linear."""
    if getattr(classic_class, "_yornis_calibration_gate_v0164", False):
        return

    original_load = getattr(classic_class, "load_image_file", None)
    original_start = getattr(classic_class, "start_calibration", None)
    original_finish = getattr(classic_class, "finish_calibration", None)

    if callable(original_load):
        def load_image_file(self, *args, **kwargs):
            # Coordinates and scale are tied to the old image; never carry them over.
            self.calibration_points = []
            self.calibration_real_mm = None
            self.points = {}
            self.mm_per_px = None
            _set_calibration_mode(self, False)
            _set_classic_canvas_state(self, "disabled")
            self._yornis_loading_image_v0164 = True
            try:
                result = original_load(self, *args, **kwargs)
            finally:
                self._yornis_loading_image_v0164 = False
            # Some legacy loaders toggle their calibration-mode flag. Reassert
            # a neutral state before deciding whether this selection needs mm/px.
            _set_calibration_mode(self, False)
            _set_classic_canvas_state(self, "disabled")
            if _requires_calibration(self):
                if callable(getattr(self, "start_calibration", None)):
                    try:
                        self.after_idle(self.start_calibration)
                    except Exception:
                        self.start_calibration()
            else:
                # Purely angular selections need no scale; permit guided tracing.
                self.mm_per_px = None
                _set_calibration_mode(self, False)
                try:
                    self.after_idle(lambda: _set_classic_canvas_state(self, "normal"))
                except Exception:
                    _set_classic_canvas_state(self, "normal")
            return result
        classic_class.load_image_file = load_image_file

    if callable(original_start):
        def start_calibration(self, *args, **kwargs):
            # Suppress a legacy loader's automatic prompt while its image import
            # is running. The load wrapper makes one selection-aware decision after
            # the import completes, preventing duplicate calibration dialogs.
            if getattr(self, "_yornis_loading_image_v0164", False):
                return None
            # Keep the prior image-specific calibration available if the user
            # opens the dialog but cancels. It remains valid for this same image.
            previous_scale = getattr(self, "mm_per_px", None)
            previous_points = getattr(self, "calibration_points", None)
            previous_real_mm = getattr(self, "calibration_real_mm", None)
            self.calibration_points = []
            self.calibration_real_mm = None
            _set_calibration_mode(self, False)
            _set_classic_canvas_state(self, "disabled")

            result = original_start(self, *args, **kwargs)

            # The legacy dialog returns with its calibration-mode flag enabled
            # only when the user accepted a positive real-world distance and
            # the engine is waiting for the two image clicks. Both the modern
            # calibration_mode and classic calib_mode names are supported.
            accepted = (
                _calibration_mode_enabled(self)
                and _positive_finite(getattr(self, "calibration_real_mm", None))
            )
            if accepted:
                self.mm_per_px = None
                _set_classic_canvas_state(self, "normal")
            else:
                self.mm_per_px = previous_scale
                self.calibration_points = previous_points or []
                self.calibration_real_mm = previous_real_mm
                _set_classic_canvas_state(
                    self, "normal" if _has_valid_scale(self) else "disabled"
                )
            return result
        classic_class.start_calibration = start_calibration

    original_calculate = getattr(classic_class, "calculate", None)
    if callable(original_calculate):
        def calculate(self, *args, **kwargs):
            if _requires_calibration(self) and not _has_valid_scale(self):
                try:
                    from tkinter import messagebox
                    messagebox.showwarning(
                        "Yornis",
                        "Las medidas lineales requieren una calibración válida de esta radiografía.",
                        parent=self,
                    )
                except Exception:
                    pass
                return None
            return original_calculate(self, *args, **kwargs)
        classic_class.calculate = calculate

    if callable(original_finish):
        def finish_calibration(self, *args, **kwargs):
            # Do not call the legacy calculation with missing, coincident, or
            # invalid calibration points: some versions divide by zero here.
            ready = (
                _positive_finite(getattr(self, "calibration_real_mm", None))
                and _has_two_distinct_calibration_points(self)
            )
            if not ready:
                self.mm_per_px = None
                _set_calibration_mode(self, False)
                _set_classic_canvas_state(self, "disabled")
                return None

            result = original_finish(self, *args, **kwargs)
            valid = _has_valid_scale(self)
            if not valid:
                self.mm_per_px = None
                _set_calibration_mode(self, False)
            _set_classic_canvas_state(self, "normal" if valid else "disabled")
            return result
        classic_class.finish_calibration = finish_calibration

    classic_class._yornis_calibration_gate_v0164 = True


def install_database() -> None:
    """Guard image identity after legacy hardening and calibration wrappers."""
    current_attach = ResearchDB.attach_image
    if not getattr(current_attach, "_yornis_image_calibration_reset_v0164", False):
        def attach_image_with_calibration_reset(self, case_id, image_path, copy_image=True):
            result = current_attach(self, case_id, image_path, copy_image)
            self.update_case_calibration(case_id, None)
            # Compatibility attach_image implementations do not all archive
            # old traces. Enforce image identity here as the final guard, while
            # avoiding repeated historical prefixes when the core layer already
            # performed the archive.
            with self.connect() as con:
                for table in ("landmarks", "results"):
                    con.execute(
                        f"UPDATE {table} SET "
                        "image_hash=CASE "
                        "WHEN COALESCE(image_hash,'') LIKE 'historical:%' THEN image_hash "
                        "ELSE 'historical:' || COALESCE(NULLIF(image_hash,''),'legacy-unidentified') END, "
                        "image_revision=-ABS(COALESCE(image_revision,1)) "
                        "WHERE case_id=? AND COALESCE(image_revision,1)>0",
                        (case_id,),
                    )
            # The cervical assessment snapshot is case/protocol scoped. Archive
            # its image identity and clear active classifications on image swap;
            # the historical result rows and audit events remain preserved.
            with self.connect() as con:
                exists = con.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='cervical_assessments'"
                ).fetchone()
                if exists:
                    cols = {row[1] for row in con.execute("PRAGMA table_info(cervical_assessments)").fetchall()}
                    if "image_hash" not in cols:
                        con.execute("ALTER TABLE cervical_assessments ADD COLUMN image_hash TEXT DEFAULT ''")
                        cols.add("image_hash")
                    if "image_revision" not in cols:
                        con.execute("ALTER TABLE cervical_assessments ADD COLUMN image_revision INTEGER NOT NULL DEFAULT 1")
                        cols.add("image_revision")
                    assignments = [
                        "image_hash='historical:' || COALESCE(NULLIF(image_hash,''),'legacy-unidentified')",
                        "image_revision=-ABS(COALESCE(image_revision,1))",
                    ]
                    for column, expression in (
                        ("lordosis_angle", "NULL"),
                        ("posture_class", "'Stale: radiograph changed'"),
                        ("cvm_stage", "NULL"),
                        ("cvm_phase", "'Stale: radiograph changed'"),
                        ("features_json", "'{}'"),
                        ("alignment_code", "NULL"),
                        ("alignment_class", "'Stale: radiograph changed'"),
                        ("alignment_notes", "''"),
                    ):
                        if column in cols:
                            assignments.append(f"{column}={expression}")
                    con.execute(
                        "UPDATE cervical_assessments SET " + ",".join(assignments) + " WHERE case_id=?",
                        (case_id,),
                    )
            case = self.case(case_id)
            if case:
                self.audit(
                    case["study_id"],
                    "image_calibration_reset",
                    case_id=case_id,
                    calibration_reset=True,
                    prior_trace_preserved=True,
                    current_image_sha256=str(case["file_hash"] or ""),
                )
            return result

        attach_image_with_calibration_reset._yornis_image_calibration_reset_v0164 = True
        ResearchDB.attach_image = attach_image_with_calibration_reset

    # Some older hardening layers replace latest_results after the core DB
    # implementation. Apply a final, SQL-backed image/revision filter after
    # those wrappers so a historical row can never reappear as current.
    current_latest = ResearchDB.latest_results
    if getattr(current_latest, "_yornis_latest_results_image_guard_v0166", False):
        return

    def latest_results_for_current_image(self, case_id: int, protocol_version: int):
        case = self.case(case_id)
        if not case:
            return []
        image_hash = self._active_image_hash(case)
        stored_hash = str(case["file_hash"] or "")
        image_revision = int(case["image_revision"] or 1)
        has_current_image = bool(image_hash and stored_hash and image_hash == stored_hash)

        # CVM and C2-C4 alignment are manually assessed outcomes. They do not
        # require an automatic landmark trace, but they must remain scoped to
        # the active image/revision. For image-less manual assessments, only
        # rows without an image identity are eligible.
        manual_analyses = (
            "CVM C2–C4",
            "Postura vertebral vertical C2–C4",
        )
        with self.connect() as con:
            if has_current_image:
                manual_rows = con.execute(
                    """
                    SELECT r.* FROM results r
                    WHERE r.case_id=? AND r.protocol_version=?
                      AND r.analysis IN (?,?)
                      AND r.image_hash=? AND r.image_revision=?
                      AND r.version=(
                        SELECT MAX(r2.version) FROM results r2
                        WHERE r2.case_id=r.case_id
                          AND r2.protocol_version=r.protocol_version
                          AND r2.analysis=r.analysis
                          AND r2.measurement=r.measurement
                          AND r2.image_hash=r.image_hash
                          AND r2.image_revision=r.image_revision
                      )
                    ORDER BY r.analysis,r.measurement
                    """,
                    (case_id, protocol_version, *manual_analyses, image_hash, image_revision),
                ).fetchall()
            else:
                manual_rows = con.execute(
                    """
                    SELECT r.* FROM results r
                    WHERE r.case_id=? AND r.protocol_version=?
                      AND r.analysis IN (?,?)
                      AND COALESCE(r.image_hash,'')=''
                      AND COALESCE(r.image_revision,1)>0
                      AND r.version=(
                        SELECT MAX(r2.version) FROM results r2
                        WHERE r2.case_id=r.case_id
                          AND r2.protocol_version=r.protocol_version
                          AND r2.analysis=r.analysis
                          AND r2.measurement=r.measurement
                          AND COALESCE(r2.image_hash,'')=''
                          AND COALESCE(r2.image_revision,1)>0
                      )
                    ORDER BY r.analysis,r.measurement
                    """,
                    (case_id, protocol_version, *manual_analyses),
                ).fetchall()

        if not has_current_image:
            return list(manual_rows)

        # Keep automatically computed outcomes only when the image and a
        # matching current trace are both present; add image-bound manual
        # outcomes independently because they are not landmark calculations.
        rows = current_latest(self, case_id, protocol_version) or []
        combined = {}
        for row in rows:
            try:
                key = (str(row["analysis"]), str(row["measurement"]), int(row["version"]))
                combined[key] = row
            except (KeyError, IndexError, TypeError, ValueError):
                continue
        for row in manual_rows:
            try:
                key = (str(row["analysis"]), str(row["measurement"]), int(row["version"]))
                combined[key] = row
            except (KeyError, IndexError, TypeError, ValueError):
                continue
        return sorted(
            combined.values(),
            key=lambda row: (str(row["analysis"]), str(row["measurement"])),
        )

    latest_results_for_current_image._yornis_latest_results_image_guard_v0166 = True
    ResearchDB.latest_results = latest_results_for_current_image
