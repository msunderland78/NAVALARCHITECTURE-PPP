import json
import unittest
from pathlib import Path

from ppp_core import compare_legacy_out_to_result, evaluate_case, merge_legacy_out_rows, route
from ppp_core.legacy_out import parse_legacy_out
from test_legacy_out import sample_out


ROOT = Path(__file__).resolve().parents[3]


class LegacyCompareTest(unittest.TestCase):
    def test_merge_legacy_out_rows(self):
        rows = merge_legacy_out_rows(parse_legacy_out(sample_out()))

        self.assertEqual(len(rows), 2)
        self.assertAlmostEqual(rows[0]["speed_knots"], 15.0)
        self.assertAlmostEqual(rows[0]["friction_coefficient"], 0.00147166)
        self.assertAlmostEqual(rows[0]["appendage_resistance_n"], 17732.7)
        self.assertAlmostEqual(rows[0]["total_resistance_n"], 391006.0)
        self.assertAlmostEqual(rows[0]["required_thrust_n"], 430000.0)

    def test_compare_legacy_out_to_result(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        modern_result = evaluate_case(case, 2)
        comparison = compare_legacy_out_to_result(parse_legacy_out(sample_out()), modern_result)
        first_fields = {field["field"]: field for field in comparison["comparisons"][0]["fields"]}

        self.assertEqual(comparison["matched_speed_count"], 2)
        self.assertEqual(comparison["unmatched_legacy_speeds"], [])
        self.assertEqual(comparison["unmatched_modern_speeds"], [])
        self.assertEqual(first_fields["frictional_resistance_n"]["status"], "numeric_delta")
        self.assertLess(first_fields["frictional_resistance_n"]["absolute_delta"], 0.3)
        self.assertEqual(first_fields["wave_resistance_n"]["status"], "numeric_delta")
        self.assertEqual(first_fields["required_thrust_n"]["status"], "numeric_delta")
        self.assertEqual(comparison["summary"]["status_counts"]["numeric_delta"], 42)
        self.assertNotIn("missing_modern", comparison["summary"]["status_counts"])
        self.assertEqual(comparison["summary"]["max_absolute_delta"]["field"], "rf_form_resistance_n")
        self.assertEqual(comparison["summary"]["max_relative_delta"]["field"], "transom_resistance_n")

    def test_compare_captured_oracle_fixture(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        oracle_out = (ROOT / "tests" / "fixtures" / "pppin_sample_legacy_oracle.OUT").read_text()
        modern_result = evaluate_case(case, 8)
        comparison = compare_legacy_out_to_result(parse_legacy_out(oracle_out), modern_result)

        self.assertTrue(comparison["legacy_calculation_completed"])
        self.assertEqual(comparison["matched_speed_count"], 8)
        self.assertEqual(comparison["unmatched_legacy_speeds"], [])
        self.assertEqual(comparison["unmatched_modern_speeds"], [])
        self.assertEqual(comparison["summary"]["status_counts"]["numeric_delta"], 168)
        self.assertNotIn("missing_modern", comparison["summary"]["status_counts"])
        self.assertLess(comparison["summary"]["max_absolute_delta"]["absolute_delta"], 100)

    def test_compare_estimated_mode_oracle_fixture(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_estimated_import.json").read_text())
        oracle_out = (ROOT / "tests" / "fixtures" / "pppin_sample_estimated_legacy_oracle.OUT").read_text()
        modern_result = evaluate_case(case, 8)
        comparison = compare_legacy_out_to_result(parse_legacy_out(oracle_out), modern_result)

        self.assertTrue(comparison["legacy_calculation_completed"])
        self.assertEqual(comparison["matched_speed_count"], 8)
        self.assertEqual(comparison["unmatched_legacy_speeds"], [])
        self.assertEqual(comparison["unmatched_modern_speeds"], [])
        self.assertEqual(comparison["summary"]["status_counts"]["numeric_delta"], 168)
        self.assertNotIn("missing_modern", comparison["summary"]["status_counts"])
        self.assertLess(comparison["summary"]["max_absolute_delta"]["absolute_delta"], 100)

    def test_compare_reports_unmatched_speeds(self):
        modern_result = {"speeds": [{"speed_knots": 20.0, "speed_mps": 10.28888}]}
        comparison = compare_legacy_out_to_result(parse_legacy_out(sample_out()), modern_result)

        self.assertEqual(comparison["matched_speed_count"], 0)
        self.assertEqual(comparison["unmatched_legacy_speeds"], [15.0, 17.0])
        self.assertEqual(comparison["unmatched_modern_speeds"], [20.0])
        self.assertEqual(comparison["summary"]["status_counts"], {})
        self.assertIsNone(comparison["summary"]["max_absolute_delta"])
        self.assertIsNone(comparison["summary"]["max_relative_delta"])

    def test_compare_out_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({
            "case": case,
            "point_count": 2,
            "legacy_out_text": sample_out(),
            "fields": ["frictional_resistance_n", "wave_resistance_n"]
        }).encode("utf-8")
        status, content_type, payload = route("POST", "/api/compare/out", body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["matched_speed_count"], 2)
        self.assertEqual(payload["comparisons"][0]["fields"][0]["field"], "frictional_resistance_n")

    def test_compare_out_route_uses_speed_tolerance(self):
        modern_result = {
            "speeds": [
                {
                    "speed_knots": 15.0004,
                    "frictional_resistance_n": 354653.8
                }
            ]
        }
        body = json.dumps({
            "modern_result": modern_result,
            "legacy_out_text": sample_out(),
            "fields": ["frictional_resistance_n"],
            "speed_tolerance": 0.001
        }).encode("utf-8")
        status, content_type, payload = route("POST", "/api/compare/out", body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["matched_speed_count"], 1)
        self.assertEqual(payload["unmatched_legacy_speeds"], [17.0])
        self.assertEqual(payload["unmatched_modern_speeds"], [])


if __name__ == "__main__":
    unittest.main()
