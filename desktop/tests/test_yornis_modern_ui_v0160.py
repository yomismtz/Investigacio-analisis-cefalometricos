from __future__ import annotations

import sys
import unittest
import tkinter as tk
import ttkbootstrap
from importlib.metadata import version
from pathlib import Path

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))

import yornis_modern_ui_v0160 as modern_ui
import yornis_theme


class ModernInterfaceV0160Tests(unittest.TestCase):
    def test_modern_ttk_backend_is_available(self):
        self.assertTrue(modern_ui.modern_backend_available())
        installed = tuple(int(part) for part in version("ttkbootstrap").split(".")[:3])
        self.assertGreaterEqual(installed, (2, 2, 7))

    def test_modern_ui_version_and_base_theme(self):
        self.assertEqual(modern_ui.MODERN_UI_VERSION, "0.16.0")
        self.assertEqual(modern_ui.BASE_THEME, "bootstrap-light")
        self.assertIn(modern_ui.backend_name(), {"ttkbootstrap", "ttk-clam-fallback"})

    def test_all_bird_palettes_feed_the_modern_design_tokens(self):
        original = yornis_theme.current_theme_name()
        try:
            for name, expected in yornis_theme.THEMES.items():
                with self.subTest(bird=name):
                    yornis_theme.apply_theme(name, persist=True)
                    tokens = modern_ui.theme_palette()
                    self.assertEqual(tokens["primary"], expected["primary"])
                    self.assertEqual(tokens["secondary"], expected["secondary"])
                    self.assertEqual(tokens["accent"], expected["accent"])
                    self.assertEqual(tokens["background"], expected["bg"])
                    self.assertEqual(tokens["surface"], expected["panel"])
        finally:
            yornis_theme.apply_theme(original, persist=False)

    def test_install_is_idempotent(self):
        self.assertTrue(modern_ui.install())
        self.assertTrue(modern_ui.install())

    def test_style_engine_rebinds_after_launcher_root_is_destroyed(self):
        modern_ui.install()
        first = tk.Tk()
        first.withdraw()
        self.assertTrue(modern_ui.apply_modern_styles(first))
        self.assertEqual(modern_ui.active_widget_theme(first), "bootstrap-light")
        first.destroy()
        self.assertIsNone(ttkbootstrap.Style.get_instance())

        second = tk.Tk()
        second.withdraw()
        try:
            self.assertTrue(modern_ui.apply_modern_styles(second))
            self.assertEqual(modern_ui.active_widget_theme(second), "bootstrap-light")
            self.assertTrue(modern_ui.primary_action_color(second))
        finally:
            second.destroy()


if __name__ == "__main__":
    unittest.main()
