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
