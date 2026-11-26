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
            if hasattr(self, "calibration_mode"):
                self.calibration_mode = False
            _set_classic_canvas_state(self, "disabled")
            self._yornis_loading_image_v0164 = True
            try:
                result = original_load(self, *args, **kwargs)
            finally:
                self._yornis_loading_image_v0164 = False
            # Some legacy loaders toggle calibration_mode themselves. Reassert
            # a neutral state before deciding whether this selection needs mm/px.
            if hasattr(self, "calibration_mode"):
                self.calibration_mode = False
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
                if hasattr(self, "calibration_mode"):
                    self.calibration_mode = False
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
            if hasattr(self, "calibration_mode"):
                self.calibration_mode = False
            _set_classic_canvas_state(self, "disabled")

            result = original_start(self, *args, **kwargs)

            # The legacy dialog returns with calibration_mode=True only when the
            # user accepted a positive real-world distance and the engine is
            # waiting for the two image clicks. Only then invalidate the old
            # scale while the new endpoints are being collected.
            accepted = (
                bool(getattr(self, "calibration_mode", False))
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
                if hasattr(self, "calibration_mode"):
                    self.calibration_mode = False
                _set_classic_canvas_state(self, "disabled")
                return None

            result = original_finish(self, *args, **kwargs)
            valid = _has_valid_scale(self)
            if not valid:
                self.mm_per_px = None
                if hasattr(self, "calibration_mode"):
                    self.calibration_mode = False
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
        rows = current_latest(self, case_id, protocol_version) or []

        # CVM and C2-C4 alignment are explicitly entered categorical outcomes,
        # not automatic landmark calculations. Keep them visible for image-less
        # cases, but bind them to the current image/revision whenever one exists.
        manual_analyses = {
            "CVM C2–C4",
            "Postura vertebral vertical C2–C4",
        }
        has_current_image = bool(image_hash and stored_hash and image_hash == stored_hash)
        if not has_current_image:
            return [
                row for row in rows
                if str(row["analysis"] or "") in manual_analyses
                and not str(row["image_hash"] or "")
            ]

        with self.connect() as con:
            current_trace = con.execute(
                "SELECT 1 FROM landmarks l JOIN cases c ON c.id=l.case_id "
                "WHERE l.case_id=? AND l.protocol_version=? AND l.image_hash=? "
                "AND l.image_hash=c.file_hash AND l.image_revision=c.image_revision LIMIT 1",
                (case_id, protocol_version, image_hash),
            ).fetchone() is not None

        current = []
        for row in rows:
            try:
                same_image = (
                    str(row["image_hash"] or "") == image_hash
                    and int(row["image_revision"] or 0) == image_revision
                )
                is_manual = str(row["analysis"] or "") in manual_analyses
                if same_image and (is_manual or current_trace):
                    current.append(row)
            except (KeyError, IndexError, TypeError, ValueError):
                continue
        return current

    latest_results_for_current_image._yornis_latest_results_image_guard_v0166 = True
    ResearchDB.latest_results = latest_results_for_current_image
