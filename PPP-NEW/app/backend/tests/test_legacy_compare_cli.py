import json
import tempfile
import unittest
from pathlib import Path

from ppp_core.legacy_compare_cli import main


ROOT = Path(__file__).resolve().parents[3]


class LegacyCompareCliTest(unittest.TestCase):
    def test_main_writes_comparison_summary(self):
        case_path = ROOT / "tests" / "fixtures" / "pppin_sample_import.json"
        out_path = ROOT / "tests" / "fixtures" / "representative_legacy.OUT"
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "comparison.json"
            code = main([
                str(case_path),
                str(out_path),
                "--point-count",
                "2",
                "--field",
                "frictional_resistance_n",
                "--field",
                "wave_resistance_n",
                "--output",
                str(output)
            ])
            result = json.loads(output.read_text())

            self.assertEqual(code, 0)
            self.assertEqual(result["matched_speed_count"], 2)
            self.assertEqual(result["case_json"], str(case_path))
            self.assertEqual(result["legacy_out"], str(out_path))
            self.assertEqual(result["comparisons"][0]["fields"][0]["field"], "frictional_resistance_n")
            self.assertLess(result["comparisons"][0]["fields"][0]["absolute_delta"], 0.3)
            self.assertEqual(result["comparisons"][0]["fields"][1]["status"], "missing_modern")


if __name__ == "__main__":
    unittest.main()
