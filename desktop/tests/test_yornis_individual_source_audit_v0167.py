from __future__ import annotations

import unittest


class IndividualClassicSourceAudit(unittest.TestCase):
    def test_dump_calibration_and_calculation_methods_for_audit(self):
        import yomceph_desktop_v130_classic as classic

        source = classic._text
        print(f"\n[AUDIT] decoded classic source length={len(source)}")
        lines = source.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("class "):
                if any(term in stripped.casefold() for term in ("calibr", "calcul", "measure", "click", "point", "image")):
                    print(f"[AUDIT] signature line {i+1}: {line}")
        terms = ("mm_per_px", "calibration_points", "calibration_real_mm", "canvasx", "canvasy", "create_image", "image_to_canvas", "canvas_to_image")
        hits = [i for i, line in enumerate(lines) if any(term in line for term in terms)]
        for i in hits:
            lo, hi = max(0, i-2), min(len(lines), i+3)
            print(f"\n[AUDIT] context lines {lo+1}-{hi}:")
            for j in range(lo, hi):
                print(f"[AUDIT] {j+1}: {lines[j]}")
