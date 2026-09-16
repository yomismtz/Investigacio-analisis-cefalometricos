from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

import yornis_desktop_v0156 as previous
import yornis_theme
import yornis_quality_ui_v0157 as quality
import yornis_reference_help_v0156 as reference_help
import yornis_virtual_assistant_v0157 as assistant

APP_VERSION = "0.15.7 Research Suite · Bird Assistant"
previous.APP_VERSION = APP_VERSION
previous.previous.legacy.APP_VERSION = APP_VERSION


class Launcher(previous.Launcher):
    """Launcher with visible palette cards and the palette bird as assistant."""

    def __init__(self):
        super().__init__()
        self.title("Yornis · Yom Dental Análisis")
        self.geometry("1040x850")
        self.minsize(940, 760)
        self._rebuild_quality_launcher()
        quality.apply_window(self, context="launcher")
        assistant.attach_assistant_button(self, compact=True)

    def _rebuild_quality_launcher(self):
        for child in self.winfo_children():
            child.destroy()

        theme_name = yornis_theme.current_theme_name()
        t = yornis_theme.THEMES[theme_name]
        profile = assistant.current_profile()

        self.main = ttk.Frame(self, padding=(32, 24))
        self.main.pack(fill="both", expand=True)

        header = ttk.Frame(self.main)
        header.pack(fill="x")
        logo_box = tk.Frame(header, bg=t["panel"], highlightthickness=2, highlightbackground=t["primary_soft"])
        logo_box.pack(side="left", padx=(0, 16))
        self.logo_photo = None
        try:
            p = previous.previous.legacy.base.resource_path("yornis_logo.png")
            im = Image.open(p).convert("RGBA")
            im.thumbnail((92, 92), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(im)
            tk.Label(logo_box, image=self.logo_photo, bg=t["panel"], padx=8, pady=8).pack()
        except Exception:
            tk.Label(logo_box, text="Y", bg=t["panel"], fg=t["primary"], font=("Segoe UI Semibold", 30), padx=18, pady=12).pack()

        brand = ttk.Frame(header)
        brand.pack(side="left", fill="x", expand=True)
        self.title_lbl = ttk.Label(brand, text="Yornis", style="Title.TLabel")
        self.title_lbl.pack(anchor="w")
        self.ver_lbl = ttk.Label(brand, text=f"Yom Dental Análisis · v{APP_VERSION}", style="Caption.TLabel")
        self.ver_lbl.pack(anchor="w", pady=(3, 0))
        self.build_badge = tk.Label(brand, text="ASISTENTE DE AVE + BUSCADOR INTERNO + HiDPI", bg=t["accent_soft"], fg=t["secondary_dark"], font=("Segoe UI Semibold", 8), padx=10, pady=4)
        self.build_badge.pack(anchor="w", pady=(8, 0))

        lang_box = ttk.Frame(header)
        lang_box.pack(side="right", anchor="ne")
        ttk.Label(lang_box, text="Idioma / Language", style="Caption.TLabel").pack(anchor="e")
        self.lang = ttk.Combobox(lang_box, state="readonly", values=["Español", "English"], width=14)
        self.lang.pack(anchor="e", pady=(4, 0))
        self.lang.current(0 if self.language == "es" else 1)
        self.lang.bind("<<ComboboxSelected>>", self.change_language)

        ttk.Separator(self.main).pack(fill="x", pady=(18, 14))

        top = ttk.Frame(self.main)
        top.pack(fill="x")
        flow = ttk.Frame(top)
        flow.pack(side="left", fill="both", expand=True, padx=(0, 14))
        assistant_card = ttk.Frame(top, style="Assistant.Card.TFrame", padding=(14, 12))
        assistant_card.pack(side="right", fill="y")

        self.question = ttk.Label(flow, text="", font=("Segoe UI Semibold", 16))
        self.question.pack(anchor="w")
        self.question_sub = ttk.Label(flow, text="", style="Caption.TLabel")
        self.question_sub.pack(anchor="w", pady=(3, 10))

        modes = ttk.Frame(flow)
        modes.pack(fill="x")
        individual = ttk.LabelFrame(modes, text="01 · INDIVIDUAL", padding=(16, 12))
        individual.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.ind_title = ttk.Label(individual, text="", style="Heading.TLabel")
        self.ind_title.pack(anchor="w")
        self.ind_desc = ttk.Label(individual, text="", wraplength=285, justify="left", style="Panel.TLabel")
        self.ind_desc.pack(anchor="w", fill="x", pady=(6, 12))
        self.ind_btn = ttk.Button(individual, text="", style="Primary.TButton", command=lambda: self.finish("individual"))
        self.ind_btn.pack(fill="x")

        research = ttk.LabelFrame(modes, text="02 · INVESTIGACIÓN", padding=(16, 12))
        research.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self.res_title = ttk.Label(research, text="", style="Heading.TLabel")
        self.res_title.pack(anchor="w")
        self.res_desc = ttk.Label(research, text="", wraplength=285, justify="left", style="Panel.TLabel")
        self.res_desc.pack(anchor="w", fill="x", pady=(6, 12))
        self.res_btn = ttk.Button(research, text="", style="Secondary.TButton", command=lambda: self.finish("research"))
        self.res_btn.pack(fill="x")

        self.assistant_photo = assistant.make_avatar_photo(self, 116, theme_name)
        tk.Label(assistant_card, image=self.assistant_photo, bg=t["panel"]).pack()
        ttk.Label(assistant_card, text=theme_name, style="Assistant.Title.TLabel").pack(pady=(4, 0))
        ttk.Label(assistant_card, text="Tu asistente virtual", style="Assistant.Subtitle.TLabel").pack()
        ttk.Label(assistant_card, text=profile["tagline"], style="Assistant.Body.TLabel", wraplength=225, justify="center").pack(pady=(6, 10))
        ttk.Button(assistant_card, text="Abrir asistente  Ctrl+K", style="Assistant.TButton", command=lambda: assistant.open_assistant(self)).pack(fill="x")
        ttk.Button(assistant_card, text="Ver referencias  F1", style="Ghost.TButton", command=lambda: reference_help.open_reference_help(self)).pack(fill="x", pady=(6, 0))

        ttk.Label(self.main, text="Elige tu ave y paleta", style="Heading.TLabel").pack(anchor="w", pady=(16, 3))
        ttk.Label(self.main, text="La paleta cambia toda la interfaz y esa ave se convierte en tu asistente. Los colores de cada tarjeta son los que verás en botones, pestañas, tablas y estados.", style="Caption.TLabel", wraplength=940, justify="left").pack(anchor="w", fill="x", pady=(0, 8))

        palette_host = ttk.Frame(self.main)
        palette_host.pack(fill="x")
        self.palette_cards = []
        for i, name in enumerate(yornis_theme.theme_names()):
            th = yornis_theme.THEMES[name]
            selected = name == theme_name
            card = tk.Frame(palette_host, bg=th["panel"], highlightthickness=(3 if selected else 1), highlightbackground=(th["primary"] if selected else th["border"]), cursor="hand2")
            card.grid(row=i // 4, column=i % 4, sticky="nsew", padx=5, pady=5)
            palette_host.grid_columnconfigure(i % 4, weight=1)
            title = tk.Label(card, text=("✓ " if selected else "") + name, bg=th["panel"], fg=th["primary_dark"], font=("Segoe UI Semibold", 9), anchor="w", padx=9, pady=6, cursor="hand2")
            title.pack(fill="x")
            swatches = tk.Frame(card, bg=th["panel"])
            swatches.pack(fill="x", padx=9, pady=(0, 7))
            for key in ("primary", "secondary", "accent", "tertiary"):
                tk.Frame(swatches, bg=th[key], width=24, height=13, bd=0).pack(side="left", fill="x", expand=True, padx=1)
            desc = tk.Label(card, text=th["description_es"], bg=th["panel"], fg=th["muted"], font=("Segoe UI", 8), wraplength=200, justify="left", anchor="w", padx=9, pady=5, cursor="hand2")
            desc.pack(fill="x")
            for widget in (card, title, desc):
                widget.bind("<Button-1>", lambda _e, n=name: self._theme_quality(n))
            self.palette_cards.append(card)

        badges = ttk.Frame(self.main)
        badges.pack(fill="x", pady=(10, 7))
        for text in ("102 mediciones", "17 tablas", "Buscador interno", "Asistente contextual", "HiDPI", "Datos locales"):
            tk.Label(badges, text="• " + text, bg=t["panel_alt"], fg=t["primary_dark"], font=("Segoe UI Semibold", 9), padx=9, pady=4).pack(side="left", padx=(0, 6), pady=2)

        self.note = ttk.Label(self.main, text="", wraplength=950, justify="left", style="Caption.TLabel")
        self.note.pack(fill="x", pady=(3, 0))
        self.refresh_text()

    def _theme_quality(self, name):
        if name == yornis_theme.current_theme_name():
            return
        yornis_theme.apply_theme(name)
        self._rebuild_quality_launcher()
        quality.apply_window(self, context="launcher")
        assistant.attach_assistant_button(self, compact=True)

    def refresh_text(self):
        if not hasattr(self, "question_sub"):
            return previous.Launcher.refresh_text(self)
        tr = self.tr
        self.title_lbl.configure(text="Yornis")
        self.ver_lbl.configure(text=f"Yom Dental Análisis · v{APP_VERSION}")
        self.question.configure(text=tr("¿Qué vamos a hacer hoy?", "What are we doing today?"))
        self.question_sub.configure(text=tr("Elige un flujo. Tu ave-asistente permanece disponible en toda la app.", "Choose a workflow. Your bird assistant remains available throughout the app."))
        self.ind_title.configure(text=tr("Caso individual", "Individual case"))
        self.ind_desc.configure(text=tr("Carga una telerradiografía, marca landmarks, calcula análisis y revisa referencias localmente.", "Load a lateral cephalogram, place landmarks, calculate analyses and review references locally."))
        self.ind_btn.configure(text=tr("Abrir caso individual  →", "Open individual case  →"))
        self.res_title.configure(text=tr("Investigación", "Research"))
        self.res_desc.configure(text=tr("Protocolos versionados, hasta 1000 casos, control de calidad, reproducibilidad y exportaciones.", "Versioned protocols, up to 1000 cases, quality control, reproducibility and exports."))
        self.res_btn.configure(text=tr("Abrir modo investigación  →", "Open research mode  →"))
        self.note.configure(text=tr("Uso educativo e investigación. El asistente explica funciones y localiza referencias dentro de Yornis, pero no sustituye criterio clínico ni inventa valores de normalidad.", "Educational and research use. The assistant explains features and locates references inside Yornis, but does not replace clinical judgment or invent normal values."))


def research_app(lang):
    app = previous.research_app(lang)
    app.title(f"Yornis · Yom Dental Análisis · v{APP_VERSION} · Investigación")
    quality.apply_window(app, context="research")
    assistant.attach_assistant_button(app)
    return app


def main():
    previous.previous.evidence.install()
    launch = Launcher()
    reference_help.attach_help_button(launch, compact=True)
    assistant.attach_assistant_button(launch, compact=True)
    launch.mainloop()
    mode = launch.choice
    lang = launch.language
    if mode == "individual":
        import yomceph_desktop_v130_classic as classic
        previous.previous.legacy.yornis_cervical_v0152.install_individual(classic.YomCephClassic)
        previous.previous.legacy.yornis_alignment_v0152.install_individual(classic.YomCephClassic)
        previous.previous.legacy.yornis_ceph_quality_v0153.install_individual(classic.YomCephClassic)
        previous.previous.hardening.install_individual(classic.YomCephClassic)
        previous.quality.install_individual(classic.YomCephClassic)
        quality.install_individual(classic.YomCephClassic)
        previous.previous.evidence.install()
        app = classic.YomCephClassic()
        app.title(f"Yornis · Yom Dental Análisis · v{APP_VERSION} · Individual")
        previous.previous.legacy.display.apply_display_quality(app, launcher=False)
        quality.apply_window(app, context="individual")
        reference_help.attach_help_button(app)
        assistant.attach_assistant_button(app)
        app.mainloop()
    elif mode == "research":
        research_app(lang).mainloop()


if __name__ == "__main__":
    main()
