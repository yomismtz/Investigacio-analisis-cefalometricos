from __future__ import annotations

import yornis_desktop_v01591 as previous

APP_VERSION = "0.15.9.2 Scroll + Bird Sounds · Bird Chorus"


class Launcher(previous.Launcher):
    """v0.15.9.2: scrollable launcher plus a distinct sound for each bird palette."""

    def __init__(self):
        super().__init__()
        self.title("Yornis · Yom Dental Análisis")
        if hasattr(self, "ver_lbl"):
            self.ver_lbl.configure(text=f"v{APP_VERSION}")

    def refresh_text(self):
        super().refresh_text()
        if hasattr(self, "ver_lbl"):
            self.ver_lbl.configure(text=f"v{APP_VERSION}")


def main():
    # Preserve the audited v0.15.9.1 clinical/application path. The scrollable
    # launcher and per-palette decorative audio are provided by the shared
    # presentation layer; clinical calculations and references are unchanged.
    previous.Launcher = Launcher
    previous.APP_VERSION = APP_VERSION
    previous.main()


if __name__ == "__main__":
    main()
