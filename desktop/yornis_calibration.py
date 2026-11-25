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
