from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import yornis_bird_signatures_v01592 as sounds
import yornis_theme


class ScrollBirdSoundsV01592Tests(unittest.TestCase):
    def test_all_palettes_have_distinct_signature(self):
        self.assertEqual(set(yornis_theme.theme_names()), set(sounds.BIRD_SIGNATURES))
        motifs = {tuple(v) for v in sounds.BIRD_SIGNATURES.values()}
        self.assertEqual(len(motifs), 8)

    def test_signature_pcm_shape(self):
        frames = sounds.synthesize_signature("Tucán", 35)
        self.assertEqual(len(frames), int(sounds.SIGNATURE_DURATION * sounds.SAMPLE_RATE) * 2)
        self.assertTrue(any(frames))

    def test_launcher_has_scroll_navigation(self):
        import yornis_desktop_v01592 as app
        launcher = app.Launcher()
        launcher.withdraw()
        launcher.update()
        try:
            self.assertTrue(hasattr(launcher, "_launcher_scrollbar"))
            self.assertTrue(launcher._launcher_scrollbar.winfo_exists())
            launcher.geometry("1000x620")
            launcher.update()
            launcher._refresh_scroll_metrics()
            self.assertGreater(launcher._scroll_max, 0)
            old = launcher._scroll_offset
            launcher._scroll_by(1)
            self.assertGreater(launcher._scroll_offset, old)
        finally:
            launcher.destroy()


if __name__ == "__main__":
    unittest.main()
