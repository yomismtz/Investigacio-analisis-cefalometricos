from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from research_db import ResearchDB
import research_protocol

_INSTALLED = False


def _ensure_profile_side_column(db: ResearchDB) -> None:
    with db.connect() as con:
        cols = {r[1] for r in con.execute("PRAGMA table_info(cases)").fetchall()}
        if "profile_side" not in cols:
            con.execute("ALTER TABLE cases ADD COLUMN profile_side TEXT DEFAULT ''")


def _profile_side(db: ResearchDB, case_id: int | None) -> str:
    if not case_id:
        return ""
    _ensure_profile_side_column(db)
    with db.connect() as con:
        row = con.execute("SELECT profile_side FROM cases WHERE id=?", (case_id,)).fetchone()
    value = (row[0] if row else "") or ""
    return value if value in {"right", "left"} else ""


def _set_profile_side(db: ResearchDB, case_id: int, side: str) -> None:
    if side not in {"", "right", "left"}:
        raise ValueError(side)
    _ensure_profile_side_column(db)
    row = db.case(case_id)
    if not row:
        raise KeyError(case_id)
    with db.connect() as con:
        con.execute("UPDATE cases SET profile_side=?,updated_at=datetime('now') WHERE id=?", (side, case_id))
    try:
        db.audit(int(row["study_id"]), "profile_side_changed", case_id=case_id, profile_side=side)
    except Exception:
        pass


def install(workspace_class) -> None:
    """Install v0.15.1 clinical-safety integration patches.

    The geometric engine remains the single source of truth. This patch only
    prevents silent orientation assumptions in Research mode and persists the
    explicit face/profile direction per case.
    """
    global _INSTALLED
    if _INSTALLED:
        return

    # Schema migration happens before ResearchWorkspace is instantiated.
    old_init_schema = ResearchDB._init_schema
    def init_schema(self):
        old_init_schema(self)
        _ensure_profile_side_column(self)
    ResearchDB._init_schema = init_schema
    ResearchDB.profile_side = lambda self, case_id: _profile_side(self, case_id)
    ResearchDB.set_profile_side = lambda self, case_id, side: _set_profile_side(self, case_id, side)

    old_build_trace = workspace_class._build_trace
    def build_trace(self):
        old_build_trace(self)
        self.profile_side_var = tk.StringVar(value="")
        box = ttk.LabelFrame(self.trace_tab, text=self.T("Orientación radiográfica", "Radiographic orientation"), padding=5)
        box.pack(fill="x", padx=5, pady=(0, 4), before=self.trace_tab.winfo_children()[0] if self.trace_tab.winfo_children() else None)
        ttk.Label(box, text=self.T("El perfil mira a:", "Profile faces:")).pack(side="left", padx=(3, 5))
        cb = ttk.Combobox(box, textvariable=self.profile_side_var, state="readonly", width=18,
                          values=["", "right", "left"])
        cb.pack(side="left")
        self.profile_side_hint = ttk.Label(box, text=self.T("Obligatorio para conservar signos anatómicos.", "Required to preserve anatomical signs."))
        self.profile_side_hint.pack(side="left", padx=8)
        def changed(_event=None):
            if self.case_id:
                self.db.set_profile_side(self.case_id, self.profile_side_var.get())
                self.calculate_preview()
        cb.bind("<<ComboboxSelected>>", changed)
        self.profile_side_combo = cb
    workspace_class._build_trace = build_trace

    old_open = workspace_class.open_selected_case
    def open_selected_case(self, *args, **kwargs):
        out = old_open(self, *args, **kwargs)
        if hasattr(self, "profile_side_var"):
            self.profile_side_var.set(self.db.profile_side(self.case_id) if self.case_id else "")
            self.calculate_preview()
        return out
    workspace_class.open_selected_case = open_selected_case

    def calculate_preview(self):
        self.results_tree.delete(*self.results_tree.get_children())
        if not self.case_id:
            return []
        c = self.db.case(self.case_id)
        side = self.db.profile_side(self.case_id)
        keys = self.protocol.get("selected_variables", [])
        if not side:
            results = []
            for v in research_protocol.selected_variables(keys):
                results.append({
                    "analysis": v.analysis, "measurement": v.name, "value": None,
                    "unit": v.unit,
                    "reference": research_protocol.reference_for(v, c["sex"], c["age"]),
                    "interpretation": self.T("Selecciona si el perfil mira a derecha o izquierda antes de calcular.",
                                               "Select whether the profile faces right or left before calculating."),
                    "missing": [],
                })
        else:
            results = research_protocol.compute_selected(
                keys, self.points, self.mm_per_px, side=side, sex=c["sex"], age=c["age"]
            )
        groups = {}
        for r in results:
            a = r["analysis"]
            groups.setdefault(a, self.results_tree.insert("", "end", text=a, open=True, values=("", "")))
            val = "—" if r["value"] is None else f"{r['value']:.2f}"
            self.results_tree.insert(groups[a], "end", text=r["measurement"], values=(val, r["unit"]))
        if hasattr(self, "profile_side_hint"):
            self.profile_side_hint.config(text=(
                self.T("✓ Orientación guardada para este caso.", "✓ Orientation saved for this case.") if side else
                self.T("⚠ Selecciona orientación: no se asumirá una por defecto.", "⚠ Select orientation: no default will be assumed.")
            ))
        return results
    workspace_class.calculate_preview = calculate_preview

    _INSTALLED = True
