from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import yornis_theme
import yornis_quality_ui_v0157 as base

QUALITY_VERSION = "0.15.8"


def _theme() -> dict:
    return yornis_theme.THEMES[yornis_theme.current_theme_name()]


def apply_styles(root) -> None:
    """Final presentation layer for Yornis v0.15.8.

    Visual-only changes: typography, spacing, hierarchy, surfaces, controls and
    data views. No measurements, geometry, references or database logic change.
    """
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
    root.option_add("*selectBackground", t["primary_soft"])
    root.option_add("*selectForeground", t["primary_dark"])

    style.configure("TFrame", background=t["bg"])
    style.configure("Panel.TFrame", background=t["panel"])
    style.configure("Surface.TFrame", background=t["panel"])
    style.configure("Elevated.TFrame", background=t["panel"], relief="solid", borderwidth=1, bordercolor=t["border"])
    style.configure("Soft.TFrame", background=t["panel_alt"])
    style.configure("Toolbar.TFrame", background=t["panel"], relief="flat")

    style.configure("TLabel", background=t["bg"], foreground=t["text"], font=("Segoe UI", 10))
    style.configure("Panel.TLabel", background=t["panel"], foreground=t["text"], font=("Segoe UI", 10))
    style.configure("Hero.TLabel", background=t["bg"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 25))
    style.configure("Title.TLabel", background=t["bg"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 22))
    style.configure("Eyebrow.TLabel", background=t["bg"], foreground=t["secondary_dark"], font=("Segoe UI Semibold", 9))
    style.configure("Heading.TLabel", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 12))
    style.configure("CardTitle.TLabel", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 13))
    style.configure("CardBody.TLabel", background=t["panel"], foreground=t["text"], font=("Segoe UI", 10))
    style.configure("Caption.TLabel", background=t["bg"], foreground=t["muted"], font=("Segoe UI", 9))
    style.configure("Muted.TLabel", background=t["panel"], foreground=t["muted"], font=("Segoe UI", 9))
    style.configure("Metric.TLabel", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 22))
    style.configure("Pill.TLabel", background=t["primary_soft"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 9), padding=(9, 4))
    style.configure("AccentPill.TLabel", background=t["accent_soft"], foreground=t["secondary_dark"], font=("Segoe UI Semibold", 9), padding=(9, 4))

    style.configure("TButton", font=("Segoe UI Semibold", 10), padding=(14, 9), background=t["panel_alt"], foreground=t["text"], bordercolor=t["border"], focusthickness=2, focuscolor=t["primary_soft"])
    style.map("TButton", background=[("active", t["primary_soft"]), ("pressed", t["primary_soft"])], foreground=[("active", t["primary_dark"])])
    style.configure("Primary.TButton", font=("Segoe UI Semibold", 10), padding=(17, 11), background=t["primary"], foreground="#FFFFFF", bordercolor=t["primary_dark"], focusthickness=2, focuscolor=t["accent"])
    style.map("Primary.TButton", background=[("active", t["primary_dark"]), ("pressed", t["primary_dark"]), ("disabled", t["primary_soft"])], foreground=[("disabled", t["muted"]), ("!disabled", "#FFFFFF")])
    style.configure("Secondary.TButton", font=("Segoe UI Semibold", 10), padding=(16, 10), background=t["secondary"], foreground="#FFFFFF", bordercolor=t["secondary_dark"])
    style.map("Secondary.TButton", background=[("active", t["secondary_dark"]), ("pressed", t["secondary_dark"])], foreground=[("!disabled", "#FFFFFF")])
    style.configure("Ghost.TButton", font=("Segoe UI Semibold", 10), padding=(13, 9), background=t["panel"], foreground=t["primary_dark"], bordercolor=t["border"])
    style.map("Ghost.TButton", background=[("active", t["panel_alt"]), ("pressed", t["primary_soft"])])
    style.configure("Assistant.TButton", font=("Segoe UI Semibold", 10), padding=(14, 9), background=t["accent"], foreground=t["primary_dark"], bordercolor=t["secondary_dark"])
    style.map("Assistant.TButton", background=[("active", t["secondary"]), ("pressed", t["secondary_dark"])], foreground=[("active", "#FFFFFF"), ("pressed", "#FFFFFF")])

    style.configure("TEntry", padding=(10, 8), fieldbackground=t["panel"], foreground=t["text"], bordercolor=t["border"], insertcolor=t["primary_dark"])
    style.configure("TCombobox", padding=(9, 7), fieldbackground=t["panel"], foreground=t["text"], background=t["panel_alt"], bordercolor=t["border"])
    style.configure("TCheckbutton", padding=(6, 5), background=t["bg"], foreground=t["text"], font=("Segoe UI", 10))
    style.configure("TRadiobutton", padding=(6, 5), background=t["bg"], foreground=t["text"], font=("Segoe UI", 10))
    style.configure("TNotebook", background=t["bg"], borderwidth=0, tabmargins=(0, 2, 0, 0))
    style.configure("TNotebook.Tab", font=("Segoe UI Semibold", 10), padding=(17, 10), background=t["panel_alt"], foreground=t["muted"], borderwidth=0)
    style.map("TNotebook.Tab", background=[("selected", t["primary"]), ("active", t["primary_soft"])], foreground=[("selected", "#FFFFFF"), ("active", t["primary_dark"])])
    style.configure("TLabelframe", background=t["panel"], borderwidth=1, relief="solid", bordercolor=t["border"], padding=(2, 2))
    style.configure("TLabelframe.Label", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 10))

    style.configure("Treeview", rowheight=34, font=("Segoe UI", 10), background=t["panel"], fieldbackground=t["panel"], foreground=t["text"], bordercolor=t["border"], lightcolor=t["border"], darkcolor=t["border"])
    style.configure("Treeview.Heading", font=("Segoe UI Semibold", 10), background=t["primary_soft"], foreground=t["primary_dark"], padding=(9, 9), bordercolor=t["border"])
    style.map("Treeview", background=[("selected", t["primary"])], foreground=[("selected", "#FFFFFF")])
    style.configure("Vertical.TScrollbar", background=t["panel_alt"], troughcolor=t["bg"], bordercolor=t["border"], arrowcolor=t["primary_dark"], width=13)
    style.configure("Horizontal.TScrollbar", background=t["panel_alt"], troughcolor=t["bg"], bordercolor=t["border"], arrowcolor=t["primary_dark"], width=13)
    style.configure("Horizontal.TProgressbar", background=t["secondary"], troughcolor=t["panel_alt"], bordercolor=t["border"], thickness=11)


def _polish_tk_widget(widget) -> None:
    t = _theme()
    cls = widget.winfo_class()
    try:
        if cls == "Listbox":
            widget.configure(bg=t["panel"], fg=t["text"], selectbackground=t["primary"], selectforeground="#FFFFFF", activestyle="none", relief="flat", highlightthickness=1, highlightbackground=t["border"], highlightcolor=t["primary"], font=("Segoe UI", 10), bd=0)
        elif cls in {"Text", "Entry"}:
            widget.configure(bg=t["panel"], fg=t["text"], insertbackground=t["primary_dark"], selectbackground=t["primary_soft"], selectforeground=t["primary_dark"], relief="flat", highlightthickness=1, highlightbackground=t["border"], highlightcolor=t["primary"])
        elif cls == "Canvas":
            current = str(widget.cget("bg")).lower()
            if current in {"white", "#ffffff", "systembuttonface", "#f0f0f0"}:
                widget.configure(bg=t["panel"], highlightthickness=1, highlightbackground=t["border"])
    except Exception:
        pass


def polish_widget_tree(root) -> None:
    stack = [root]
    while stack:
        parent = stack.pop()
        try:
            children = parent.winfo_children()
        except Exception:
            children = []
        for child in children:
            _polish_tk_widget(child)
            stack.append(child)


def apply_window(root, *, context: str = "app") -> None:
    t = _theme()
    try:
        root.configure(bg=t["bg"])
    except Exception:
        pass
    apply_styles(root)
    polish_widget_tree(root)
    try:
        root.after_idle(lambda: polish_widget_tree(root))
        root.after(220, lambda: polish_widget_tree(root))
        root.after(650, lambda: polish_widget_tree(root))
    except Exception:
        pass


def install_research(workspace_class) -> None:
    if getattr(workspace_class, "_yornis_quality_v0158", False):
        return
    old_style = workspace_class._style

    def style(self):
        old_style(self)
        apply_styles(self)

    workspace_class._style = style
    workspace_class._yornis_quality_v0158 = True


def install_individual(classic_class) -> None:
    if getattr(classic_class, "_yornis_quality_v0158", False):
        return
    old_init = classic_class.__init__

    def init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        apply_window(self, context="individual")

    classic_class.__init__ = init
    classic_class._yornis_quality_v0158 = True
