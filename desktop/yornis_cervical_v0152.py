from __future__ import annotations

import json
import math
import sqlite3
from copy import copy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import classic_engine as engine

POSTURE_ANALYSIS = "Postura cervical C1–C7"
POSTURE_MEASUREMENT = "Lordosis cervical C1–C7"
CVM_ANALYSIS = "CVM C2–C4"
CVM_MEASUREMENT = "Estadio CVM Baccetti"

LORDOSIS_POINTS = ("C1 tub post", "C1 tub ant", "C7 inf post", "C7 inf ant")
LORDOSIS_REFERENCE = "Media 40°; rango de referencia 35–45°. Interpretar con la técnica y posición radiográfica."
CVM_REFERENCE = "Baccetti–Franchi–McNamara: CS1–CS6 por morfología de C2–C4; no equivale a una edad cronológica exacta."

_ENGINE_PATCHED = False
_RESEARCH_INSTALLED = False


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _norm(points: dict[str, tuple[float, float]], side: str) -> dict[str, tuple[float, float]]:
    if side == "left":
        return {k: (-float(x), float(y)) for k, (x, y) in points.items()}
    return {k: (float(x), float(y)) for k, (x, y) in points.items()}


def _vector(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return b[0] - a[0], b[1] - a[1]


def _signed_angle(v1: tuple[float, float], v2: tuple[float, float]) -> float:
    d = v1[0] * v2[0] + v1[1] * v2[1]
    c = v1[0] * v2[1] - v1[1] * v2[0]
    if math.hypot(*v1) < 1e-9 or math.hypot(*v2) < 1e-9:
        raise ValueError("Línea cervical de longitud cero")
    return math.degrees(math.atan2(c, d))


def cervical_lordosis_angle(points: dict[str, tuple[float, float]], side: str = "right") -> float:
    """Signed C1–C7 cervical curve angle.

    Uses the C1 line through the posterior/anterior atlas tubercles and the
    inferior endplate line of C7. Coordinates are normalized so mirrored
    radiographs preserve the same anatomical sign.
    """
    p = _norm(points, side)
    missing = [name for name in LORDOSIS_POINTS if name not in p]
    if missing:
        raise KeyError(", ".join(missing))
    c1 = _vector(p["C1 tub post"], p["C1 tub ant"])
    c7 = _vector(p["C7 inf post"], p["C7 inf ant"])
    # Directed C7 -> C1 rotation: positive in the conventional lordotic pattern.
    angle = _signed_angle(c7, c1)
    while angle > 90:
        angle -= 180
    while angle < -90:
        angle += 180
    return float(angle)


def posture_classification(angle: float) -> tuple[str, str]:
    if angle < 0:
        return (
            "Cifosis / inversión de la curva",
            "El signo indica inversión respecto a la orientación lordótica esperada. Confirmar técnica, postura y trazado.",
        )
    if angle < 35:
        return (
            "Lordosis disminuida / compatible con rectificación",
            "Valor por debajo del rango de referencia 35–45°. La posición durante la radiografía puede reducir la lordosis aparente.",
        )
    if angle <= 45:
        return (
            "Lordosis dentro del rango de referencia",
            "Rango de referencia usado por Yornis: 35–45°, media aproximada 40°.",
        )
    return (
        "Hiperlordosis",
        "Valor por encima del rango de referencia de 45°. Interpretar con el resto de la evaluación cervical.",
    )


def classify_cvm(c2_concavity: str, c3_concavity: str, c4_concavity: str, c3_shape: str, c4_shape: str) -> dict:
    """Classify Baccetti modified CVM using explicit morphology choices.

    Concavity: 'no'/'si'. Shapes: 'trapezoidal', 'horizontal', 'cuadrada', 'vertical'.
    Inconsistent or incomplete combinations return stage=None instead of guessing.
    """
    cc = [c2_concavity, c3_concavity, c4_concavity]
    if any(v not in {"si", "no"} for v in cc):
        return {"stage": None, "phase": "No concluyente", "timing": "Falta definir la concavidad inferior de C2–C4.", "reason": "Datos incompletos"}
    if c3_shape not in {"trapezoidal", "horizontal", "cuadrada", "vertical"} or c4_shape not in {"trapezoidal", "horizontal", "cuadrada", "vertical"}:
        return {"stage": None, "phase": "No concluyente", "timing": "Falta definir la forma de C3 y C4.", "reason": "Datos incompletos"}

    conc = tuple(v == "si" for v in cc)
    shapes = {c3_shape, c4_shape}

    if conc == (False, False, False) and shapes == {"trapezoidal"}:
        return {"stage": 1, "phase": "Prepuberal", "timing": "El pico de crecimiento mandibular no se espera antes de ~2 años.", "reason": "Bordes inferiores planos; C3 y C4 trapezoidales."}
    if conc == (True, False, False) and shapes == {"trapezoidal"}:
        return {"stage": 2, "phase": "Prepuberal", "timing": "El pico de crecimiento mandibular suele aproximarse dentro de ~1 año.", "reason": "Concavidad en C2; C3 y C4 trapezoidales."}
    if conc == (True, True, False) and shapes.issubset({"trapezoidal", "horizontal"}):
        return {"stage": 3, "phase": "Circumpuberal", "timing": "El pico de crecimiento mandibular ocurre en el intervalo CS3–CS4.", "reason": "Concavidad en C2 y C3; C3/C4 trapezoidales u horizontales."}
    if conc == (True, True, True) and shapes == {"horizontal"}:
        return {"stage": 4, "phase": "Circumpuberal", "timing": "El pico de crecimiento mandibular ocurrió aproximadamente 1–2 años antes.", "reason": "Concavidad en C2–C4; C3 y C4 rectangulares horizontales."}
    if conc == (True, True, True) and "cuadrada" in shapes and shapes.issubset({"horizontal", "cuadrada"}):
        return {"stage": 5, "phase": "Postpuberal", "timing": "El pico de crecimiento mandibular terminó al menos ~1 año antes.", "reason": "Concavidad en C2–C4; al menos C3 o C4 cuadrada."}
    if conc == (True, True, True) and "vertical" in shapes and shapes.issubset({"cuadrada", "vertical"}):
        return {"stage": 6, "phase": "Postpuberal", "timing": "El estadio se registra al menos ~2 años después del pico de crecimiento.", "reason": "Concavidad en C2–C4; al menos C3 o C4 rectangular vertical."}

    return {
        "stage": None,
        "phase": "No concluyente",
        "timing": "La combinación morfológica no encaja de forma inequívoca en CS1–CS6; revisar el contorno y no forzar una etapa.",
        "reason": "Combinación morfológica discordante",
    }


def _clone_measurement() -> object:
    if not getattr(engine, "MEASUREMENTS", None):
        raise RuntimeError("Motor cefalométrico sin mediciones")
    m = copy(engine.MEASUREMENTS[0])
    attrs = {
        "analysis": POSTURE_ANALYSIS,
        "name": POSTURE_MEASUREMENT,
        "pts": LORDOSIS_POINTS,
        "unit": "°",
        "kind": "yornis_cervical_lordosis",
        "norm_text": LORDOSIS_REFERENCE,
        "reference": LORDOSIS_REFERENCE,
        "lo": 35.0,
        "hi": 45.0,
    }
    for key, value in attrs.items():
        try:
            object.__setattr__(m, key, value)
        except Exception:
            try:
                setattr(m, key, value)
            except Exception:
                pass
    return m


def _point_help_value(es: str, en: str):
    try:
        sample = next(iter(engine.POINT_HELP.values()))
    except Exception:
        sample = ""
    if isinstance(sample, dict):
        return {"es": es, "en": en}
    if isinstance(sample, tuple):
        if len(sample) >= 2:
            return (es, en) + tuple(sample[2:])
        return (es,)
    if isinstance(sample, list):
        return [es, en]
    return es


def patch_engine() -> None:
    global _ENGINE_PATCHED
    if _ENGINE_PATCHED:
        return
    if POSTURE_ANALYSIS not in engine.ANALYSES:
        engine.ANALYSES.append(POSTURE_ANALYSIS)
    keys = {(getattr(m, "analysis", ""), getattr(m, "name", "")) for m in engine.MEASUREMENTS}
    if (POSTURE_ANALYSIS, POSTURE_MEASUREMENT) not in keys:
        engine.MEASUREMENTS.append(_clone_measurement())

    helpers = {
        "C1 tub post": ("Tubérculo posterior del atlas (C1), centro del punto cortical posterior usado para la línea de C1.", "Posterior atlas (C1) tubercle."),
        "C1 tub ant": ("Tubérculo anterior del atlas (C1), centro del punto cortical anterior usado para la línea de C1.", "Anterior atlas (C1) tubercle."),
        "C7 inf post": ("Esquina posteroinferior del cuerpo de C7 sobre la placa terminal inferior.", "Posteroinferior C7 body corner on the inferior endplate."),
        "C7 inf ant": ("Esquina anteroinferior del cuerpo de C7 sobre la placa terminal inferior.", "Anteroinferior C7 body corner on the inferior endplate."),
    }
    for name, (es, en) in helpers.items():
        if name not in engine.POINT_HELP:
            engine.POINT_HELP[name] = _point_help_value(es, en)

    original_compute = engine.compute

    def compute(measurement, points, mm_per_px, side="right"):
        if getattr(measurement, "analysis", "") == POSTURE_ANALYSIS and getattr(measurement, "name", "") == POSTURE_MEASUREMENT:
            return cervical_lordosis_angle(points, side)
        return original_compute(measurement, points, mm_per_px, side)

    engine.compute = compute
    _ENGINE_PATCHED = True


patch_engine()


def _ensure_table(db) -> None:
    with db.connect() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS cervical_assessments (
                id INTEGER PRIMARY KEY,
                case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                protocol_version INTEGER NOT NULL DEFAULT 0,
                lordosis_angle REAL,
                posture_class TEXT DEFAULT '',
                cvm_stage INTEGER,
                cvm_phase TEXT DEFAULT '',
                features_json TEXT DEFAULT '{}',
                updated_at TEXT NOT NULL,
                UNIQUE(case_id, protocol_version)
            );
            """
        )


def _case_protocol_version(workspace) -> int:
    try:
        return int(getattr(workspace, "protocol_version", 0) or 0)
    except Exception:
        return 0


def _save_cvm(workspace, result: dict, features: dict) -> None:
    if not getattr(workspace, "case_id", None) or not hasattr(workspace, "db"):
        return
    db = workspace.db
    _ensure_table(db)
    version = _case_protocol_version(workspace)
    with db.connect() as con:
        con.execute(
            "INSERT INTO cervical_assessments(case_id,protocol_version,cvm_stage,cvm_phase,features_json,updated_at) VALUES(?,?,?,?,?,?) "
            "ON CONFLICT(case_id,protocol_version) DO UPDATE SET cvm_stage=excluded.cvm_stage,cvm_phase=excluded.cvm_phase,features_json=excluded.features_json,updated_at=excluded.updated_at",
            (workspace.case_id, version, result.get("stage"), result.get("phase", ""), json.dumps(features, ensure_ascii=False), _now()),
        )
        con.execute("DELETE FROM results WHERE case_id=? AND protocol_version=? AND analysis=? AND measurement=?", (workspace.case_id, version, CVM_ANALYSIS, CVM_MEASUREMENT))
        if result.get("stage"):
            con.execute(
                "INSERT INTO results(case_id,protocol_version,analysis,measurement,value,unit,reference_text,interpretation,version,created_at) VALUES(?,?,?,?,?,?,?,?,1,?)",
                (workspace.case_id, version, CVM_ANALYSIS, CVM_MEASUREMENT, float(result["stage"]), "CS", CVM_REFERENCE, f"{result['phase']}. {result['timing']}", _now()),
            )
    try:
        row = db.case(workspace.case_id)
        if row:
            db.audit(int(row["study_id"]), "cvm_assessed", case_id=workspace.case_id, stage=result.get("stage"), phase=result.get("phase"), features=features)
    except Exception:
        pass


def _save_posture(workspace, angle: float) -> None:
    if not getattr(workspace, "case_id", None) or not hasattr(workspace, "db"):
        return
    db = workspace.db
    _ensure_table(db)
    version = _case_protocol_version(workspace)
    label, note = posture_classification(angle)
    with db.connect() as con:
        con.execute(
            "INSERT INTO cervical_assessments(case_id,protocol_version,lordosis_angle,posture_class,updated_at) VALUES(?,?,?,?,?) "
            "ON CONFLICT(case_id,protocol_version) DO UPDATE SET lordosis_angle=excluded.lordosis_angle,posture_class=excluded.posture_class,updated_at=excluded.updated_at",
            (workspace.case_id, version, float(angle), label, _now()),
        )
    try:
        row = db.case(workspace.case_id)
        if row:
            db.audit(int(row["study_id"]), "cervical_posture_assessed", case_id=workspace.case_id, angle=angle, classification=label)
    except Exception:
        pass


def _open_cvm_dialog(root, workspace=None) -> None:
    import tkinter as tk
    from tkinter import ttk, messagebox

    win = tk.Toplevel(root)
    win.title("Yornis · Maduración vertebral cervical (CVM)")
    win.transient(root)
    win.geometry("720x620")
    try:
        from yornis_display_v0152 import apply_display_quality
        apply_display_quality(win, launcher=False)
    except Exception:
        pass

    outer = ttk.Frame(win, padding=18)
    outer.pack(fill="both", expand=True)
    ttk.Label(outer, text="Maduración esquelética cervical · Baccetti CS1–CS6", font=("Segoe UI", 15, "bold")).pack(anchor="w")
    ttk.Label(outer, text="Evalúa C2, C3 y C4. El resultado es un estadio de maduración esquelética; no una edad cronológica exacta en años.", wraplength=650).pack(anchor="w", pady=(4, 14))

    conc_values = ["", "No", "Sí"]
    shape_values = ["", "Trapezoidal", "Rectangular horizontal", "Cuadrada", "Rectangular vertical"]
    vars_ = {}
    grid = ttk.Frame(outer)
    grid.pack(fill="x")
    ttk.Label(grid, text="Característica", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=4, pady=5)
    ttk.Label(grid, text="Selección", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w", padx=4, pady=5)
    rows = [
        ("c2", "Concavidad inferior de C2", conc_values),
        ("c3", "Concavidad inferior de C3", conc_values),
        ("c4", "Concavidad inferior de C4", conc_values),
        ("s3", "Forma del cuerpo de C3", shape_values),
        ("s4", "Forma del cuerpo de C4", shape_values),
    ]
    for r, (key, label, values) in enumerate(rows, 1):
        ttk.Label(grid, text=label).grid(row=r, column=0, sticky="w", padx=4, pady=6)
        v = tk.StringVar(value="")
        vars_[key] = v
        cb = ttk.Combobox(grid, textvariable=v, state="readonly", values=values, width=30)
        cb.grid(row=r, column=1, sticky="ew", padx=4, pady=6)
    grid.columnconfigure(1, weight=1)

    result_var = tk.StringVar(value="Completa la morfología y pulsa Clasificar.")
    detail_var = tk.StringVar(value="")
    box = ttk.LabelFrame(outer, text="Resultado", padding=12)
    box.pack(fill="x", pady=14)
    ttk.Label(box, textvariable=result_var, font=("Segoe UI", 12, "bold"), wraplength=640).pack(anchor="w")
    ttk.Label(box, textvariable=detail_var, wraplength=640).pack(anchor="w", pady=(6, 0))

    def code_yes(value: str) -> str:
        return "si" if value == "Sí" else "no" if value == "No" else ""

    def code_shape(value: str) -> str:
        return {"Trapezoidal": "trapezoidal", "Rectangular horizontal": "horizontal", "Cuadrada": "cuadrada", "Rectangular vertical": "vertical"}.get(value, "")

    def classify():
        features = {
            "c2_concavity": code_yes(vars_["c2"].get()),
            "c3_concavity": code_yes(vars_["c3"].get()),
            "c4_concavity": code_yes(vars_["c4"].get()),
            "c3_shape": code_shape(vars_["s3"].get()),
            "c4_shape": code_shape(vars_["s4"].get()),
        }
        res = classify_cvm(features["c2_concavity"], features["c3_concavity"], features["c4_concavity"], features["c3_shape"], features["c4_shape"])
        if res["stage"]:
            result_var.set(f"CS{res['stage']} · {res['phase']}")
        else:
            result_var.set(res["phase"])
        detail_var.set(f"{res['reason']}\n{res['timing']}")
        if workspace is not None:
            _save_cvm(workspace, res, features)
        return res

    buttons = ttk.Frame(outer)
    buttons.pack(fill="x")
    ttk.Button(buttons, text="Clasificar", command=classify).pack(side="left")
    ttk.Button(buttons, text="Cerrar", command=win.destroy).pack(side="right")
    ttk.Label(outer, text="Referencia: Baccetti, Franchi & McNamara, Seminars in Orthodontics 2005; guía de usuario McNamara & Franchi 2018.", wraplength=650).pack(anchor="w", pady=(14, 0))
    ttk.Label(outer, text="La clasificación debe basarse en la morfología visible. Si hay duda o discordancia, Yornis devuelve ‘No concluyente’ en vez de forzar una etapa.", wraplength=650).pack(anchor="w", pady=(5, 0))


def _open_posture_dialog(root, workspace=None) -> None:
    import tkinter as tk
    from tkinter import ttk, messagebox

    win = tk.Toplevel(root)
    win.title("Yornis · Postura / lordosis cervical")
    win.transient(root)
    win.geometry("720x520")
    try:
        from yornis_display_v0152 import apply_display_quality
        apply_display_quality(win, launcher=False)
    except Exception:
        pass
    outer = ttk.Frame(win, padding=18)
    outer.pack(fill="both", expand=True)
    ttk.Label(outer, text="Postura cervical C1–C7", font=("Segoe UI", 15, "bold")).pack(anchor="w")
    ttk.Label(outer, text="Medición angular entre la línea de C1 (tubérculo posterior–anterior) y la placa terminal inferior de C7. Rango de referencia usado: 35–45°, media ~40°.", wraplength=650).pack(anchor="w", pady=(4, 12))

    status = tk.StringVar(value="Coloca los 4 landmarks de la medición en el trazado y vuelve a abrir este panel.")
    ttk.Label(outer, textvariable=status, wraplength=650, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=8)
    ttk.Label(outer, text="Landmarks: C1 tub post · C1 tub ant · C7 inf post · C7 inf ant", wraplength=650).pack(anchor="w", pady=4)

    if workspace is not None and hasattr(workspace, "points"):
        side = "right"
        try:
            side = workspace.db.profile_side(workspace.case_id) if getattr(workspace, "case_id", None) and hasattr(workspace.db, "profile_side") else getattr(workspace, "face_direction", "right") or "right"
        except Exception:
            side = getattr(workspace, "face_direction", "right") or "right"
        try:
            value = cervical_lordosis_angle(workspace.points, side)
            label, note = posture_classification(value)
            status.set(f"{value:.2f}° · {label}\n{note}")
            _save_posture(workspace, value)
        except KeyError as exc:
            status.set(f"Faltan landmarks: {exc}")
        except Exception as exc:
            status.set(f"No calculable: {exc}")

    ttk.Separator(outer).pack(fill="x", pady=14)
    ttk.Label(outer, text="Importante", font=("Segoe UI", 10, "bold")).pack(anchor="w")
    ttk.Label(outer, text="La postura durante la toma radiográfica puede enderezar la curva cervical. Una lordosis disminuida debe interpretarse junto con la técnica de adquisición y otros hallazgos; Yornis no la usa como diagnóstico aislado.", wraplength=650).pack(anchor="w")
    ttk.Button(outer, text="Cerrar", command=win.destroy).pack(anchor="e", pady=(18, 0))


def add_cervical_menu(root, workspace=None) -> None:
    import tkinter as tk

    try:
        menu_name = root.cget("menu")
        menubar = root.nametowidget(menu_name) if menu_name else None
    except Exception:
        menubar = None
    if menubar is None or not isinstance(menubar, tk.Menu):
        menubar = tk.Menu(root)
        root.config(menu=menubar)
    try:
        end = menubar.index("end")
        if end is not None:
            for i in range(end + 1):
                try:
                    if menubar.type(i) == "cascade" and str(menubar.entrycget(i, "label")).upper() == "CERVICAL":
                        return
                except Exception:
                    pass
    except Exception:
        pass
    cervical = tk.Menu(menubar, tearoff=False)
    cervical.add_command(label="Postura / lordosis C1–C7", command=lambda: _open_posture_dialog(root, workspace))
    cervical.add_command(label="Maduración ósea CVM · CS1–CS6", command=lambda: _open_cvm_dialog(root, workspace))
    cervical.add_separator()
    cervical.add_command(label="Guía: no convertir CVM a edad cronológica exacta", state="disabled")
    menubar.add_cascade(label="CERVICAL", menu=cervical)


def install_research(workspace_class) -> None:
    global _RESEARCH_INSTALLED
    if _RESEARCH_INSTALLED:
        return
    old_init = workspace_class.__init__

    def init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        try:
            _ensure_table(self.db)
        except Exception:
            pass
        try:
            add_cervical_menu(self, self)
        except Exception:
            pass

    workspace_class.__init__ = init
    _RESEARCH_INSTALLED = True


def install_individual(classic_class) -> None:
    if getattr(classic_class, "_yornis_cervical_v0152", False):
        return
    old_init = classic_class.__init__

    def init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        try:
            add_cervical_menu(self, self)
        except Exception:
            pass

    classic_class.__init__ = init
    classic_class._yornis_cervical_v0152 = True
