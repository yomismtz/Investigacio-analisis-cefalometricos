from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import unittest
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import yornis_bird_calls_v01592 as calls
import yornis_theme


class BirdCallsV01592Tests(unittest.TestCase):
    def test_every_palette_has_a_distinct_call(self):
        names = yornis_theme.theme_names()
        self.assertEqual(set(names), set(calls._BIRD_PATTERNS))
        hashes = []
        expected = int(calls.CALL_DURATION * calls.SAMPLE_RATE) * 2
        for name in names:
            frames = calls.synthesize_bird_call(name, 35)
            self.assertEqual(len(frames), expected)
            self.assertNotEqual(frames, b"\x00" * len(frames))
            hashes.append(hashlib.sha256(frames).hexdigest())
        self.assertEqual(len(set(hashes)), len(names))

    def test_bird_call_wav_writer(self):
        old = os.environ.get("APPDATA")
        with tempfile.TemporaryDirectory() as td:
            os.environ["APPDATA"] = td
            try:
                path = calls.ensure_bird_call_wav("Tucán", 35)
                self.assertTrue(path.exists())
                with wave.open(str(path), "rb") as wav:
                    self.assertEqual(wav.getnchannels(), 1)
                    self.assertEqual(wav.getsampwidth(), 2)
                    self.assertEqual(wav.getframerate(), calls.SAMPLE_RATE)
                    self.assertGreater(wav.getnframes(), 40000)
            finally:
                if old is None:
                    os.environ.pop("APPDATA", None)
                else:
                    os.environ["APPDATA"] = old


class LauncherScrollV01592Tests(unittest.TestCase):
    def test_launcher_has_fixed_vertical_scrollbar_and_can_move(self):
        from yornis_desktop_v01592 import Launcher

        launcher = Launcher()
        try:
            launcher.geometry("1000x790")
            launcher.update()
            launcher._sync_launcher_scroll()
            self.assertIsNotNone(launcher._launcher_scrollbar)
            self.assertTrue(launcher._launcher_scrollbar.winfo_exists())
            self.assertGreaterEqual(launcher._scroll_max, 0)
            if launcher._scroll_max > 0:
                launcher._scroll_by(120)
                self.assertGreater(launcher._scroll_offset, 0)
                self.assertLessEqual(launcher._scroll_offset, launcher._scroll_max)
        finally:
            launcher.destroy()


if __name__ == "__main__":
    unittest.main()
