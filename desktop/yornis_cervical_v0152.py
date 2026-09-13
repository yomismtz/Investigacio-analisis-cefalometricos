from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk

import classic_engine as engine
import research_protocol as rp
from research_db import ResearchDB

VERSION = "0.15.2"

# References used by the implementation. These are shown to the examiner in the
# guided panel; the program deliberately does not convert CVM into an exact
# biological age because stage-to-chronological-age varies by sex/population.
CVM_REFERENCE = (
    "Baccetti, Franchi & McNamara: CVM method (CS1–CS6); "
    "McNamara & Franchi 2018 user's guide; Bedoya et al. 2016."
)
LORDOSIS_REFERENCE = (
    "C1–C7 cervical lordosis angle: atlas plane vs inferior endplate of C7; "
    "reference commonly reported around 40° (35–45°). Interpret with positioning."
)

SHAPES_ES = {
    "trapezoidal": "Trapezoidal",
    "rect_horizontal": "Rectangular horizontal",
    "square": "Cuadrada",
    "rect_vertical": "Rectangular vertical",
}
SHAPES_EN = {
    "trapezoidal": "Trapezoidal",
    "rect_horizontal": "Horizontal rectangular",
    "square": "Square",
    "rect_vertical": "Vertical rectangular",
}

POSTURE_CODES = {
    1: ("Lordosis fisiológica", "Physiologic lordosis"),
    2: ("Rectificación / lordosis disminuida", "Straightening / reduced lordosis"),
    3: ("Cifosis cervical", "Cervical kyphosis"),
    4: ("Hiperlordosis / lordosis aumentada", "Hyperlordosis / increased lordosis"),
    5: ("No clasificable", "Not classifiable"),
}

CVM_INFO = {
    1: {
        "es": "CS1 · C2–C4 con bordes inferiores planos; C3 y C4 trapezoidales. Etapa prepuberal; el pico de crecimiento no se espera antes de ~2 años.",
        "en": "CS1 · Flat inferior borders C2–C4; C3 and C4 trapezoidal. Prepubertal; growth peak is not expected earlier than ~2 years.",
        "mean_age": "9.7 años (IC95% 9.4–10.1)",
    },
    2: {
        "es": "CS2 · Concavidad en C2; C3 y C4 aún trapezoidales. Etapa prepuberal; el pico suele aproximarse en ~1 año.",
        "en": "CS2 · Concavity at C2; C3 and C4 remain trapezoidal. Prepubertal; peak growth is typically about 1 year away.",
        "mean_age": "10.8 años (IC95% 10.5–11.1)",
    },
    3: {
        "es": "CS3 · Concavidades en C2 y C3; C3/C4 trapezoidales o rectangulares horizontales. Inicio del intervalo del pico puberal.",
        "en": "CS3 · Concavities at C2 and C3; C3/C4 trapezoidal or horizontal rectangular. Beginning of the pubertal peak interval.",
        "mean_age": "12.0 años (IC95% 11.7–12.2)",
    },
    4: {
        "es": "CS4 · Concavidades en C2, C3 y C4; C3/C4 rectangulares horizontales. El pico mandibular ocurre entre CS3 y CS4.",
        "en": "CS4 · Concavities at C2, C3 and C4; C3/C4 horizontal rectangular. Mandibular growth peak occurs between CS3 and CS4.",
        "mean_age": "13.4 años (IC95% 13.2–13.6)",
    },
    5: {
        "es": "CS5 · Concavidades persistentes; al menos C3 o C4 es cuadrada. Etapa post-pico.",
        "en": "CS5 · Concavities persist; at least C3 or C4 is square. Post-peak stage.",
        "mean_age": "14.7 años (IC95% 14.4–15.1)",
    },
    6: {
        "es": "CS6 · Concavidades marcadas; al menos C3 o C4 es rectangular vertical (la otra puede ser cuadrada). Etapa post-pico tardía.",
        "en": "CS6 · Marked concavities; at least C3 or C4 is vertical rectangular (the other may be square). Late post-peak stage.",
        "mean_age": "15.8 años (IC95% 15.3–16.3)",
    },
}


@dataclass
class ExtraMeasurement:
    analysis: str
    name: str
    pts: tuple[str, ...]
    kind: str
    unit: str = ""
    lo: float | None = None
    hi: float | None = None
    norm_text: str = ""
    source: str = ""


LORDOSIS_MEASUREMENT = ExtraMeasurement(
    analysis="Cráneo-cervical",
    name="Lordosis cervical C1–C7 (atlas–C7)",
    pts=("C1ant", "C1post", "C7inf_ant", "C7inf_post"),
    kind="yornis_c1c7_lordosis",
    unit="°",
    lo=35.0,
    hi=45.0,
    norm_text="Referencia radiográfica del método C1–C7: ~40°; rango 35–45°. Interpretar según posicionamiento.",
    source=LORDOSIS_REFERENCE,
)

MANUAL_CVM = rp.Variable(
    analysis="CVM C2–C4",
    name="Etapa de maduración cervical (CS1–CS6)",
    points=(),
    unit="CS",
    reference="Baccetti CVM: clasificación morfológica C2–C4; no equivale a edad cronológica exacta.",
    kind="manual_cvm",
)
MANUAL_POSTURE = rp.Variable(
    analysis="Cráneo-cervical",
    name="Clasificación postural cervical",
    points=(),
    unit="código",
    reference="1=lordosis, 2=rectificación, 3=cifosis, 4=hiperlordosis, 5=no clasificable.",
    kind="manual_cervical_posture",
)

_ENGINE_PATCHED = False
_PROTOCOL_PATCHED = False
_RESEARCH_INSTALLED = False
_INDIVIDUAL_INSTALLED = False


def _angle_between_lines(a1, a2, b1, b2) -> float:
    va = (float(a2[0]) - float(a1[0]), float(a2[1]) - float(a1[1]))
    vb = (float(b2[0]) - float(b1[0]), float(b2[1]) - float(b1[1]))
    na = math.hypot(*va); nb = math.hypot(*vb)
    if na <= 1e-9 or nb <= 1e-9:
        raise ValueError("Línea degenerada")
    c = max(-1.0, min(1.0, (va[0] * vb[0] + va[1] * vb[1]) / (na * nb)))
    angle = math.degrees(math.acos(c))
    return 180.0 - angle if angle > 90.0 else angle


def cervical_lordosis_angle(points: dict[str, tuple[float, float]]) -> float:
    req = LORDOSIS_MEASUREMENT.pts
    missing = [p for p in req if p not in points]
    if missing:
        raise KeyError(", ".join(missing))
    return _angle_between_lines(points["C1ant"], points["C1post"], points["C7inf_ant"], points["C7inf_post"])


def lordosis_interpretation(value: float | None, lang: str = "es") -> str:
    if value is None:
        return "—"
    if value < 35:
        es = "Ángulo <35°: curvatura disminuida/rectificación según esta referencia; correlacionar con posicionamiento y otros hallazgos."
        en = "Angle <35°: reduced curvature/straightening by this reference; correlate with positioning and other findings."
    elif value > 45:
        es = "Ángulo >45°: curvatura aumentada según esta referencia; no usar de forma aislada como diagnóstico."
        en = "Angle >45°: increased curvature by this reference; do not use in isolation as a diagnosis."
    else:
        es = "35–45°: dentro del rango radiográfico de referencia descrito para este método."
        en = "35–45°: within the radiographic reference range described for this method."
    return es if lang == "es" else en


def classify_cvm(c2: bool, c3: bool, c4: bool, c3_shape: str, c4_shape: str) -> int | None:
    """Strict, transparent implementation of the Baccetti visual rules.

    Ambiguous/non-canonical feature combinations return None so the examiner
    reviews the radiograph rather than receiving a fabricated automatic stage.
    """
    if not c2 and not c3 and not c4 and c3_shape == "trapezoidal" and c4_shape == "trapezoidal":
        return 1
    if c2 and not c3 and not c4 and c3_shape == "trapezoidal" and c4_shape == "trapezoidal":
        return 2
    if c2 and c3 and not c4 and c3_shape in {"trapezoidal", "rect_horizontal"} and c4_shape in {"trapezoidal", "rect_horizontal"}:
        return 3
    if c2 and c3 and c4 and c3_shape == "rect_horizontal" and c4_shape == "rect_horizontal":
        return 4
    if c2 and c3 and c4 and (c3_shape == "square" or c4_shape == "square") and c3_shape in {"square", "rect_horizontal"} and c4_shape in {"square", "rect_horizontal"}:
        return 5
    if c2 and c3 and c4 and (c3_shape == "rect_vertical" or c4_shape == "rect_vertical") and c3_shape in {"rect_vertical", "square"} and c4_shape in {"rect_vertical", "square"}:
        return 6
    return None


def cvm_description(stage: int | None, lang: str = "es") -> str:
    if stage not in CVM_INFO:
        return (
            "La combinación no coincide de forma inequívoca con CS1–CS6. Revisa concavidades y forma de C3/C4."
            if lang == "es" else
            "The combination does not match CS1–CS6 unambiguously. Review concavities and C3/C4 shape."
        )
    base = CVM_INFO[stage][lang]
    mean = CVM_INFO[stage]["mean_age"]
    caution_es = f" Edad cronológica media agrupada publicada: {mean}; NO es una edad ósea exacta y varía por sexo/población."
    caution_en = f" Published pooled mean chronological age: {mean}; this is NOT an exact skeletal age and varies by sex/population."
    return base + (caution_es if lang == "es" else caution_en)


def patch_engine() -> None:
    global _ENGINE_PATCHED
    if _ENGINE_PATCHED:
        return

    # Make the four landmarks available to both Individual and Research modes.
    help_map = getattr(engine, "POINT_HELP", None)
    if isinstance(help_map, dict):
        help_map.update({
            "C1ant": "C1 tubérculo anterior del atlas: centro del tubérculo anterior.",
            "C1post": "C1 tubérculo posterior del atlas: centro del tubérculo posterior.",
            "C7inf_ant": "C7 borde inferior anterior: esquina anterior de la placa terminal inferior.",
            "C7inf_post": "C7 borde inferior posterior: esquina posterior de la placa terminal inferior.",
        })

    keys = {(getattr(m, "analysis", ""), getattr(m, "name", "")) for m in getattr(engine, "MEASUREMENTS", [])}
    key = (LORDOSIS_MEASUREMENT.analysis, LORDOSIS_MEASUREMENT.name)
    if key not in keys:
        engine.MEASUREMENTS = list(getattr(engine, "MEASUREMENTS", [])) + [LORDOSIS_MEASUREMENT]

    original_compute = engine.compute

    def compute(measurement, points, mm_per_px, side="right"):
        if getattr(measurement, "kind", "") == "yornis_c1c7_lordosis":
            return cervical_lordosis_angle(points)
        return original_compute(measurement, points, mm_per_px, side)

    engine.compute = compute
    _ENGINE_PATCHED = True


def patch_protocol() -> None:
    global _PROTOCOL_PATCHED
    if _PROTOCOL_PATCHED:
        return
    patch_engine()
    original_catalog = rp.analysis_catalog
    original_compute_selected = rp.compute_selected

    def analysis_catalog():
        out = original_catalog()
        # Clone lists so repeated calls never mutate the engine-derived cache.
        out = {k: list(v) for k, v in out.items()}
        for variable in (MANUAL_CVM, MANUAL_POSTURE):
            bucket = out.setdefault(variable.analysis, [])
            if all(v.key != variable.key for v in bucket):
                bucket.append(variable)
        return out

    def compute_selected(variable_keys, points, mm_per_px, side="right", sex="", age=None, population=""):
        manual = {MANUAL_CVM.key, MANUAL_POSTURE.key}
        regular_keys = [k for k in variable_keys if k not in manual]
        results = original_compute_selected(regular_keys, points, mm_per_px, side=side, sex=sex, age=age, population=population)
        selected = set(variable_keys)
        if MANUAL_CVM.key in selected:
            results.append({
                "analysis": MANUAL_CVM.analysis, "measurement": MANUAL_CVM.name,
                "value": None, "unit": MANUAL_CVM.unit, "reference": MANUAL_CVM.reference,
                "interpretation": "Requiere clasificación manual guiada C2–C4", "missing": [],
            })
        if MANUAL_POSTURE.key in selected:
            results.append({
                "analysis": MANUAL_POSTURE.analysis, "measurement": MANUAL_POSTURE.name,
                "value": None, "unit": MANUAL_POSTURE.unit, "reference": MANUAL_POSTURE.reference,
                "interpretation": "Requiere clasificación visual documentada", "missing": [],
            })
        return results

    rp.analysis_catalog = analysis_catalog
    rp.compute_selected = compute_selected
    _PROTOCOL_PATCHED = True


def _ensure_table(db: ResearchDB) -> None:
    with db.connect() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS cervical_assessments(
                case_id INTEGER PRIMARY KEY,
                study_id INTEGER NOT NULL,
                cvm_stage INTEGER,
                c2_concave INTEGER NOT NULL DEFAULT 0,
                c3_concave INTEGER NOT NULL DEFAULT 0,
                c4_concave INTEGER NOT NULL DEFAULT 0,
                c3_shape TEXT NOT NULL DEFAULT '',
                c4_shape TEXT NOT NULL DEFAULT '',
                posture_code INTEGER,
                posture_label TEXT NOT NULL DEFAULT '',
                lordosis_angle REAL,
                notes TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
            )
            """
        )


def _assessment(db: ResearchDB, case_id: int | None) -> dict:
    if not case_id:
        return {}
    _ensure_table(db)
    with db.connect() as con:
        row = con.execute("SELECT * FROM cervical_assessments WHERE case_id=?", (case_id,)).fetchone()
    return dict(row) if row else {}


def _save_assessment(db: ResearchDB, case_id: int, **data) -> None:
    _ensure_table(db)
    case = db.case(case_id)
    if not case:
        raise KeyError(case_id)
    stage = data.get("cvm_stage")
    posture_code = data.get("posture_code")
    if stage not in (None, 1, 2, 3, 4, 5, 6):
        raise ValueError("CVM stage must be CS1–CS6")
    if posture_code not in (None, 1, 2, 3, 4, 5):
        raise ValueError("Invalid cervical posture code")
    label = POSTURE_CODES.get(posture_code, ("", ""))[0] if posture_code else ""
    with db.connect() as con:
        con.execute(
            """
            INSERT INTO cervical_assessments(
                case_id,study_id,cvm_stage,c2_concave,c3_concave,c4_concave,
                c3_shape,c4_shape,posture_code,posture_label,lordosis_angle,notes,updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
            ON CONFLICT(case_id) DO UPDATE SET
                cvm_stage=excluded.cvm_stage,c2_concave=excluded.c2_concave,
                c3_concave=excluded.c3_concave,c4_concave=excluded.c4_concave,
                c3_shape=excluded.c3_shape,c4_shape=excluded.c4_shape,
                posture_code=excluded.posture_code,posture_label=excluded.posture_label,
                lordosis_angle=excluded.lordosis_angle,notes=excluded.notes,
                updated_at=datetime('now')
            """,
            (
                case_id, int(case["study_id"]), stage,
                int(bool(data.get("c2_concave"))), int(bool(data.get("c3_concave"))), int(bool(data.get("c4_concave"))),
                str(data.get("c3_shape") or ""), str(data.get("c4_shape") or ""),
                posture_code, label, data.get("lordosis_angle"), str(data.get("notes") or ""),
            ),
        )
    try:
        db.audit(int(case["study_id"]), "cervical_assessment_saved", case_id=case_id, cvm_stage=stage, posture_code=posture_code)
    except Exception:
        pass


def _patch_db() -> None:
    if getattr(ResearchDB, "_yornis_cervical_v0152", False):
        return
    old_init = ResearchDB._init_schema

    def init_schema(self):
        old_init(self)
        _ensure_table(self)

    ResearchDB._init_schema = init_schema
    ResearchDB.cervical_assessment = lambda self, case_id: _assessment(self, case_id)
    ResearchDB.save_cervical_assessment = lambda self, case_id, **data: _save_assessment(self, case_id, **data)
    ResearchDB._yornis_cervical_v0152 = True


def _fill_manual_results(results: list[dict], assessment: dict, lang: str) -> list[dict]:
    stage = assessment.get("cvm_stage") if assessment else None
    posture = assessment.get("posture_code") if assessment else None
    for r in results:
        if r.get("analysis") == MANUAL_CVM.analysis and r.get("measurement") == MANUAL_CVM.name:
            r["value"] = float(stage) if stage else None
            r["unit"] = "CS"
            r["interpretation"] = cvm_description(int(stage), lang) if stage else ("Clasificación CVM pendiente" if lang == "es" else "CVM classification pending")
        elif r.get("analysis") == MANUAL_POSTURE.analysis and r.get("measurement") == MANUAL_POSTURE.name:
            r["value"] = float(posture) if posture else None
            r["unit"] = "código"
            if posture:
                r["interpretation"] = POSTURE_CODES[int(posture)][0 if lang == "es" else 1]
            else:
                r["interpretation"] = "Clasificación postural pendiente" if lang == "es" else "Posture classification pending"
        elif r.get("analysis") == LORDOSIS_MEASUREMENT.analysis and r.get("measurement") == LORDOSIS_MEASUREMENT.name and r.get("value") is not None:
            r["interpretation"] = lordosis_interpretation(float(r["value"]), lang)
    return results


def _refresh_results_tree(workspace, results: list[dict]) -> None:
    if not hasattr(workspace, "results_tree"):
        return
    by = {(r.get("analysis"), r.get("measurement")): r for r in results}
    for group in workspace.results_tree.get_children(""):
        analysis = workspace.results_tree.item(group, "text")
        for item in workspace.results_tree.get_children(group):
            name = workspace.results_tree.item(item, "text")
            r = by.get((analysis, name))
            if not r:
                continue
            value = r.get("value")
            val = "—" if value is None else f"{float(value):.2f}"
            workspace.results_tree.item(item, values=(val, r.get("unit", "")))


def _shape_key(display: str, lang: str) -> str:
    mapping = SHAPES_ES if lang == "es" else SHAPES_EN
    for key, value in mapping.items():
        if value == display:
            return key
    return ""


def _open_assessment_dialog(self, *, research: bool) -> None:
    lang = getattr(self, "language", "es") if research else "es"
    T = (lambda es, en: es if lang == "es" else en)
    case_id = getattr(self, "case_id", None) if research else None
    if research and not case_id:
        messagebox.showinfo("Yornis", T("Abre un caso antes de registrar la evaluación cervical.", "Open a case before recording the cervical assessment."), parent=self)
        return

    saved = self.db.cervical_assessment(case_id) if research else getattr(self, "yornis_cervical_assessment", {})
    w = tk.Toplevel(self)
    w.title(T("Yornis · Análisis cervical", "Yornis · Cervical analysis"))
    w.transient(self)
    w.grab_set()
    try:
        w.geometry("760x680")
        w.minsize(680, 600)
    except Exception:
        pass

    outer = ttk.Frame(w, padding=12); outer.pack(fill="both", expand=True)
    ttk.Label(outer, text=T("Postura cervical y maduración esquelética", "Cervical posture and skeletal maturation"), font=("Segoe UI", 16, "bold")).pack(anchor="w")
    ttk.Label(outer, text=T(
        "Dos evaluaciones separadas: lordosis/postura cervical y CVM C2–C4. La clasificación CVM no se convierte en una edad ósea exacta.",
        "Two separate assessments: cervical lordosis/posture and C2–C4 CVM. CVM classification is not converted into an exact skeletal age."
    ), wraplength=700).pack(anchor="w", pady=(4, 10))

    # Lordosis / posture
    lord = ttk.LabelFrame(outer, text=T("1 · Lordosis / postura cervical", "1 · Cervical lordosis / posture"), padding=10)
    lord.pack(fill="x", pady=5)
    angle = None
    try:
        angle = cervical_lordosis_angle(getattr(self, "points", {}) or {})
    except Exception:
        angle = None
    angle_text = f"{angle:.2f}° · {lordosis_interpretation(angle, lang)}" if angle is not None else T(
        "Ángulo C1–C7 pendiente. Selecciona 'Lordosis cervical C1–C7' y coloca C1ant, C1post, C7inf_ant y C7inf_post.",
        "C1–C7 angle pending. Select 'C1–C7 cervical lordosis' and place C1ant, C1post, C7inf_ant and C7inf_post."
    )
    ttk.Label(lord, text=angle_text, wraplength=680).pack(anchor="w")
    posture_var = tk.StringVar()
    saved_posture = saved.get("posture_code") if saved else None
    posture_labels = [POSTURE_CODES[i][0 if lang == "es" else 1] for i in sorted(POSTURE_CODES)]
    if saved_posture in POSTURE_CODES:
        posture_var.set(POSTURE_CODES[int(saved_posture)][0 if lang == "es" else 1])
    ttk.Label(lord, text=T("Clasificación visual documentada:", "Documented visual classification:")).pack(anchor="w", pady=(8, 2))
    ttk.Combobox(lord, textvariable=posture_var, state="readonly", values=posture_labels, width=48).pack(anchor="w")
    ttk.Label(lord, text=T(
        "La categoría visual complementa el ángulo. El ángulo C1–C7 por sí solo no debe usarse para diagnosticar cifosis y puede cambiar con el posicionamiento.",
        "The visual category complements the angle. The C1–C7 angle alone should not diagnose kyphosis and may change with positioning."
    ), wraplength=680).pack(anchor="w", pady=(7, 0))

    # CVM
    cvm = ttk.LabelFrame(outer, text=T("2 · Maduración cervical CVM (C2–C4)", "2 · Cervical maturation CVM (C2–C4)"), padding=10)
    cvm.pack(fill="both", expand=True, pady=5)
    c2v = tk.BooleanVar(value=bool(saved.get("c2_concave")) if saved else False)
    c3v = tk.BooleanVar(value=bool(saved.get("c3_concave")) if saved else False)
    c4v = tk.BooleanVar(value=bool(saved.get("c4_concave")) if saved else False)
    conc = ttk.Frame(cvm); conc.pack(fill="x")
    ttk.Label(conc, text=T("Concavidad visible en borde inferior:", "Visible inferior-border concavity:")).pack(side="left", padx=(0, 8))
    ttk.Checkbutton(conc, text="C2", variable=c2v).pack(side="left", padx=5)
    ttk.Checkbutton(conc, text="C3", variable=c3v).pack(side="left", padx=5)
    ttk.Checkbutton(conc, text="C4", variable=c4v).pack(side="left", padx=5)

    shapes = SHAPES_ES if lang == "es" else SHAPES_EN
    c3s = tk.StringVar(value=shapes.get(saved.get("c3_shape", ""), ""))
    c4s = tk.StringVar(value=shapes.get(saved.get("c4_shape", ""), ""))
    grid = ttk.Frame(cvm); grid.pack(fill="x", pady=8)
    ttk.Label(grid, text=T("Forma C3:", "C3 shape:")).grid(row=0, column=0, sticky="w", padx=3, pady=3)
    ttk.Combobox(grid, textvariable=c3s, state="readonly", values=list(shapes.values()), width=28).grid(row=0, column=1, sticky="w", padx=3, pady=3)
    ttk.Label(grid, text=T("Forma C4:", "C4 shape:")).grid(row=1, column=0, sticky="w", padx=3, pady=3)
    ttk.Combobox(grid, textvariable=c4s, state="readonly", values=list(shapes.values()), width=28).grid(row=1, column=1, sticky="w", padx=3, pady=3)

    result_var = tk.StringVar()
    stage_holder = {"stage": saved.get("cvm_stage") if saved else None}

    def determine(*_):
        stage = classify_cvm(c2v.get(), c3v.get(), c4v.get(), _shape_key(c3s.get(), lang), _shape_key(c4s.get(), lang))
        stage_holder["stage"] = stage
        if stage:
            result_var.set(cvm_description(stage, lang))
        else:
            result_var.set(cvm_description(None, lang))

    for var in (c2v, c3v, c4v, c3s, c4s):
        var.trace_add("write", determine)
    determine()
    ttk.Label(cvm, textvariable=result_var, wraplength=680, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(4, 4))
    ttk.Label(cvm, text=T(
        "La edad cronológica mostrada en el texto es sólo una media agrupada de estudios publicados; no debe reportarse como edad ósea individual.",
        "The chronological age shown in the text is only a pooled mean from published studies; it must not be reported as an individual's skeletal age."
    ), wraplength=680).pack(anchor="w")

    notes_var = tk.StringVar(value=str(saved.get("notes") or "") if saved else "")
    ttk.Label(outer, text=T("Observación:", "Note:")).pack(anchor="w", pady=(5, 2))
    ttk.Entry(outer, textvariable=notes_var).pack(fill="x")

    def save():
        posture_code = None
        for code, labels in POSTURE_CODES.items():
            if posture_var.get() == labels[0 if lang == "es" else 1]:
                posture_code = code; break
        payload = {
            "cvm_stage": stage_holder["stage"],
            "c2_concave": c2v.get(), "c3_concave": c3v.get(), "c4_concave": c4v.get(),
            "c3_shape": _shape_key(c3s.get(), lang), "c4_shape": _shape_key(c4s.get(), lang),
            "posture_code": posture_code, "lordosis_angle": angle, "notes": notes_var.get().strip(),
        }
        if research:
            self.db.save_cervical_assessment(case_id, **payload)
            if hasattr(self, "update_cervical_summary"):
                self.update_cervical_summary()
            try:
                self.calculate_preview()
            except Exception:
                pass
        else:
            self.yornis_cervical_assessment = payload
        w.destroy()

    buttons = ttk.Frame(outer); buttons.pack(fill="x", pady=(10, 0))
    ttk.Button(buttons, text=T("Guardar evaluación", "Save assessment"), command=save, style="Primary.TButton").pack(side="right")
    ttk.Button(buttons, text=T("Cerrar", "Close"), command=w.destroy).pack(side="right", padx=6)
    ttk.Label(buttons, text=T("Fuentes: Baccetti CVM · McNamara/Franchi · referencias radiográficas C1–C7", "Sources: Baccetti CVM · McNamara/Franchi · C1–C7 radiographic references"), font=("Segoe UI", 8)).pack(side="left")


def install_research(workspace_class) -> None:
    global _RESEARCH_INSTALLED
    if _RESEARCH_INSTALLED:
        return
    patch_protocol(); _patch_db()

    # research_ui imported engine helpers by value; repoint them to the patched
    # protocol layer so the selector and calculations include the new items.
    import research_ui as rui
    rui.analysis_catalog = rp.analysis_catalog
    rui.compute_selected = rp.compute_selected
    rui.minimum_landmarks = rp.minimum_landmarks
    rui.shared_landmark_summary = rp.shared_landmark_summary
    rui.LANDMARK_HELP.update({
        "C1ant": "Atlas C1: centro del tubérculo anterior.",
        "C1post": "Atlas C1: centro del tubérculo posterior.",
        "C7inf_ant": "C7: esquina anterior de la placa terminal inferior.",
        "C7inf_post": "C7: esquina posterior de la placa terminal inferior.",
    })

    old_build_trace = workspace_class._build_trace
    def build_trace(self):
        old_build_trace(self)
        box = ttk.LabelFrame(self.trace_tab, text=self.T("Análisis cervical ampliado", "Extended cervical analysis"), padding=6)
        box.pack(fill="x", padx=5, pady=(0, 5))
        self.cervical_summary = ttk.Label(box, text=self.T("CVM/postura: pendiente", "CVM/posture: pending"))
        self.cervical_summary.pack(side="left", padx=4)
        ttk.Button(box, text=self.T("CVM + postura cervical…", "CVM + cervical posture…"), command=self.open_cervical_assessment).pack(side="right", padx=4)
    workspace_class._build_trace = build_trace

    workspace_class.open_cervical_assessment = lambda self: _open_assessment_dialog(self, research=True)

    def update_cervical_summary(self):
        a = self.db.cervical_assessment(self.case_id) if self.case_id else {}
        stage = f"CS{a['cvm_stage']}" if a.get("cvm_stage") else "—"
        posture = POSTURE_CODES.get(a.get("posture_code"), ("—", "—"))[0 if self.language == "es" else 1]
        angle = a.get("lordosis_angle")
        angle_txt = f"{float(angle):.1f}°" if angle is not None else "—"
        if hasattr(self, "cervical_summary"):
            self.cervical_summary.config(text=f"CVM {stage} · {posture} · C1–C7 {angle_txt}")
    workspace_class.update_cervical_summary = update_cervical_summary

    old_open = workspace_class.open_selected_case
    def open_selected_case(self, *args, **kwargs):
        out = old_open(self, *args, **kwargs)
        try: self.update_cervical_summary()
        except Exception: pass
        return out
    workspace_class.open_selected_case = open_selected_case

    old_calc = workspace_class.calculate_preview
    def calculate_preview(self):
        results = old_calc(self)
        if not self.case_id:
            return results
        assessment = self.db.cervical_assessment(self.case_id)
        # Refresh the measured angle in the assessment whenever the four points exist.
        try:
            angle = cervical_lordosis_angle(self.points)
            if assessment:
                payload = dict(assessment)
                payload.pop("case_id", None); payload.pop("study_id", None); payload.pop("posture_label", None); payload.pop("updated_at", None)
                payload["lordosis_angle"] = angle
                self.db.save_cervical_assessment(self.case_id, **payload)
                assessment = self.db.cervical_assessment(self.case_id)
        except Exception:
            pass
        _fill_manual_results(results, assessment, self.language)
        _refresh_results_tree(self, results)
        try: self.update_cervical_summary()
        except Exception: pass
        return results
    workspace_class.calculate_preview = calculate_preview

    # Add a menu entry without replacing the existing Research menu.
    old_build_menu = workspace_class._build_menu
    def build_menu(self):
        old_build_menu(self)
        try:
            menu = self.nametowidget(self.cget("menu"))
            cv = tk.Menu(menu, tearoff=0)
            cv.add_command(label=self.T("Maduración CVM CS1–CS6…", "CVM maturation CS1–CS6…"), command=self.open_cervical_assessment)
            cv.add_command(label=self.T("Postura/lordosis cervical…", "Cervical posture/lordosis…"), command=self.open_cervical_assessment)
            menu.add_cascade(label=self.T("CERVICAL", "CERVICAL"), menu=cv)
        except Exception:
            pass
    workspace_class._build_menu = build_menu

    _RESEARCH_INSTALLED = True


def install_individual(classic_class) -> None:
    global _INDIVIDUAL_INSTALLED
    if _INDIVIDUAL_INSTALLED:
        return
    patch_protocol()
    old_init = classic_class.__init__

    def init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        self.yornis_cervical_assessment = {}
        try:
            menu = self.nametowidget(self.cget("menu"))
            cv = tk.Menu(menu, tearoff=0)
            cv.add_command(label="Maduración CVM CS1–CS6…", command=lambda: _open_assessment_dialog(self, research=False))
            cv.add_command(label="Postura/lordosis cervical…", command=lambda: _open_assessment_dialog(self, research=False))
            menu.add_cascade(label="CERVICAL", menu=cv)
        except Exception:
            pass
    classic_class.__init__ = init
    _INDIVIDUAL_INSTALLED = True


patch_engine()
patch_protocol()
