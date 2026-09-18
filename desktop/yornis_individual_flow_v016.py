from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

import research_workflow as workflow

_ORIGINAL_SELECTED_NAMES = workflow.selected_names


def _tr(self, es: str, en: str) -> str:
    return en if getattr(self, "lang", "es") == "en" else es


def _selected_names(self, analysis: str):
    """Respect the exact measurement/angle selection for individual cases."""
    if getattr(self, "mode", None) == "individual":
        mapping = getattr(self, "individual_measurements", None)
        if mapping is not None and analysis in mapping:
            return list(mapping[analysis])
    return _ORIGINAL_SELECTED_NAMES(self, analysis)


def _prepare_individual_state(self) -> None:
    self.mode = "individual"
    self.active_study_id = None
    self.active_study_name = ""
    self.study_protocol = None
    if not hasattr(self, "individual_measurements"):
        self.individual_measurements = {}


def _start_individual(self) -> None:
    """Enter the individual flow through selection, never directly through tracing."""
    _prepare_individual_state(self)
    self.open_analysis_selector()


def _start_workspace(self) -> None:
    try:
        try:
            self.new_case(reset_view=False)
        except TypeError:
            self.new_case()
        self.build_workspace()
        self.apply_analysis_selection()
    except Exception as exc:
        messagebox.showerror(
            "Yornis",
            _tr(
                self,
                f"No fue posible abrir el trazado individual.\n\n{exc}",
                f"The individual tracing workspace could not be opened.\n\n{exc}",
            ),
            parent=self,
        )
        try:
            self.show_home()
        except Exception:
            pass


def _open_individual_selector(self) -> None:
    """Choose one or more analyses and the exact measurements/angles before tracing."""
    _prepare_individual_state(self)

    host = workflow.HOST or {}
    analyses = list(host.get("ANALYSES") or [])
    if not analyses:
        messagebox.showerror(
            "Yornis",
            _tr(
                self,
                "No se encontró el catálogo de análisis cefalométricos.",
                "The cephalometric analysis catalog could not be found.",
            ),
            parent=self,
        )
        return

    previous_analyses = set(getattr(self, "selected_analyses", set()) or set())
    previous_measurements = getattr(self, "individual_measurements", {}) or {}

    selected = {
        analysis: set(previous_measurements.get(analysis) or workflow.measure_choices(analysis))
        for analysis in analyses
    }
    analysis_vars = {
        analysis: tk.BooleanVar(value=analysis in previous_analyses)
        for analysis in analyses
    }

    dialog = tk.Toplevel(self)
    dialog.title(_tr(self, "Yornis · Caso individual · Selección", "Yornis · Individual case · Selection"))
    dialog.geometry("980x760")
    dialog.minsize(860, 650)
    dialog.transient(self)
    dialog.grab_set()

    root = ttk.Frame(dialog, padding=(20, 18))
    root.pack(fill="both", expand=True)

    ttk.Label(
        root,
        text=_tr(self, "1 · Elige análisis y medidas/ángulos", "1 · Choose analyses and measurements/angles"),
        style="Title.TLabel",
    ).pack(anchor="w")
    ttk.Label(
        root,
        text=_tr(
            self,
            "Puedes seleccionar uno o varios análisis. Después elige exactamente qué ángulos o medidas quieres obtener. Yornis pedirá sólo los puntos necesarios.",
            "Select one or more analyses, then choose the exact angles or measurements you want. Yornis will request only the required landmarks.",
        ),
        style="Subtitle.TLabel",
        wraplength=900,
        justify="left",
    ).pack(anchor="w", pady=(5, 14))

    body = ttk.Frame(root)
    body.pack(fill="both", expand=True)

    canvas = tk.Canvas(body, highlightthickness=0)
    scrollbar = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
    inner = ttk.Frame(canvas)
    window_id = canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window_id, width=max(1, e.width)))

    count_vars = {analysis: tk.StringVar() for analysis in analyses}

    def refresh_count(analysis: str) -> None:
        total = len(workflow.measure_choices(analysis))
        chosen = len(selected[analysis])
        count_vars[analysis].set(
            _tr(self, f"{chosen} de {total} seleccionadas", f"{chosen} of {total} selected")
        )

    def choose_measurements(analysis: str) -> None:
        choices = workflow.measure_choices(analysis)
        popup = tk.Toplevel(dialog)
        popup.title(analysis + " · " + _tr(self, "Medidas / ángulos", "Measurements / angles"))
        popup.geometry("760x650")
        popup.transient(dialog)
        popup.grab_set()

        outer = ttk.Frame(popup, padding=16)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text=analysis, style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text=_tr(
                self,
                "Marca únicamente las medidas o ángulos que deseas calcular.",
                "Select only the measurements or angles you want to calculate.",
            ),
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 10))

        area = ttk.Frame(outer)
        area.pack(fill="both", expand=True)
        c = tk.Canvas(area, highlightthickness=0)
        sb = ttk.Scrollbar(area, orient="vertical", command=c.yview)
        checks = ttk.Frame(c)
        wid = c.create_window((0, 0), window=checks, anchor="nw")
        c.configure(yscrollcommand=sb.set)
        c.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        checks.bind("<Configure>", lambda _e: c.configure(scrollregion=c.bbox("all")))
        c.bind("<Configure>", lambda e: c.itemconfigure(wid, width=max(1, e.width)))

        variables = {
            name: tk.BooleanVar(value=name in selected[analysis])
            for name in choices
        }
        for name in choices:
            ttk.Checkbutton(checks, text=name, variable=variables[name]).pack(
                anchor="w", fill="x", padx=4, pady=2
            )

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=(12, 0))

        def mark_all(value: bool) -> None:
            for var in variables.values():
                var.set(value)

        def accept() -> None:
            chosen = {name for name, var in variables.items() if var.get()}
            if not chosen:
                messagebox.showwarning(
                    "Yornis",
                    _tr(
                        self,
                        "Selecciona al menos una medida o ángulo para este análisis.",
                        "Select at least one measurement or angle for this analysis.",
                    ),
                    parent=popup,
                )
                return
            selected[analysis] = chosen
            analysis_vars[analysis].set(True)
            refresh_count(analysis)
            popup.destroy()

        ttk.Button(actions, text=_tr(self, "Seleccionar todo", "Select all"), command=lambda: mark_all(True)).pack(side="left")
        ttk.Button(actions, text=_tr(self, "Limpiar", "Clear"), command=lambda: mark_all(False)).pack(side="left", padx=6)
        ttk.Button(actions, text=_tr(self, "Aceptar", "Accept"), style="Accent.TButton", command=accept).pack(side="right")

    for row_index, analysis in enumerate(analyses):
        row = ttk.Frame(inner, padding=(8, 7))
        row.grid(row=row_index, column=0, sticky="ew", pady=2)
        inner.grid_columnconfigure(0, weight=1)
        ttk.Checkbutton(row, text=analysis, variable=analysis_vars[analysis]).pack(side="left")
        ttk.Label(row, textvariable=count_vars[analysis], style="Muted.TLabel").pack(side="left", padx=(14, 8))
        ttk.Button(
            row,
            text=_tr(self, "Elegir medidas / ángulos…", "Choose measurements / angles…"),
            command=lambda a=analysis: choose_measurements(a),
        ).pack(side="right")
        refresh_count(analysis)

    footer = ttk.Frame(root)
    footer.pack(fill="x", pady=(14, 0))

    def cancel() -> None:
        dialog.destroy()

    def continue_to_points() -> None:
        chosen_analyses = [a for a in analyses if analysis_vars[a].get()]
        if not chosen_analyses:
            messagebox.showwarning(
                "Yornis",
                _tr(self, "Selecciona al menos un análisis.", "Select at least one analysis."),
                parent=dialog,
            )
            return

        empty = [a for a in chosen_analyses if not selected[a]]
        if empty:
            messagebox.showwarning(
                "Yornis",
                _tr(
                    self,
                    "Cada análisis seleccionado debe tener al menos una medida o ángulo.",
                    "Each selected analysis must contain at least one measurement or angle.",
                ),
                parent=dialog,
            )
            return

        self.selected_analyses = set(chosen_analyses)
        self.individual_measurements = {
            analysis: sorted(selected[analysis])
            for analysis in chosen_analyses
        }
        dialog.destroy()
        _start_workspace(self)

    ttk.Button(footer, text=_tr(self, "Cancelar", "Cancel"), command=cancel).pack(side="left")
    ttk.Label(
        footer,
        text=_tr(
            self,
            "2 · Continuar abre el trazado y la colocación guiada de puntos.",
            "2 · Continue opens tracing and guided landmark placement.",
        ),
        style="Caption.TLabel",
    ).pack(side="left", padx=14)
    ttk.Button(
        footer,
        text=_tr(self, "Continuar a puntos  →", "Continue to landmarks  →"),
        style="Accent.TButton",
        command=continue_to_points,
    ).pack(side="right")


def install(classic_class) -> None:
    """Install the individual selector hotfix without changing research behavior."""
    if getattr(classic_class, "_yornis_individual_selector_v016", False):
        return

    original_open_selector = classic_class.open_analysis_selector
    original_calculate = classic_class.calculate

    def open_analysis_selector(self):
        if getattr(self, "mode", None) == "individual":
            return _open_individual_selector(self)
        return original_open_selector(self)

    def calculate(self):
        original_calculate(self)
        if getattr(self, "mode", None) != "individual":
            return

        mapping = getattr(self, "individual_measurements", {}) or {}
        if not mapping:
            return

        keep = {
            (analysis, name)
            for analysis, names in mapping.items()
            for name in names
        }
        try:
            self.results = [
                result
                for result in self.results
                if (result.get("analysis"), result.get("name")) in keep
            ]
        except Exception:
            return

        for renderer in ("render_results", "render_qc", "render_summary"):
            method = getattr(self, renderer, None)
            if callable(method):
                try:
                    method()
                except Exception:
                    pass

    workflow.selected_names = _selected_names
    classic_class.start_individual = _start_individual
    classic_class.open_analysis_selector = open_analysis_selector
    classic_class.calculate = calculate
    classic_class._yornis_individual_selector_v016 = True
