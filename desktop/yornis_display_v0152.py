from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path

_DPI_ENABLED = False


def enable_windows_dpi_awareness() -> None:
    """Enable the sharpest Windows DPI mode available before any Tk window exists."""
    global _DPI_ENABLED
    if _DPI_ENABLED or sys.platform != "win32":
        return
    try:
        # Windows 10+: Per-Monitor v2.  -4 is DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2.
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        _DPI_ENABLED = True
        return
    except Exception:
        pass
    try:
        # Windows 8.1 fallback: PROCESS_PER_MONITOR_DPI_AWARE = 2.
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        _DPI_ENABLED = True
        return
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        _DPI_ENABLED = True
    except Exception:
        pass


def _window_dpi(root) -> int:
    if sys.platform != "win32":
        return 96
    try:
        hwnd = int(root.winfo_id())
        dpi = int(ctypes.windll.user32.GetDpiForWindow(hwnd))
        return dpi if dpi > 0 else 96
    except Exception:
        try:
            return int(ctypes.windll.user32.GetDpiForSystem())
        except Exception:
            return 96


def touch_capable() -> bool:
    if sys.platform != "win32":
        return False
    try:
        # SM_DIGITIZER=94: NID_READY(0x80) + NID_MULTI_INPUT(0x40) / NID_INTEGRATED_TOUCH(0x01)
        digitizer = int(ctypes.windll.user32.GetSystemMetrics(94))
        touches = int(ctypes.windll.user32.GetSystemMetrics(95))  # SM_MAXIMUMTOUCHES
        return touches > 0 and bool(digitizer & 0xC1)
    except Exception:
        return False


def _resource(name: str) -> Path | None:
    candidates = []
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle:
        candidates.append(Path(bundle) / name)
    candidates += [Path(__file__).resolve().parent / "assets" / name, Path(__file__).resolve().parent / name]
    for p in candidates:
        if p.exists():
            return p
    return None


def set_yornis_window_icon(root) -> None:
    """Use the Yornis bird/skull logo for title bar and taskbar windows."""
    try:
        ico = _resource("yornis.ico")
        if ico:
            root.iconbitmap(default=str(ico))
    except Exception:
        pass
    try:
        import tkinter as tk
        png = _resource("yornis_logo.png")
        if png:
            photo = tk.PhotoImage(file=str(png))
            root.iconphoto(True, photo)
            root._yornis_icon_photo = photo
    except Exception:
        pass


def _work_area(root) -> tuple[int, int]:
    # Tk reports the monitor work-space sufficiently for our layout decisions.
    try:
        return max(640, int(root.winfo_screenwidth())), max(480, int(root.winfo_screenheight()))
    except Exception:
        return 1366, 768


def fit_window(root, *, launcher: bool = False) -> None:
    """Fit to small laptops, 4K displays, tablets and touch Windows devices."""
    sw, sh = _work_area(root)
    if launcher:
        width = min(980, max(700, int(sw * 0.78)))
        height = min(780, max(560, int(sh * 0.82)))
        x = max(0, (sw - width) // 2)
        y = max(0, (sh - height) // 3)
        root.minsize(min(720, max(620, int(sw * 0.60))), min(560, max(500, int(sh * 0.62))))
        root.geometry(f"{width}x{height}+{x}+{y}")
    else:
        root.minsize(min(820, max(680, int(sw * 0.55))), min(600, max(500, int(sh * 0.58))))
        try:
            if sw <= 1600 or sh <= 900 or touch_capable():
                root.state("zoomed")
            else:
                width, height = int(sw * 0.92), int(sh * 0.90)
                root.geometry(f"{width}x{height}+{(sw-width)//2}+{max(0,(sh-height)//3)}")
        except Exception:
            pass


def _apply_named_fonts(root, dpi: int) -> None:
    import tkinter.font as tkfont

    # Point sizes remain physical-size aware when Tk scaling follows DPI.
    base = 10
    family = "Segoe UI"
    definitions = {
        "TkDefaultFont": (base, "normal"),
        "TkTextFont": (base, "normal"),
        "TkMenuFont": (base, "normal"),
        "TkHeadingFont": (base, "bold"),
        "TkCaptionFont": (base, "bold"),
        "TkSmallCaptionFont": (9, "normal"),
        "TkIconFont": (base, "normal"),
        "TkTooltipFont": (9, "normal"),
        "TkFixedFont": (10, "normal"),
    }
    for name, (size, weight) in definitions.items():
        try:
            f = tkfont.nametofont(name, root=root)
            f.configure(family=family, size=size, weight=weight)
        except Exception:
            pass


def _apply_ttk_metrics(root, dpi: int) -> None:
    from tkinter import ttk

    style = ttk.Style(root)
    scale = max(1.0, dpi / 96.0)
    touch = touch_capable()
    target = 44 if touch else 34
    rowheight = max(target, int(round(target * min(scale, 1.6))))
    pad_x = max(10, int(round((12 if touch else 9) * min(scale, 1.5))))
    pad_y = max(5, int(round((8 if touch else 5) * min(scale, 1.5))))
    try:
        style.configure("TButton", padding=(pad_x, pad_y))
        style.configure("Toolbutton", padding=(pad_x, pad_y))
        style.configure("TCombobox", padding=(max(5, pad_x // 2), max(3, pad_y // 2)))
        style.configure("TEntry", padding=(max(5, pad_x // 2), max(3, pad_y // 2)))
        style.configure("Treeview", rowheight=rowheight)
        style.configure("Treeview.Heading", padding=(pad_x, pad_y))
        style.configure("TNotebook.Tab", padding=(pad_x + 3, pad_y + 2))
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
    except Exception:
        pass


def apply_display_quality(root, *, launcher: bool = False) -> None:
    """Apply crisp fonts, DPI scaling, touch metrics, responsive sizing and logo icon."""
    try:
        root.update_idletasks()
    except Exception:
        pass
    dpi = _window_dpi(root)
    try:
        # Tk uses pixels-per-point; 1 point = 1/72 inch.
        root.tk.call("tk", "scaling", dpi / 72.0)
    except Exception:
        pass
    _apply_named_fonts(root, dpi)
    _apply_ttk_metrics(root, dpi)
    set_yornis_window_icon(root)
    fit_window(root, launcher=launcher)
    root._yornis_last_dpi = dpi

    # Per-monitor DPI can change when a laptop/tablet window is moved to another display.
    def refresh(_event=None):
        try:
            new_dpi = _window_dpi(root)
            if new_dpi != getattr(root, "_yornis_last_dpi", None):
                root._yornis_last_dpi = new_dpi
                root.tk.call("tk", "scaling", new_dpi / 72.0)
                _apply_named_fonts(root, new_dpi)
                _apply_ttk_metrics(root, new_dpi)
        except Exception:
            pass

    try:
        root.bind("<Configure>", refresh, add="+")
    except Exception:
        pass


enable_windows_dpi_awareness()
