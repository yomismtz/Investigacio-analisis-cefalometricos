from __future__ import annotations

"""Evidence update for Yornis v0.15.5.

This module deliberately does not interpolate missing ages and does not turn
sample means into diagnostic cut-offs. It only changes references when the
published geometry matches the measurement used by Yornis closely enough.
"""

import classic_engine as engine
import yornis_cervical_v0152 as cervical
import yornis_reference_help_v0154_all as reference_help


C1_C7_REFERENCE = (
    "C1–C7 (línea del atlas C1 por arcos/tubérculos anterior-posterior frente a placa inferior de C7). "
    "Been et al., Spine J 2017, DOI 10.1016/j.spinee.2017.02.007: 6–19 años 50.7±10.5° "
    "(niños 49.7±10.4°, niñas 52.7±10.9°); 20–50 años 45.6±10.4° "
    "(hombres 47.4±10.7°, mujeres 43.7±10.1°). Son referencias de muestra, no límites de normalidad. "
    "No se encontró una referencia compatible año por año para 4–30 años; no interpolar ni extrapolar."
)

AIRWAY_SOURCE = (
    "McNamara JA Jr. Am J Orthod. 1984;86(6):449-469, DOI 10.1016/S0002-9416(84)90352-X; "
    "Pérez-Rodríguez LM, Diéguez-Pérez M, Millón-Cruz A. J Clin Exp Dent. 2021;13(9):e941-e947, "
    "DOI 10.4317/jced.58105. Valores pediátricos de muestra caucásica, 6/8/10/12 años, usando las "
    "mediciones superior e inferior de McNamara. No interpolar edades intermedias."
)

CRANIOCERVICAL_SOURCE = (
    "Solow B, Tallgren A. Am J Phys Anthropol. 1976;44(3):417-435, DOI 10.1002/ajpa.1330440306: "
    "muestra original de 120 varones daneses de 22–30 años; no constituye una norma universal pediátrica o femenina. "
    "Como contexto pediátrico, una muestra control reciente de 9–16 años reportó SN-OPT 101.72±7.68° y "
    "SN-CVT 106.59±8.00°. Estos datos se muestran como referencias de muestra y no como cortes diagnósticos."
)


def _set_attr(obj, name: str, value) -> None:
    try:
        object.__setattr__(obj, name, value)
    except Exception:
        setattr(obj, name, value)


def _table(table_id: str) -> dict:
    for item in reference_help.TABLES:
        if item.get("id") == table_id:
            return item
    raise KeyError(table_id)


def _sample_row(label: str, mean: str, spread: str, context: str) -> tuple[str, str, str, str, str, str]:
    return (
        label,
        mean,
        spread,
        "Referencia de muestra: un valor menor no equivale por sí solo a patología.",
        context,
        "Referencia de muestra: un valor mayor no equivale por sí solo a patología.",
    )


def _patch_c1_c7() -> None:
    cervical.LORDOSIS_REFERENCE = C1_C7_REFERENCE

    def descriptive_classification(angle: float) -> tuple[str, str]:
        if angle < 0:
            return (
                "Curvatura C1–C7 invertida / valor negativo",
                "Resultado descriptivo. Confirmar orientación, postura y trazado; no convertir el signo aislado en diagnóstico.",
            )
        return (
            "Lordosis C1–C7 · valor descriptivo",
            C1_C7_REFERENCE,
        )

    cervical.posture_classification = descriptive_classification

    for measurement in engine.MEASUREMENTS:
        if (
            getattr(measurement, "analysis", "") == cervical.POSTURE_ANALYSIS
            and getattr(measurement, "name", "") == cervical.POSTURE_MEASUREMENT
        ):
            _set_attr(measurement, "norm_text", C1_C7_REFERENCE)
            _set_attr(measurement, "reference", C1_C7_REFERENCE)
            # The former 35–45° band was being treated like a universal cut-off.
            # Remove automatic low/high classification; age/sex context is shown instead.
            _set_attr(measurement, "lo", None)
            _set_attr(measurement, "hi", None)

    table = _table("lordosis_c1_c7")
    table["title"] = "LORDOSIS CERVICAL C1–C7 · EDAD Y SEXO"
    table["subtitle"] = "Método C1–C7 compatible · referencias de muestra, no normalidad universal"
    table["source"] = (
        "Been E, Shefi S, Soudack M. Cervical lordosis: the effect of age and gender. "
        "Spine J. 2017;17(6):880-888. DOI 10.1016/j.spinee.2017.02.007."
    )
    table["rows"] = [
        (
            "C1–C7 · 4–5 años",
            "Sin referencia compatible encontrada",
            "—",
            "No extrapolar desde niños mayores.",
            "Yornis conserva el ángulo como dato descriptivo.",
            "No extrapolar desde niños mayores.",
        ),
        _sample_row("C1–C7 · 6–19 años · ambos sexos", "50.7°", "±10.5°", "Media de la muestra infantil/adolescente de Been et al."),
        _sample_row("C1–C7 · 6–19 años · niños", "49.7°", "±10.4°", "Subgrupo masculino; no es un intervalo diagnóstico."),
        _sample_row("C1–C7 · 6–19 años · niñas", "52.7°", "±10.9°", "Subgrupo femenino; no es un intervalo diagnóstico."),
        _sample_row("C1–C7 · 20–50 años · ambos sexos", "45.6°", "±10.4°", "Incluye 20–30 años, pero no ofrece medias para cada año individual."),
        _sample_row("C1–C7 · 20–50 años · hombres", "47.4°", "±10.7°", "Subgrupo masculino adulto de Been et al."),
        _sample_row("C1–C7 · 20–50 años · mujeres", "43.7°", "±10.1°", "Subgrupo femenino adulto de Been et al."),
        (
            "Edades individuales 6–30",
            "No disponibles con este método",
            "—",
            "No interpolar 7, 8, 9… a partir de medias agrupadas.",
            "Usar únicamente el grupo publicado que corresponda a la edad y documentar sexo/protocolo.",
            "No extrapolar fuera del rango publicado.",
        ),
    ]
    table["note"] = (
        "La geometría de Yornis se aproxima al C1–C7 de Been et al. Se retiró el antiguo corte universal 35–45°. "
        "Estudios pediátricos que usan C2–C7 o C3–C7 demuestran cambios con crecimiento, pero no se mezclan con C1–C7."
    )


def _patch_airway_help() -> None:
    table = _table("via_aerea")
    table["title"] = "VÍA AÉREA · McNAMARA · EDAD Y SEXO"
    table["subtitle"] = "Diámetros faríngeos 2D · referencias de muestra"
    table["source"] = AIRWAY_SOURCE
    rows = []
    pediatric = {
        6: ((7.500, 1.827), (12.018, 2.857)),
        8: ((8.529, 2.149), (11.428, 2.663)),
        10: ((10.111, 2.312), (11.556, 2.549)),
        12: ((11.416, 2.261), (11.222, 2.458)),
    }
    for age, (upper, lower) in pediatric.items():
        rows.append(_sample_row(f"McNamara superior · {age} años", f"{upper[0]:.3f} mm", f"±{upper[1]:.3f} mm", "Muestra caucásica pediátrica; la vía superior aumentó significativamente con la edad."))
        rows.append(_sample_row(f"McNamara inferior · {age} años", f"{lower[0]:.3f} mm", f"±{lower[1]:.3f} mm", "Muestra caucásica pediátrica; no mostró una tendencia significativa por edad en este estudio."))
    rows.extend([
        _sample_row("McNamara superior · niñas 6–12 (global)", "9.315 mm", "±2.601 mm", "Promedio por sexo; diferencia frente a niños no significativa."),
        _sample_row("McNamara superior · niños 6–12 (global)", "9.472 mm", "±2.616 mm", "Promedio por sexo; diferencia frente a niñas no significativa."),
        _sample_row("McNamara inferior · niñas 6–12 (global)", "11.714 mm", "±2.658 mm", "Promedio por sexo; diferencia frente a niños no significativa."),
        _sample_row("McNamara inferior · niños 6–12 (global)", "11.399 mm", "±2.626 mm", "Promedio por sexo; diferencia frente a niñas no significativa."),
        _sample_row("McNamara superior · referencia histórica de la app", "17 mm", "±4 mm", "Valor histórico no estratificado por edad en esta revisión; se conserva para trazabilidad y no se usa como corte pediátrico universal."),
        _sample_row("McNamara inferior · referencia histórica de la app", "12 mm", "±3 mm", "Valor histórico no estratificado por edad en esta revisión; se conserva para trazabilidad y no se usa como corte pediátrico universal."),
        (
            "Edades 4–5, 7, 9, 11 y 13–30",
            "Sin valor anual validado en esta tabla",
            "—",
            "No interpolar ni extrapolar.",
            "Conservar la medición 2D como descriptiva y contextualizar con edad, clase esquelética y clínica respiratoria.",
            "No interpolar ni extrapolar.",
        ),
    ])
    table["rows"] = rows
    table["note"] = (
        "En la muestra de 480 niños, la vía superior de McNamara aumentó con la edad; la inferior no mostró cambio significativo. "
        "No hubo diferencias significativas por sexo para estas dos variables. Se conservan 17±4 mm y 12±3 mm sólo como referencias históricas de trazabilidad, no como normas pediátricas. "
        "La cefalometría 2D no diagnostica obstrucción ni apnea."
    )


def _patch_craniocervical_help() -> None:
    table = _table("craneo_cervical")
    table["title"] = "ANÁLISIS CRÁNEO-CERVICAL · CONTEXTO DE EDAD"
    table["subtitle"] = "Solow–Tallgren y datos pediátricos · referencias de muestra"
    table["source"] = CRANIOCERVICAL_SOURCE
    additions = [
        _sample_row("SN-OPT · control pediátrico 9–16 años", "101.72°", "±7.68°", "Muestra control contemporánea; no es una norma anual ni universal."),
        _sample_row("SN-CVT · control pediátrico 9–16 años", "106.59°", "±8.00°", "Muestra control contemporánea; no es una norma anual ni universal."),
        (
            "Solow–Tallgren original",
            "22–30 años · varones",
            "n=120",
            "No extrapolar a niños o mujeres.",
            "La cohorte original fue de estudiantes daneses varones; los valores históricos deben leerse en ese contexto.",
            "No extrapolar a otras poblaciones como límite diagnóstico.",
        ),
    ]
    existing_labels = {row[0] for row in table["rows"]}
    table["rows"].extend(row for row in additions if row[0] not in existing_labels)
    table["note"] = (
        "No se encontró una serie compatible que permita asignar SN-OPT, SN-CVT, OPT-CVT u otros valores año por año de 4 a 30 años. "
        "Se conservan las referencias históricas existentes, pero se identifican como orientativas/de muestra y no como normalidad universal."
    )


def install() -> None:
    # Deliberately reapplied on every call. Older compatibility/audit layers can
    # be imported after this module during test discovery or application startup;
    # reapplying makes v0.15.5 authoritative without duplicating reference rows.
    _patch_c1_c7()
    _patch_airway_help()
    _patch_craniocervical_help()
    reference_help.validate_tables()


install()
