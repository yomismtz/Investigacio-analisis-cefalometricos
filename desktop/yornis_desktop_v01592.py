from __future__ import annotations

from tkinter import ttk

import yornis_desktop_v01591 as previous
import yornis_bird_signatures_v01592 as bird_signatures

APP_VERSION = "0.15.9.2 Scroll + Bird Signatures · Bird Chorus"


class Launcher(previous.Launcher):
    """v0.15.9.2: scrollable launcher plus a distinct sound for each bird palette."""

    def __init__(self):
        self._scroll_offset = 0
        self._scroll_max = 0
        self._pending_scroll_fraction = 0.0
        self._scroll_refreshing = False
        super().__init__()
        self.title("Yornis · Yom Dental Análisis")
        self.bind("<Prior>", lambda _e: self._scroll_by(-1, pages=True), add="+")
        self.bind("<Next>", lambda _e: self._scroll_by(1, pages=True), add="+")
        self.bind("<Home>", lambda _e: self._set_scroll_offset(0), add="+")
        self.bind("<End>", lambda _e: self._set_scroll_offset(self._scroll_max), add="+")
        self.bind("<Configure>", self._schedule_scroll_refresh, add="+")
        self.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.after_idle(self._refresh_scroll_metrics)

    def _rebuild_quality_launcher(self):
        super()._rebuild_quality_launcher()
        self._install_scroll_navigation()
        if hasattr(self, "ver_lbl"):
            self.ver_lbl.configure(text=f"v{APP_VERSION}")

    def _install_scroll_navigation(self):
        """Move the polished root frame vertically under a real right scrollbar."""
        old = getattr(self, "_launcher_scrollbar", None)
        if old is not None:
            try:
                if old.winfo_exists():
                    old.destroy()
            except Exception:
                pass

        try:
            self.main.pack_forget()
        except Exception:
            pass

        self._launcher_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._scrollbar_command)
        self._launcher_scrollbar.place(relx=1.0, x=-2, y=0, relheight=1.0, anchor="ne")
        try:
            self._launcher_scrollbar.lift()
        except Exception:
            pass
        self.after_idle(self._restore_scroll_after_rebuild)

    def _schedule_scroll_refresh(self, _event=None):
        if getattr(self, "_scroll_refreshing", False):
            return
        try:
            self.after_idle(self._refresh_scroll_metrics)
        except Exception:
            pass

    def _restore_scroll_after_rebuild(self):
        self._refresh_scroll_metrics()
        fraction = max(0.0, min(1.0, float(getattr(self, "_pending_scroll_fraction", 0.0))))
        self._set_scroll_offset(int(round(fraction * self._scroll_max)))

    def _refresh_scroll_metrics(self):
        if not hasattr(self, "main") or getattr(self, "_scroll_refreshing", False):
            return
        self._scroll_refreshing = True
        try:
            viewport = max(1, int(self.winfo_height()))
            content = max(1, int(self.main.winfo_reqheight()))
            self._scroll_max = max(0, content - viewport)
            self._scroll_offset = max(0, min(int(getattr(self, "_scroll_offset", 0)), self._scroll_max))
            self.main.place(x=0, y=-self._scroll_offset, relwidth=1.0, width=-18)
            first = self._scroll_offset / content
            last = min(1.0, (self._scroll_offset + viewport) / content)
            self._launcher_scrollbar.set(first, last)
        except Exception:
            return
        finally:
            self._scroll_refreshing = False

    def _set_scroll_offset(self, value: int):
        self._scroll_offset = max(0, min(int(value), int(getattr(self, "_scroll_max", 0))))
        self._refresh_scroll_metrics()

    def _scroll_by(self, amount: int, *, pages: bool = False):
        step = max(80, int(self.winfo_height() * 0.82)) if pages else 62
        self._set_scroll_offset(self._scroll_offset + int(amount) * step)
        return "break"

    def _scrollbar_command(self, *args):
        if not args:
            return
        if args[0] == "moveto" and len(args) >= 2:
            try:
                fraction = float(args[1])
            except Exception:
                return
            self._set_scroll_offset(int(round(fraction * self._scroll_max)))
        elif args[0] == "scroll" and len(args) >= 3:
            try:
                amount = int(args[1])
            except Exception:
                return
            self._scroll_by(amount, pages=(args[2] == "pages"))

    def _on_mousewheel(self, event):
        delta = getattr(event, "delta", 0)
        if not delta:
            return None
        steps = -1 if delta > 0 else 1
        magnitude = max(1, abs(int(delta)) // 120)
        return self._scroll_by(steps * magnitude)

    def _theme_quality(self, name):
        import yornis_theme
        # Clicking the active bird also previews its signature.
        if name == yornis_theme.current_theme_name():
            bird_signatures.play_signature(name, self)
            return
        if self._scroll_max > 0:
            self._pending_scroll_fraction = self._scroll_offset / self._scroll_max
        else:
            self._pending_scroll_fraction = 0.0
        super()._theme_quality(name)
        bird_signatures.play_signature(name, self)
        self.after_idle(self._restore_scroll_after_rebuild)

    def refresh_text(self):
        super().refresh_text()
        if hasattr(self, "ver_lbl"):
            self.ver_lbl.configure(text=f"v{APP_VERSION}")


def main():
    # Preserve the audited v0.15.9.1 clinical/application path. Only launcher
    # navigation and decorative bird-selection audio are extended here.
    previous.Launcher = Launcher
    previous.APP_VERSION = APP_VERSION
    previous.main()


if __name__ == "__main__":
    main()
