from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

import yornis_desktop_v0157 as previous
import yornis_theme
import yornis_quality_ui_v0158 as quality
import yornis_reference_help_v0156 as reference_help
import yornis_virtual_assistant_v0157 as assistant

APP_VERSION = "0.15.8 Final Polish · Bird Assistant"


class Launcher(previous.Launcher):
    """Final launcher: cleaner hierarchy, richer palette cards and clearer actions."""

    def __init__(self):
        super().__init__()
        self.title("Yornis · Yom Dental Análisis")
        self.geometry("1120x900")
        self.minsize(1000, 790)
        quality.apply_window(self, context="launcher")
        assistant.attach_assistant_button(self, compact=True)

    def _rebuild_quality_launcher(self):
        for child in self.winfo_children():
            child.destroy()

        theme_name = yornis_theme.current_theme_name()
        t = yornis_theme.THEMES[theme_name]
        profile = assistant.current_profile()

        # The launcher is taller than many notebook/desktop viewports. Keep the
        # content in a real scrollable canvas with a permanent vertical bar.
        self._scroll_shell = ttk.Frame(self)
        self._scroll_shell.pack(fill="both", expand=True)
        self._scroll_canvas = tk.Canvas(
            self._scroll_shell,
            bd=0,
            highlightthickness=0,
            bg=t.get("bg", t.get("panel_alt", "#ffffff")),
        )
        self._scrollbar = ttk.Scrollbar(self._scroll_shell, orient="vertical", command=self._scroll_canvas.yview)
        self._scroll_canvas.configure(yscrollcommand=self._scrollbar.set)
        self._scrollbar.pack(side="right", fill="y")
        self._scroll_canvas.pack(side="left", fill="both", expand=True)

        self.main = ttk.Frame(self._scroll_canvas, padding=(38, 28))
        self._scroll_window = self._scroll_canvas.create_window((0, 0), window=self.main, anchor="nw")
        self.main.bind("<Configure>", self._update_launcher_scrollregion)
        self._scroll_canvas.bind("<Configure>", self._resize_launcher_scroll_window)
        # Toplevel bindings are present in the bindtags of child widgets, so the
        # mouse wheel works even while the pointer is over cards/buttons.
        self.bind("<MouseWheel>", self._on_launcher_mousewheel)
        self.bind("<Prior>", lambda _e: self._scroll_canvas.yview_scroll(-1, "pages"))
        self.bind("<Next>", lambda _e: self._scroll_canvas.yview_scroll(1, "pages"))
        self.bind("<Home>", lambda _e: self._scroll_canvas.yview_moveto(0.0))
        self.bind("<End>", lambda _e: self._scroll_canvas.yview_moveto(1.0))

        topbar = ttk.Frame(self.main)
        topbar.pack(fill="x")

        logo_box = tk.Frame(topbar, bg=t["panel"], highlightthickness=1, highlightbackground=t["border"])
        logo_box.pack(side="left", padx=(0, 16))
        self.logo_photo = None
        try:
            p = previous.previous.previous.legacy.base.resource_path("yornis_logo.png")
            im = Image.open(p).convert("RGBA")
            im.thumbnail((78, 78), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(im)
            tk.Label(logo_box, image=self.logo_photo, bg=t["panel"], padx=10, pady=10).pack()
        except Exception:
            tk.Label(logo_box, text="Y", bg=t["panel"], fg=t["primary"], font=("Segoe UI Semibold", 30), padx=18, pady=14).pack()

        brand = ttk.Frame(topbar)
        brand.pack(side="left", fill="x", expand=True)
        ttk.Label(brand, text="YOM DENTAL ANÁLISIS", style="Eyebrow.TLabel").pack(anchor="w")
        self.title_lbl = ttk.Label(brand, text="Yornis", style="Title.TLabel")
        self.title_lbl.pack(anchor="w", pady=(1, 0))
        self.ver_lbl = ttk.Label(brand, text=f"v{APP_VERSION}", style="Caption.TLabel")
        self.ver_lbl.pack(anchor="w", pady=(2, 0))

        utilities = ttk.Frame(topbar)
        utilities.pack(side="right", anchor="ne")
        self.lang = ttk.Combobox(utilities, state="readonly", values=["Español", "English"], width=13)
        self.lang.grid(row=0, column=0, padx=(0, 7), sticky="e")
        self.lang.current(0 if self.language == "es" else 1)
        self.lang.bind("<<ComboboxSelected>>", self.change_language)
        ttk.Button(utilities, text="Referencias  F1", style="Ghost.TButton", command=lambda: reference_help.open_reference_help(self)).grid(row=0, column=1, padx=(0, 7))
        ttk.Button(utilities, text="Asistente  Ctrl+K", style="Assistant.TButton", command=lambda: assistant.open_assistant(self)).grid(row=0, column=2)

        ttk.Separator(self.main).pack(fill="x", pady=(18, 18))

        hero = ttk.Frame(self.main)
        hero.pack(fill="x")
        hero_copy = ttk.Frame(hero)
        hero_copy.pack(side="left", fill="both", expand=True, padx=(0, 18))
        self.hero_title = ttk.Label(hero_copy, text="", style="Hero.TLabel", wraplength=680, justify="left")
        self.hero_title.pack(anchor="w")
        self.hero_sub = ttk.Label(hero_copy, text="", style="Caption.TLabel", wraplength=710, justify="left")
        self.hero_sub.pack(anchor="w", pady=(8, 0))

        assistant_card = ttk.Frame(hero, style="Elevated.TFrame", padding=(16, 14))
        assistant_card.pack(side="right", fill="y")
        assistant_top = ttk.Frame(assistant_card, style="Panel.TFrame")
        assistant_top.pack(fill="x")
        self.assistant_photo = assistant.make_avatar_photo(self, 94, theme_name)
        tk.Label(assistant_top, image=self.assistant_photo, bg=t["panel"]).pack(side="left", padx=(0, 12))
        assistant_text = ttk.Frame(assistant_top, style="Panel.TFrame")
        assistant_text.pack(side="left", fill="both", expand=True)
        ttk.Label(assistant_text, text=theme_name, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(assistant_text, text="Tu asistente virtual", style="Muted.TLabel").pack(anchor="w", pady=(1, 4))
        ttk.Label(assistant_text, text=profile["personality"], style="CardBody.TLabel", wraplength=210, justify="left").pack(anchor="w")
        ttk.Label(assistant_card, text=profile["tagline"], style="Muted.TLabel", wraplength=300, justify="left").pack(anchor="w", fill="x", pady=(10, 0))

        stats = ttk.Frame(self.main)
        stats.pack(fill="x", pady=(18, 16))
        stat_data = [
            ("102", "mediciones"),
            ("17", "tablas de referencia"),
            ("8", "paletas + asistentes"),
            ("HiDPI", "interfaz optimizada"),
        ]
        for idx, (big, small) in enumerate(stat_data):
            card = ttk.Frame(stats, style="Elevated.TFrame", padding=(14, 10))
            card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 5, 0 if idx == len(stat_data)-1 else 5))
            stats.grid_columnconfigure(idx, weight=1)
            ttk.Label(card, text=big, style="Metric.TLabel").pack(anchor="w")
            ttk.Label(card, text=small, style="Muted.TLabel").pack(anchor="w", pady=(1, 0))

        self.question = ttk.Label(self.main, text="", font=("Segoe UI Semibold", 15))
        self.question.pack(anchor="w", pady=(2, 2))
        self.question_sub = ttk.Label(self.main, text="", style="Caption.TLabel")
        self.question_sub.pack(anchor="w", pady=(0, 9))

        modes = ttk.Frame(self.main)
        modes.pack(fill="x")
        mode_specs = [
            ("01", "INDIVIDUAL", "Caso individual", "Carga una telerradiografía, marca landmarks, calcula análisis y consulta referencias sin salir de la app.", "Primary.TButton", lambda: self.finish("individual")),
            ("02", "INVESTIGACIÓN", "Modo investigación", "Protocolos versionados, control de calidad, reproducibilidad, base de casos y exportaciones para análisis.", "Secondary.TButton", lambda: self.finish("research")),
        ]
        mode_widgets = []
        for i, (num, eyebrow, title, desc, btn_style, command) in enumerate(mode_specs):
            card = ttk.Frame(modes, style="Elevated.TFrame", padding=(18, 16))
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 7, 0 if i == 1 else 7))
            modes.grid_columnconfigure(i, weight=1)
            top = ttk.Frame(card, style="Panel.TFrame")
            top.pack(fill="x")
            ttk.Label(top, text=num, style="Pill.TLabel").pack(side="left")
            ttk.Label(top, text=eyebrow, style="Muted.TLabel").pack(side="left", padx=(8, 0))
            title_lbl = ttk.Label(card, text=title, style="CardTitle.TLabel")
            title_lbl.pack(anchor="w", pady=(10, 3))
            desc_lbl = ttk.Label(card, text=desc, style="CardBody.TLabel", wraplength=440, justify="left")
            desc_lbl.pack(anchor="w", fill="x", pady=(0, 12))
            btn = ttk.Button(card, text="Abrir  →", style=btn_style, command=command)
            btn.pack(fill="x")
            mode_widgets.append((title_lbl, desc_lbl, btn))
        self.ind_title, self.ind_desc, self.ind_btn = mode_widgets[0]
        self.res_title, self.res_desc, self.res_btn = mode_widgets[1]

        palette_header = ttk.Frame(self.main)
        palette_header.pack(fill="x", pady=(18, 6))
        ttk.Label(palette_header, text="Elige tu ave y paleta", style="Heading.TLabel").pack(side="left")
        ttk.Label(palette_header, text="La selección cambia el aspecto completo de Yornis · cada ave tiene su canto", style="Caption.TLabel").pack(side="right")

        palette_host = ttk.Frame(self.main)
        palette_host.pack(fill="x")
        self.palette_cards = []
        self.palette_photos = []
        for i, name in enumerate(yornis_theme.theme_names()):
            th = yornis_theme.THEMES[name]
            selected = name == theme_name
            card = tk.Frame(palette_host, bg=th["panel"], highlightthickness=(3 if selected else 1), highlightbackground=(th["primary"] if selected else th["border"]), cursor="hand2")
            card.grid(row=i // 4, column=i % 4, sticky="nsew", padx=5, pady=5)
            palette_host.grid_columnconfigure(i % 4, weight=1)

            top = tk.Frame(card, bg=th["panel"], cursor="hand2")
            top.pack(fill="x", padx=9, pady=(8, 3))
            photo = assistant.make_avatar_photo(self, 42, name)
            self.palette_photos.append(photo)
            avatar = tk.Label(top, image=photo, bg=th["panel"], cursor="hand2")
            avatar.pack(side="left", padx=(0, 7))
            title_box = tk.Frame(top, bg=th["panel"], cursor="hand2")
            title_box.pack(side="left", fill="x", expand=True)
            title = tk.Label(title_box, text=("✓ " if selected else "") + name, bg=th["panel"], fg=th["primary_dark"], font=("Segoe UI Semibold", 9), anchor="w", cursor="hand2")
            title.pack(fill="x")
            subtitle = tk.Label(title_box, text=("Activa · ♪" if selected else "Seleccionar · ♪"), bg=th["panel"], fg=th["muted"], font=("Segoe UI", 8), anchor="w", cursor="hand2")
            subtitle.pack(fill="x")

            swatches = tk.Frame(card, bg=th["panel"], cursor="hand2")
            swatches.pack(fill="x", padx=9, pady=(2, 8))
            for key in ("primary", "secondary", "accent", "tertiary"):
                tk.Frame(swatches, bg=th[key], height=11, bd=0, cursor="hand2").pack(side="left", fill="x", expand=True, padx=1)

            for widget in (card, top, avatar, title_box, title, subtitle, swatches):
                widget.bind("<Button-1>", lambda _e, n=name: self._theme_quality(n))
            self.palette_cards.append(card)

        footer = ttk.Frame(self.main)
        footer.pack(fill="x", pady=(14, 0))
        self.note = ttk.Label(footer, text="", wraplength=820, justify="left", style="Caption.TLabel")
        self.note.pack(side="left", fill="x", expand=True)
        ttk.Label(footer, text="FINAL POLISH · 0.15.8", style="AccentPill.TLabel").pack(side="right", padx=(12, 0))
        self.refresh_text()
        self.after_idle(self._update_launcher_scrollregion)

    def _update_launcher_scrollregion(self, _event=None):
        canvas = getattr(self, "_scroll_canvas", None)
        if canvas is None:
            return
        try:
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=bbox)
        except Exception:
            pass

    def _resize_launcher_scroll_window(self, event):
        try:
            self._scroll_canvas.itemconfigure(self._scroll_window, width=max(1, event.width))
            self._update_launcher_scrollregion()
        except Exception:
            pass

    def _on_launcher_mousewheel(self, event):
        canvas = getattr(self, "_scroll_canvas", None)
        if canvas is None:
            return
        try:
            first, last = canvas.yview()
            if first <= 0.0 and last >= 1.0:
                return
            steps = max(1, abs(int(event.delta / 120))) if event.delta else 1
            canvas.yview_scroll(-steps if event.delta > 0 else steps, "units")
        except Exception:
            pass

    def _theme_quality(self, name):
        # Always play the selected bird's own short signature, even if the user
        # clicks the palette that is already active.
        try:
            import yornis_bird_signature_v01592 as bird_audio
            bird_audio.play_bird_signature(name, self)
        except Exception:
            pass
        if name == yornis_theme.current_theme_name():
            return
        try:
            position = self._scroll_canvas.yview()[0]
        except Exception:
            position = 0.0
        yornis_theme.apply_theme(name)
        self._rebuild_quality_launcher()
        quality.apply_window(self, context="launcher")
        assistant.attach_assistant_button(self, compact=True)
        try:
            self.after_idle(lambda p=position: self._scroll_canvas.yview_moveto(p))
        except Exception:
            pass

    def refresh_text(self):
        if not hasattr(self, "hero_title"):
            return previous.Launcher.refresh_text(self)
        tr = self.tr
        self.title_lbl.configure(text="Yornis")
        self.ver_lbl.configure(text=f"v{APP_VERSION}")
        self.hero_title.configure(text=tr("Cefalometría más clara, visual y auditable.", "Clearer, more visual and auditable cephalometrics."))
        self.hero_sub.configure(text=tr("Una interfaz refinada para docencia, análisis individual e investigación, con ayuda contextual, referencias y paletas visuales integradas.", "A refined interface for teaching, individual analysis and research, with contextual help, references and integrated visual palettes."))
        self.question.configure(text=tr("¿Qué vamos a hacer hoy?", "What are we doing today?"))
        self.question_sub.configure(text=tr("Elige un flujo. Tu ave-asistente y el buscador permanecen disponibles en toda la aplicación.", "Choose a workflow. Your bird assistant and search remain available throughout the application."))
        self.ind_title.configure(text=tr("Caso individual", "Individual case"))
        self.ind_desc.configure(text=tr("Carga una telerradiografía, marca landmarks, calcula análisis y consulta referencias sin salir de la app.", "Load a lateral cephalogram, place landmarks, calculate analyses and review references without leaving the app."))
        self.ind_btn.configure(text=tr("Abrir caso individual  →", "Open individual case  →"))
        self.res_title.configure(text=tr("Modo investigación", "Research mode"))
        self.res_desc.configure(text=tr("Protocolos versionados, control de calidad, reproducibilidad, base de casos y exportaciones para análisis.", "Versioned protocols, quality control, reproducibility, case database and analysis exports."))
        self.res_btn.configure(text=tr("Abrir investigación  →", "Open research  →"))
        self.note.configure(text=tr("Uso educativo e investigación. Las referencias se contextualizan por método, edad y sexo cuando existe evidencia compatible; Yornis no inventa valores faltantes ni sustituye criterio clínico.", "Educational and research use. References are contextualized by method, age and sex when compatible evidence exists; Yornis does not invent missing values or replace clinical judgment."))


def research_app(lang):
    app = previous.research_app(lang)
    app.title(f"Yornis · Yom Dental Análisis · v{APP_VERSION} · Investigación")
    quality.apply_window(app, context="research")
    assistant.attach_assistant_button(app)
    return app


def main():
    previous.previous.previous.evidence.install()
    launch = Launcher()
    reference_help.attach_help_button(launch, compact=True)
    assistant.attach_assistant_button(launch, compact=True)
    launch.mainloop()
    mode = launch.choice
    lang = launch.language
    if mode == "individual":
        import yomceph_desktop_v130_classic as classic
        previous.previous.previous.legacy.yornis_cervical_v0152.install_individual(classic.YomCephClassic)
        previous.previous.previous.legacy.yornis_alignment_v0152.install_individual(classic.YomCephClassic)
        previous.previous.previous.legacy.yornis_ceph_quality_v0153.install_individual(classic.YomCephClassic)
        previous.previous.previous.hardening.install_individual(classic.YomCephClassic)
        previous.previous.quality.install_individual(classic.YomCephClassic)
        previous.quality.install_individual(classic.YomCephClassic)
        quality.install_individual(classic.YomCephClassic)
        previous.previous.previous.evidence.install()
        app = classic.YomCephClassic()
        app.title(f"Yornis · Yom Dental Análisis · v{APP_VERSION} · Individual")
        previous.previous.previous.legacy.display.apply_display_quality(app, launcher=False)
        quality.apply_window(app, context="individual")
        reference_help.attach_help_button(app)
        assistant.attach_assistant_button(app)
        app.mainloop()
    elif mode == "research":
        research_app(lang).mainloop()


if __name__ == "__main__":
    main()
