from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import yornis_reference_help_v0156 as reference_help
import yornis_virtual_assistant_v0157 as assistant
from yornis_desktop_v01591 import APP_VERSION, Launcher


class LauncherLayoutHotfixTests(unittest.TestCase):
    def test_version(self):
        self.assertTrue(APP_VERSION.startswith("0.15.9.1"))

    def test_floating_duplicates_are_removed(self):
        launcher = Launcher()
        try:
            launcher.withdraw()
            # Simulate the compatibility attachments made by the v0.15.8 path.
            reference_help.attach_help_button(launcher, compact=True)
            assistant.attach_assistant_button(launcher, compact=True)
            launcher.update()
            for attr in launcher._FLOATING_ATTRS:
                widget = getattr(launcher, attr, None)
                if widget is not None:
                    self.assertFalse(widget.winfo_exists(), attr)

            # Integrated topbar actions remain available.
            texts = []
            stack = [launcher]
            while stack:
                parent = stack.pop()
                for child in parent.winfo_children():
                    stack.append(child)
                    try:
                        text = child.cget("text")
                    except Exception:
                        text = ""
                    if text:
                        texts.append(str(text))
            self.assertTrue(any("Referencias" in t for t in texts))
            self.assertTrue(any("Asistente" in t and "Ctrl+K" in t for t in texts))
        finally:
            launcher.destroy()


if __name__ == "__main__":
    unittest.main()
