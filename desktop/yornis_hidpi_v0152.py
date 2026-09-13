from __future__ import annotations

import os
import sys

_DPI_AWARE = False


def enable_process_dpi_awareness() -> str:
    """Enable the best Windows DPI mode available before the first Tk root.

    Per-monitor-v2 prevents Windows from bitmap-scaling the whole Tk window,
    which is the main cause of visibly blurred/pixelated text on 125–250% DPI.
    Falls back safely on older Windows versions.
    """
    global _DPI_AWARE
    if _DPI_AWARE or sys.platform != "win32":
        return "already" if _DPI_AWARE else "non-windows"
    try:
        import ctypes
        user32 = ctypes.windll.user32
        try:
            # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 == -4
            if user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4)):
                _DPI_AWARE = True
                return "per-monitor-v2"
        except Exception:
            pass
        try:
            shcore = ctypes.windll.shcore
            # PROCESS_PER_MONITOR_DPI_AWARE == 2 (Windows 8.1+)
            if shcore.SetProcessDpiAwareness(2) in (0, -2147024891):
                _DPI_AWARE = True
                return "per-monitor"
        except Exception:
            pass
        try:
            if user32.SetProcessDPIAware():
                _DPI_AWARE = True
                return "system-dpi"
        except Exception:
            pass
    except Exception:
        pass
    return "unavailable"


def touch_capable() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        # SM_MAXIMUMTOUCHES = 95. A positive value means Windows reports touch.
        return int(ctypes.windll.user32.GetSystemMetrics(95)) > 0
    except Exception:
        return False


def _window_dpi(root) -> float:
    try:
        root.update_idletasks()
        if sys.platform == "win32":
            import ctypes
            hwnd = root.winfo_id()
            get_dpi = getattr(ctypes.windll.user32, "GetDpiForWindow", None)
            if get_dpi:
                dpi = float(get_dpi(hwnd))
                if 72 <= dpi <= 768:
                    return dpi
        dpi = float(root.winfo_fpixels("1i"))
        if 72 <= dpi <= 768:
            return dpi
    except Exception:
        pass
    return 96.0


def _configure_named_fonts(root, touch: bool, compact: bool) -> None:
    try:
        import tkinter.font as tkfont
        base = 10
        if touch and not compact:
            base = 11
        if compact:
            base = 9
        specs = {
            "TkDefaultFont": (base, "normal"),
            "TkTextFont": (base, "normal"),
            "TkMenuFont": (base, "normal"),
            "TkHeadingFont": (base, "bold"),
            "TkCaptionFont": (base, "bold"),
            "TkSmallCaptionFont": (max(8, base - 1), "normal"),
            "TkIconFont": (base, "normal"),
            "TkTooltipFont": (max(8, base - 1), "normal"),
        }
        for name, (size, weight) in specs.items():
            try:
                f = tkfont.nametofont(name, root=root)
                f.configure(family="Segoe UI", size=size, weight=weight)
            except Exception:
                pass
    except Exception:
        pass


def _configure_ttk(root, touch: bool, compact: bool) -> None:
    try:
        from tkinter import ttk
        style = ttk.Style(root)
        if touch and not compact:
            button_pad = (13, 9)
            check_pad = (7, 7)
            tab_pad = (12, 8)
            rowheight = 36
        elif compact:
            button_pad = (7, 4)
            check_pad = (4, 3)
            tab_pad = (7, 4)
            rowheight = 25
        else:
            button_pad = (10, 6)
            check_pad = (5, 4)
            tab_pad = (9, 6)
            rowheight = 29
        style.configure("TButton", padding=button_pad)
        style.configure("TCheckbutton", padding=check_pad)
        style.configure("TRadiobutton", padding=check_pad)
        style.configure("TCombobox", padding=(5, 4 if not touch else 7))
        style.configure("TEntry", padding=(5, 4 if not touch else 7))
        style.configure("Treeview", rowheight=rowheight)
        style.configure("TNotebook.Tab", padding=tab_pad)
    except Exception:
        pass


def configure_window(root, *, role: str = "main") -> dict:
    """Apply crisp text, DPI scaling, responsive geometry and touch sizing."""
    dpi = _window_dpi(root)
    scale = max(1.0, min(4.0, dpi / 72.0))
    try:
        root.tk.call("tk", "scaling", scale)
    except Exception:
        pass

    sw = max(640, int(root.winfo_screenwidth()))
    sh = max(480, int(root.winfo_screenheight()))
    compact = sw < 1200 or sh < 720
    touch = touch_capable()
    _configure_named_fonts(root, touch, compact)
    _configure_ttk(root, touch, compact)

    margin_x = 48 if sw >= 1100 else 16
    margin_y = 72 if sh >= 760 else 36
    max_w = max(640, sw - margin_x)
    max_h = max(480, sh - margin_y)

    try:
        if role == "launcher":
            w = min(920, max_w)
            h = min(720, max_h)
            root.minsize(min(720, w), min(540, h))
            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 2)
            root.geometry(f"{w}x{h}+{x}+{y}")
        else:
            # Large workspaces use all available pixels on smaller screens.
            root.minsize(min(900, max_w), min(560, max_h))
            if sw < 1500 or sh < 900:
                try:
                    root.state("zoomed")
                except Exception:
                    root.geometry(f"{max_w}x{max_h}+0+0")
            else:
                w = min(1540, max_w)
                h = min(940, max_h)
                x = max(0, (sw - w) // 2)
                y = max(0, (sh - h) // 2)
                root.geometry(f"{w}x{h}+{x}+{y}")
    except Exception:
        pass

    # Expose the state for diagnostics and future settings UI.
    state = {
        "dpi": dpi,
        "tk_scaling": scale,
        "touch": touch,
        "compact": compact,
        "screen_width": sw,
        "screen_height": sh,
    }
    try:
        root.yornis_display_profile = state
    except Exception:
        pass
    return state


enable_process_dpi_awareness()
