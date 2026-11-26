from __future__ import annotations

"""Mandatory image-specific calibration guard for Yornis research cases."""

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
    points = getattr(app, "calibration_points", None)
    if not isinstance(points, (list, tuple)) or len(points) < 2:
        return False
    try:
        return points[0] != points[1]
    except Exception:
        return False


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
        import classic_engine
        measurements = [
            m for m in classic_engine.MEASUREMENTS
            if (str(m.analysis), str(m.name)) in selected
        ]
    except Exception:
        return True
    # If a selected label cannot be resolved, retain the safe calibration gate.
    if len(measurements) != len(selected):
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
    """Require a fresh, accepted two-point calibration for every loaded image."""
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
            result = original_load(self, *args, **kwargs)
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
            # A new calibration attempt invalidates any previous scale immediately.
            self.calibration_points = []
            self.calibration_real_mm = None
            self.mm_per_px = None
            if hasattr(self, "calibration_mode"):
                self.calibration_mode = False
            _set_classic_canvas_state(self, "disabled")

            result = original_start(self, *args, **kwargs)

            # The legacy dialog returns with calibration_mode=True only when the
            # user accepted a positive real-world distance and the engine is
            # waiting for the two image clicks. Cancellation/invalid input stays
            # locked; merely closing the modal dialog is not calibration.
            accepted = (
                bool(getattr(self, "calibration_mode", False))
                and _positive_finite(getattr(self, "calibration_real_mm", None))
            )
            _set_classic_canvas_state(self, "normal" if accepted else "disabled")
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
    """Wrap the active image-import layer without replacing its privacy behavior."""
    current = ResearchDB.attach_image
    if getattr(current, "_yornis_image_calibration_reset_v0164", False):
        return

    def attach_image_with_calibration_reset(self, case_id, image_path, copy_image=True):
        result = current(self, case_id, image_path, copy_image)
        self.update_case_calibration(case_id, None)
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
