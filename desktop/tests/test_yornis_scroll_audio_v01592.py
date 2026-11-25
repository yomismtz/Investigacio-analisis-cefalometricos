from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import yornis_bird_signature_v01592 as sounds
import yornis_theme


class YornisV01592Tests(unittest.TestCase):
    def test_all_palettes_have_their_own_uploaded_recording(self):
        names = yornis_theme.theme_names()
        self.assertEqual(set(names), set(sounds.BIRD_AUDIO_FILES))
        source_names = [sounds.BIRD_AUDIO_FILES[name] for name in names]
        self.assertEqual(len(set(source_names)), 10)
        for name in names:
            self.assertTrue(sounds.source_audio_path(name).is_file())
            for volume in sounds.VOLUME_LEVELS:
                self.assertTrue(sounds.bundled_signature_path(name, volume).is_file())
                self.assertTrue(sounds.bundled_startup_path(name, volume).is_file())

    def test_version(self):
        import yornis_desktop_v01592 as app
        self.assertTrue(app.APP_VERSION.startswith("0.16.3"))


if __name__ == "__main__":
    unittest.main()
