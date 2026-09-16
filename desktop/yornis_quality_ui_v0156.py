from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import yornis_theme

QUALITY_VERSION = "0.15.6"


def _theme() -> dict:
    return yornis_theme.THEMES[yornis_theme.current_theme_name()]


def apply_styles(root) -> None:
    """Apply one coherent visual system to launcher, Individual and Research.

    The function only changes presentation. It does not touch calculations,
    measurements, database contents or clinical reference logic.
    """
    t = _theme()
    style = ttk.Style(root)
    try:
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass

    # Global typography / surfaces.
    root.option_add("*Font", ("Segoe UI", 10))
    root.option_add("*Menu.font", ("Segoe UI", 10))
    root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10))
    root.option_add("*selectBackground", t["primary_soft"])
    root.option_add("*selectForeground", t["text"])

    style.configure("TFrame", background=t["bg"])
    style.configure("Panel.TFrame", background=t["panel"])
    style.configure("Card.TFrame", background=t["panel"], relief="flat")
    style.configure("TLabel", background=t["bg"], foreground=t["text"], font=("Segoe UI", 10))
    style.configure("Panel.TLabel", background=t["panel"], foreground=t["text"])
    style.configure("Title.TLabel", background=t["bg"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 21))
    style.configure("Heading.TLabel", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 12))
    style.configure("Muted.TLabel", background=t["panel"], foreground=t["muted"], font=("Segoe UI", 9))
    style.configure("Caption.TLabel", background=t["bg"], foreground=t["muted"], font=("Segoe UI", 9))
    style.configure("Metric.TLabel", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 20))

    # Buttons. The native Vista theme keeps platform behavior while these styles
    # improve hierarchy and hit target size.
    style.configure("TButton", font=("Segoe UI Semibold", 10), padding=(12, 8))
    style.configure("Primary.TButton", font=("Segoe UI Semibold", 10), padding=(14, 9), foreground=t["primary_dark"])
    style.configure("Secondary.TButton", font=("Segoe UI Semibold", 10), padding=(13, 8), foreground=t["secondary_dark"])
    style.configure("Ghost.TButton", font=("Segoe UI", 10), padding=(12, 8))
    style.configure("Mode.TButton", font=("Segoe UI Semibold", 12), padding=(16, 16))

    # Inputs / tabs / groups.
    style.configure("TEntry", padding=(8, 6))
    style.configure("TCombobox", padding=(7, 5))
    style.configure("TCheckbutton", padding=(4, 4), background=t["bg"], foreground=t["text"])
    style.configure("TRadiobutton", padding=(4, 4), background=t["bg"], foreground=t["text"])
    style.configure("TLabelframe", background=t["panel"], borderwidth=1, relief="solid")
    style.configure("TLabelframe.Label", background=t["panel"], foreground=t["primary_dark"], font=("Segoe UI Semibold", 10))
    style.configure("TNotebook", background=t["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", font=("Segoe UI Semibold", 10), padding=(14, 8))

    # Data views.
    style.configure("Treeview", rowheight=30, font=("Segoe UI", 9), background=t["panel"], fieldbackground=t["panel"], foreground=t["text"], bordercolor=t["border"])
    style.configure("Treeview.Heading", font=("Segoe UI Semibold", 9), background=t["panel_alt"], foreground=t["primary_dark"], padding=(7, 7))


def _polish_tk_widget(widget) -> None:
    t = _theme()
    cls = widget.winfo_class()
    try:
        if cls == "Listbox":
            widget.configure(
                bg=t["panel"], fg=t["text"], selectbackground=t["primary_soft"],
                selectforeground=t["primary_dark"], activestyle="none", relief="flat",
                highlightthickness=1, highlightbackground=t["border"], highlightcolor=t["primary"],
                font=("Segoe UI", 10), bd=0,
            )
        elif cls in {"Text", "Entry"}:
            widget.configure(
                bg=t["panel"], fg=t["text"], insertbackground=t["primary_dark"],
                relief="flat", highlightthickness=1, highlightbackground=t["border"],
                highlightcolor=t["primary"],
            )
        elif cls == "Canvas":
            # Preserve dark radiograph canvases; only harmonize light utility canvases.
            current = str(widget.cget("bg")).lower()
            if current in {"white", "#ffffff", "systembuttonface", "#f0f0f0"}:
                widget.configure(bg=t["panel"], highlightbackground=t["border"])
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
    """Polish a fully-built window and add conservative accessibility defaults."""
    t = _theme()
    try:
        root.configure(bg=t["bg"])
    except Exception:
        pass
    apply_styles(root)
    polish_widget_tree(root)
    try:
        root.bind_all("<Alt-F4>", lambda _e: root.event_generate("<<CloseWindow>>"), add="+")
    except Exception:
        pass
    try:
        root.after_idle(lambda: polish_widget_tree(root))
        root.after(300, lambda: polish_widget_tree(root))
    except Exception:
        pass


def install_research(workspace_class) -> None:
    if getattr(workspace_class, "_yornis_quality_v0156", False):
        return
    old_style = workspace_class._style

    def style(self):
        old_style(self)
        apply_styles(self)

    workspace_class._style = style
    workspace_class._yornis_quality_v0156 = True


def install_individual(classic_class) -> None:
    if getattr(classic_class, "_yornis_quality_v0156", False):
        return
    old_init = classic_class.__init__

    def init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        apply_window(self, context="individual")

    classic_class.__init__ = init
    classic_class._yornis_quality_v0156 = True
