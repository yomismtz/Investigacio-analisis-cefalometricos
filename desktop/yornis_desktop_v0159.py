from __future__ import annotations

import yornis_desktop_v0158 as previous
import yornis_startup_audio_v0159 as startup_audio

APP_VERSION = "0.15.9 Bird Chorus · Final Polish"


class Launcher(previous.Launcher):
    """v0.15.9 launcher with a local procedural bird chorus on startup."""

    def __init__(self):
        super().__init__()
        self.title("Yornis · Yom Dental Análisis")
        startup_audio.play_startup_chorus(self)

    def _rebuild_quality_launcher(self):
        super()._rebuild_quality_launcher()
        startup_audio.attach_sound_controls(self)

    def refresh_text(self):
        super().refresh_text()
        if hasattr(self, "ver_lbl"):
            self.ver_lbl.configure(text=f"v{APP_VERSION}")


def main():
    # Reuse the fully audited v0.15.8 execution path while substituting only
    # the launcher/version presentation layer. Clinical geometry is untouched.
    previous.Launcher = Launcher
    previous.APP_VERSION = APP_VERSION
    previous.main()


if __name__ == "__main__":
    main()
