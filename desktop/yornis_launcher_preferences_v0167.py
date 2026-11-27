from __future__ import annotations

"""Initial screen, global typography and responsive launcher preferences for Yornis."""

import tkinter as tk
from tkinter import ttk
from types import MethodType

import yornis_theme
import yornis_startup_audio_v0159 as startup_audio

FONT_FAMILIES = (
    "Segoe UI", "Arial", "Calibri", "Aptos", "Tahoma", "Verdana",
    "Georgia", "Times New Roman",
)
FONT_SIZES = (9, 10, 11, 12, 13, 14, 16, 18, 20, 22, 24, 28, 32)
_INSTALLED = False


def _prefs() -> dict:
    data = yornis_theme.load_settings()
    return {
        "font_family": str(data.get("font_family", "Segoe UI")),
        "font_size": max(9, min(32, int(data.get("font_size", 10)))),
    }


def _save_pref(key: str, value) -> None:
    data = yornis_theme.load_settings()
    data[key] = value
    yornis_theme.save_settings(data)


def _play_welcome_chorus(root=None, *, force: bool = False) -> None:
    """Play the pre-mixed chorus of the ten original birds, offline."""
    enabled, volume = startup_audio.settings()
    if not enabled or volume <= 0:
        return

    def launch():
        try:
            import winsound
            from pathlib import Path
            import sys
            assets = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "assets"
            path = assets / "bird_startup_audio" / f"chorus_{volume}.wav"
            if path.is_file():
                winsound.PlaySound(
                    str(path),
                    winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
                )
                return
            # Older builds without the mixed file still play each original bird
            # excerpt in a short, non-blocking sequence.
            import yornis_bird_signature_v01592 as bird_audio
            for bird in yornis_theme.theme_names():
                excerpt = bird_audio.bundled_startup_path(bird, volume)
                if excerpt.is_file():
                    winsound.PlaySound(
                        str(excerpt),
                        winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
                    )
        except Exception:
            return

    try:
        if root is not None:
            root.after(280, launch)
        else:
            launch()
    except Exception:
        launch()


def _apply_typography(root, family: str, size: int) -> None:
    font = (family, size)
    scale = size / 10.0
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
                if cls in {"Label", "TLabel", "Button", "TButton", "Checkbutton",
                           "TCheckbutton", "Radiobutton", "TRadiobutton",
                           "Entry", "TEntry", "Listbox", "Text", "Combobox",
                           "TCombobox", "Menubutton"}:
                    widget.configure(font=font)
                # Center card/bullet copy and let Tk's geometry managers resize
                # the containing card to the new font metrics.
                if cls in {"Label", "TLabel"}:
                    try:
                        widget.configure(anchor="center", justify="center")
                    except Exception:
                        pass
                    try:
                        base = getattr(widget, "_yornis_base_wraplength", None)
                        current = int(widget.cget("wraplength") or 0)
                        if base is None:
                            base = current
                            widget._yornis_base_wraplength = base
                        if base > 0:
                            widget.configure(wraplength=max(220, int(base * scale)))
                    except Exception:
                        pass
                stack.append(widget)
            except Exception:
                pass
    try:
        root.option_add("*Font", font)
        root.option_add("*Menu.font", font)
        root.update_idletasks()
    except Exception:
        pass


def _install_horizontal_scroll(launcher) -> None:
    canvas = getattr(launcher, "_scroll_canvas", None)
    shell = getattr(launcher, "_scroll_shell", None)
    main = getattr(launcher, "main", None)
    if canvas is None or shell is None or main is None:
        return
    try:
        if not getattr(launcher, "_yornis_hbar_v0167", None):
            bar = ttk.Scrollbar(shell, orient="horizontal", command=canvas.xview)
            bar.pack(side="bottom", fill="x")
            launcher._yornis_hbar_v0167 = bar
        canvas.configure(xscrollcommand=launcher._yornis_hbar_v0167.set)
        canvas.configure(confine=False)
        original_resize = getattr(launcher, "_yornis_original_resize_v0167", None)
        if original_resize is None:
            original_resize = launcher._resize_launcher_scroll_window
            launcher._yornis_original_resize_v0167 = original_resize

            def resize(_self, event):
                try:
                    main.update_idletasks()
                    requested = max(event.width, main.winfo_reqwidth())
                    canvas.itemconfigure(launcher._scroll_window, width=requested)
                    bbox = canvas.bbox("all")
                    if bbox:
                        canvas.configure(scrollregion=bbox)
                except Exception:
                    original_resize(event)

            launcher._resize_launcher_scroll_window = MethodType(resize, launcher)
        canvas.bind(
            "<Shift-MouseWheel>",
            lambda event: (canvas.xview_scroll(-1 if event.delta > 0 else 1, "units"), "break")[1],
            add="+",
        )
        canvas.bind(
            "<Control-MouseWheel>",
            lambda event: (canvas.xview_scroll(-1 if event.delta > 0 else 1, "units"), "break")[1],
            add="+",
        )
    except Exception:
        pass


def _decorate(launcher) -> None:
    if not hasattr(launcher, "main") or not hasattr(launcher, "ind_btn"):
        return
    # The individual/research choices are deliberately deferred until Iniciar.
    try:
        mode_box = launcher.ind_btn.master.master
        launcher._yornis_mode_box_v0167 = mode_box
        if not getattr(launcher, "_yornis_started_v0167", False):
            mode_box.pack_forget()
    except Exception:
        return

    try:
        palette_host = launcher.palette_cards[0].master if launcher.palette_cards else None
        old = getattr(launcher, "_yornis_initial_panel_v0167", None)
        if old is not None and old.winfo_exists():
            old.destroy()
        panel = ttk.Frame(launcher.main, style="Elevated.TFrame", padding=(16, 12))
        if palette_host is not None:
            panel.pack(fill="x", pady=(8, 12), before=palette_host)
        else:
            panel.pack(fill="x", pady=10)

        title = ttk.Label(panel, text="INICIAL", style="CardTitle.TLabel", anchor="center", justify="center")
        title.pack(fill="x", pady=(0, 8))
        controls = ttk.Frame(panel, style="Panel.TFrame")
        controls.pack(fill="x")
        pref = _prefs()

        ttk.Label(controls, text="Tipo de letra", style="Muted.TLabel").pack(side="left", padx=(0, 6))
        family = ttk.Combobox(
            controls, state="readonly", width=17,
            values=FONT_FAMILIES,
        )
        family.set(pref["font_family"] if pref["font_family"] in FONT_FAMILIES else "Segoe UI")
        family.pack(side="left", padx=(0, 14))

        ttk.Label(controls, text="Tamaño", style="Muted.TLabel").pack(side="left", padx=(0, 6))
        size = ttk.Combobox(
            controls, state="readonly", width=5,
            values=tuple(str(n) for n in FONT_SIZES),
        )
        size.set(str(pref["font_size"]))
        size.pack(side="left")

        def apply_preferences(_event=None):
            chosen_family = family.get() or "Segoe UI"
            try:
                chosen_size = int(size.get())
            except Exception:
                chosen_size = 10
            _save_pref("font_family", chosen_family)
            _save_pref("font_size", chosen_size)
            _apply_typography(launcher, chosen_family, chosen_size)
            _install_horizontal_scroll(launcher)

        family.bind("<<ComboboxSelected>>", apply_preferences)
        size.bind("<<ComboboxSelected>>", apply_preferences)

        launcher._yornis_initial_panel_v0167 = panel
        launcher._yornis_font_family_v0167 = family
        launcher._yornis_font_size_v0167 = size
        launcher.question.configure(text="INICIAL", anchor="center", justify="center")
        launcher.question_sub.configure(
            text="Configura la paleta, la tipografía y el tamaño de letra antes de iniciar.",
            anchor="center", justify="center",
        )

        def start():
            import yornis_bird_signature_v01592 as bird_audio
            bird_audio.play_bird_signature(yornis_theme.current_theme_name(), launcher)
            launcher._yornis_started_v0167 = True
            launcher.question.configure(
                text="¿Cómo deseas trabajar?",
                anchor="center", justify="center",
            )
            launcher.question_sub.configure(
                text="Selecciona el flujo después de configurar tu espacio de trabajo.",
                anchor="center", justify="center",
            )
            mode_box.pack(fill="x", before=palette_host) if palette_host is not None else mode_box.pack(fill="x")
            try:
                launcher._scroll_canvas.update_idletasks()
                launcher._scroll_canvas.configure(scrollregion=launcher._scroll_canvas.bbox("all"))
            except Exception:
                pass

        launcher._yornis_start_button_v0167 = ttk.Button(
            panel, text="Iniciar  →", style="Primary.TButton", command=start,
        )
        launcher._yornis_start_button_v0167.pack(fill="x", pady=(12, 0))
        _apply_typography(launcher, pref["font_family"], pref["font_size"])
        _install_horizontal_scroll(launcher)
    except Exception:
        # A presentation preference must never prevent the clinical launcher opening.
        return


def install(launcher_class) -> bool:
    global _INSTALLED
    if getattr(launcher_class, "_yornis_launcher_preferences_v0167", False):
        return True

    original_init = launcher_class.__init__
    original_rebuild = launcher_class._rebuild_quality_launcher
    try:
        import yornis_modern_ui_v0160 as modern_ui
        original_modern_apply = modern_ui.apply_modern_styles

        def apply_saved_typography(root):
            pref = _prefs()
            family, size = pref["font_family"], pref["font_size"]
            modern_ui._FONT = (family, size)
            modern_ui._FONT_MEDIUM = (family, size)
            modern_ui._FONT_TITLE = (family, size + 12)
            result = original_modern_apply(root)
            _apply_typography(root, family, size)
            return result

        modern_ui.apply_modern_styles = apply_saved_typography
    except Exception:
        pass

    def init(self, *args, **kwargs):
        # v0.15.9 used this hook for a single selected-bird startup call. Replace
        # it with the ten-bird welcome chorus before the inherited constructor runs.
        startup_audio.play_startup_chorus = _play_welcome_chorus
        original_init(self, *args, **kwargs)
        try:
            self.after_idle(lambda: _decorate(self))
        except Exception:
            _decorate(self)

    def rebuild(self, *args, **kwargs):
        result = original_rebuild(self, *args, **kwargs)
        try:
            self.after_idle(lambda: _decorate(self))
        except Exception:
            pass
        return result

    launcher_class.__init__ = init
    launcher_class._rebuild_quality_launcher = rebuild
    launcher_class._yornis_launcher_preferences_v0167 = True
    _INSTALLED = True
    return True
