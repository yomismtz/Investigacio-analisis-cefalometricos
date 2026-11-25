from __future__ import annotations

"""Mandatory image-specific calibration guard for Yornis research cases."""

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


def install_individual(classic_class) -> None:
    """Require a fresh two-point calibration each time Individual loads an image."""
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
            if hasattr(self, "mm_per_px"):
                self.mm_per_px = None
            if hasattr(self, "calibration_mode"):
                self.calibration_mode = False
            result = original_load(self, *args, **kwargs)
            _set_classic_canvas_state(self, "disabled")
            if callable(getattr(self, "start_calibration", None)):
                try:
                    self.after_idle(self.start_calibration)
                except Exception:
                    self.start_calibration()
            return result
        classic_class.load_image_file = load_image_file

    if callable(original_start):
        def start_calibration(self, *args, **kwargs):
            # The image canvas is enabled only for the two calibration clicks.
            _set_classic_canvas_state(self, "normal")
            # The distance dialog is modal and must close before the user can
            # click the radiograph. Do not infer calibration readiness from a
            # private attribute name: the legacy engine stores this value in
            # its own state. Keep the image canvas enabled for the two clicks;
            # finish_calibration() will decide whether tracing can continue.
            result = original_start(self, *args, **kwargs)
            _set_classic_canvas_state(self, "normal")
            return result
        classic_class.start_calibration = start_calibration

    if callable(original_finish):
        def finish_calibration(self, *args, **kwargs):
            result = original_finish(self, *args, **kwargs)
            calibrated = bool(getattr(self, "mm_per_px", None)) or (
                bool(getattr(self, "calibration_real_mm", None))
                and len(getattr(self, "calibration_points", []) or []) >= 2
            )
            _set_classic_canvas_state(self, "normal" if calibrated else "disabled")
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
        # The image importer (including the pseudonymizing hardening layer) owns
        # file naming and hashing. This wrapper only clears the old image scale.
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
