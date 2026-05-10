import json
import unittest
from pathlib import Path

from ppp_core import evaluate_case


ROOT = Path(__file__).resolve().parents[3]


class PppCoreTest(unittest.TestCase):
    def test_sample_case_derivations(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        result = evaluate_case(case, point_count=1)

        self.assertEqual(result["project"]["name"], "Holtrop and Mennen Example")
        self.assertAlmostEqual(result["derived"]["mean_draft_m"], 11.0)
        self.assertAlmostEqual(result["derived"]["prismatic_coefficient"], 0.6122448979591837)
        self.assertAlmostEqual(result["derived"]["beam_draft_ratio"], 2.909090909090909)
        self.assertAlmostEqual(result["derived"]["lwl_beam_ratio"], 6.625)
        self.assertAlmostEqual(result["derived"]["lcb_m_from_fp"], 107.59)

    def test_sample_case_speed_terms(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        result = evaluate_case(case, point_count=2)

        first = result["speeds"][0]
        second = result["speeds"][1]
        self.assertAlmostEqual(first["speed_knots"], 15.0)
        self.assertAlmostEqual(second["speed_knots"], 17.0)
        self.assertAlmostEqual(first["speed_mps"], 7.71666)
        self.assertAlmostEqual(first["froude_number"], 0.16923925200101986)
        self.assertAlmostEqual(first["speed_length_ratio"], 0.5687623106703097)
        self.assertAlmostEqual(first["reynolds_number"], 1376687833.982715)
        self.assertAlmostEqual(first["friction_coefficient"], 0.001471656717746287)
        self.assertAlmostEqual(first["frictional_resistance_n"], 354653.773723008)
        self.assertAlmostEqual(first["appendage_resistance_n"], 17732.6886861504)
        self.assertEqual(first["appendage_mode"], "percent_bare_hull_resistance")
        self.assertAlmostEqual(first["implemented_resistance_subtotal_n"], 372386.4624091584)
        self.assertAlmostEqual(first["design_margin_resistance_n"], 18619.32312045792)
        self.assertAlmostEqual(first["total_resistance_n"], 391005.78552961635)
        self.assertAlmostEqual(first["effective_power_kw"], 3017.258704964969)
        self.assertEqual(first["resistance_status"], "partial_source_safe_components")
        self.assertIsNone(first["residual_resistance_coefficient"])
        self.assertIsNone(first["correlation_allowance_coefficient"])
        self.assertIsNone(first["rf_form_resistance_n"])
        self.assertIsNone(first["wave_resistance_n"])
        self.assertIsNone(first["wake_fraction"])
        self.assertIsNone(first["thrust_deduction"])
        self.assertIsNone(first["required_thrust_n"])
        self.assertIsNone(first["hull_efficiency"])
        self.assertIsNone(first["relative_rotative_efficiency"])

    def test_sample_case_applicability(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        result = evaluate_case(case, point_count=1)

        self.assertTrue(all(check["ok"] for check in result["applicability"]))

    def test_appendage_equivalent_area_mode(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["appendages"]["mode"] = "equivalent_area_form_factor"
        case["appendages"]["percent_bare_hull_resistance"] = 99.0
        case["appendages"]["equivalent_wetted_area_form_factor_m2"] = 250.0
        result = evaluate_case(case, point_count=1)
        first = result["speeds"][0]
        expected_appendage = first["frictional_resistance_n"] / case["modeling"]["wetted_surface_m2"] * 250.0

        self.assertEqual(first["appendage_mode"], "equivalent_area_form_factor")
        self.assertAlmostEqual(first["appendage_resistance_n"], expected_appendage)
        self.assertAlmostEqual(first["implemented_resistance_subtotal_n"], first["frictional_resistance_n"] + expected_appendage)


if __name__ == "__main__":
    unittest.main()
