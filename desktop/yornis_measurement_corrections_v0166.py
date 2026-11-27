from __future__ import annotations

import math
from dataclasses import replace

_INSTALLED = False


def install() -> None:
    """Apply source-checked corrections to the classic measurement engine."""
    global _INSTALLED
    if _INSTALLED:
        return

    # Ensure the cervical extension has installed its own compute wrapper first.
    import yornis_cervical_v0152  # noqa: F401
    import classic_engine as engine
    if getattr(engine, "_yornis_measurement_corrections_v0166", False):
        _INSTALLED = True
        return

    updated = []
    for measurement in engine.MEASUREMENTS:
        changes = {}
        analysis = str(measurement.analysis)
        name = str(measurement.name).replace("–", "-").replace("—", "-")
        if analysis == "Steiner" and name == "SN-GoGn":
            # Steiner reports the 32° mean; ±5° is a later commonly used band,
            # not a standard deviation published in the original paper.
            changes.update(ref="32° ±5° (banda posterior de uso común; Steiner publicó la media sin DE)", lo=27.0, hi=37.0)
        elif analysis == "Tweed" and name == "FMIA":
            changes.update(
                ref=(
                    "Objetivo condicional: ≈68° si FMA 21°–29°; "
                    "≈65° si FMA ≥30°; si FMA ≤20°, valorar IMPA y no aplicar FMIA fijo."
                ),
                lo=None,
                hi=None,
            )
        elif analysis == "Tweed" and name == "IMPA":
            changes.update(
                ref="90° ±5° histórico; con FMA ≤20°, el límite superior publicado para IMPA varía según fuente/edición (≈92°–94°); no aplicar un corte automático.",
                lo=None,
                hi=None,
            )
        elif analysis == "Downs" and name == "L1/plano oclusal":
            # The engine's obtuse construction is 90° + the Downs deviation.
            changes.update(ref="14.5° ±3.5° (desviación respecto a 90°)", lo=11.0, hi=18.0)
        elif analysis == "Downs" and name == "U1 a A-Pg":
            changes.update(ref="Descriptiva; sin límite universal adoptado", lo=None, hi=None)
        elif analysis == "Steiner" and name == "Pog a NB":
            changes.update(ref="2 mm aprox.; media histórica sin banda validada", lo=None, hi=None)
        elif analysis == "Ricketts" and name == "Convexidad A a N-Pg":
            changes.update(ref="≈2 mm a los 9 años; ajustar por edad según Ricketts, sin corte automático", lo=None, hi=None)
        elif analysis == "Ricketts" and name == "L1 a A-Pg":
            changes.update(ref="1 mm; desviación clínica ±2 mm (no DE); referencia dependiente de edad y población, sin límite fijo", lo=None, hi=None)
        elif analysis == "Ricketts" and name == "U1 a A-Pg":
            changes.update(ref="Descriptiva; sin norma universal adoptada", lo=None, hi=None)
        updated.append(replace(measurement, **changes) if changes else measurement)

    engine.MEASUREMENTS[:] = updated

    names = {(m.analysis, m.name) for m in engine.MEASUREMENTS}
    if ("Downs", "Ángulo de convexidad") not in names:
        engine.MEASUREMENTS.append(
            engine.Measurement(
                "Downs",
                "Ángulo de convexidad",
                "straight_dev",
                ("N", "A", "Pg"),
                "0°; rango observado −8.5° a +10°",
                -8.5,
                10.0,
                "°",
                "Downs 1948",
            )
        )
    if ("Downs", "Plano A-B") not in names:
        engine.MEASUREMENTS.append(
            engine.Measurement(
                "Downs",
                "Plano A-B",
                "signed_ab_plane",
                ("N", "Pg", "A", "B"),
                "−4.6°; rango observado −9° a 0°",
                -9.0,
                0.0,
                "°",
                "Downs 1948",
            )
        )

    if ("Steiner", "SND") not in names:
        engine.MEASUREMENTS.append(
            engine.Measurement(
                "Steiner",
                "SND",
                "angle3",
                ("S", "N", "D"),
                "76° (media histórica; banda no verificada)",
                None,
                None,
                "°",
                "Steiner 1953",
            )
        )
    if ("Ricketts", "L1 a A-Pg (°)") not in names:
        engine.MEASUREMENTS.append(
            engine.Measurement(
                "Ricketts",
                "L1 a A-Pg (°)",
                "acute",
                ("L1i", "L1a", "A", "Pg"),
                "22° ±4° (banda clínica posterior; no DE original)",
                18.0,
                26.0,
                "°",
                "Ricketts 1960",
            )
        )

    if "Downs" not in engine.ANALYSES:
        engine.ANALYSES.append("Downs")

    original_compute = engine.compute

    def compute(measurement, points, mm_per_px, face_direction="right"):
        # Never silently interpret raw pixels as millimetres. The research
        # protocol and individual calibration gate both validate the scale,
        # but enforce the unit contract here as the final engine boundary too.
        unit = str(getattr(measurement, "unit", "") or "").strip().lower()
        if unit in {"mm", "cm"}:
            try:
                scale = float(mm_per_px)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("Esta medición lineal requiere una calibración mm/píxel válida.") from exc
            if not math.isfinite(scale) or scale <= 0:
                raise ValueError("Esta medición lineal requiere una calibración mm/píxel válida.")
        if measurement.analysis == "Downs" and measurement.name == "L1/plano oclusal":
            return original_compute(measurement, points, mm_per_px, face_direction) - 90.0
        if measurement.kind == "signed_ab_plane":
            is_right = str(face_direction).strip().casefold() in {"right", "r", "derecha"}
            anterior = (1.0, 0.0) if is_right else (-1.0, 0.0)
            facial_raw = engine.vec(points["Pg"], points["N"])
            ab_raw = engine.vec(points["B"], points["A"])
            if not all(math.isfinite(v) for v in (*facial_raw, *ab_raw)):
                raise ValueError("Landmarks no finitos para el plano A-B de Downs")
            if math.hypot(*facial_raw) < 1e-9 or math.hypot(*ab_raw) < 1e-9:
                raise ValueError("No se puede calcular el plano A-B con una línea de longitud cero")
            facial = engine.oriented_axis(facial_raw, anterior)
            ab = engine.oriented_axis(ab_raw, anterior)
            cross = ab[0] * facial[1] - ab[1] * facial[0]
            dot = ab[0] * facial[0] + ab[1] * facial[1]
            side_sign = 1.0 if is_right else -1.0
            return side_sign * math.degrees(math.atan2(cross, dot))
        return original_compute(measurement, points, mm_per_px, face_direction)

    engine.compute = compute
    engine._yornis_measurement_corrections_v0166 = True
    _INSTALLED = True
