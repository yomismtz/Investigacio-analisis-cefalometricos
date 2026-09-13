from __future__ import annotations

import json
import locale
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from PIL import Image, ImageTk

from yomceph_theme import PALETTE, SEMANTIC

APP_VERSION = "0.14.0 Classic Research Suite"
APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "YomCeph"
SETTINGS = APP_DIR / "settings.json"


def resource_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    p = base / name
    if p.exists():
        return p
    return Path(__file__).resolve().parent / "assets" / name


def load_settings() -> dict:
    try:
        return json.loads(SETTINGS.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_settings(data: dict):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def default_language() -> str:
    saved = load_settings().get("language")
    if saved in {"es", "en"}:
        return saved
    try:
        loc = (locale.getlocale()[0] or "").lower()
    except Exception:
        loc = ""
    return "es" if loc.startswith("es") else "en"


class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.language = default_language()
        self.choice = None
        self.title("YomCeph Desktop")
        self.geometry("780x570")
        self.resizable(False, False)
        self.configure(bg=PALETTE["lavender_050"])
        self.logo_photo = None
        self._style()
        self._build()

    def _style(self):
        s = ttk.Style(self)
        try:
            s.theme_use("vista")
        except Exception:
            pass
        s.configure("Launch.TFrame", background=PALETTE["lavender_050"])
        s.configure("LaunchTitle.TLabel", background=PALETTE["lavender_050"], foreground=PALETTE["violet_950"], font=("Segoe UI", 22, "bold"))
        s.configure("LaunchSub.TLabel", background=PALETTE["lavender_050"], foreground=PALETTE["ink_soft"], font=("Segoe UI", 10))
        s.configure("Mode.TButton", font=("Segoe UI", 13, "bold"), padding=(12, 18))

    def tr(self, es, en):
        return es if self.language == "es" else en

    def _build(self):
        self.main = ttk.Frame(self, style="Launch.TFrame", padding=22)
        self.main.pack(fill="both", expand=True)
        try:
            im = Image.open(resource_path("yomceph_logo.png")).convert("RGBA")
            im.thumbnail((145, 145))
            self.logo_photo = ImageTk.PhotoImage(im)
            tk.Label(self.main, image=self.logo_photo, bg=PALETTE["lavender_050"]).pack(pady=(0, 4))
        except Exception:
            pass
        self.title_lbl = ttk.Label(self.main, text="YomCeph Desktop", style="LaunchTitle.TLabel")
        self.title_lbl.pack()
        self.ver_lbl = ttk.Label(self.main, text=f"v{APP_VERSION}", style="LaunchSub.TLabel")
        self.ver_lbl.pack(pady=(0, 12))
        langrow = ttk.Frame(self.main, style="Launch.TFrame")
        langrow.pack(pady=6)
        ttk.Label(langrow, text="Idioma / Language:", style="LaunchSub.TLabel").pack(side="left", padx=5)
        self.lang = ttk.Combobox(langrow, state="readonly", values=["Español", "English"], width=14)
        self.lang.pack(side="left")
        self.lang.current(0 if self.language == "es" else 1)
        self.lang.bind("<<ComboboxSelected>>", self.change_language)
        self.question = ttk.Label(self.main, text="", style="LaunchSub.TLabel", font=("Segoe UI", 13, "bold"))
        self.question.pack(pady=(18, 10))
        modes = ttk.Frame(self.main, style="Launch.TFrame")
        modes.pack(fill="x", padx=35)
        self.ind_btn = ttk.Button(modes, style="Mode.TButton", command=lambda: self.finish("individual"))
        self.ind_btn.pack(side="left", fill="both", expand=True, padx=6)
        self.res_btn = ttk.Button(modes, style="Mode.TButton", command=lambda: self.finish("research"))
        self.res_btn.pack(side="left", fill="both", expand=True, padx=6)
        self.note = ttk.Label(self.main, text="", style="LaunchSub.TLabel", wraplength=680, justify="center")
        self.note.pack(pady=18)
        self.refresh_text()

    def change_language(self, _=None):
        self.language = "es" if self.lang.current() == 0 else "en"
        save_settings({**load_settings(), "language": self.language})
        self.refresh_text()

    def refresh_text(self):
        self.question.config(text=self.tr("¿Qué vamos a hacer hoy?", "What are we doing today?"))
        self.ind_btn.config(text=self.tr("CASO INDIVIDUAL\nTrazado y análisis cefalométrico", "INDIVIDUAL CASE\nCephalometric tracing and analysis"))
        self.res_btn.config(text=self.tr("INVESTIGACIÓN\nProtocolo, base de datos y hasta 1000 casos", "RESEARCH\nProtocol, database and up to 1000 cases"))
        self.note.config(text=self.tr(
            "La versión Classic conserva el flujo visual de YomCeph 0.12.x. El modo Investigación añade protocolo versionado, selección exacta de resultados, trazado guiado, auditoría y exportación estadística.",
            "Classic preserves the YomCeph 0.12.x visual workflow. Research mode adds versioned protocols, exact outcome selection, guided tracing, audit and statistical export.",
        ))

    def finish(self, mode):
        self.choice = mode
        save_settings({**load_settings(), "language": self.language, "last_mode": mode})
        self.destroy()


def main():
    launch = Launcher()
    launch.mainloop()
    mode = launch.choice
    lang = launch.language
    if mode == "individual":
        import yomceph_desktop_v130_classic as classic
        app = classic.YomCephClassic()
        try:
            app.title(f"YomCeph Desktop · v{APP_VERSION} · Individual")
        except Exception:
            pass
        app.mainloop()
    elif mode == "research":
        import research_ui
        import research_enhancements
        research_enhancements.install(research_ui.ResearchWorkspace)
        app = research_ui.ResearchWorkspace(lang)
        app.mainloop()


if __name__ == "__main__":
    main()
