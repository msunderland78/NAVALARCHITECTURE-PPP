#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args(argv)
    base_url = args.base_url.rstrip("/")
    case = json.loads((FIXTURES / "pppin_sample_import.json").read_text())
    estimated_case = json.loads((FIXTURES / "pppin_sample_estimated_import.json").read_text())
    legacy_out = (FIXTURES / "pppin_sample_legacy_oracle.OUT").read_text()
    frontend = request_text(base_url, "GET", "/")

    checks = [
        check_json("health", request_json(base_url, "GET", "/health"), {"status": "ok"}),
        check_text_contains("frontend", frontend, "case-form"),
        check_text_contains("frontend engineering note", frontend, "engineering-note"),
        check_text_contains("frontend eight-point default", frontend, 'name="point_count" type="number" min="1" max="20" step="1" value="8"'),
        check_evaluate(base_url, case),
        check_air_drag_disabled(base_url, case),
        check_estimated_evaluate(base_url, estimated_case),
        check_csv_export(base_url, case),
        check_json_export(base_url, case),
        check_report_export(base_url, case),
        check_legacy_in_export(base_url, estimated_case),
        check_out_compare(base_url, case, legacy_out)
    ]
    result = {
        "base_url": base_url,
        "passed": all(check["passed"] for check in checks),
        "checks": checks
    }
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


def check_evaluate(base_url, case):
    payload = request_json(base_url, "POST", "/api/evaluate", {"case": case})
    review = payload.get("engineering_review", {})
    passed = (
        len(payload.get("speeds", [])) == 8
        and abs(payload["speeds"][0]["total_resistance_n"] - 610051.8852955248) < 1e-6
        and review.get("status") == "partial_source_safe_components"
    )
    return {
        "name": "evaluate user-mode sample",
        "passed": passed,
        "details": {
            "speed_count": len(payload.get("speeds", [])),
            "first_total_resistance_n": payload.get("speeds", [{}])[0].get("total_resistance_n"),
            "engineering_review_status": review.get("status")
        }
    }


def check_estimated_evaluate(base_url, case):
    payload = request_json(base_url, "POST", "/api/evaluate", {"case": case, "point_count": 1})
    modeling = payload.get("modeling", {})
    return {
        "name": "evaluate estimated-mode sample",
        "passed": abs(modeling.get("wetted_surface_m2", 0) - 8074.589977924038) < 1e-9 and abs(modeling.get("half_angle_entrance_degrees", 0) - 12.503189765172571) < 1e-9,
        "details": modeling
    }


def check_air_drag_disabled(base_url, case):
    payload_case = json.loads(json.dumps(case))
    payload_case["modeling"]["air_drag"] = False
    payload = request_json(base_url, "POST", "/api/evaluate", {"case": payload_case, "point_count": 1})
    return {
        "name": "evaluate air-drag disabled sample",
        "passed": payload.get("speeds", [{}])[0].get("air_resistance_n") == 0.0,
        "details": {
            "air_resistance_n": payload.get("speeds", [{}])[0].get("air_resistance_n")
        }
    }


def check_csv_export(base_url, case):
    text = request_text(base_url, "POST", "/api/export/csv", {"case": case, "point_count": 2})
    return {
        "name": "export CSV results",
        "passed": "speed_knots,speed_mps" in text and "610051.8852955248" in text,
        "details": {
            "length": len(text)
        }
    }


def check_json_export(base_url, case):
    payload = request_json(base_url, "POST", "/api/export/json", {"case": case, "point_count": 2})
    return {
        "name": "export JSON results",
        "passed": payload.get("project", {}).get("run_id") == "Test 1.0" and len(payload.get("speeds", [])) == 2,
        "details": {
            "run_id": payload.get("project", {}).get("run_id"),
            "speed_count": len(payload.get("speeds", []))
        }
    }


def check_report_export(base_url, case):
    text = request_text(base_url, "POST", "/api/export/report.md", {"case": case, "point_count": 2})
    return {
        "name": "export markdown report",
        "passed": "# Holtrop and Mennen Example" in text and "Calculation status: `partial_source_safe_components`" in text,
        "details": {
            "length": len(text)
        }
    }


def check_legacy_in_export(base_url, case):
    text = request_text(base_url, "POST", "/api/export/legacy-in-candidate", {"case": case})
    lines = text.splitlines()
    return {
        "name": "export estimated legacy IN",
        "passed": len(lines) >= 5 and lines[4] == "8074.58997792 12.5031897652 8",
        "details": {
            "line_5": lines[4] if len(lines) >= 5 else None
        }
    }


def check_out_compare(base_url, case, legacy_out):
    payload = request_json(base_url, "POST", "/api/compare/out", {
        "case": case,
        "point_count": 8,
        "legacy_out_text": legacy_out
    })
    max_delta = payload.get("summary", {}).get("max_absolute_delta") or {}
    return {
        "name": "compare captured legacy OUT",
        "passed": payload.get("matched_speed_count") == 8 and max_delta.get("absolute_delta", 10 ** 9) < 100,
        "details": {
            "matched_speed_count": payload.get("matched_speed_count"),
            "max_absolute_delta": max_delta
        }
    }


def check_json(name, actual, expected):
    return {
        "name": name,
        "passed": actual == expected,
        "details": actual
    }


def check_text_contains(name, text, needle):
    return {
        "name": name,
        "passed": needle in text,
        "details": {
            "needle": needle,
            "length": len(text)
        }
    }


def request_json(base_url, method, path, payload=None):
    return json.loads(request_text(base_url, method, path, payload))


def request_text(base_url, method, path, payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(f"{base_url}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        sys.stderr.write(error.read().decode("utf-8", errors="replace"))
        raise


if __name__ == "__main__":
    raise SystemExit(main())
