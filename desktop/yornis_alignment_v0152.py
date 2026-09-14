from __future__ import annotations

from datetime import datetime

import classic_engine as engine
import yornis_cervical_v0152 as cervical

ALIGNMENT_ANALYSIS = "Postura vertebral vertical C2–C4"
ALIGNMENT_MEASUREMENT = "Alineación posterior C2–C4"
ALIGNMENT_REFERENCE = (
    "Clasificación cualitativa guiada de la alineación posterior/distal C2–C4. "
    "Categorías: lordosis normal, rectificación, cifosis e hiperlordosis. "
    "La guía aportada no define umbrales angulares universales, por lo que Yornis no fuerza una clasificación automática."
)
ALIGNMENT_CODEBOOK = {
    "Lordosis normal": 1,
    "Rectificación": 2,
    "Cifosis": 3,
    "Hiperlordosis": 4,
}

_ENGINE_PATCHED = False
_RESEARCH_INSTALLED = False


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def patch_engine() -> None:
    """Register the C2-C4 posture analysis as an explicit special analysis.

    It is intentionally not added as an automatic numeric Measurement because
    the supplied classification guide is qualitative and does not provide a
    validated universal angular threshold for its four categories.
    """
    global _ENGINE_PATCHED
    if _ENGINE_PATCHED:
        return
    if ALIGNMENT_ANALYSIS not in engine.ANALYSES:
        engine.ANALYSES.append(ALIGNMENT_ANALYSIS)
    _ENGINE_PATCHED = True


patch_engine()


def classify_alignment(label: str) -> dict:
    label = (label or "").strip()
    if label not in ALIGNMENT_CODEBOOK:
        return {
            "code": None,
            "label": "No concluyente",
            "interpretation": "Selecciona una categoría sólo cuando C2, C3 y C4 sean visibles y evaluables.",
        }
    notes = {
        "Lordosis normal": "Patrón lordótico conservado según la alineación posterior/distal visible de C2–C4.",
        "Rectificación": "Disminución o pérdida visual de la curvatura lordótica en el segmento C2–C4.",
        "Cifosis": "Inversión visual del patrón lordótico en el segmento C2–C4. Confirmar posición radiográfica y trazado.",
        "Hiperlordosis": "Curvatura lordótica visualmente aumentada en el segmento C2–C4.",
    }
    return {
        "code": ALIGNMENT_CODEBOOK[label],
        "label": label,
        "interpretation": notes[label],
    }


def _ensure_columns(db) -> None:
    cervical._ensure_table(db)
    with db.connect() as con:
        cols = {r[1] for r in con.execute("PRAGMA table_info(cervical_assessments)").fetchall()}
        if "alignment_code" not in cols:
            con.execute("ALTER TABLE cervical_assessments ADD COLUMN alignment_code INTEGER")
        if "alignment_class" not in cols:
            con.execute("ALTER TABLE cervical_assessments ADD COLUMN alignment_class TEXT DEFAULT ''")
        if "alignment_notes" not in cols:
            con.execute("ALTER TABLE cervical_assessments ADD COLUMN alignment_notes TEXT DEFAULT ''")


def _protocol_version(workspace) -> int:
    try:
        return int(getattr(workspace, "protocol_version", 0) or 0)
    except Exception:
        return 0


def _save_alignment(workspace, result: dict, notes: str = "") -> None:
    if not getattr(workspace, "case_id", None) or not hasattr(workspace, "db"):
        return
    if result.get("code") is None:
        return
    db = workspace.db
    _ensure_columns(db)
    version = _protocol_version(workspace)
    interpretation = result["interpretation"]
    if notes.strip():
        interpretation += " Observaciones: " + notes.strip()
    with db.connect() as con:
        con.execute(
            "INSERT INTO cervical_assessments(case_id,protocol_version,alignment_code,alignment_class,alignment_notes,updated_at) "
            "VALUES(?,?,?,?,?,?) "
            "ON CONFLICT(case_id,protocol_version) DO UPDATE SET "
            "alignment_code=excluded.alignment_code,alignment_class=excluded.alignment_class," 
            "alignment_notes=excluded.alignment_notes,updated_at=excluded.updated_at",
            (workspace.case_id, version, int(result["code"]), result["label"], notes.strip(), _now()),
        )
        con.execute(
            "DELETE FROM results WHERE case_id=? AND protocol_version=? AND analysis=? AND measurement=?",
            (workspace.case_id, version, ALIGNMENT_ANALYSIS, ALIGNMENT_MEASUREMENT),
        )
        con.execute(
            "INSERT INTO results(case_id,protocol_version,analysis,measurement,value,unit,reference_text,interpretation,version,created_at) "
            "VALUES(?,?,?,?,?,?,?,?,1,?)",
            (
                workspace.case_id,
                version,
                ALIGNMENT_ANALYSIS,
                ALIGNMENT_MEASUREMENT,
                float(result["code"]),
                "categoría",
                ALIGNMENT_REFERENCE + " Código: 1=Lordosis normal; 2=Rectificación; 3=Cifosis; 4=Hiperlordosis.",
                interpretation,
                _now(),
            ),
        )
    try:
        row = db.case(workspace.case_id)
        if row:
            db.audit(
                int(row["study_id"]),
                "c2c4_alignment_assessed",
                case_id=workspace.case_id,
                code=result["code"],
                classification=result["label"],
                notes=notes.strip(),
            )
    except Exception:
        pass


def _open_alignment_dialog(root, workspace=None) -> None:
    import tkinter as tk
    from tkinter import messagebox, ttk

    win = tk.Toplevel(root)
    win.title("Yornis · Postura vertebral vertical C2–C4")
    win.transient(root)
    win.geometry("760x610")
    try:
        from yornis_display_v0152 import apply_display_quality
        apply_display_quality(win, launcher=False)
    except Exception:
        pass

    outer = ttk.Frame(win, padding=18)
    outer.pack(fill="both", expand=True)
    ttk.Label(
        outer,
        text="Alineación vertebral posterior/distal C2–C4",
        font=("Segoe UI", 15, "bold"),
    ).pack(anchor="w")
    ttk.Label(
        outer,
        text=(
            "Evalúa visualmente la continuidad de C2, C3 y C4 en la radiografía lateral. "
            "La clasificación se guarda como resultado cualitativo y auditado."
        ),
        wraplength=700,
    ).pack(anchor="w", pady=(4, 12))

    quality = ttk.LabelFrame(outer, text="Control previo", padding=10)
    quality.pack(fill="x")
    visible_vars = []
    for text in (
        "C2 es visible y su borde posterior/distal puede evaluarse",
        "C3 es visible y su borde posterior/distal puede evaluarse",
        "C4 es visible y su borde posterior/distal puede evaluarse",
    ):
        v = tk.BooleanVar(value=False)
        visible_vars.append(v)
        ttk.Checkbutton(quality, text=text, variable=v).pack(anchor="w", pady=3)

    ttk.Label(
        quality,
        text="Si alguna vértebra no es evaluable, registra el caso como no concluyente o exclúyelo según tu protocolo.",
        wraplength=680,
    ).pack(anchor="w", pady=(6, 0))

    body = ttk.LabelFrame(outer, text="Clasificación", padding=12)
    body.pack(fill="x", pady=12)
    choice = tk.StringVar(value="")
    values = ["", "Lordosis normal", "Rectificación", "Cifosis", "Hiperlordosis"]
    ttk.Label(body, text="Patrón observado:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=6)
    combo = ttk.Combobox(body, textvariable=choice, state="readonly", values=values, width=28)
    combo.grid(row=0, column=1, sticky="ew", pady=6)
    body.columnconfigure(1, weight=1)

    ttk.Label(body, text="Observaciones:").grid(row=1, column=0, sticky="nw", padx=(0, 10), pady=6)
    notes = tk.Text(body, height=5, wrap="word")
    notes.grid(row=1, column=1, sticky="nsew", pady=6)

    result_var = tk.StringVar(value="Selecciona una categoría para ver su interpretación.")
    ttk.Label(outer, textvariable=result_var, wraplength=700, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(2, 10))

    def preview(_event=None):
        result = classify_alignment(choice.get())
        if result["code"] is None:
            result_var.set(result["interpretation"])
        else:
            result_var.set(f"{result['label']} · {result['interpretation']}")

    combo.bind("<<ComboboxSelected>>", preview)

    def save():
        if not all(v.get() for v in visible_vars):
            messagebox.showwarning(
                "Yornis",
                "C2, C3 y C4 deben ser visibles/evaluables antes de guardar esta clasificación.",
                parent=win,
            )
            return
        result = classify_alignment(choice.get())
        if result["code"] is None:
            messagebox.showwarning("Yornis", "Selecciona una categoría de alineación.", parent=win)
            return
        if workspace is not None:
            _save_alignment(workspace, result, notes.get("1.0", "end").strip())
        result_var.set(f"✓ Guardado: {result['label']} · {result['interpretation']}")

    buttons = ttk.Frame(outer)
    buttons.pack(fill="x", pady=(4, 0))
    ttk.Button(buttons, text="Guardar evaluación", command=save).pack(side="left")
    ttk.Button(buttons, text="Cerrar", command=win.destroy).pack(side="right")

    ttk.Separator(outer).pack(fill="x", pady=14)
    ttk.Label(
        outer,
        text="Nota metodológica",
        font=("Segoe UI", 10, "bold"),
    ).pack(anchor="w")
    ttk.Label(
        outer,
        text=(
            "Esta herramienta reproduce la clasificación cualitativa mostrada en tu guía. "
            "No asigna la categoría por un umbral numérico inventado. La lordosis angular C1–C7 se calcula por separado en el menú CERVICAL."
        ),
        wraplength=700,
    ).pack(anchor="w")


def _find_cervical_menu(root):
    import tkinter as tk
    try:
        menu_name = root.cget("menu")
        menubar = root.nametowidget(menu_name) if menu_name else None
    except Exception:
        return None
    if not isinstance(menubar, tk.Menu):
        return None
    try:
        end = menubar.index("end")
        if end is None:
            return None
        for i in range(end + 1):
            if menubar.type(i) == "cascade" and str(menubar.entrycget(i, "label")).upper() == "CERVICAL":
                submenu_name = menubar.entrycget(i, "menu")
                return root.nametowidget(submenu_name)
    except Exception:
        return None
    return None


def add_alignment_menu(root, workspace=None) -> None:
    if getattr(root, "_yornis_alignment_menu_v0152", False):
        return
    cervical.add_cervical_menu(root, workspace)
    menu = _find_cervical_menu(root)
    if menu is None:
        return
    try:
        menu.insert_separator(2)
        menu.insert_command(
            3,
            label="Postura vertebral vertical C2–C4",
            command=lambda: _open_alignment_dialog(root, workspace),
        )
    except Exception:
        menu.add_separator()
        menu.add_command(
            label="Postura vertebral vertical C2–C4",
            command=lambda: _open_alignment_dialog(root, workspace),
        )
    root._yornis_alignment_menu_v0152 = True


def install_research(workspace_class) -> None:
    global _RESEARCH_INSTALLED
    if _RESEARCH_INSTALLED:
        return
    old_init = workspace_class.__init__

    def init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        try:
            _ensure_columns(self.db)
        except Exception:
            pass
        try:
            add_alignment_menu(self, self)
        except Exception:
            pass

    workspace_class.__init__ = init
    _RESEARCH_INSTALLED = True


def install_individual(classic_class) -> None:
    if getattr(classic_class, "_yornis_alignment_v0152", False):
        return
    old_init = classic_class.__init__

    def init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        try:
            add_alignment_menu(self, self)
        except Exception:
            pass

    classic_class.__init__ = init
    classic_class._yornis_alignment_v0152 = True
