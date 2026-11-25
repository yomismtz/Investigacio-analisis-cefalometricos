from __future__ import annotations

import sys
import unittest
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import yornis_bird_signature_v01592 as sounds
import yornis_theme


class ScrollBirdSoundsV01592Tests(unittest.TestCase):
    def test_all_palettes_use_their_own_uploaded_recording(self):
        names = yornis_theme.theme_names()
        self.assertEqual(set(names), set(sounds.BIRD_AUDIO_FILES))
        sources = [sounds.BIRD_AUDIO_FILES[name] for name in names]
        self.assertEqual(len(set(sources)), 10)
        for name in names:
            self.assertTrue(sounds.source_audio_path(name).is_file())
            full = sounds.bundled_signature_path(name, 35)
            startup = sounds.bundled_startup_path(name, 35)
            self.assertTrue(full.is_file())
            self.assertTrue(startup.is_file())
            with wave.open(str(full), "rb") as wav:
                self.assertEqual((wav.getnchannels(), wav.getsampwidth()), (1, 2))
                self.assertEqual(wav.getframerate(), sounds.SAMPLE_RATE)
                self.assertGreater(wav.getnframes(), sounds.SAMPLE_RATE // 5)
            with wave.open(str(startup), "rb") as wav:
                self.assertEqual((wav.getnchannels(), wav.getsampwidth()), (1, 2))
                self.assertEqual(wav.getframerate(), sounds.SAMPLE_RATE)
                self.assertGreater(wav.getnframes(), sounds.SAMPLE_RATE // 5)
                self.assertLessEqual(wav.getnframes(), int(sounds.SAMPLE_RATE * 2.8))

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
