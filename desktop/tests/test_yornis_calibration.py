import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yornis_calibration as calibration
import research_protocol


class CalibrationHelpersTests(unittest.TestCase):
    def test_known_distance_returns_mm_per_pixel(self):
        self.assertAlmostEqual(calibration.calculate_mm_per_px((10, 20), (110, 20), 25.4), 0.254)

    def test_diagonal_distance_uses_euclidean_geometry(self):
        self.assertAlmostEqual(calibration.calculate_mm_per_px((0, 0), (3, 4), 10), 2.0)

    def test_coincident_endpoints_are_rejected(self):
        with self.assertRaises(ValueError):
            calibration.calculate_mm_per_px((4, 8), (4, 8), 10)

    def test_nonpositive_and_nonfinite_real_distance_are_rejected(self):
        for value in (0, -1, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                calibration.calculate_mm_per_px((0, 0), (10, 0), value)

    def test_nonfinite_coordinates_are_rejected(self):
        with self.assertRaises(ValueError):
            calibration.calculate_mm_per_px((0, 0), (float("nan"), 1), 10)

    def test_point_must_be_inside_source_image(self):
        self.assertTrue(calibration.point_inside_image((0, 0), 100, 100))
        self.assertTrue(calibration.point_inside_image((99.9, 99.9), 100, 100))
        for point in ((-0.1, 10), (100, 50), (50, 100), (float("nan"), 1)):
            with self.subTest(point=point):
                self.assertFalse(calibration.point_inside_image(point, 100, 100))

    def test_confidence_values_are_normalized(self):
        self.assertEqual(calibration.normalize_landmark_confidence("HIGH"), "Alta")
        self.assertEqual(calibration.normalize_landmark_confidence("Media"), "Media")
        self.assertEqual(calibration.normalize_landmark_confidence("low"), "Baja")
        self.assertEqual(calibration.normalize_landmark_confidence("pending"), "Pendiente")

    def test_invalid_confidence_is_rejected(self):
        with self.assertRaises(ValueError):
            calibration.normalize_landmark_confidence("maybe")

    def test_quality_control_reports_pending_and_low_confidence(self):
        catalog = research_protocol.analysis_catalog()
        analysis, measurements = next((name, values) for name, values in catalog.items() if values)
        selected = [measurements[0].key]
        required = research_protocol.minimum_landmarks(selected)
        self.assertTrue(required)
        points = {name: (index * 25.0, index * 13.0) for index, name in enumerate(required)}
        high = {name: "Alta" for name in required}
        issues = research_protocol.trace_qc(selected, points, 0.25, high)
        self.assertFalse(any(item["code"] in {"pending_landmark_confidence", "low_landmark_confidence"} for item in issues))
        pending = dict(high)
        pending[required[0]] = "Pendiente"
        issues = research_protocol.trace_qc(selected, points, 0.25, pending)
        self.assertTrue(any(item["code"] == "pending_landmark_confidence" for item in issues))
        low = dict(high)
        low[required[0]] = "Baja"
        issues = research_protocol.trace_qc(selected, points, 0.25, low)
        self.assertTrue(any(item["code"] == "low_landmark_confidence" for item in issues))


if __name__ == "__main__":
    unittest.main()
