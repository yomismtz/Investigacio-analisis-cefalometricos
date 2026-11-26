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
        if analysis == "Tweed" and name == "FMIA":
            changes.update(
                ref=(
                    "Objetivo condicional: ≈68° si FMA 21°–29°; "
                    "≈65° si FMA ≥30°; si FMA ≤20°, valorar IMPA y no aplicar FMIA fijo."
                ),
                lo=None,
                hi=None,
            )
        elif analysis == "Downs" and name == "L1/plano oclusal":
            # The engine's obtuse construction is 90° + the Downs deviation.
            changes.update(ref="14.5° ±3.5° (desviación respecto a 90°)", lo=11.0, hi=18.0)
        elif analysis == "Downs" and name == "U1 a A-Pg":
            changes.update(ref="Descriptiva; sin límite universal adoptado", lo=None, hi=None)
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

    if "Downs" not in engine.ANALYSES:
        engine.ANALYSES.append("Downs")

    original_compute = engine.compute

    def compute(measurement, points, mm_per_px, face_direction="right"):
        if measurement.analysis == "Downs" and measurement.name == "L1/plano oclusal":
            return original_compute(measurement, points, mm_per_px, face_direction) - 90.0
        if measurement.kind == "signed_ab_plane":
            anterior = (1.0, 0.0) if face_direction == "right" else (-1.0, 0.0)
            facial = engine.oriented_axis(engine.vec(points["Pg"], points["N"]), anterior)
            ab = engine.oriented_axis(engine.vec(points["B"], points["A"]), anterior)
            cross = ab[0] * facial[1] - ab[1] * facial[0]
            dot = ab[0] * facial[0] + ab[1] * facial[1]
            return math.degrees(math.atan2(cross, dot))
        return original_compute(measurement, points, mm_per_px, face_direction)

    engine.compute = compute
    engine._yornis_measurement_corrections_v0166 = True
    _INSTALLED = True
