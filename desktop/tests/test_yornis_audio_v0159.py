from __future__ import annotations

import sys
import unittest
import wave
from pathlib import Path

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))

import yornis_theme
import yornis_bird_signature_v01592 as signatures
import yornis_startup_audio_v0159 as startup_audio


class OriginalBirdAudioTests(unittest.TestCase):
    def test_all_ten_palettes_map_to_the_uploaded_mp3_recordings(self):
        self.assertEqual(set(signatures.BIRD_AUDIO_FILES), set(yornis_theme.theme_names()))
        for bird, filename in signatures.BIRD_AUDIO_FILES.items():
            source = signatures.source_audio_path(bird)
            self.assertEqual(source.name, filename)
            self.assertTrue(source.is_file(), f"Missing uploaded source recording: {source}")
            self.assertGreater(source.stat().st_size, 1000)

    def test_full_palette_and_short_startup_wavs_exist_for_all_birds(self):
        for bird in yornis_theme.theme_names():
            for volume in signatures.VOLUME_LEVELS:
                full = signatures.bundled_signature_path(bird, volume)
                startup = startup_audio.bundled_wav_path(bird, volume)
                self.assertTrue(full.is_file(), f"Missing full palette sound: {full}")
                self.assertTrue(startup.is_file(), f"Missing startup excerpt: {startup}")
                for path in (full, startup):
                    with wave.open(str(path), "rb") as wav:
                        self.assertEqual((wav.getnchannels(), wav.getsampwidth()), (1, 2))
                        self.assertEqual(wav.getframerate(), signatures.SAMPLE_RATE)
                        self.assertGreater(wav.getnframes(), signatures.SAMPLE_RATE // 5)
                        self.assertLessEqual(wav.getnframes(), signatures.SAMPLE_RATE * 15)

    def test_startup_uses_the_selected_palette_recording(self):
        for bird in yornis_theme.theme_names():
            self.assertEqual(
                startup_audio.bundled_wav_path(bird, 35).name,
                signatures.bundled_startup_path(bird, 35).name,
            )


if __name__ == "__main__":
    unittest.main()
