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
            self.assertEqual(result["comparisons"][0]["fields"][1]["status"], "numeric_delta")
            self.assertEqual(result["summary"]["status_counts"], {"numeric_delta": 4})
            self.assertEqual(result["summary"]["max_relative_delta"]["field"], "wave_resistance_n")
            self.assertTrue(result["passed"])
            self.assertEqual(result["failures"], [])

    def test_main_returns_failure_for_thresholds(self):
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
                "--max-absolute-delta",
                "0.1",
                "--max-relative-delta",
                "0.0000001",
                "--fail-on-missing-modern",
                "--require-matched-speed-count",
                "3",
                "--output",
                str(output)
            ])
            result = json.loads(output.read_text())

            self.assertEqual(code, 1)
            self.assertFalse(result["passed"])
            self.assertEqual([failure["rule"] for failure in result["failures"]], [
                "require_matched_speed_count",
                "max_absolute_delta",
                "max_relative_delta"
            ])

    def test_main_passes_captured_oracle_thresholds(self):
        case_path = ROOT / "tests" / "fixtures" / "pppin_sample_import.json"
        out_path = ROOT / "tests" / "fixtures" / "pppin_sample_legacy_oracle.OUT"
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "comparison.json"
            code = main([
                str(case_path),
                str(out_path),
                "--point-count",
                "8",
                "--require-matched-speed-count",
                "8",
                "--max-absolute-delta",
                "100",
                "--fail-on-missing-modern",
                "--output",
                str(output)
            ])
            result = json.loads(output.read_text())

            self.assertEqual(code, 0)
            self.assertTrue(result["passed"])
            self.assertEqual(result["failures"], [])
            self.assertLess(result["summary"]["max_absolute_delta"]["absolute_delta"], 100)

    def test_main_passes_estimated_mode_oracle_thresholds(self):
        case_path = ROOT / "tests" / "fixtures" / "pppin_sample_estimated_import.json"
        out_path = ROOT / "tests" / "fixtures" / "pppin_sample_estimated_legacy_oracle.OUT"
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "comparison.json"
            code = main([
                str(case_path),
                str(out_path),
                "--point-count",
                "8",
                "--require-matched-speed-count",
                "8",
                "--max-absolute-delta",
                "100",
                "--fail-on-missing-modern",
                "--output",
                str(output)
            ])
            result = json.loads(output.read_text())

            self.assertEqual(code, 0)
            self.assertTrue(result["passed"])
            self.assertEqual(result["failures"], [])
            self.assertLess(result["summary"]["max_absolute_delta"]["absolute_delta"], 100)


if __name__ == "__main__":
    unittest.main()
