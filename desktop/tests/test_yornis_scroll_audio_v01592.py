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


class YornisV01592Tests(unittest.TestCase):
    def test_all_palettes_have_distinct_signature(self):
        names = yornis_theme.theme_names()
        self.assertEqual(set(names), set(sounds._SIGNATURES))
        digests = []
        for name in names:
            frames = sounds.synthesize_signature(name, 35)
            self.assertEqual(len(frames), int(sounds.SIGNATURE_DURATION * sounds.SAMPLE_RATE) * 2)
            self.assertTrue(any(frames))
            digests.append(hashlib.sha256(frames).hexdigest())
        self.assertEqual(len(set(digests)), 8)

    def test_version(self):
        import yornis_desktop_v01592 as app
        self.assertTrue(app.APP_VERSION.startswith("0.15.9.2"))


if __name__ == "__main__":
    unittest.main()
