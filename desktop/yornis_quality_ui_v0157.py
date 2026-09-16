from __future__ import annotations

from tkinter import ttk

import yornis_theme
import yornis_quality_ui_v0156 as base

QUALITY_VERSION = "0.15.7"


def _theme() -> dict:
    return yornis_theme.THEMES[yornis_theme.current_theme_name()]


def apply_styles(root) -> None:
    """High-contrast, palette-forward styling for v0.15.7."""
    base.apply_styles(root)
    t = _theme()
    style = ttk.Style(root)
    try:
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass

    root.option_add("*Font", ("Segoe UI", 11))
    root.option_add("*Menu.font", ("Segoe UI", 10))
    root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10))

    style.configure("TFrame", background=t["bg"])
    style.configure("Panel.TFrame", background=t["panel"])
    style.configure("Card.TFrame", background=t["panel"], relief="flat")
    style.configure("Assistant.Card.TFrame", background=t["panel"], relief="solid", borderwidth=1)
    style.configure("TLabel", background=t["bg"], foreground=t["text"], font=("Segoe UI", 10))
    style.configure("Panel.TLabel", background=t["panel"], foreground=t["text"])
    style.configure("Title.TLabel", background=t["bg"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 22))
    style.configure("Heading.TLabel", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 12))
    style.configure("Caption.TLabel", background=t["bg"], foreground=t["muted"], font=("Segoe UI", 9))
    style.configure("Muted.TLabel", background=t["panel"], foreground=t["muted"], font=("Segoe UI", 9))
    style.configure("Metric.TLabel", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 21))

    style.configure("Assistant.Title.TLabel", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 18))
    style.configure("Assistant.Subtitle.TLabel", background=t["panel"], foreground=t["secondary_dark"], font=("Segoe UI Semibold", 10))
    style.configure("Assistant.Heading.TLabel", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 10))
    style.configure("Assistant.Body.TLabel", background=t["panel"], foreground=t["text"], font=("Segoe UI", 10))
    style.configure("Assistant.Muted.TLabel", background=t["panel"], foreground=t["muted"], font=("Segoe UI", 9))

    style.configure("TButton", font=("Segoe UI Semibold", 10), padding=(13, 8), background=t["panel_alt"], foreground=t["text"], bordercolor=t["border"], lightcolor=t["panel_alt"], darkcolor=t["border"])
    style.map("TButton", background=[("active", t["primary_soft"]), ("pressed", t["primary_soft"])], foreground=[("active", t["primary_dark"])])
    style.configure("Primary.TButton", font=("Segoe UI Semibold", 10), padding=(15, 10), background=t["primary"], foreground="#FFFFFF", bordercolor=t["primary_dark"])
    style.map("Primary.TButton", background=[("active", t["primary_dark"]), ("pressed", t["primary_dark"]), ("disabled", t["primary_soft"])], foreground=[("disabled", t["muted"]), ("!disabled", "#FFFFFF")])
    style.configure("Secondary.TButton", font=("Segoe UI Semibold", 10), padding=(14, 9), background=t["secondary"], foreground="#FFFFFF", bordercolor=t["secondary_dark"])
    style.map("Secondary.TButton", background=[("active", t["secondary_dark"]), ("pressed", t["secondary_dark"])], foreground=[("!disabled", "#FFFFFF")])
    style.configure("Ghost.TButton", font=("Segoe UI", 10), padding=(12, 8), background=t["panel"], foreground=t["primary_dark"], bordercolor=t["border"])
    style.map("Ghost.TButton", background=[("active", t["panel_alt"]), ("pressed", t["primary_soft"])])
    style.configure("Assistant.TButton", font=("Segoe UI Semibold", 10), padding=(12, 8), background=t["accent"], foreground=t["primary_dark"], bordercolor=t["secondary_dark"])
    style.map("Assistant.TButton", background=[("active", t["secondary"]), ("pressed", t["secondary_dark"])], foreground=[("active", "#FFFFFF"), ("pressed", "#FFFFFF")])

    style.configure("TEntry", padding=(9, 7), fieldbackground=t["panel"], foreground=t["text"], bordercolor=t["border"])
    style.configure("TCombobox", padding=(8, 6), fieldbackground=t["panel"], foreground=t["text"], background=t["panel_alt"], bordercolor=t["border"])
    style.configure("TNotebook", background=t["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", font=("Segoe UI Semibold", 10), padding=(15, 9), background=t["panel_alt"], foreground=t["muted"])
    style.map("TNotebook.Tab", background=[("selected", t["primary"]), ("active", t["primary_soft"])], foreground=[("selected", "#FFFFFF"), ("active", t["primary_dark"])])
    style.configure("TLabelframe", background=t["panel"], borderwidth=1, relief="solid", bordercolor=t["border"])
    style.configure("TLabelframe.Label", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 10))

    style.configure("Treeview", rowheight=32, font=("Segoe UI", 10), background=t["panel"], fieldbackground=t["panel"], foreground=t["text"], bordercolor=t["border"])
    style.configure("Treeview.Heading", font=("Segoe UI Semibold", 10), background=t["primary_soft"], foreground=t["primary_dark"], padding=(8, 8), bordercolor=t["border"])
    style.map("Treeview", background=[("selected", t["primary"])], foreground=[("selected", "#FFFFFF")])
    style.configure("Horizontal.TProgressbar", background=t["secondary"], troughcolor=t["panel_alt"], bordercolor=t["border"])


def apply_window(root, *, context: str = "app") -> None:
    t = _theme()
    try:
        root.configure(bg=t["bg"])
    except Exception:
        pass
    apply_styles(root)
    base.polish_widget_tree(root)
    try:
        root.after_idle(lambda: base.polish_widget_tree(root))
        root.after(250, lambda: base.polish_widget_tree(root))
    except Exception:
        pass


def install_research(workspace_class) -> None:
    if getattr(workspace_class, "_yornis_quality_v0157", False):
        return
    old_style = workspace_class._style
    def style(self):
        old_style(self)
        apply_styles(self)
    workspace_class._style = style
    workspace_class._yornis_quality_v0157 = True


def install_individual(classic_class) -> None:
    if getattr(classic_class, "_yornis_quality_v0157", False):
        return
    old_init = classic_class.__init__
    def init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        apply_window(self, context="individual")
    classic_class.__init__ = init
    classic_class._yornis_quality_v0157 = True
