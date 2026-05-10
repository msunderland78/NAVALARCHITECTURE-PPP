import json
import unittest
from pathlib import Path

from ppp_core import route


ROOT = Path(__file__).resolve().parents[3]


class ApiTest(unittest.TestCase):
    def test_health_route(self):
        status, content_type, payload = route("GET", "/health")

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload, {"status": "ok"})

    def test_evaluate_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({"case": case, "point_count": 2}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(len(payload["speeds"]), 2)
        self.assertAlmostEqual(payload["speeds"][0]["total_resistance_n"], 391005.78552961635)

    def test_csv_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/export/csv", body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/csv")
        self.assertIn("speed_knots,speed_mps", payload)
        self.assertIn("391005.78552961635", payload)

    def test_missing_route(self):
        status, content_type, payload = route("GET", "/missing")

        self.assertEqual(status, 404)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload, {"error": "not found"})


if __name__ == "__main__":
    unittest.main()
