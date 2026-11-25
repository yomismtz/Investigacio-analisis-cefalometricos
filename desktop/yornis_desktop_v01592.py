from __future__ import annotations

import yornis_desktop_v01591 as previous
import yornis_modern_ui_v0160 as modern_ui

modern_ui.install()

APP_VERSION = "0.16.2 Paletas Búho + Colibrí + Audios Reales"


class Launcher(previous.Launcher):
    """v0.16.2: ten bird palettes, real offline recordings and unchanged clinical workflows."""

    def __init__(self):
        super().__init__()
        self.title("Yornis · Análisis clínico y cefalométrico")
        # Responsive starting size: wide enough for a modern dashboard, while
        # staying inside typical laptop screens and remaining resizable.
        try:
            screen_w = max(980, int(self.winfo_screenwidth()) - 64)
            screen_h = max(700, int(self.winfo_screenheight()) - 110)
            width = min(1380, screen_w)
            height = min(900, screen_h)
            self.geometry(f"{width}x{height}")
            self.minsize(960, 680)
            self.resizable(True, True)
        except Exception:
            pass
        modern_ui.apply_modern_styles(self)
        if hasattr(self, "ver_lbl"):
            self.ver_lbl.configure(text=f"v{APP_VERSION}")

    def refresh_text(self):
        super().refresh_text()
        if hasattr(self, "ver_lbl"):
            self.ver_lbl.configure(text=f"v{APP_VERSION}")


def main():
    # Preserve the audited clinical/application path. The modern visual layer
    # skins existing windows and controls; formulas and research data stay unchanged.
    previous.Launcher = Launcher
    previous.APP_VERSION = APP_VERSION
    previous.main()


if __name__ == "__main__":
    main()
