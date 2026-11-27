from __future__ import annotations

import sys
import unittest
from pathlib import Path

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))

import yornis_launcher_preferences_v0167 as preferences


class LauncherPreferencesV0167Tests(unittest.TestCase):
    def test_font_options_are_available(self):
        self.assertIn("Segoe UI", preferences.FONT_FAMILIES)
        self.assertIn("Arial", preferences.FONT_FAMILIES)
        self.assertIn(10, preferences.FONT_SIZES)
        self.assertIn(24, preferences.FONT_SIZES)

    def test_initial_screen_defers_mode_selection_until_start(self):
        source = Path(preferences.__file__).read_text(encoding="utf-8")
        self.assertIn('text="INICIAL"', source)
        self.assertIn('text="Iniciar  →"', source)
        self.assertIn("mode_box.pack_forget()", source)
        self.assertIn("mode_box.pack(fill=\"x\", before=palette_host)", source)

    def test_bullet_copy_is_centered_and_wrap_width_scales_with_font(self):
        source = Path(preferences.__file__).read_text(encoding="utf-8")
        self.assertIn('anchor="center", justify="center"', source)
        self.assertIn("base * scale", source)

    def test_horizontal_and_vertical_launcher_scrolling(self):
        source = Path(preferences.__file__).read_text(encoding="utf-8")
        self.assertIn('orient="horizontal"', source)
        self.assertIn('orient="vertical"', source)
        self.assertIn("<Shift-MouseWheel>", source)

    def test_startup_uses_ten_bird_chorus_and_start_uses_selected_palette(self):
        source = Path(preferences.__file__).read_text(encoding="utf-8")
        self.assertIn("chorus_{volume}.wav", source)
        self.assertIn("bird_audio.play_bird_signature(yornis_theme.current_theme_name(), launcher)", source)


if __name__ == "__main__":
    unittest.main()
