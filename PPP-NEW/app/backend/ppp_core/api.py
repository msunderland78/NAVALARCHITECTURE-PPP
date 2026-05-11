import json
import struct
from math import isfinite

from .core import DEFAULT_POINT_COUNT, evaluate_case
from .export import result_to_markdown, speeds_to_csv
from .legacy_compare import compare_legacy_out_to_result
from .legacy_in import generate_candidate_legacy_in
from .legacy_out import parse_legacy_out
from .legacy_ppp import import_legacy_ppp


def health_response():
    return 200, "application/json", {"status": "ok"}


def evaluate_response(body):
    payload = json.loads(body.decode("utf-8"))
    point_count = payload.get("point_count", DEFAULT_POINT_COUNT)
    case = payload["case"]
    return 200, "application/json", evaluate_case(case, point_count)


def csv_response(body):
    payload = json.loads(body.decode("utf-8"))
    point_count = payload.get("point_count", DEFAULT_POINT_COUNT)
    case = payload["case"]
    result = evaluate_case(case, point_count)
    return 200, "text/csv", speeds_to_csv(result)


def json_export_response(body):
    payload = json.loads(body.decode("utf-8"))
    point_count = payload.get("point_count", DEFAULT_POINT_COUNT)
    case = payload["case"]
    return 200, "application/json", evaluate_case(case, point_count)


def report_markdown_response(body):
    payload = json.loads(body.decode("utf-8"))
    point_count = payload.get("point_count", DEFAULT_POINT_COUNT)
    case = payload["case"]
    return 200, "text/markdown", result_to_markdown(evaluate_case(case, point_count), case)


def legacy_in_export_response(body):
    payload = json.loads(body.decode("utf-8"))
    case = payload["case"]
    options = payload.get("options", {})
    if not isinstance(options, dict):
        raise ValueError("options must be an object")
    validate_legacy_in_options(options)
    return 200, "text/plain", generate_candidate_legacy_in(case, options)


def import_response(body):
    return 200, "application/json", import_legacy_ppp(body, "upload.ppp")


def import_out_response(body):
    return 200, "application/json", parse_legacy_out(body.decode("utf-8", errors="replace"), "upload.OUT")


def compare_out_response(body):
    payload = json.loads(body.decode("utf-8"))
    parsed_out = payload.get("legacy_out")
    if parsed_out is None:
        parsed_out = parse_legacy_out(payload["legacy_out_text"], payload.get("legacy_filename", "upload.OUT"))
    modern_result = payload.get("modern_result")
    if modern_result is None:
        modern_result = evaluate_case(payload["case"], payload.get("point_count", DEFAULT_POINT_COUNT))
    speed_tolerance = payload.get("speed_tolerance", 1e-6)
    if isinstance(speed_tolerance, bool) or not isinstance(speed_tolerance, (int, float)) or not isfinite(speed_tolerance) or speed_tolerance < 0:
        raise ValueError("speed_tolerance must be a non-negative finite number")
    fields = payload.get("fields")
    if fields is not None and (not isinstance(fields, list) or not all(isinstance(field, str) for field in fields)):
        raise ValueError("fields must be a list of strings")
    return 200, "application/json", compare_legacy_out_to_result(
        parsed_out,
        modern_result,
        fields,
        speed_tolerance
    )


def validate_legacy_in_options(options):
    numeric_options = [
        "stern_correction",
        "pitch_diameter_ratio",
        "water_type_code",
        "propulsion_type_code",
        "appendage_primary_value",
        "appendage_model_total"
    ]
    for name in numeric_options:
        value = options.get(name)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value)):
            raise ValueError(f"{name} must be a finite number")


def route(method, path, body=b""):
    try:
        if method == "GET" and path == "/health":
            return health_response()
        if method == "POST" and path == "/api/evaluate":
            return evaluate_response(body)
        if method == "POST" and path == "/api/export/csv":
            return csv_response(body)
        if method == "POST" and path == "/api/export/json":
            return json_export_response(body)
        if method == "POST" and path == "/api/export/report.md":
            return report_markdown_response(body)
        if method == "POST" and path == "/api/export/legacy-in-candidate":
            return legacy_in_export_response(body)
        if method == "POST" and path == "/api/import/ppp":
            return import_response(body)
        if method == "POST" and path == "/api/import/out":
            return import_out_response(body)
        if method == "POST" and path == "/api/compare/out":
            return compare_out_response(body)
        return 404, "application/json", {"error": "not found"}
    except (KeyError, TypeError, UnicodeDecodeError, ValueError, json.JSONDecodeError, struct.error) as error:
        return 400, "application/json", {"error": str(error)}
