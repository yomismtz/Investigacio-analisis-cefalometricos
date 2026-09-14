from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

import classic_engine as engine

EXCLUSION_REASONS_ES = [
    "Calidad radiográfica insuficiente",
    "Landmarks requeridos no identificables",
    "Estructura fuera del campo radiográfico",
    "Distorsión o posición no aceptable",
    "Calibración no disponible para variables lineales",
    "Incumple criterio de inclusión",
    "Cirugía craneofacial previa",
    "Anomalía craneofacial excluida por el protocolo",
    "Duplicado",
    "Otro",
]
EXCLUSION_REASONS_EN = [
    "Insufficient radiographic quality",
    "Required landmarks cannot be identified",
    "Required structure outside the radiographic field",
    "Unacceptable distortion or positioning",
    "Calibration unavailable for linear variables",
    "Does not meet inclusion criteria",
    "Previous craniofacial surgery",
    "Craniofacial anomaly excluded by protocol",
    "Duplicate",
    "Other",
]


@dataclass(frozen=True)
class Variable:
    analysis: str
    name: str
    points: tuple[str, ...]
    unit: str = ""
    reference: str = ""
    kind: str = ""

    @property
    def key(self) -> str:
        return f"{self.analysis}::{self.name}"


def _measurements():
    for attr in ("MEASUREMENTS", "MEAS", "MEASURES"):
        value = getattr(engine, attr, None)
        if value:
            return list(value)
    return []


def _analyses_from_engine() -> list[str]:
    direct = getattr(engine, "ANALYSES", None)
    if direct:
        return list(direct)
    out: list[str] = []
    for m in _measurements():
        a = str(getattr(m, "analysis", "")).strip()
        if a and a not in out:
            out.append(a)
    return out


def analysis_catalog() -> dict[str, list[Variable]]:
    out: dict[str, list[Variable]] = {a: [] for a in _analyses_from_engine()}
    for m in _measurements():
        analysis = str(getattr(m, "analysis", "")).strip()
        name = str(getattr(m, "name", getattr(m, "label", ""))).strip()
        points = tuple(getattr(m, "pts", getattr(m, "points", ())) or ())
        unit = str(getattr(m, "unit", "") or "")
        reference = str(getattr(m, "norm_text", getattr(m, "reference", "")) or "")
        kind = str(getattr(m, "kind", "") or "")
        if analysis and name:
            out.setdefault(analysis, []).append(Variable(analysis, name, points, unit, reference, kind))
    # Preserve engine order while dropping exact duplicate labels.
    clean: dict[str, list[Variable]] = {}
    for analysis, variables in out.items():
        seen: set[str] = set(); clean[analysis] = []
        for v in variables:
            if v.name not in seen:
                seen.add(v.name); clean[analysis].append(v)
    return clean


def variable_map() -> dict[str, Variable]:
    return {v.key: v for vs in analysis_catalog().values() for v in vs}


def selected_variables(keys: list[str]) -> list[Variable]:
    m = variable_map()
    return [m[k] for k in keys if k in m]


def minimum_landmarks(keys: list[str]) -> list[str]:
    out: list[str] = []
    for v in selected_variables(keys):
        for p in v.points:
            if p and p not in out:
                out.append(p)
    return out


def landmark_usage(keys: list[str]) -> dict[str, list[str]]:
    usage: dict[str, list[str]] = {}
    for v in selected_variables(keys):
        for p in v.points:
            usage.setdefault(p, []).append(v.key)
    return usage


def shared_landmark_summary(keys: list[str]) -> dict[str, Any]:
    variables = selected_variables(keys)
    usage = landmark_usage(keys)
    shared = {p: vars_ for p, vars_ in usage.items() if len(vars_) > 1}
    return {
        "analysis_count": len({v.analysis for v in variables}),
        "measurement_count": len(variables),
        "unique_landmark_count": len(usage),
        "shared_landmark_count": len(shared),
        "landmarks": list(usage),
        "shared": shared,
    }


def protocol_config(title: str, variable_keys: list[str], include_criteria: list[str], exclude_criteria: list[str], *, blind_mode: bool = False, randomize_order: bool = False, study_mm_per_px: float | None = None, examiner: str = "", custom: dict | None = None) -> dict:
    variables = selected_variables(variable_keys)
    return {
        "title": title,
        "selected_variables": [v.key for v in variables],
        "selected_analyses": list(dict.fromkeys(v.analysis for v in variables)),
        "required_landmarks": minimum_landmarks([v.key for v in variables]),
        "include_criteria": list(include_criteria),
        "exclude_criteria": list(exclude_criteria),
        "blind_mode": bool(blind_mode),
        "randomize_order": bool(randomize_order),
        "study_mm_per_px": study_mm_per_px,
        "examiner": examiner,
        "custom": custom or {},
    }


# Norm/reference layer deliberately independent from geometry. The engine value
# is preserved even when no reference is available for age/sex/population.
REFERENCE_OVERRIDES: dict[str, dict[str, str]] = {
    "Steiner::SNA": {"default": "82° ±2°"},
    "Steiner::SNB": {"default": "80° ±2°"},
    "Steiner::ANB": {"default": "2° ±2°"},
    "Tweed::FMA": {"default": "25° ±4°"},
    "Tweed::FMIA": {"default": "65° ±5°"},
    "Tweed::IMPA": {"default": "90° ±5°"},
    "Wits::AO-BO": {"default": "Interpretar con sexo, población y convención de signo del protocolo"},
    "Sassouni::Arquitectura 4 planos": {"default": "Arquitectura/convergencia; no usar un umbral universal inventado"},
}


def reference_for(variable: Variable, sex: str = "", age: float | None = None, population: str = "") -> str:
    override = REFERENCE_OVERRIDES.get(variable.key, {})
    if override.get("default"):
        return override["default"]
    return variable.reference or "Referencia no fijada; conservar valor geométrico y documentar norma del protocolo"


def _is_linear(v: Variable) -> bool:
    u = v.unit.lower().replace(" ", "")
    return u in {"mm", "cm"} or "distance" in v.kind.lower() or "lineal" in v.kind.lower()


def compute_selected(variable_keys: list[str], points: dict[str, tuple[float, float]], mm_per_px: float | None, side: str = "right", sex: str = "", age: float | None = None, population: str = "") -> list[dict]:
    results: list[dict] = []
    scale = mm_per_px or 1.0
    measure_objs = _measurements()
    by_key: dict[str, Any] = {}
    for m in measure_objs:
        analysis = str(getattr(m, "analysis", "")).strip()
        name = str(getattr(m, "name", getattr(m, "label", ""))).strip()
        by_key[f"{analysis}::{name}"] = m
    for v in selected_variables(variable_keys):
        if not all(p in points for p in v.points):
            results.append({"analysis": v.analysis, "measurement": v.name, "value": None, "unit": v.unit, "reference": reference_for(v, sex, age, population), "interpretation": "Faltan landmarks", "missing": [p for p in v.points if p not in points]})
            continue
        if _is_linear(v) and not mm_per_px:
            results.append({"analysis": v.analysis, "measurement": v.name, "value": None, "unit": v.unit or "mm", "reference": reference_for(v, sex, age, population), "interpretation": "Requiere calibración", "missing": []})
            continue
        try:
            obj = by_key[v.key]
            value = engine.compute(obj, points, scale, side)
            results.append({"analysis": v.analysis, "measurement": v.name, "value": float(value), "unit": v.unit, "reference": reference_for(v, sex, age, population), "interpretation": "Valor geométrico calculado; interpretar con la norma seleccionada", "missing": []})
        except Exception as exc:
            results.append({"analysis": v.analysis, "measurement": v.name, "value": None, "unit": v.unit, "reference": reference_for(v, sex, age, population), "interpretation": f"No calculable: {exc}", "missing": []})
    return results


def trace_qc(variable_keys: list[str], points: dict[str, tuple[float, float]], mm_per_px: float | None) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    required = minimum_landmarks(variable_keys)
    missing = [p for p in required if p not in points]
    if missing:
        issues.append({"level": "review", "code": "missing_landmarks", "message": f"Faltan {len(missing)} landmarks: " + ", ".join(missing[:12]) + ("…" if len(missing) > 12 else "")})
    variables = selected_variables(variable_keys)
    if any(_is_linear(v) for v in variables) and not mm_per_px:
        issues.append({"level": "review", "code": "missing_calibration", "message": "El protocolo contiene variables lineales y no hay calibración mm/píxel."})
    placed = [(k, points[k]) for k in required if k in points]
    for i, (a, pa) in enumerate(placed):
        for b, pb in placed[i + 1:]:
            if math.hypot(pa[0] - pb[0], pa[1] - pb[1]) < 3.0:
                issues.append({"level": "review", "code": "near_superimposed", "message": f"{a} y {b} están casi superpuestos (<3 px)."})
                if len(issues) > 20:
                    break
    if not issues:
        issues.append({"level": "ok", "code": "basic_qc_ok", "message": "Sin alertas geométricas básicas. Esto no equivale a validación clínica."})
    return issues


def serialize_catalog() -> dict:
    return {analysis: [asdict(v) | {"key": v.key} for v in variables] for analysis, variables in analysis_catalog().items()}
