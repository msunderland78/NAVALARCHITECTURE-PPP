import json
import unittest
from pathlib import Path

from ppp_core import evaluate_case, result_to_markdown, speeds_to_csv

ROOT = Path(__file__).resolve().parents[3]


class ExportTest(unittest.TestCase):
    def test_speeds_to_csv(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        result = evaluate_case(case, point_count=2)
        csv_text = speeds_to_csv(result)
        lines = csv_text.splitlines()

        self.assertEqual(lines[0], "speed_knots,speed_mps,froude_number,speed_length_ratio,reynolds_number,friction_coefficient,residual_resistance_coefficient,correlation_allowance_coefficient,appendage_mode,appendage_equivalent_wetted_area_form_factor_m2,frictional_resistance_n,rf_form_resistance_n,appendage_resistance_n,wave_resistance_n,bulb_resistance_n,transom_resistance_n,correlation_allowance_resistance_n,air_resistance_n,implemented_resistance_subtotal_n,design_margin_resistance_n,total_resistance_n,effective_power_kw,wake_fraction,thrust_deduction,required_thrust_n,hull_efficiency,relative_rotative_efficiency,resistance_status")
        self.assertEqual(len(lines), 3)
        self.assertIn("15.0,7.71666,0.16923925200101986", lines[1])
        self.assertIn("17.0,8.745548,0.19180448560115582", lines[2])
        self.assertIn("partial_source_safe_components", lines[1])

    def test_speeds_to_csv_rejects_bad_result_shape(self):
        with self.assertRaisesRegex(ValueError, "result must be an object"):
            speeds_to_csv([])
        with self.assertRaisesRegex(ValueError, "result.speeds must be a list"):
            speeds_to_csv({"speeds": {}})
        with self.assertRaisesRegex(ValueError, "result.speeds rows must be objects"):
            speeds_to_csv({"speeds": ["bad"]})
        with self.assertRaisesRegex(ValueError, "result.speeds.speed_knots is required"):
            speeds_to_csv({"speeds": [{}]})

    def test_speeds_to_csv_rejects_non_finite_numbers(self):
        result = evaluate_case(json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text()), point_count=1)
        result["speeds"][0]["speed_knots"] = True
        with self.assertRaisesRegex(ValueError, "result.speeds.speed_knots must be a finite number"):
            speeds_to_csv(result)

        result = evaluate_case(json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text()), point_count=1)
        result["speeds"][0]["total_resistance_n"] = float("nan")
        with self.assertRaisesRegex(ValueError, "result.speeds.total_resistance_n must be a finite number"):
            speeds_to_csv(result)

    def test_result_to_markdown(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        result = evaluate_case(case, point_count=2)
        text = result_to_markdown(result, case)

        self.assertIn("# Holtrop and Mennen Example", text)
        self.assertIn("Run ID: Test 1.0", text)
        self.assertIn("## Engineering Review", text)
        self.assertIn("Calculation status: `partial_source_safe_components`", text)
        self.assertIn("## Input Summary", text)
        self.assertIn("| Initial speed, kn | 15.0000 |", text)
        self.assertIn("| Speed increment, kn | 2.0000 |", text)
        self.assertIn("| Water type | salt_water_15_c |", text)
        self.assertIn("| Kinematic viscosity, m2/s | 1.18831e-06 |", text)
        self.assertIn("| Propulsion type | single_screw_conventional_stern |", text)
        self.assertIn("| Appendage mode | percent_bare_hull_resistance |", text)
        self.assertIn("| Wetted surface mode | user |", text)
        self.assertIn("| Half angle mode | user |", text)
        self.assertIn("| Air drag | yes |", text)
        self.assertIn("| V, kn | Fn | RT, kN | PE, kW | Required thrust, kN | Status |", text)
        self.assertIn("| 15.0000 | 0.1692 | 610.05 | 4707.56 | 747.73 | `partial_source_safe_components` |", text)

    def test_result_to_markdown_includes_nonconventional_propulsion_warning(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["propulsion"]["type"] = "single_screw_open_flow_stern"
        result = evaluate_case(case, point_count=1)
        text = result_to_markdown(result, case)

        self.assertIn("Warnings:", text)
        self.assertIn("Single-screw open-stern propulsion factors", text)
        self.assertIn("tentative", text)

    def test_result_to_markdown_rejects_bad_result_shape(self):
        with self.assertRaisesRegex(ValueError, "result must be an object"):
            result_to_markdown([])
        with self.assertRaisesRegex(ValueError, "result.project must be an object"):
            result_to_markdown({})
        with self.assertRaisesRegex(ValueError, "result.engineering_review.warnings must be a list"):
            result_to_markdown({
                "project": {"name": "Example", "run_id": "1"},
                "engineering_review": {"note": "note", "statuses": ["status"], "warnings": "bad"},
                "derived": {},
                "modeling": {},
                "applicability": [],
                "speeds": []
            })

    def test_result_to_markdown_rejects_bad_rows(self):
        result = evaluate_case(json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text()), point_count=1)
        result["applicability"] = ["bad"]
        with self.assertRaisesRegex(ValueError, "result.applicability rows must be objects"):
            result_to_markdown(result)

        result = evaluate_case(json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text()), point_count=1)
        del result["speeds"][0]["total_resistance_n"]
        with self.assertRaisesRegex(ValueError, "result.speeds.total_resistance_n is required"):
            result_to_markdown(result)

    def test_result_to_markdown_rejects_non_finite_numbers(self):
        result = evaluate_case(json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text()), point_count=1)
        result["derived"]["mean_draft_m"] = "bad"
        with self.assertRaisesRegex(ValueError, "result.derived.mean_draft_m must be a finite number"):
            result_to_markdown(result)

        result = evaluate_case(json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text()), point_count=1)
        result["applicability"][0]["value"] = True
        with self.assertRaisesRegex(ValueError, "result.applicability.value must be a finite number"):
            result_to_markdown(result)

        result = evaluate_case(json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text()), point_count=1)
        result["speeds"][0]["effective_power_kw"] = float("inf")
        with self.assertRaisesRegex(ValueError, "result.speeds.effective_power_kw must be a finite number"):
            result_to_markdown(result)

    def test_result_to_markdown_rejects_bad_case_summary_shape(self):
        result = evaluate_case(json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text()), point_count=1)
        with self.assertRaisesRegex(ValueError, "case must be an object"):
            result_to_markdown(result, [])
        with self.assertRaisesRegex(ValueError, "case.speed_sweep must be an object"):
            result_to_markdown(result, {})

    def test_result_to_markdown_rejects_bad_case_summary_values(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        result = evaluate_case(case, point_count=1)
        case["speed_sweep"]["initial_speed_knots"] = "fast"
        with self.assertRaisesRegex(ValueError, "case.speed_sweep.initial_speed_knots must be a finite number"):
            result_to_markdown(result, case)

        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        result = evaluate_case(case, point_count=1)
        case["modeling"]["air_drag"] = "yes"
        with self.assertRaisesRegex(ValueError, "case.modeling.air_drag must be boolean"):
            result_to_markdown(result, case)


if __name__ == "__main__":
    unittest.main()
