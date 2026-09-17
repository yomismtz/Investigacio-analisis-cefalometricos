from __future__ import annotations

import yornis_desktop_v0159 as previous
import yornis_reference_help_v0156 as reference_help
import yornis_virtual_assistant_v0157 as assistant

APP_VERSION = "0.15.9.1 Layout Hotfix · Bird Chorus"


class Launcher(previous.Launcher):
    """v0.15.9.1: keep launcher actions inside the real layout, never floating over cards."""

    _FLOATING_ATTRS = (
        "_yornis_assistant_button_v0157",
        "_yornis_reference_help_button_v0156",
    )

    def __init__(self):
        super().__init__()
        self.title("Yornis · Yom Dental Análisis")
        # The polished launcher already contains integrated Referencias/Asistente
        # controls in its topbar. Older compatibility helpers also create
        # place()-positioned buttons on the root. Remove those duplicate widgets
        # after all startup helpers have had a chance to attach them.
        self.bind("<F1>", lambda _e: reference_help.open_reference_help(self), add="+")
        self.bind("<Control-k>", lambda _e: assistant.open_assistant(self), add="+")
        self.after_idle(self._remove_duplicate_floating_controls)

    def _rebuild_quality_launcher(self):
        super()._rebuild_quality_launcher()
        # Theme switching rebuilds the integrated topbar and legacy code may
        # reattach the floating assistant afterwards. The idle cleanup runs
        # after that callback returns, preventing any overlap at every palette.
        self.after_idle(self._remove_duplicate_floating_controls)

    def _remove_duplicate_floating_controls(self):
        for attr in self._FLOATING_ATTRS:
            widget = getattr(self, attr, None)
            if widget is None:
                continue
            try:
                if widget.winfo_exists():
                    widget.destroy()
            except Exception:
                pass
            try:
                setattr(self, attr, None)
            except Exception:
                pass


def main():
    # Preserve the v0.15.9 Bird Chorus execution path and clinical engine;
    # only substitute the launcher class/version presentation layer.
    previous.Launcher = Launcher
    previous.APP_VERSION = APP_VERSION
    previous.main()


if __name__ == "__main__":
    main()
