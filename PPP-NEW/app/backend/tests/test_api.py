import json
import unittest
from pathlib import Path

from ppp_core import route
from test_legacy_ppp import sample_ole_document
from server import FRONTEND


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

    def test_json_export_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/export/json", body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["project"]["run_id"], "Test 1.0")
        self.assertAlmostEqual(payload["speeds"][0]["effective_power_kw"], 3017.258704964969)

    def test_import_route(self):
        status, content_type, payload = route("POST", "/api/import/ppp", sample_ole_document())

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["project"]["name"], "Holtrop and Mennen Example")
        self.assertAlmostEqual(payload["hull"]["lwl_m"], 212.0)

    def test_bad_import_route(self):
        status, content_type, payload = route("POST", "/api/import/ppp", b"not a ppp file")

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertIn("not an OLE Compound Document", payload["error"])

    def test_missing_route(self):
        status, content_type, payload = route("GET", "/missing")

        self.assertEqual(status, 404)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload, {"error": "not found"})

    def test_frontend_files_exist(self):
        self.assertTrue((FRONTEND / "index.html").exists())
        self.assertTrue((FRONTEND / "styles.css").exists())
        self.assertTrue((FRONTEND / "app.js").exists())
        self.assertIn("case-form", (FRONTEND / "index.html").read_text())
        self.assertIn("checks", (FRONTEND / "index.html").read_text())
        self.assertIn("/api/evaluate", (FRONTEND / "app.js").read_text())
        self.assertIn("case-json-button", (FRONTEND / "index.html").read_text())
        self.assertIn("import-json-file", (FRONTEND / "index.html").read_text())
        self.assertIn("print-button", (FRONTEND / "index.html").read_text())
        self.assertIn("@media print", (FRONTEND / "styles.css").read_text())
        self.assertIn("size: 8.5in 11in", (FRONTEND / "styles.css").read_text())
        self.assertIn("margin: 1in", (FRONTEND / "styles.css").read_text())
        self.assertIn("width: 6.5in", (FRONTEND / "styles.css").read_text())


if __name__ == "__main__":
    unittest.main()
