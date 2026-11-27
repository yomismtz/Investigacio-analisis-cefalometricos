from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = os.path.dirname(__file__)
DESKTOP = os.path.dirname(HERE)
if DESKTOP not in sys.path:
    sys.path.insert(0, DESKTOP)


class _FakeDB:
    def __init__(self, image_path):
        self.image_path = str(image_path)
        self.audit_events = []
        self.case_data = {
            "id": 7, "study_id": 3, "study_code": "CASE-007",
            "status": "complete", "sex": "F", "age": 12.5,
            "examiner": "Examiner A", "image_path": self.image_path,
            "original_filename": "lateral_ceph.png", "image_revision": 2,
            "case_mm_per_px": 0.12,
        }
        self.study_data = {
            "id": 3, "title": "PDF regression study",
            "study_mm_per_px": 0.1,
        }

    def case(self, case_id):
        return self.case_data

    def study(self, study_id):
        return self.study_data

    def case_protocol_version(self, case_id):
        return 1

    def protocol_by_version(self, study_id, version):
        return {"version": 1, "config": {"selected_variables": []}}

    def latest_landmarks(self, case_id, version):
        return {"S": (40.0, 45.0), "N": (90.0, 30.0), "A": (80.0, 80.0)}

    def latest_results(self, case_id, version):
        return [
            {
                "analysis": "Regression",
                "measurement": f"Measurement {index:03d}",
                "value": index / 10,
                "unit": "°",
                "reference_text": "Reference text with enough words to wrap safely in the PDF table.",
                "interpretation": "Interpretation with long explanatory text that must wrap and continue on later pages without clipping.",
            }
            for index in range(95)
        ]

    def audit(self, *args, **kwargs):
        self.audit_events.append((args, kwargs))


class YornisPDFReportTests(unittest.TestCase):
    def test_case_pdf_wraps_long_table_and_contains_case_metadata(self):
        import fitz
        from PIL import Image
        from yornis_visual_report_v015 import export_case_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            image_path = temp / "lateral_ceph.png"
            Image.new("RGB", (1400, 900), "white").save(image_path)
            output = temp / "case-report.pdf"
            db = _FakeDB(image_path)

            result = export_case_pdf(db, 7, str(output))

            self.assertEqual(result, str(output))
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 10_000)
            self.assertEqual(len(db.audit_events), 1)

            with fitz.open(output) as pdf:
                self.assertGreaterEqual(len(pdf), 2)
                text = "\n".join(page.get_text() for page in pdf)
                self.assertIn("CASE-007", text)
                self.assertIn("Radiografía original", text)
                self.assertIn("Radiografía con landmarks", text)
                self.assertIn("Control técnico del trazado", text)
                self.assertIn("Interpretation", text)
                self.assertIn("Página", text)


if __name__ == "__main__":
    unittest.main()
