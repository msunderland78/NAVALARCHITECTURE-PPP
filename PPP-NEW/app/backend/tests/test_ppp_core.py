import json
import unittest
from pathlib import Path

from ppp_core import evaluate_case


ROOT = Path(__file__).resolve().parents[3]


class PppCoreTest(unittest.TestCase):
    def test_sample_case_modern_result_fixture(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        expected = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_modern_result.json").read_text())
        result = evaluate_case(case, point_count=2)

        self.assertEqual(result, expected)

    def test_sample_case_derivations(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        result = evaluate_case(case, point_count=1)

        self.assertEqual(result["project"]["name"], "Holtrop and Mennen Example")
        self.assertAlmostEqual(result["derived"]["mean_draft_m"], 11.0)
        self.assertAlmostEqual(result["derived"]["prismatic_coefficient"], 0.6122448979591837)
        self.assertAlmostEqual(result["derived"]["beam_draft_ratio"], 2.909090909090909)
        self.assertAlmostEqual(result["derived"]["draft_beam_ratio"], 0.34375)
        self.assertAlmostEqual(result["derived"]["lwl_beam_ratio"], 6.625)
        self.assertAlmostEqual(result["derived"]["beam_lwl_ratio"], 0.1509433962264151)
        self.assertAlmostEqual(result["derived"]["lcb_m_from_fp"], 107.59)
        self.assertAlmostEqual(result["derived"]["lcb_percent_lwl_from_fp"], 50.75)
        self.assertAlmostEqual(result["derived"]["midship_area_m2"], 344.96)
        self.assertAlmostEqual(result["derived"]["waterplane_area_m2"], 5088.0)
        self.assertAlmostEqual(result["derived"]["displacement_volume_m3"], 44774.4)
        self.assertAlmostEqual(result["derived"]["length_displacement_ratio"], 5.970251173727414)
        self.assertAlmostEqual(result["derived"]["displacement_mass_tonnes"], 45932.713728)
        self.assertEqual(result["modeling"]["wetted_surface_mode"], "user")
        self.assertAlmostEqual(result["modeling"]["wetted_surface_m2"], 7890.0)
        self.assertEqual(result["modeling"]["half_angle_entrance_mode"], "user")
        self.assertAlmostEqual(result["modeling"]["half_angle_entrance_degrees"], 12.11)

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

    def test_unsupported_modeling_modes(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["modeling"]["wetted_surface_mode"] = "estimated"
        with self.assertRaisesRegex(ValueError, "modeling.wetted_surface_mode is not supported"):
            evaluate_case(case, point_count=1)

        case["modeling"]["wetted_surface_mode"] = "user"
        case["modeling"]["half_angle_entrance_mode"] = "estimated"
        with self.assertRaisesRegex(ValueError, "modeling.half_angle_entrance_mode is not supported"):
            evaluate_case(case, point_count=1)

    def test_unsupported_case_enums(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["features"]["stern_type"] = "unknown"
        with self.assertRaisesRegex(ValueError, "features.stern_type is not supported"):
            evaluate_case(case, point_count=1)

        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["propulsion"]["type"] = "unknown"
        with self.assertRaisesRegex(ValueError, "propulsion.type is not supported"):
            evaluate_case(case, point_count=1)

        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["water"]["type"] = "unknown"
        with self.assertRaisesRegex(ValueError, "water.type is not supported"):
            evaluate_case(case, point_count=1)

    def test_invalid_coefficients(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["hull"]["block_coefficient"] = 1.1
        with self.assertRaisesRegex(ValueError, "hull.block_coefficient must be less than or equal to 1"):
            evaluate_case(case, point_count=1)

        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["hull"]["midship_coefficient"] = 1.1
        with self.assertRaisesRegex(ValueError, "hull.midship_coefficient must be less than or equal to 1"):
            evaluate_case(case, point_count=1)

        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["hull"]["waterplane_coefficient"] = 1.1
        with self.assertRaisesRegex(ValueError, "hull.waterplane_coefficient must be less than or equal to 1"):
            evaluate_case(case, point_count=1)

    def test_invalid_feature_and_modeling_dimensions(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["features"]["bulb_area_station_0_m2"] = -1
        with self.assertRaisesRegex(ValueError, "features.bulb_area_station_0_m2 must be non-negative"):
            evaluate_case(case, point_count=1)

        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["modeling"]["deckhouse_cargo_frontal_area_m2"] = -1
        with self.assertRaisesRegex(ValueError, "modeling.deckhouse_cargo_frontal_area_m2 must be non-negative"):
            evaluate_case(case, point_count=1)

        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["modeling"]["half_angle_entrance_degrees"] = 0
        with self.assertRaisesRegex(ValueError, "modeling.half_angle_entrance_degrees must be positive"):
            evaluate_case(case, point_count=1)

    def test_invalid_propulsion_dimensions(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["propulsion"]["propeller_diameter_m"] = 0
        with self.assertRaisesRegex(ValueError, "propulsion.propeller_diameter_m must be positive"):
            evaluate_case(case, point_count=1)

        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["propulsion"]["expanded_area_ratio"] = 1.1
        with self.assertRaisesRegex(ValueError, "propulsion.expanded_area_ratio must be between 0 and 1"):
            evaluate_case(case, point_count=1)

        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["propulsion"]["pitch_diameter_ratio"] = -1
        with self.assertRaisesRegex(ValueError, "propulsion.pitch_diameter_ratio must be non-negative"):
            evaluate_case(case, point_count=1)

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
