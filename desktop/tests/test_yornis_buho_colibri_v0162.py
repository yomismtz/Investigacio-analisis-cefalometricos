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
import yornis_virtual_assistant_v0157 as assistant

LEGACY_BIRDS = {
    "Agaporni", "Tucán", "Pavorreal", "Ninfa", "Faisán", "Quetzal",
    "Guacamaya Roja", "Guacamaya Azul",
}
NEW_BIRDS = {"Búho", "Colibrí"}


class BuhoColibriPaletteTests(unittest.TestCase):
    def test_new_palettes_keep_all_originals_and_original_default(self):
        self.assertEqual(set(yornis_theme.theme_names()), LEGACY_BIRDS | NEW_BIRDS)
        self.assertEqual(yornis_theme.DEFAULT_THEME, "Agaporni")

    def test_new_palette_colors_are_complete(self):
        owl = yornis_theme.THEMES["Búho"]
        hummingbird = yornis_theme.THEMES["Colibrí"]
        self.assertEqual((owl["primary"], owl["secondary"], owl["accent"], owl["accent_soft"]),
                         ("#493052", "#76518A", "#C49A45", "#F3E8D2"))
        self.assertEqual((hummingbird["primary"], hummingbird["secondary"], hummingbird["accent"], hummingbird["panel_alt"]),
                         ("#087D64", "#16AFA5", "#A5D94D", "#DDF5E9"))
        for theme in (owl, hummingbird):
            self.assertEqual(set(theme), {
                "description_es", "bg", "panel", "panel_alt", "text", "muted",
                "primary", "primary_dark", "primary_soft", "secondary", "secondary_dark",
                "accent", "accent_soft", "tertiary", "warning", "danger", "canvas", "border",
            })
            for key, value in theme.items():
                if key != "description_es":
                    self.assertRegex(value, r"^#[0-9A-Fa-f]{6}$")

    def test_both_birds_have_assistant_profiles_and_audio_signatures(self):
        self.assertEqual(set(yornis_theme.theme_names()), set(assistant.BIRD_PROFILES))
        self.assertEqual(assistant.BIRD_PROFILES["Búho"]["shape"], "owl")
        self.assertEqual(assistant.BIRD_PROFILES["Colibrí"]["shape"], "hummingbird")
        self.assertEqual(set(yornis_theme.theme_names()), set(signatures._SIGNATURES))
        self.assertEqual(set(yornis_theme.theme_names()), set(startup_audio._THEME_FINALE))
        self.assertNotEqual(signatures.synthesize_signature("Búho", 35),
                            signatures.synthesize_signature("Colibrí", 35))

    def test_offline_audio_variants_exist_for_both_new_birds(self):
        for bird in NEW_BIRDS:
            for folder in ("bird_audio", "bird_startup_audio"):
                for volume in (20, 35, 50, 70, 90):
                    path = DESKTOP / "assets" / folder / f"{bird}_{volume}.wav"
                    self.assertTrue(path.is_file(), f"Missing {path}")
                    with wave.open(str(path), "rb") as wav:
                        self.assertEqual((wav.getnchannels(), wav.getsampwidth()), (1, 2))
                        self.assertGreater(wav.getnframes(), 1000)

    def test_two_original_vector_mascots_are_available(self):
        for bird in NEW_BIRDS:
            svg = DESKTOP / "assets" / "birds" / f"{bird}.svg"
            self.assertTrue(svg.is_file(), f"Missing {svg}")
            self.assertIn("<svg", svg.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
