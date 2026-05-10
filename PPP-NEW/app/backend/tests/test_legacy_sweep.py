import json
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

from ppp_core import candidate_option_sets, run_oracle_sweep
from ppp_core.legacy_in import generate_candidate_legacy_in


ROOT = Path(__file__).resolve().parents[3]


class LegacySweepTest(unittest.TestCase):
    def test_candidate_option_sets(self):
        options = candidate_option_sets(stern_corrections=[0, -10], pitch_diameter_ratios=[0.8], water_type_codes=[2, 3])

        self.assertEqual(len(options), 4)
        self.assertEqual(options[0], {"stern_correction": 0, "pitch_diameter_ratio": 0.8, "water_type_code": 2})
        self.assertEqual(options[3], {"stern_correction": -10, "pitch_diameter_ratio": 0.8, "water_type_code": 3})

    def test_candidate_option_sets_appendage_fields(self):
        options = candidate_option_sets(stern_corrections=[0], pitch_diameter_ratios=[0.8], water_type_codes=[3], appendage_primary_values=[0.05, 5], appendage_model_totals=[0, 0.05])

        self.assertEqual(len(options), 4)
        self.assertEqual(options[0]["appendage_primary_value"], 0.05)
        self.assertEqual(options[0]["appendage_model_total"], 0)
        self.assertEqual(options[3]["appendage_primary_value"], 5)
        self.assertEqual(options[3]["appendage_model_total"], 0.05)

    def test_candidate_option_sets_first_record_order(self):
        options = candidate_option_sets(stern_corrections=[0], pitch_diameter_ratios=[0.8], water_type_codes=[3], first_record_orders=["depth_before_drafts", "drafts_before_depth"])

        self.assertEqual(len(options), 2)
        self.assertEqual(options[0]["first_record_order"], "depth_before_drafts")
        self.assertEqual(options[1]["first_record_order"], "drafts_before_depth")

    def test_candidate_option_sets_empty_values_are_not_defaulted(self):
        options = candidate_option_sets(stern_corrections=[], pitch_diameter_ratios=[0.8], water_type_codes=[3])

        self.assertEqual(options, [])

    def test_run_oracle_sweep_with_fake_wine(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        option_sets = candidate_option_sets(stern_corrections=[0], pitch_diameter_ratios=[0, 0.8], water_type_codes=[1])
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            fake_exe = temp / "fake.exe"
            fake_exe.write_bytes(b"legacy")
            fake_wine = temp / "fake_wine.sh"
            fake_wine.write_text("#!/bin/sh\nif grep -q '0.8 0.8 1' IN; then printf 'Calculation Completed Successfully!' > OUT; fi\nexit 0\n")
            fake_wine.chmod(0o755)
            result = run_oracle_sweep(case, fake_exe, temp / "sweep", option_sets, wine=str(fake_wine), timeout_seconds=5)

            self.assertEqual(result["attempt_count"], 2)
            self.assertEqual(result["out_count"], 1)
            self.assertTrue(result["successful_attempts"][0]["out_exists"])
            successful = result["successful_attempts"][0]
            expected_input = generate_candidate_legacy_in(case, successful["options"])
            self.assertEqual(successful["options"]["pitch_diameter_ratio"], 0.8)
            self.assertEqual(successful["input_line_count"], 8)
            self.assertEqual(successful["input_first_record"], "212 32 21 11 11 321")
            self.assertEqual(successful["input_sha256"], sha256(expected_input.encode("ascii")).hexdigest())


if __name__ == "__main__":
    unittest.main()
