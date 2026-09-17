from __future__ import annotations

from tkinter import ttk

import yornis_desktop_v01591 as previous
import yornis_bird_calls_v01592 as bird_calls
import yornis_theme

APP_VERSION = "0.15.9.2 Scroll + Bird Calls · Bird Chorus"


class Launcher(previous.Launcher):
    """v0.15.9.2: vertical launcher scrolling plus per-palette bird calls."""

    def __init__(self):
        # Plain Python attributes are safe before Tk initialises. They are used
        # by the overridden rebuild method, which can be called during super().
        self._scroll_offset = 0.0
        self._scroll_max = 0.0
        self._scroll_content_height = 1.0
        self._launcher_scrollbar = None
        self._scroll_root_bind = None
        super().__init__()
        self.title("Yornis · Yom Dental Análisis")
        self.after_idle(self._sync_launcher_scroll)

    def _rebuild_quality_launcher(self):
        # Keep the user's vertical position while a palette rebuilds the UI.
        previous_offset = float(getattr(self, "_scroll_offset", 0.0) or 0.0)
        super()._rebuild_quality_launcher()
        self._scroll_offset = previous_offset
        self._install_launcher_scroll()

    def _install_launcher_scroll(self):
        main = getattr(self, "main", None)
        if main is None:
            return

        # The polished launcher originally packed one tall frame directly into
        # the root. On smaller displays its bottom was unreachable. Keep that
        # exact UI, but turn the root into a viewport and move the existing
        # frame vertically while a fixed scrollbar stays on the right.
        try:
            main.pack_forget()
        except Exception:
            pass

        old = getattr(self, "_launcher_scrollbar", None)
        if old is not None:
            try:
                if old.winfo_exists():
                    old.destroy()
            except Exception:
                pass

        bar = ttk.Scrollbar(self, orient="vertical", command=self._scrollbar_command)
        bar.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")
        self._launcher_scrollbar = bar

        # Reserve a narrow strip for the scrollbar so it never overlays cards.
        main.place(x=0, y=-int(self._scroll_offset), relwidth=1.0, width=-20)

        if self._scroll_root_bind:
            try:
                self.unbind("<Configure>", self._scroll_root_bind)
            except Exception:
                pass
        self._scroll_root_bind = self.bind("<Configure>", self._schedule_scroll_sync, add="+")
        self.bind("<MouseWheel>", self._on_launcher_mousewheel, add="+")
        self.bind("<Prior>", lambda _e: self._scroll_by(-0.82 * max(1, self.winfo_height())), add="+")
        self.bind("<Next>", lambda _e: self._scroll_by(0.82 * max(1, self.winfo_height())), add="+")
        main.bind("<Configure>", self._schedule_scroll_sync, add="+")
        self.after_idle(self._sync_launcher_scroll)

    def _schedule_scroll_sync(self, _event=None):
        try:
            self.after_idle(self._sync_launcher_scroll)
        except Exception:
            pass

    def _sync_launcher_scroll(self):
        main = getattr(self, "main", None)
        bar = getattr(self, "_launcher_scrollbar", None)
        if main is None or bar is None:
            return
        try:
            if not main.winfo_exists() or not bar.winfo_exists():
                return
            main.update_idletasks()
            content_h = max(1, int(main.winfo_reqheight()))
            viewport_h = max(1, int(self.winfo_height()))
            self._scroll_content_height = float(content_h)
            self._scroll_max = float(max(0, content_h - viewport_h))
            self._scroll_offset = max(0.0, min(float(self._scroll_offset), self._scroll_max))
            main.place_configure(y=-int(self._scroll_offset), relwidth=1.0, width=-20)
            if content_h <= viewport_h:
                bar.set(0.0, 1.0)
            else:
                first = self._scroll_offset / content_h
                last = min(1.0, (self._scroll_offset + viewport_h) / content_h)
                bar.set(first, last)
        except Exception:
            return

    def _set_scroll_offset(self, value: float):
        self._scroll_offset = max(0.0, min(float(value), float(getattr(self, "_scroll_max", 0.0))))
        self._sync_launcher_scroll()

    def _scroll_by(self, delta: float):
        self._set_scroll_offset(float(getattr(self, "_scroll_offset", 0.0)) + float(delta))
        return "break"

    def _scrollbar_command(self, *args):
        self._sync_launcher_scroll()
        if not args:
            return
        if args[0] == "moveto" and len(args) >= 2:
            fraction = max(0.0, min(1.0, float(args[1])))
            self._set_scroll_offset(fraction * self._scroll_content_height)
        elif args[0] == "scroll" and len(args) >= 3:
            amount = int(args[1])
            step = max(48.0, self.winfo_height() * .82) if args[2] == "pages" else 58.0
            self._scroll_by(amount * step)

    def _on_launcher_mousewheel(self, event):
        if float(getattr(self, "_scroll_max", 0.0)) <= 0:
            return None
        delta = int(getattr(event, "delta", 0) or 0)
        if delta == 0:
            return None
        notches = delta / 120.0
        if abs(notches) < 1.0:
            notches = 1.0 if delta > 0 else -1.0
        return self._scroll_by(-notches * 64.0)

    def _theme_quality(self, name):
        # Base logic applies the palette and rebuilds the full launcher. After
        # the rebuild, play only the selected bird's short procedural signature.
        super()._theme_quality(name)
        bird_calls.play_bird_call(self, theme_name=name)


def main():
    # Preserve v0.15.9.1 overlap fix, v0.15.9 startup chorus and all clinical
    # layers; substitute only the launcher/version presentation layer.
    previous.Launcher = Launcher
    previous.APP_VERSION = APP_VERSION
    previous.main()


if __name__ == "__main__":
    main()
