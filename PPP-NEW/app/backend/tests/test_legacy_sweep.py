import json
import tempfile
import unittest
from pathlib import Path

from ppp_core import candidate_option_sets, run_oracle_sweep


ROOT = Path(__file__).resolve().parents[3]


class LegacySweepTest(unittest.TestCase):
    def test_candidate_option_sets(self):
        options = candidate_option_sets(stern_corrections=[0, -10], pitch_diameter_ratios=[0.8], water_type_codes=[2, 3])

        self.assertEqual(len(options), 4)
        self.assertEqual(options[0], {"stern_correction": 0, "pitch_diameter_ratio": 0.8, "water_type_code": 2})
        self.assertEqual(options[3], {"stern_correction": -10, "pitch_diameter_ratio": 0.8, "water_type_code": 3})

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
            self.assertEqual(result["successful_attempts"][0]["options"]["pitch_diameter_ratio"], 0.8)


if __name__ == "__main__":
    unittest.main()
