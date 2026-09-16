from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

import yornis_desktop_v0155 as previous
import yornis_theme
import yornis_quality_ui_v0156 as quality
import yornis_reference_help_v0156 as reference_help

APP_VERSION = "0.15.6 Research Suite · Quality & UX"
previous.legacy.APP_VERSION = APP_VERSION


class Launcher(previous.Launcher):
    """High-quality launcher while preserving the established mode/language flow."""

    def __init__(self):
        super().__init__()
        self.title("Yornis · Yom Dental Análisis")
        self.geometry("920x720")
        self.minsize(860, 660)
        self.resizable(True, True)
        self._rebuild_quality_launcher()
        quality.apply_window(self, context="launcher")

    def _rebuild_quality_launcher(self):
        for child in self.winfo_children():
            child.destroy()

        t = yornis_theme.THEMES[yornis_theme.current_theme_name()]
        self.main = ttk.Frame(self, padding=(34, 26))
        self.main.pack(fill="both", expand=True)

        # Brand header.
        header = ttk.Frame(self.main)
        header.pack(fill="x")
        logo_box = tk.Frame(header, bg=t["panel"], highlightthickness=1, highlightbackground=t["border"])
        logo_box.pack(side="left", padx=(0, 18))
        self.logo_photo = None
        try:
            p = previous.legacy.base.resource_path("yornis_logo.png")
            im = Image.open(p).convert("RGBA")
            im.thumbnail((88, 88))
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
        self.build_badge = tk.Label(
            brand, text="CALIDAD + UX · EVIDENCIA POR EDAD/SEXO", bg=t["accent_soft"], fg=t["secondary_dark"],
            font=("Segoe UI Semibold", 8), padx=10, pady=4,
        )
        self.build_badge.pack(anchor="w", pady=(8, 0))

        lang_box = ttk.Frame(header)
        lang_box.pack(side="right", anchor="ne")
        ttk.Label(lang_box, text="Idioma / Language", style="Caption.TLabel").pack(anchor="e")
        self.lang = ttk.Combobox(lang_box, state="readonly", values=["Español", "English"], width=14)
        self.lang.pack(anchor="e", pady=(4, 0))
        self.lang.current(0 if self.language == "es" else 1)
        self.lang.bind("<<ComboboxSelected>>", self.change_language)

        ttk.Separator(self.main).pack(fill="x", pady=(22, 18))

        self.question = ttk.Label(self.main, text="", font=("Segoe UI Semibold", 16))
        self.question.pack(anchor="w")
        self.question_sub = ttk.Label(self.main, text="", style="Caption.TLabel")
        self.question_sub.pack(anchor="w", pady=(3, 12))

        modes = ttk.Frame(self.main)
        modes.pack(fill="x")

        individual = ttk.LabelFrame(modes, text="01 · INDIVIDUAL", padding=(18, 14))
        individual.pack(side="left", fill="both", expand=True, padx=(0, 7))
        self.ind_title = ttk.Label(individual, text="", style="Heading.TLabel")
        self.ind_title.pack(anchor="w")
        self.ind_desc = ttk.Label(individual, text="", wraplength=340, justify="left", style="Panel.TLabel")
        self.ind_desc.pack(anchor="w", fill="x", pady=(6, 14))
        self.ind_btn = ttk.Button(individual, text="", style="Primary.TButton", command=lambda: self.finish("individual"))
        self.ind_btn.pack(fill="x")

        research = ttk.LabelFrame(modes, text="02 · INVESTIGACIÓN", padding=(18, 14))
        research.pack(side="left", fill="both", expand=True, padx=(7, 0))
        self.res_title = ttk.Label(research, text="", style="Heading.TLabel")
        self.res_title.pack(anchor="w")
        self.res_desc = ttk.Label(research, text="", wraplength=340, justify="left", style="Panel.TLabel")
        self.res_desc.pack(anchor="w", fill="x", pady=(6, 14))
        self.res_btn = ttk.Button(research, text="", style="Secondary.TButton", command=lambda: self.finish("research"))
        self.res_btn.pack(fill="x")

        # Product capability bullets / badges.
        badges = ttk.Frame(self.main)
        badges.pack(fill="x", pady=(18, 12))
        self.badge_labels = []
        for text in ("102 mediciones", "17 tablas", "Edad/sexo", "HiDPI", "Datos locales"):
            lbl = tk.Label(
                badges, text="• " + text, bg=t["panel_alt"], fg=t["primary_dark"],
                font=("Segoe UI Semibold", 9), padx=10, pady=5,
            )
            lbl.pack(side="left", padx=(0, 7), pady=2)
            self.badge_labels.append(lbl)

        appearance = ttk.LabelFrame(self.main, text="Apariencia", padding=(12, 9))
        appearance.pack(fill="x", pady=(2, 10))
        self.theme_prompt = ttk.Label(appearance, text="", style="Panel.TLabel")
        self.theme_prompt.pack(side="left")
        self.theme_combo = ttk.Combobox(appearance, state="readonly", values=yornis_theme.theme_names(), width=20)
        self.theme_combo.set(yornis_theme.current_theme_name())
        self.theme_combo.pack(side="left", padx=10)
        self.theme_combo.bind("<<ComboboxSelected>>", lambda _e: self._theme_quality(self.theme_combo.get()))
        ttk.Button(appearance, text="Referencias · F1", style="Ghost.TButton", command=lambda: reference_help.open_reference_help(self)).pack(side="right")

        self.note = ttk.Label(self.main, text="", wraplength=820, justify="left", style="Caption.TLabel")
        self.note.pack(fill="x", pady=(4, 0))
        self.refresh_text()

    def _theme_quality(self, name):
        yornis_theme.apply_theme(name)
        self._rebuild_quality_launcher()
        quality.apply_window(self, context="launcher")

    def refresh_text(self):
        # The inherited launcher calls refresh_text() while its own widgets are
        # still being constructed. Delegate that early call to the previous
        # implementation; only use v0.15.6 controls after our rebuild exists.
        if not hasattr(self, "question_sub"):
            return previous.Launcher.refresh_text(self)
        tr = self.tr
        self.title_lbl.configure(text="Yornis")
        self.ver_lbl.configure(text=f"Yom Dental Análisis · v{APP_VERSION}")
        self.question.configure(text=tr("¿Qué vamos a hacer hoy?", "What are we doing today?"))
        self.question_sub.configure(text=tr(
            "Elige un flujo. Ambos usan el mismo motor cefalométrico auditado.",
            "Choose a workflow. Both use the same audited cephalometric engine.",
        ))
        self.ind_title.configure(text=tr("Caso individual", "Individual case"))
        self.ind_desc.configure(text=tr(
            "Carga una telerradiografía, marca landmarks, calcula análisis y revisa referencias sin enviar datos a la nube.",
            "Load a lateral cephalogram, place landmarks, calculate analyses and review references without sending data to the cloud.",
        ))
        self.ind_btn.configure(text=tr("Abrir caso individual  →", "Open individual case  →"))
        self.res_title.configure(text=tr("Investigación", "Research"))
        self.res_desc.configure(text=tr(
            "Protocolos versionados, hasta 1000 casos, control de calidad, reproducibilidad, base de datos y exportaciones científicas.",
            "Versioned protocols, up to 1000 cases, quality control, reproducibility, database and scientific exports.",
        ))
        self.res_btn.configure(text=tr("Abrir modo investigación  →", "Open research mode  →"))
        self.theme_prompt.configure(text=tr("Tema inspirado en aves", "Bird-inspired theme"))
        self.note.configure(text=tr(
            "Uso educativo e investigación. Las referencias históricas o de muestra no equivalen por sí solas a diagnóstico; Yornis muestra edad/sexo cuando la evidencia es compatible y evita interpolar valores no publicados.",
            "Educational and research use. Historical or sample references are not diagnoses by themselves; Yornis shows age/sex when compatible evidence exists and avoids interpolating unpublished values.",
        ))


def research_app(lang):
    import research_ui, research_ui_compat, research_enhancements
    import research_stability_db_v0141, research_stability_ui_core_v0141, research_stability_ui_perf_v0141, research_stability_export_ui_v0141
    import yornis_storage_v015, yornis_import_v015, yornis_background_import_v015, yornis_research_controls_v015, yornis_ui_theme_v015, yornis_export_ui_v015, yornis_backup_v015, yornis_backup_ui_v015

    research_ui_compat.install(research_ui.ResearchWorkspace)
    research_enhancements.install(research_ui.ResearchWorkspace)
    research_stability_db_v0141.install()
    yornis_storage_v015.install()
    yornis_import_v015.install()
    yornis_backup_v015.install()
    research_stability_ui_core_v0141.install(research_ui.ResearchWorkspace, research_ui.ScrollChecks)
    research_stability_ui_perf_v0141.install(research_ui.ResearchWorkspace)
    research_stability_export_ui_v0141.install(research_ui.ResearchWorkspace)
    yornis_background_import_v015.install(research_ui.ResearchWorkspace)
    yornis_research_controls_v015.install(research_ui.ResearchWorkspace)
    yornis_ui_theme_v015.install(research_ui.ResearchWorkspace)
    yornis_export_ui_v015.install(research_ui.ResearchWorkspace)
    yornis_backup_ui_v015.install(research_ui.ResearchWorkspace)
    previous.legacy.yornis_clinical_audit_v0151.install(research_ui.ResearchWorkspace)
    previous.legacy.yornis_cervical_v0152.install_research(research_ui.ResearchWorkspace)
    previous.legacy.yornis_alignment_v0152.install_research(research_ui.ResearchWorkspace)
    previous.legacy.yornis_ceph_quality_v0153.install_research(research_ui.ResearchWorkspace)
    previous.hardening.install_research(research_ui.ResearchWorkspace)
    quality.install_research(research_ui.ResearchWorkspace)
    previous.evidence.install()

    app = research_ui.ResearchWorkspace(lang)
    app.title(f"Yornis · Yom Dental Análisis · v{APP_VERSION} · Investigación")
    previous.legacy.display.apply_display_quality(app, launcher=False)
    quality.apply_window(app, context="research")
    reference_help.attach_help_button(app)
    return app


def main():
    previous.evidence.install()
    launch = Launcher()
    reference_help.attach_help_button(launch, compact=True)
    launch.mainloop()
    mode = launch.choice
    lang = launch.language
    if mode == "individual":
        import yomceph_desktop_v130_classic as classic
        previous.legacy.yornis_cervical_v0152.install_individual(classic.YomCephClassic)
        previous.legacy.yornis_alignment_v0152.install_individual(classic.YomCephClassic)
        previous.legacy.yornis_ceph_quality_v0153.install_individual(classic.YomCephClassic)
        previous.hardening.install_individual(classic.YomCephClassic)
        quality.install_individual(classic.YomCephClassic)
        previous.evidence.install()
        app = classic.YomCephClassic()
        app.title(f"Yornis · Yom Dental Análisis · v{APP_VERSION} · Individual")
        previous.legacy.display.apply_display_quality(app, launcher=False)
        quality.apply_window(app, context="individual")
        reference_help.attach_help_button(app)
        app.mainloop()
    elif mode == "research":
        research_app(lang).mainloop()


if __name__ == "__main__":
    main()
