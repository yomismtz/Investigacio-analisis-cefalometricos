from __future__ import annotations

import sys
import unittest
from pathlib import Path

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))

import yornis_theme


class BirdPaletteContrastTests(unittest.TestCase):
    def test_all_thirteen_palettes_keep_readable_semantic_text(self):
        for name, theme in yornis_theme.THEMES.items():
            with self.subTest(bird=name):
                for foreground in ("text", "muted", "primary_dark", "secondary_dark"):
                    for background in ("bg", "panel"):
                        ratio = yornis_theme.contrast_ratio(theme[foreground], theme[background])
                        self.assertGreaterEqual(
                            ratio, 4.5,
                            f"{name}: {foreground} on {background} has contrast {ratio:.2f}:1",
                        )

    def test_all_palette_action_buttons_choose_accessible_text(self):
        for name, theme in yornis_theme.THEMES.items():
            with self.subTest(bird=name):
                for surface in ("primary", "secondary"):
                    foreground = yornis_theme.readable_foreground(theme[surface])
                    ratio = yornis_theme.contrast_ratio(foreground, theme[surface])
                    self.assertGreaterEqual(
                        ratio, 4.5,
                        f"{name}: button text on {surface} has contrast {ratio:.2f}:1",
                    )
                hover_foreground = yornis_theme.readable_foreground(theme["primary_dark"])
                self.assertGreaterEqual(
                    yornis_theme.contrast_ratio(hover_foreground, theme["primary_dark"]),
                    4.5,
                )

    def test_plumage_swatches_never_overwrite_dark_text_tokens(self):
        for name, theme in yornis_theme.THEMES.items():
            with self.subTest(bird=name):
                self.assertNotEqual(theme["primary_dark"], yornis_theme.BIRD_COLOR_SWATCHES[name][7])
                self.assertNotEqual(theme["secondary_dark"], yornis_theme.BIRD_COLOR_SWATCHES[name][7])


if __name__ == "__main__":
    unittest.main()
