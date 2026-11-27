from __future__ import annotations

import unittest


class IndividualClassicSourceAudit(unittest.TestCase):
    def test_dump_calibration_and_calculation_methods_for_audit(self):
        import yomceph_desktop_v130_classic as classic

        source = classic._text
        for method in ("start_calibration", "finish_calibration", "calculate", "load_image_file"):
            marker = "def " + method + "("
            start = source.find(marker)
            if start < 0:
                print(f"\n[AUDIT] {marker}: NOT FOUND")
                continue
            end = source.find("\n    def ", start + len(marker))
            if end < 0:
                end = min(len(source), start + 9000)
            snippet = source[start:min(end, start + 9000)]
            print(f"\n[AUDIT] {method} source ({len(snippet)} chars):\n{snippet}")
        lines = source.splitlines()
        hits = [i for i, line in enumerate(lines) if "mm_per_px" in line or "calibration_points" in line or "calibration_real_mm" in line]
        for i in hits[:60]:
            print(f"[AUDIT] line {i+1}: {lines[i]}")
