import json
import unittest
from pathlib import Path

from ppp_core.legacy_in import generate_candidate_legacy_in


ROOT = Path(__file__).resolve().parents[3]


class LegacyInTest(unittest.TestCase):
    def test_generate_candidate_legacy_in(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        text = generate_candidate_legacy_in(case)
        fixture = (ROOT / "tests" / "fixtures" / "pppin_sample_candidate.IN").read_text()
        lines = text.splitlines()

        self.assertEqual(text, fixture)
        self.assertEqual(len(lines), 8)
        self.assertEqual(lines[0], "212 32 21 11 11 321")
        self.assertEqual(lines[1], "0.6 0.98 0.75 0.05")
        self.assertEqual(lines[2], "0.05 0 21 4 16 0 1")
        self.assertEqual(lines[3], "-0.75")
        self.assertEqual(lines[4], "7890 12.11 8")
        self.assertEqual(lines[5], "0.8 0 3")
        self.assertEqual(lines[6], "15 2")
        self.assertEqual(lines[7], "1025.87 1.18831e-06")

    def test_generate_candidate_legacy_in_options(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        text = generate_candidate_legacy_in(case, {
            "stern_correction": -10,
            "pitch_diameter_ratio": 0.8,
            "water_type_code": 2,
            "appendage_primary_value": 5,
            "appendage_model_total": 0.05
        })
        lines = text.splitlines()

        self.assertEqual(lines[2], "5 0.05 21 4 16 -10 1")
        self.assertEqual(lines[5], "0.8 0.8 2")

    def test_generate_candidate_legacy_in_rejects_bad_options_directly(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())

        with self.assertRaisesRegex(ValueError, "options must be an object"):
            generate_candidate_legacy_in(case, "bad")
        with self.assertRaisesRegex(ValueError, "stern_correction must be a finite number"):
            generate_candidate_legacy_in(case, {"stern_correction": True})
        with self.assertRaisesRegex(ValueError, "pitch_diameter_ratio must be a finite number"):
            generate_candidate_legacy_in(case, {"pitch_diameter_ratio": float("inf")})

    def test_generate_candidate_legacy_in_fresh_water_code(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["water"] = {
            "type": "fresh_water_15_c",
            "density_kg_m3": 999.1026,
            "kinematic_viscosity_m2_s": 0.0000011386
        }
        text = generate_candidate_legacy_in(case)
        lines = text.splitlines()

        self.assertEqual(lines[5], "0.8 0 2")
        self.assertEqual(lines[7], "999.1026 1.1386e-06")

    def test_generate_candidate_legacy_in_propulsion_type_codes(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["propulsion"]["type"] = "single_screw_open_flow_stern"
        open_flow = generate_candidate_legacy_in(case).splitlines()

        case["propulsion"]["type"] = "twin_screw"
        twin_screw = generate_candidate_legacy_in(case).splitlines()

        self.assertEqual(open_flow[2], "0.05 0 21 4 16 0 2")
        self.assertEqual(twin_screw[2], "0.05 0 21 4 16 0 3")

    def test_generate_candidate_legacy_in_old_propeller_record_order(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        text = generate_candidate_legacy_in(case, {"propeller_record_order": "dp_wetted_half"})

        self.assertEqual(text.splitlines()[4], "8 7890 12.11")

    def test_generate_candidate_legacy_in_estimated_modeling_values(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["modeling"]["wetted_surface_mode"] = "estimated"
        case["modeling"]["half_angle_entrance_mode"] = "estimated"
        case["modeling"]["wetted_surface_m2"] = 1
        case["modeling"]["half_angle_entrance_degrees"] = 1
        text = generate_candidate_legacy_in(case)

        self.assertEqual(text.splitlines()[4], "8074.58997792 12.5031897652 8")

    def test_generate_candidate_legacy_in_first_record_order(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        text = generate_candidate_legacy_in(case, {"first_record_order": "drafts_before_depth"})

        self.assertEqual(text.splitlines()[0], "212 32 11 11 21 321")

    def test_generate_candidate_legacy_in_appendage_area_mode(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["appendages"]["mode"] = "equivalent_area_form_factor"
        case["appendages"]["equivalent_wetted_area_form_factor_m2"] = 250.0
        text = generate_candidate_legacy_in(case)

        self.assertEqual(text.splitlines()[2], "250 250 21 4 16 0 1")


if __name__ == "__main__":
    unittest.main()
