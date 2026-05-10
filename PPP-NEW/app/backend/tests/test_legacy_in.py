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
        self.assertEqual(lines[4], "8 7890 12.11")
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

    def test_generate_candidate_legacy_in_appendage_area_mode(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["appendages"]["mode"] = "equivalent_area_form_factor"
        case["appendages"]["equivalent_wetted_area_form_factor_m2"] = 250.0
        text = generate_candidate_legacy_in(case)

        self.assertEqual(text.splitlines()[2], "250 250 21 4 16 0 1")


if __name__ == "__main__":
    unittest.main()
