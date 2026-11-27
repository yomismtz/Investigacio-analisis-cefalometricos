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
                         ("#805137", "#452B25", "#C68A32", "#F0E2C9"))
        self.assertEqual((hummingbird["primary"], hummingbird["secondary"], hummingbird["accent"], hummingbird["accent_soft"]),
                         ("#15966D", "#20B9B1", "#2777CF", "#F8F8F0"))
        for theme in (owl, hummingbird):
            self.assertEqual(set(theme), {
                "description_es", "bg", "panel", "panel_alt", "text", "muted",
                "primary", "primary_dark", "primary_soft", "secondary", "secondary_dark",
                "accent", "accent_soft", "tertiary", "warning", "danger", "canvas", "border",
            })
            for key, value in theme.items():
                if key != "description_es":
                    self.assertRegex(value, r"^#[0-9A-Fa-f]{6}$")

    def test_every_bird_has_eight_distinct_species_colors(self):
        self.assertEqual(set(yornis_theme.BIRD_COLOR_SWATCHES), set(yornis_theme.theme_names()))
        for bird, colors in yornis_theme.BIRD_COLOR_SWATCHES.items():
            self.assertEqual(len(colors), 8, bird)
            self.assertEqual(len(set(colors)), 8, bird)
            for color in colors:
                self.assertRegex(color, r"^#[0-9A-Fa-f]{6}$")
        for bird in yornis_theme.theme_names():
            yornis_theme.apply_theme(bird, persist=False)
            for index, color in enumerate(yornis_theme.BIRD_COLOR_SWATCHES[bird], 1):
                self.assertEqual(yornis_theme.base.PALETTE[f"bird_color_{index}"], color)

    def test_both_new_birds_have_matching_original_audio_and_assistant_profiles(self):
        self.assertEqual(set(yornis_theme.theme_names()), set(assistant.BIRD_PROFILES))
        self.assertEqual(assistant.BIRD_PROFILES["Búho"]["shape"], "owl")
        self.assertEqual(assistant.BIRD_PROFILES["Colibrí"]["shape"], "hummingbird")
        self.assertEqual(signatures.BIRD_AUDIO_FILES["Búho"], "buho real.mp3")
        self.assertEqual(signatures.BIRD_AUDIO_FILES["Colibrí"], "colibri.mp3")
        for bird in NEW_BIRDS:
            self.assertTrue(signatures.source_audio_path(bird).is_file())
            for volume in signatures.VOLUME_LEVELS:
                for path in (
                    signatures.bundled_signature_path(bird, volume),
                    startup_audio.bundled_wav_path(bird, volume),
                ):
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
