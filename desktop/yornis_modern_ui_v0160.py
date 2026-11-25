from __future__ import annotations

"""Modern visual layer for Yornis.

This module changes presentation only. All existing tkinter widgets remain in
place, but ttk controls are rendered with ttkbootstrap and the active bird
palette supplies the application accents. The clinical engine is untouched.
"""

from tkinter import ttk
import tkinter as tk

import yornis_theme

MODERN_UI_VERSION = "0.16.0"
BASE_THEME = "bootstrap-light"
_FONT = ("Segoe UI", 10)
_FONT_MEDIUM = ("Segoe UI Semibold", 10)
_FONT_TITLE = ("Segoe UI Semibold", 22)

try:
    import ttkbootstrap as ttkb
except Exception:  # pragma: no cover - deployment test catches missing dependency
    ttkb = None

_INSTALLED = False
_ORIGINAL_APPLY_STYLES = None


def modern_backend_available() -> bool:
    return ttkb is not None


def _tokens() -> dict:
    return yornis_theme.THEMES[yornis_theme.current_theme_name()]


def _safe_configure(style, name: str, **options) -> None:
    try:
        style.configure(name, **options)
    except Exception:
        # A platform theme can omit a cosmetic option; keep the rest of the UI usable.
        pass


def _safe_map(style, name: str, **options) -> None:
    try:
        style.map(name, **options)
    except Exception:
        pass


def apply_modern_styles(root) -> bool:
    """Apply the modern flat theme and the currently selected bird palette."""
    if ttkb is None:
        return False

    t = _tokens()
    try:
        # ttkbootstrap attaches to the existing Tk interpreter; the application
        # keeps its current Tk/Toplevel architecture and does not create a new root.
        style = ttkb.Style(master=root, theme=BASE_THEME)
        style.theme_use(BASE_THEME)
        root._yornis_modern_style_v0160 = style
    except Exception:
        return False

    try:
        root.configure(background=t["bg"])
        root.option_add("*Font", _FONT)
        root.option_add("*Menu.font", _FONT)
        root.option_add("*TCombobox*Listbox.font", _FONT)
        root.option_add("*selectBackground", t["primary_soft"])
        root.option_add("*selectForeground", t["primary_dark"])
    except Exception:
        pass

    # Neutral, bright surfaces with a restrained palette accent. The same tokens
    # are applied to launcher, individual case, assistant and research windows.
    _safe_configure(style, "TFrame", background=t["bg"])
    _safe_configure(style, "Panel.TFrame", background=t["panel"])
    _safe_configure(style, "Surface.TFrame", background=t["panel"])
    _safe_configure(
        style, "Elevated.TFrame",
        background=t["panel"], relief="solid", borderwidth=1, bordercolor=t["border"],
    )
    _safe_configure(style, "Card.TFrame", background=t["panel"], relief="flat", borderwidth=0)
    _safe_configure(style, "Soft.TFrame", background=t["panel_alt"])
    _safe_configure(style, "Toolbar.TFrame", background=t["panel"], relief="flat", borderwidth=0)

    _safe_configure(style, "TLabel", background=t["bg"], foreground=t["text"], font=_FONT)
    _safe_configure(style, "Panel.TLabel", background=t["panel"], foreground=t["text"], font=_FONT)
    _safe_configure(style, "Hero.TLabel", background=t["bg"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 27))
    _safe_configure(style, "Title.TLabel", background=t["bg"], foreground=t["primary_dark"], font=_FONT_TITLE)
    _safe_configure(style, "Eyebrow.TLabel", background=t["bg"], foreground=t["secondary_dark"], font=("Segoe UI Semibold", 9))
    _safe_configure(style, "Heading.TLabel", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 13))
    _safe_configure(style, "CardTitle.TLabel", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 14))
    _safe_configure(style, "CardBody.TLabel", background=t["panel"], foreground=t["text"], font=_FONT)
    _safe_configure(style, "Caption.TLabel", background=t["bg"], foreground=t["muted"], font=("Segoe UI", 9))
    _safe_configure(style, "Muted.TLabel", background=t["panel"], foreground=t["muted"], font=("Segoe UI", 9))
    _safe_configure(style, "Metric.TLabel", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 24))
    _safe_configure(style, "Pill.TLabel", background=t["primary_soft"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 9), padding=(10, 5))
    _safe_configure(style, "AccentPill.TLabel", background=t["accent_soft"], foreground=t["secondary_dark"], font=("Segoe UI Semibold", 9), padding=(10, 5))

    _safe_configure(
        style, "TButton",
        font=_FONT_MEDIUM, padding=(16, 10), background=t["panel_alt"],
        foreground=t["text"], borderwidth=0, focusthickness=2, focuscolor=t["primary_soft"],
    )
    _safe_map(
        style, "TButton",
        background=[("pressed", t["primary_soft"]), ("active", t["panel_alt"]), ("disabled", t["bg"])],
        foreground=[("disabled", t["muted"]), ("active", t["primary_dark"])],
    )
    _safe_configure(
        style, "Primary.TButton",
        font=_FONT_MEDIUM, padding=(18, 12), background=t["primary"],
        foreground="#FFFFFF", borderwidth=0, focusthickness=2, focuscolor=t["accent"],
    )
    _safe_map(
        style, "Primary.TButton",
        background=[("pressed", t["primary_dark"]), ("active", t["primary_dark"]), ("disabled", t["primary_soft"])],
        foreground=[("disabled", t["muted"]), ("!disabled", "#FFFFFF")],
    )
    _safe_configure(
        style, "Secondary.TButton",
        font=_FONT_MEDIUM, padding=(17, 11), background=t["secondary"],
        foreground="#FFFFFF", borderwidth=0,
    )
    _safe_map(style, "Secondary.TButton", background=[("pressed", t["secondary_dark"]), ("active", t["secondary_dark"])], foreground=[("!disabled", "#FFFFFF")])
    _safe_configure(
        style, "Ghost.TButton",
        font=_FONT_MEDIUM, padding=(14, 9), background=t["panel"],
        foreground=t["primary_dark"], borderwidth=1, bordercolor=t["border"],
    )
    _safe_map(style, "Ghost.TButton", background=[("pressed", t["primary_soft"]), ("active", t["panel_alt"])])
    _safe_configure(
        style, "Assistant.TButton",
        font=_FONT_MEDIUM, padding=(14, 9), background=t["accent"],
        foreground=t["primary_dark"], borderwidth=0,
    )
    _safe_map(style, "Assistant.TButton", background=[("pressed", t["secondary_dark"]), ("active", t["secondary"])], foreground=[("pressed", "#FFFFFF"), ("active", "#FFFFFF")])

    _safe_configure(style, "IndividualCard.TFrame", background=t["panel"], relief="solid", borderwidth=1, bordercolor=t["border"])
    _safe_configure(style, "IndividualCardSelected.TFrame", background=t["panel"], relief="solid", borderwidth=2, bordercolor=t["primary"])
    _safe_configure(style, "IndividualTitle.TLabel", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 13))
    _safe_configure(style, "IndividualBody.TLabel", background=t["panel"], foreground=t["muted"], font=("Segoe UI", 9))
    _safe_configure(style, "IndividualCount.TLabel", background=t["primary_soft"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 9), padding=(10, 5))
    _safe_configure(style, "IndividualStep.TLabel", background=t["accent_soft"], foreground=t["secondary_dark"], font=("Segoe UI Semibold", 9), padding=(10, 5))
    _safe_configure(style, "IndividualPrimary.TButton", font=_FONT_MEDIUM, padding=(16, 10), background=t["primary"], foreground="#FFFFFF", borderwidth=0)
    _safe_map(style, "IndividualPrimary.TButton", background=[("pressed", t["primary_dark"]), ("active", t["primary_dark"])], foreground=[("!disabled", "#FFFFFF")])
    _safe_configure(style, "IndividualGhost.TButton", font=_FONT_MEDIUM, padding=(13, 9), background=t["panel_alt"], foreground=t["primary_dark"], borderwidth=0)
    _safe_map(style, "IndividualGhost.TButton", background=[("pressed", t["primary_soft"]), ("active", t["primary_soft"])])

    _safe_configure(style, "TEntry", padding=(11, 9), fieldbackground=t["panel"], foreground=t["text"], bordercolor=t["border"], insertcolor=t["primary_dark"])
    _safe_configure(style, "TCombobox", padding=(10, 8), fieldbackground=t["panel"], foreground=t["text"], background=t["panel_alt"], bordercolor=t["border"])
    _safe_configure(style, "TCheckbutton", padding=(7, 6), background=t["bg"], foreground=t["text"], font=_FONT)
    _safe_configure(style, "TRadiobutton", padding=(7, 6), background=t["bg"], foreground=t["text"], font=_FONT)
    _safe_configure(style, "TNotebook", background=t["bg"], borderwidth=0, tabmargins=(0, 3, 0, 0))
    _safe_configure(style, "TNotebook.Tab", font=_FONT_MEDIUM, padding=(18, 11), background=t["panel_alt"], foreground=t["muted"], borderwidth=0)
    _safe_map(style, "TNotebook.Tab", background=[("selected", t["primary"]), ("active", t["primary_soft"])], foreground=[("selected", "#FFFFFF"), ("active", t["primary_dark"])])
    _safe_configure(style, "TLabelframe", background=t["panel"], borderwidth=1, relief="solid", bordercolor=t["border"], padding=(4, 4))
    _safe_configure(style, "TLabelframe.Label", background=t["panel"], foreground=t["primary_dark"], font=_FONT_MEDIUM)

    _safe_configure(style, "Treeview", rowheight=38, font=_FONT, background=t["panel"], fieldbackground=t["panel"], foreground=t["text"], borderwidth=0)
    _safe_configure(style, "Treeview.Heading", font=_FONT_MEDIUM, background=t["panel_alt"], foreground=t["primary_dark"], padding=(11, 10), borderwidth=0)
    _safe_map(style, "Treeview", background=[("selected", t["primary"])], foreground=[("selected", "#FFFFFF")])
    _safe_configure(style, "Vertical.TScrollbar", width=10, background=t["panel_alt"], troughcolor=t["bg"], borderwidth=0, arrowcolor=t["muted"])
    _safe_configure(style, "Horizontal.TScrollbar", width=10, background=t["panel_alt"], troughcolor=t["bg"], borderwidth=0, arrowcolor=t["muted"])
    _safe_configure(style, "Horizontal.TProgressbar", background=t["secondary"], troughcolor=t["panel_alt"], borderwidth=0, thickness=10)

    _polish_native_widgets(root, t)
    return True


def _polish_native_widgets(root, t: dict) -> None:
    """Remove raised Windows-style chrome from legacy tkinter-only controls."""
    stack = [root]
    while stack:
        parent = stack.pop()
        try:
            children = parent.winfo_children()
        except Exception:
            children = []
        for widget in children:
            try:
                cls = widget.winfo_class()
                if cls == "Button":
                    widget.configure(
                        relief="flat", bd=0, highlightthickness=0,
                        bg=t["panel_alt"], fg=t["text"],
                        activebackground=t["primary_soft"], activeforeground=t["primary_dark"],
                        padx=14, pady=9, font=_FONT_MEDIUM, cursor="hand2",
                    )
                elif cls == "Menubutton":
                    widget.configure(
                        relief="flat", bd=0, highlightthickness=0,
                        bg=t["panel"], fg=t["text"],
                        activebackground=t["primary_soft"], activeforeground=t["primary_dark"],
                        padx=12, pady=8, font=_FONT_MEDIUM, cursor="hand2",
                    )
                elif cls == "Radiobutton":
                    widget.configure(
                        relief="flat", bd=0, bg=t["bg"], fg=t["text"],
                        activebackground=t["bg"], activeforeground=t["primary"],
                        selectcolor=t["primary_soft"], font=_FONT,
                    )
                elif cls == "Checkbutton":
                    widget.configure(
                        relief="flat", bd=0, bg=t["bg"], fg=t["text"],
                        activebackground=t["bg"], activeforeground=t["primary"],
                        selectcolor=t["accent_soft"], font=_FONT,
                    )
                elif cls == "Label":
                    current_font = str(widget.cget("font"))
                    if current_font in {"TkDefaultFont", "TkTextFont", ""}:
                        widget.configure(font=_FONT)
            except Exception:
                pass
            stack.append(widget)


def install() -> bool:
    """Patch the existing global quality layer once, preserving its window hooks."""
    global _INSTALLED, _ORIGINAL_APPLY_STYLES
    if _INSTALLED:
        return modern_backend_available()
    try:
        import yornis_quality_ui_v0158 as quality
        _ORIGINAL_APPLY_STYLES = quality.apply_styles

        def modern_apply_styles(root):
            _ORIGINAL_APPLY_STYLES(root)
            apply_modern_styles(root)

        quality.apply_styles = modern_apply_styles
        _INSTALLED = True
        return modern_backend_available()
    except Exception:
        return False


def active_widget_theme(root) -> str:
    """Return the actual ttk theme currently applied to a window."""
    style = getattr(root, "_yornis_modern_style_v0160", None)
    if style is None:
        return ""
    try:
        return str(style.theme_use())
    except Exception:
        return ""


def primary_action_color(root) -> str:
    """Expose the current primary-button fill for GUI regression tests."""
    style = getattr(root, "_yornis_modern_style_v0160", None)
    if style is None:
        return ""
    try:
        return str((style.configure("Primary.TButton") or {}).get("background", ""))
    except Exception:
        return ""


def theme_palette() -> dict:
    """Expose the active theme's semantic tokens for tests and diagnostics."""
    t = _tokens()
    return {
        "primary": t["primary"],
        "secondary": t["secondary"],
        "accent": t["accent"],
        "background": t["bg"],
        "surface": t["panel"],
        "text": t["text"],
    }
