from __future__ import annotations

import math
from typing import Sequence

_CONFIDENCE = {
    "alta": "Alta", "high": "Alta",
    "media": "Media", "medium": "Media",
    "baja": "Baja", "low": "Baja",
    "pendiente": "Pendiente", "pending": "Pendiente",
}


def normalize_landmark_confidence(value: object) -> str:
    """Return the canonical Spanish confidence label or raise ValueError."""
    key = str(value or "").strip().casefold()
    if key not in _CONFIDENCE:
        raise ValueError("Confidence must be Alta, Media, Baja or Pendiente.")
    return _CONFIDENCE[key]


def point_inside_image(point: Sequence[float], width: int, height: int) -> bool:
    """Check that a point maps to a real pixel area of the source radiograph."""
    try:
        x, y = float(point[0]), float(point[1])
        w, h = int(width), int(height)
    except (TypeError, ValueError, IndexError, OverflowError):
        return False
    return math.isfinite(x) and math.isfinite(y) and w > 0 and h > 0 and 0.0 <= x < w and 0.0 <= y < h

def confidence_quality_issues(
    required_landmarks: Sequence[str],
    points: dict[str, object],
    confidence: dict[str, object] | None = None,
) -> list[dict[str, str]]:
    """Return review alerts for placed landmarks with low or pending confidence."""
    values = confidence or {}
    issues: list[dict[str, str]] = []
    for name in required_landmarks:
        if name not in points:
            continue
        try:
            level = normalize_landmark_confidence(values.get(name, "Pendiente"))
        except ValueError:
            level = "Pendiente"
        if level == "Baja":
            issues.append({
                "level": "review",
                "code": "low_landmark_confidence",
                "message": f"{name}: confianza baja; revisar la identificación anatómica.",
            })
        elif level == "Pendiente":
            issues.append({
                "level": "review",
                "code": "pending_landmark_confidence",
                "message": f"{name}: confianza pendiente; registrar la revisión del punto.",
            })
    return issues



def calibration_guidance(language: str = "es") -> str:
    """Explain the two-point, known-distance calibration before the user clicks."""
    if str(language or "es").lower().startswith("en"):
        return (
            "To calibrate this radiograph:\\n"
            "1. Identify two visible reference points whose REAL distance is known.\\n"
            "2. Enter the real distance between those points in millimeters.\\n"
            "3. Click the first endpoint and then the second endpoint on the radiograph.\\n\\n"
            "Both clicks must match the reference distance. Do not estimate the distance."
        )
    return (
        "Para calibrar esta radiografía:\\n"
        "1. Identifica dos puntos de referencia visibles cuya distancia REAL conozcas.\\n"
        "2. Indica cuántos milímetros hay realmente entre esos dos puntos.\\n"
        "3. Después marca el primer extremo y el segundo extremo sobre la radiografía.\\n\\n"
        "Los dos clics deben corresponder a la distancia que indicaste. No la estimes."
    )


def calibration_distance_prompt(language: str = "es") -> str:
    if str(language or "es").lower().startswith("en"):
        return "How many REAL millimeters are there between the two points you are going to mark?"
    return "¿A cuántos milímetros REALES equivalen los dos puntos que vas a marcar?"


def calculate_mm_per_px(first: Sequence[float], second: Sequence[float], real_distance_mm: float) -> float:
    """Compute the image-specific mm/pixel scale from two distinct image points."""
    try:
        x1, y1 = float(first[0]), float(first[1])
        x2, y2 = float(second[0]), float(second[1])
        real_mm = float(real_distance_mm)
    except (TypeError, ValueError, IndexError, OverflowError) as exc:
        raise ValueError("Invalid calibration values.") from exc
    values = (x1, y1, x2, y2, real_mm)
    if not all(math.isfinite(value) for value in values) or real_mm <= 0:
        raise ValueError("Calibration values must be finite and the distance must be positive.")
    distance_px = math.hypot(x2 - x1, y2 - y1)
    if distance_px <= 1e-9:
        raise ValueError("The calibration endpoints must be different.")
    scale = real_mm / distance_px
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("The calibration scale is invalid.")
    return scale
