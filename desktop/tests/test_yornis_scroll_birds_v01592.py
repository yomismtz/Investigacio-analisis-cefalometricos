from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import yornis_bird_signature_v01592 as sounds
import yornis_theme


class ScrollBirdSoundsV01592Tests(unittest.TestCase):
    def test_all_palettes_have_distinct_signature(self):
        self.assertEqual(set(yornis_theme.theme_names()), set(sounds._SIGNATURES))
        digests = {
            hashlib.sha256(sounds.synthesize_signature(name, 35)).hexdigest()
            for name in yornis_theme.theme_names()
        }
        self.assertEqual(len(digests), 8)

    def test_signature_pcm_shape(self):
        frames = sounds.synthesize_signature("Tucán", 35)
        self.assertEqual(len(frames), int(sounds.SIGNATURE_DURATION * sounds.SAMPLE_RATE) * 2)
        self.assertTrue(any(frames))

    def test_launcher_has_scroll_navigation(self):
        import yornis_desktop_v01592 as app
        launcher = app.Launcher()
        launcher.withdraw()
        try:
            launcher.geometry("1000x620")
            launcher.update()
            launcher.update_idletasks()
            self.assertTrue(hasattr(launcher, "_scrollbar"))
            self.assertTrue(launcher._scrollbar.winfo_exists())
            self.assertTrue(hasattr(launcher, "_scroll_canvas"))
            self.assertTrue(launcher._scroll_canvas.winfo_exists())
            bbox = launcher._scroll_canvas.bbox("all")
            self.assertIsNotNone(bbox)
            self.assertGreater(bbox[3] - bbox[1], launcher._scroll_canvas.winfo_height())
            old = launcher._scroll_canvas.yview()[0]
            launcher._scroll_canvas.yview_scroll(8, "units")
            launcher.update_idletasks()
            self.assertGreater(launcher._scroll_canvas.yview()[0], old)
        finally:
            launcher.destroy()


if __name__ == "__main__":
    unittest.main()
