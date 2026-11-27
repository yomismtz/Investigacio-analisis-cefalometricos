from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import yornis_viewport_v0165 as viewport


class RadiographViewportTests(unittest.TestCase):
    def test_install_is_idempotent(self):
        viewport.install()
        viewport.install()
        self.assertTrue(viewport._INSTALLED)

    def test_only_large_image_canvases_get_viewport_bars(self):
        source = Path(viewport.__file__).read_text(encoding="utf-8")
        self.assertIn("(bounds[2] - bounds[0]) >= 600", source)
        self.assertIn("(bounds[3] - bounds[1]) >= 400", source)
        self.assertIn('orient="horizontal"', source)
        self.assertIn('orient="vertical"', source)

    def test_magnifier_has_larger_minimum_and_geometry(self):
        source = Path(viewport.__file__).read_text(encoding="utf-8")
        self.assertIn("self.minsize(520, 440)", source)
        self.assertIn('self.geometry("640x520")', source)


if __name__ == "__main__":
    unittest.main()
