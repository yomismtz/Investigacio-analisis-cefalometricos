from __future__ import annotations

import os
import sys
import tempfile
import unittest
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import yornis_startup_audio_v0159 as audio


class StartupAudioV0159Tests(unittest.TestCase):
    def test_chorus_is_pcm_and_nonempty(self):
        frames = audio.synthesize_chorus("Quetzal", 35)
        expected = int(audio.DURATION * audio.SAMPLE_RATE) * 2
        self.assertEqual(len(frames), expected)
        self.assertNotEqual(frames[:5000], b"\x00" * min(5000, len(frames)))

    def test_all_bird_palettes_have_signature(self):
        import yornis_theme
        self.assertEqual(set(yornis_theme.theme_names()), set(audio._THEME_FINALE))

    def test_wav_writer(self):
        old = os.environ.get("APPDATA")
        with tempfile.TemporaryDirectory() as td:
            os.environ["APPDATA"] = td
            try:
                path = audio.ensure_wav("Agaporni", 20)
                self.assertTrue(path.exists())
                with wave.open(str(path), "rb") as wav:
                    self.assertEqual(wav.getnchannels(), 1)
                    self.assertEqual(wav.getsampwidth(), 2)
                    self.assertEqual(wav.getframerate(), audio.SAMPLE_RATE)
                    self.assertGreater(wav.getnframes(), 100000)
            finally:
                if old is None:
                    os.environ.pop("APPDATA", None)
                else:
                    os.environ["APPDATA"] = old


if __name__ == "__main__":
    unittest.main()
