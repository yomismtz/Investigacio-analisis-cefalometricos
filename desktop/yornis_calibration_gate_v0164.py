from __future__ import annotations

"""Mandatory image-specific calibration guard for Yornis research cases."""

from research_db import ResearchDB


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
