import json
import unittest
from pathlib import Path

from ppp_core import route
from test_legacy_ppp import sample_ole_document
from server import FRONTEND, request_content_length, request_path


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
        self.assertAlmostEqual(payload["speeds"][0]["total_resistance_n"], 610051.8852955248)

    def test_evaluate_route_defaults_to_legacy_eight_speed_run(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({"case": case}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(len(payload["speeds"]), 8)
        self.assertAlmostEqual(payload["speeds"][-1]["speed_knots"], 29.0)

    def test_bad_evaluate_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["hull"]["lwl_m"] = 0
        body = json.dumps({"case": case, "point_count": 2}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "hull.lwl_m must be positive")

    def test_malformed_evaluate_payload_route(self):
        status, content_type, payload = route("POST", "/api/evaluate", b'{"case": null}')

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertIn("object is not subscriptable", payload["error"])

        status, content_type, payload = route("POST", "/api/evaluate", b"\xff")

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertIn("invalid start byte", payload["error"])

    def test_bad_point_count_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({"case": case, "point_count": 0}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "point_count must be between 1 and 20")

    def test_point_count_route_rejects_browser_max_overflow(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({"case": case, "point_count": 21}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "point_count must be between 1 and 20")

    def test_point_count_route_rejects_fractional_values(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({"case": case, "point_count": 2.5}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "point_count must be an integer")

        body = json.dumps({"case": case, "point_count": True}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "point_count must be an integer")

    def test_bad_speed_increment_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["speed_sweep"]["speed_increment_knots"] = 0
        body = json.dumps({"case": case, "point_count": 2}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "speed_sweep.speed_increment_knots must be positive when point_count is greater than 1")

    def test_bad_coefficient_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["hull"]["block_coefficient"] = 1.1
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "hull.block_coefficient must be less than or equal to 1")

    def test_bad_waterplane_coefficient_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["hull"]["waterplane_coefficient"] = 0
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "hull.waterplane_coefficient must be positive")

    def test_bad_propulsion_dimension_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["propulsion"]["expanded_area_ratio"] = -1
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "propulsion.expanded_area_ratio must be between 0 and 1")

    def test_bad_appendage_mode_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["appendages"]["mode"] = "unknown"
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "appendages.mode is not supported")

    def test_bad_water_type_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["water"]["type"] = "unknown"
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "water.type is not supported")

    def test_bad_non_finite_numeric_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["water"]["density_kg_m3"] = float("nan")
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "water.density_kg_m3 must be finite")

    def test_bad_non_finite_modeling_numeric_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["modeling"]["half_angle_entrance_degrees"] = float("nan")
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "modeling.half_angle_entrance_degrees must be finite")

    def test_bad_formula_domain_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["hull"]["block_coefficient"] = case["hull"]["midship_coefficient"]
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "derived prismatic_coefficient must be less than 1")

        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["hull"]["block_coefficient"] = 0.2
        case["hull"]["midship_coefficient"] = 0.8
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "derived prismatic_coefficient must be greater than 0.25")

        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["modeling"]["half_angle_entrance_degrees"] = 90
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "modeling.half_angle_entrance_degrees must be less than 90")

        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["hull"]["lcb_percent_lwl_from_midships_forward_positive"] = -30
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "derived run length factor must be positive")

    def test_bad_appendage_area_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["appendages"]["equivalent_wetted_area_form_factor_m2"] = -1
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "appendages.equivalent_wetted_area_form_factor_m2 must be non-negative")

    def test_bad_modeling_mode_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["modeling"]["wetted_surface_mode"] = "unknown"
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "modeling.wetted_surface_mode is not supported")

    def test_estimated_modeling_mode_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["modeling"]["wetted_surface_mode"] = "estimated"
        case["modeling"]["half_angle_entrance_mode"] = "estimated"
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertAlmostEqual(payload["modeling"]["wetted_surface_m2"], 8074.589977924038)
        self.assertAlmostEqual(payload["modeling"]["half_angle_entrance_degrees"], 12.503189765172571)

    def test_air_drag_disabled_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["modeling"]["air_drag"] = False
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertAlmostEqual(payload["speeds"][0]["air_resistance_n"], 0.0)

    def test_bad_air_drag_type_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        case["modeling"]["air_drag"] = "false"
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/evaluate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "modeling.air_drag must be boolean")

    def test_csv_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/export/csv", body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/csv")
        self.assertIn("speed_knots,speed_mps", payload)
        self.assertIn("610051.8852955248", payload)

    def test_json_export_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/export/json", body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["project"]["run_id"], "Test 1.0")
        self.assertEqual(payload["engineering_review"]["status"], "partial_source_safe_components")
        self.assertAlmostEqual(payload["speeds"][0]["effective_power_kw"], 4707.562981184565)

    def test_report_markdown_export_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({"case": case, "point_count": 1}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/export/report.md", body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/markdown")
        self.assertIn("# Holtrop and Mennen Example", payload)
        self.assertIn("Calculation status: `partial_source_safe_components`", payload)
        self.assertIn("## Input Summary", payload)
        self.assertIn("| Water type | salt_water_15_c |", payload)
        self.assertIn("| Propulsion type | single_screw_conventional_stern |", payload)
        self.assertIn("| Appendage mode | percent_bare_hull_resistance |", payload)
        self.assertIn("| Wetted surface mode | user |", payload)
        self.assertIn("| Half angle mode | user |", payload)

    def test_legacy_in_candidate_export_route(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({"case": case}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/export/legacy-in-candidate", body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/plain")
        self.assertIn("212 32 21 11 11 321", payload)
        self.assertIn("1025.87 1.18831e-06", payload)

    def test_legacy_in_candidate_export_route_options(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({
            "case": case,
            "options": {
                "first_record_order": "drafts_before_depth",
                "stern_correction": -10,
                "pitch_diameter_ratio": 0.8,
                "water_type_code": 2,
                "appendage_primary_value": 5,
                "appendage_model_total": 0.05
            }
        }).encode("utf-8")
        status, content_type, payload = route("POST", "/api/export/legacy-in-candidate", body)
        lines = payload.splitlines()

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/plain")
        self.assertEqual(lines[0], "212 32 11 11 21 321")
        self.assertEqual(lines[2], "5 0.05 21 4 16 -10 1")
        self.assertEqual(lines[5], "0.8 0.8 2")

    def test_legacy_in_candidate_export_route_rejects_bad_options(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        body = json.dumps({"case": case, "options": []}).encode("utf-8")
        status, content_type, payload = route("POST", "/api/export/legacy-in-candidate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "options must be an object")

        body = json.dumps({
            "case": case,
            "options": {
                "water_type_code": "2"
            }
        }).encode("utf-8")
        status, content_type, payload = route("POST", "/api/export/legacy-in-candidate", body)

        self.assertEqual(status, 400)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["error"], "water_type_code must be a finite number")

    def test_import_route(self):
        status, content_type, payload = route("POST", "/api/import/ppp", sample_ole_document())

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(payload["project"]["name"], "Holtrop and Mennen Example")
        self.assertAlmostEqual(payload["hull"]["lwl_m"], 212.0)

    def test_import_out_route(self):
        body = b"Input Verification:\nLength of Waterline LWL (m) = 212.0\n"
        status, content_type, payload = route("POST", "/api/import/out", body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertAlmostEqual(payload["input_verification"]["length_of_waterline_lwl_m"]["numeric_value"], 212.0)

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

    def test_server_request_path_ignores_query_string(self):
        self.assertEqual(request_path("/health?ready=1"), "/health")
        self.assertEqual(request_path("/app.js?v=20260511"), "/app.js")

    def test_server_request_content_length_validation(self):
        self.assertEqual(request_content_length("0"), 0)
        self.assertEqual(request_content_length("27"), 27)
        with self.assertRaisesRegex(ValueError, "Content-Length must be a non-negative integer"):
            request_content_length("abc")
        with self.assertRaisesRegex(ValueError, "Content-Length must be a non-negative integer"):
            request_content_length("-1")

    def test_frontend_files_exist(self):
        self.assertTrue((FRONTEND / "index.html").exists())
        self.assertTrue((FRONTEND / "styles.css").exists())
        self.assertTrue((FRONTEND / "app.js").exists())
        self.assertTrue((ROOT / "tests" / "fixtures" / "README.md").exists())
        self.assertIn("case-form", (FRONTEND / "index.html").read_text())
        self.assertIn("checks", (FRONTEND / "index.html").read_text())
        self.assertIn("engineering-note", (FRONTEND / "index.html").read_text())
        self.assertIn('name="speed_sweep.initial_speed_knots" type="number" min="0.01"', (FRONTEND / "index.html").read_text())
        self.assertIn('max="1"', (FRONTEND / "index.html").read_text())
        self.assertIn('min="0.01"', (FRONTEND / "index.html").read_text())
        self.assertIn("/api/evaluate", (FRONTEND / "app.js").read_text())
        self.assertIn("case-json-button", (FRONTEND / "index.html").read_text())
        self.assertIn('name="point_count" type="number" min="1" max="20" step="1" value="8"', (FRONTEND / "index.html").read_text())
        self.assertIn("report-button", (FRONTEND / "index.html").read_text())
        self.assertIn("legacy-in-button", (FRONTEND / "index.html").read_text())
        self.assertIn("import-json-file", (FRONTEND / "index.html").read_text())
        self.assertIn("import-out-file", (FRONTEND / "index.html").read_text())
        self.assertIn("legacy_options.first_record_order", (FRONTEND / "index.html").read_text())
        self.assertIn("legacy_options.propeller_record_order", (FRONTEND / "index.html").read_text())
        self.assertIn("legacy_options.speed_tolerance", (FRONTEND / "index.html").read_text())
        self.assertIn("print-button", (FRONTEND / "index.html").read_text())
        self.assertIn("@media print", (FRONTEND / "styles.css").read_text())
        self.assertIn("size: 8.5in 11in", (FRONTEND / "styles.css").read_text())
        self.assertIn("margin: 1in", (FRONTEND / "styles.css").read_text())
        self.assertIn("width: 6.5in", (FRONTEND / "styles.css").read_text())
        self.assertIn("WATER_PRESETS", (FRONTEND / "app.js").read_text())
        self.assertIn("fresh_water_15_c", (FRONTEND / "app.js").read_text())
        self.assertIn("appendages.mode", (FRONTEND / "index.html").read_text())
        self.assertIn("modeling.wetted_surface_mode", (FRONTEND / "index.html").read_text())
        self.assertIn("modeling.half_angle_entrance_mode", (FRONTEND / "index.html").read_text())
        self.assertIn('name="modeling.half_angle_entrance_degrees" type="number" min="0.01" max="89.99"', (FRONTEND / "index.html").read_text())
        self.assertIn("equivalent_wetted_area_form_factor_m2", (FRONTEND / "app.js").read_text())
        self.assertIn("required_thrust_n", (FRONTEND / "app.js").read_text())
        self.assertIn("RF*K1 N", (FRONTEND / "app.js").read_text())
        self.assertIn("/api/export/legacy-in-candidate", (FRONTEND / "app.js").read_text())
        self.assertIn("/api/export/report.md", (FRONTEND / "app.js").read_text())
        self.assertIn("CSV export failed", (FRONTEND / "app.js").read_text())
        self.assertIn("Import JSON failed", (FRONTEND / "app.js").read_text())
        self.assertIn("buildLegacyOptions", (FRONTEND / "app.js").read_text())
        self.assertIn("propeller_record_order", (FRONTEND / "app.js").read_text())
        self.assertIn("legacySpeedTolerance", (FRONTEND / "app.js").read_text())
        self.assertIn("speed_tolerance", (FRONTEND / "app.js").read_text())
        self.assertIn("/api/compare/out", (FRONTEND / "app.js").read_text())
        self.assertIn("numeric deltas", (FRONTEND / "app.js").read_text())
        self.assertIn("Engineering review status", (FRONTEND / "app.js").read_text())
        self.assertIn("review.warnings", (FRONTEND / "app.js").read_text())


if __name__ == "__main__":
    unittest.main()
