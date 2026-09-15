from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reportlab.pdfgen import canvas
from yornis_pdf_safe_v0155 import render_pdf_first_page


class PDFSafetyTests(unittest.TestCase):
    def test_valid_pdf_renders_in_isolated_worker(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "simple.pdf"
            c = canvas.Canvas(str(path), pagesize=(300, 200))
            c.drawString(40, 100, "Yornis PDF isolation test")
            c.showPage()
            c.save()
            image = render_pdf_first_page(path, timeout=10.0, scale=1.0)
            self.assertEqual(image.mode, "RGB")
            self.assertGreater(image.width, 10)
            self.assertGreater(image.height, 10)

    def test_empty_pdf_is_rejected_without_entering_renderer(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "empty.pdf"
            path.write_bytes(b"")
            with self.assertRaises(ValueError):
                render_pdf_first_page(path)

    def test_invalid_timeout_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "x.pdf"
            path.write_bytes(b"%PDF-1.4\n%%EOF\n")
            with self.assertRaises(ValueError):
                render_pdf_first_page(path, timeout=0)


if __name__ == "__main__":
    unittest.main()
