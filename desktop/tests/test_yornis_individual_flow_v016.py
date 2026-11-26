from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import research_workflow as workflow
import yornis_individual_flow_v016 as flow


class _FakeClassic:
    def __init__(self):
        self.mode = "individual"
        self.individual_measurements = {"Steiner": ["SNA"]}
        self.results = []
        self.rendered = 0

    def open_analysis_selector(self):
        return "legacy-selector"

    def calculate(self):
        self.results = [
            {"analysis": "Steiner", "name": "SNA", "display": "82°"},
            {"analysis": "Steiner", "name": "SNB", "display": "80°"},
        ]

    def render_results(self):
        self.rendered += 1

    def render_qc(self):
        self.rendered += 1

    def render_summary(self):
        self.rendered += 1


class IndividualSelectorFlowTests(unittest.TestCase):
    def setUp(self):
        self.old_host = workflow.HOST
        workflow.HOST = {
            "ANALYSES": ["Steiner"],
            "MEASUREMENTS": [],
        }

    def tearDown(self):
        workflow.HOST = self.old_host

    def test_individual_selected_names_respects_exact_choice(self):
        obj = _FakeClassic()
        self.assertEqual(flow._selected_names(obj, "Steiner"), ["SNA"])

    def test_install_filters_unselected_individual_results(self):
        class Fake(_FakeClassic):
            pass

        flow.install(Fake)
        obj = Fake()
        obj.calculate()
        self.assertEqual(
            [(r["analysis"], r["name"]) for r in obj.results],
            [("Steiner", "SNA")],
        )
        self.assertEqual(obj.rendered, 3)

    def test_prepare_individual_state_resets_research_context(self):
        obj = _FakeClassic()
        obj.mode = "research"
        obj.active_study_id = 14
        obj.active_study_name = "Study"
        obj.study_protocol = {"analyses": ["Steiner"]}
        flow._prepare_individual_state(obj)
        self.assertEqual(obj.mode, "individual")
        self.assertIsNone(obj.active_study_id)
        self.assertEqual(obj.active_study_name, "")
        self.assertIsNone(obj.study_protocol)

    def test_calibration_gate_disables_image_canvas_until_calibration_is_started(self):
        import tkinter as tk
        import yornis_calibration_gate_v0164 as gate

        class FakeClassic:
            def __init__(self, root):
                self.canvas = tk.Canvas(root, width=20, height=20)
                self.canvas.pack()
                self.points = {"S": (1.0, 2.0)}
                self.calibration_points = [(1.0, 1.0)]
                self.calibration_real_mm = 5.0
                self.mm_per_px = 0.5
                self.start_count = 0
                self.next_scale = 0.2

            def winfo_children(self):
                return [self.canvas]

            def after_idle(self, callback):
                callback()

            def load_image_file(self, _path):
                self.image_path = _path

            def start_calibration(self):
                self.start_count += 1
                self.calibration_real_mm = None if getattr(self, "cancel_calibration", False) else 12.0
                self.calibration_mode = self.calibration_real_mm is not None

            def finish_calibration(self):
                self.mm_per_px = self.next_scale
                self.calibration_points = []

        root = tk.Tk()
        root.withdraw()
        try:
            gate.install_individual(FakeClassic)
            app = FakeClassic(root)
            app.load_image_file("new-radiograph.png")
            self.assertEqual(app.points, {})
            self.assertIsNone(app.mm_per_px)
            self.assertEqual(app.start_count, 1)
            self.assertEqual(str(app.canvas.cget("state")), "normal")

            app.cancel_calibration = True
            app.start_calibration()
            self.assertEqual(str(app.canvas.cget("state")), "disabled")

            app.cancel_calibration = False
            app.start_calibration()
            app.calibration_points = [(1.0, 1.0), (21.0, 1.0)]
            app.finish_calibration()
            self.assertEqual(str(app.canvas.cget("state")), "normal")

            app.start_calibration()
            app.calibration_points = [(4.0, 4.0), (4.0, 4.0)]
            app.mm_per_px = 0.2
            app.finish_calibration()
            self.assertIsNone(app.mm_per_px)
            self.assertEqual(str(app.canvas.cget("state")), "disabled")

            app.start_calibration()
            app.calibration_points = [(1.0, 1.0), (21.0, 1.0)]
            app.next_scale = 0
            app.finish_calibration()
            self.assertIsNone(app.mm_per_px)
            self.assertEqual(str(app.canvas.cget("state")), "disabled")
        finally:
            root.destroy()

    def test_angular_only_individual_case_skips_mm_calibration(self):
        import tkinter as tk
        import yornis_calibration_gate_v0164 as gate

        class AngularClassic:
            def __init__(self, root):
                self.canvas = tk.Canvas(root, width=20, height=20)
                self.canvas.pack()
                self.individual_measurements = {"Steiner": ["SNA"]}
                self.points = {}
                self.mm_per_px = None
                self.start_count = 0
                self.calculated = False

            def winfo_children(self):
                return [self.canvas]

            def after_idle(self, callback):
                callback()

            def load_image_file(self, _path):
                self.image_path = _path

            def start_calibration(self):
                self.start_count += 1

            def calculate(self):
                self.calculated = True

        root = tk.Tk()
        root.withdraw()
        try:
            gate.install_individual(AngularClassic)
            app = AngularClassic(root)
            app.load_image_file("angular-only.png")
            self.assertEqual(app.start_count, 0)
            self.assertIsNone(app.mm_per_px)
            self.assertEqual(str(app.canvas.cget("state")), "normal")
            app.calculate()
            self.assertTrue(app.calculated)
        finally:
            root.destroy()

    def test_linear_calculation_is_blocked_until_scale_is_valid(self):
        import tkinter as tk
        from unittest.mock import patch
        import yornis_calibration_gate_v0164 as gate

        class LinearClassic:
            def __init__(self, root):
                self.canvas = tk.Canvas(root, width=20, height=20)
                self.canvas.pack()
                self.individual_measurements = {"Steiner": ["U1–NA (mm)"]}
                self.points = {}
                self.mm_per_px = None
                self.start_count = 0
                self.calculated = False

            def winfo_children(self):
                return [self.canvas]

            def after_idle(self, callback):
                callback()

            def load_image_file(self, _path):
                self.image_path = _path

            def start_calibration(self):
                self.start_count += 1

            def calculate(self):
                self.calculated = True

        root = tk.Tk()
        root.withdraw()
        try:
            gate.install_individual(LinearClassic)
            app = LinearClassic(root)
            app.load_image_file("linear-measure.png")
            self.assertEqual(app.start_count, 1)
            with patch("tkinter.messagebox.showwarning"):
                self.assertIsNone(app.calculate())
            self.assertFalse(app.calculated)
            app.mm_per_px = 0.5
            app.calculate()
            self.assertTrue(app.calculated)
        finally:
            root.destroy()

    def test_linear_individual_selection_still_requires_calibration(self):
        import yornis_calibration_gate_v0164 as gate
        import yornis_cervical_v0152 as cervical_module
        angular = type("Angular", (), {"individual_measurements": {"Steiner": ["SNA"]}})()
        linear = type("Linear", (), {"individual_measurements": {"Steiner": ["U1–NA (mm)"]}})()
        cvm = type("CVM", (), {"individual_measurements": {cervical_module.CVM_ANALYSIS: [cervical_module.CVM_MEASUREMENT]}})()
        cervical = type("Cervical", (), {"individual_measurements": {cervical_module.POSTURE_ANALYSIS: [cervical_module.POSTURE_MEASUREMENT]}})()
        self.assertFalse(gate._requires_calibration(angular))
        self.assertFalse(gate._requires_calibration(cvm))
        self.assertFalse(gate._requires_calibration(cervical))
        self.assertTrue(gate._requires_calibration(linear))

    def test_real_classic_individual_click_opens_selector_dialog(self):
        import tkinter as tk
        import yomceph_desktop_v130_classic as classic

        flow.install(classic.YomCephClassic)
        app = classic.YomCephClassic()
        app.withdraw()
        try:
            app.start_individual()
            app.update_idletasks()
            dialogs = [
                child
                for child in app.winfo_children()
                if isinstance(child, tk.Toplevel)
            ]
            self.assertTrue(dialogs, "Caso individual debe abrir un selector antes del trazado")
            self.assertTrue(
                any(
                    "Selección" in child.title() or "Selection" in child.title()
                    for child in dialogs
                )
            )
        finally:
            for child in list(app.winfo_children()):
                if isinstance(child, tk.Toplevel):
                    try:
                        child.destroy()
                    except Exception:
                        pass
            app.destroy()


if __name__ == "__main__":
    unittest.main()
