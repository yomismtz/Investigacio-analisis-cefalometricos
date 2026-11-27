from __future__ import annotations

import yornis_desktop_v01591 as previous
import yornis_modern_ui_v0160 as modern_ui
import yornis_viewport_v0165 as viewport_ui
import yornis_launcher_preferences_v0167 as launcher_preferences

viewport_ui.install()
modern_ui.install()

APP_VERSION = "0.16.8 Identidad YOM Dental · Cefalometría"


class Launcher(previous.Launcher):
    """YOM Dental · Cefalometría — clinical workflows and offline bird palettes."""

    def __init__(self):
        super().__init__()
        self.title("YOM Dental · Cefalometría")
        try:
            screen_w = max(980, int(self.winfo_screenwidth()) - 64)
            screen_h = max(700, int(self.winfo_screenheight()) - 110)
            width = min(1380, screen_w)
            height = min(900, screen_h)
            self.geometry(f"{width}x{height}")
            self.minsize(760, 600)
            self.resizable(True, True)
        except Exception:
            pass
        modern_ui.apply_modern_styles(self)
        import yornis_startup_audio_v0159 as startup_audio
        startup_audio.attach_sound_controls(self)
        if hasattr(self, "ver_lbl"):
            self.ver_lbl.configure(text=f"v{APP_VERSION}")

    def refresh_text(self):
        super().refresh_text()
        if hasattr(self, "ver_lbl"):
            self.ver_lbl.configure(text=f"v{APP_VERSION}")


launcher_preferences.install(Launcher)


def main():
    previous.Launcher = Launcher
    previous.APP_VERSION = APP_VERSION
    previous.main()


if __name__ == "__main__":
    main()
