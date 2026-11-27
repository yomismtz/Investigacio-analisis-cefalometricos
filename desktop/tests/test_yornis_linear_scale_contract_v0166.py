from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yornis_measurement_corrections_v0166 as corrections
corrections.install()
import classic_engine as engine


class LinearScaleContractTests(unittest.TestCase):
    def setUp(self):
        self.points = {
            "A": (0.0, 0.0),
            "B": (100.0, 0.0),
            "C": (0.0, 100.0),
            "D": (100.0, 100.0),
        }

    def test_known_distances_are_converted_once(self):
        measurement = engine.Measurement("Test", "Distance", "distance", ("A", "B"), unit="mm")
        cases = ((100.0, 0.5, 50.0), (200.0, 0.2, 40.0), (50.0, 1.0, 50.0))
        for pixels, scale, expected in cases:
            points = dict(self.points)
            points["B"] = (pixels, 0.0)
            with self.subTest(pixels=pixels, scale=scale):
                self.assertAlmostEqual(engine.compute(measurement, points, scale), expected)

    def test_linear_measurements_reject_missing_or_invalid_scale(self):
        measurement = engine.Measurement("Test", "Distance", "distance", ("A", "B"), unit="mm")
        for scale in (None, 0, -0.5, float("nan"), float("inf")):
            with self.subTest(scale=scale), self.assertRaises(ValueError):
                engine.compute(measurement, self.points, scale)

    def test_signed_linear_measurement_scales_once(self):
        measurement = engine.Measurement("Test", "Offset", "signed_line", ("C", "A", "B"), unit="mm")
        one = engine.compute(measurement, self.points, 1.0)
        half = engine.compute(measurement, self.points, 0.5)
        self.assertAlmostEqual(half, one * 0.5)

    def test_angular_measurement_does_not_require_scale_or_change_with_scale(self):
        measurement = engine.Measurement("Test", "Angle", "angle3", ("A", "B", "C"), unit="°")
        unscaled = engine.compute(measurement, self.points, None)
        scaled = engine.compute(measurement, self.points, 0.25)
        self.assertTrue(math.isfinite(unscaled))
        self.assertAlmostEqual(unscaled, scaled)


if __name__ == "__main__":
    unittest.main()
