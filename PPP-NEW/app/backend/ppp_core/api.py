import json
import struct

from .core import evaluate_case
from .export import speeds_to_csv
from .legacy_in import generate_candidate_legacy_in
from .legacy_out import parse_legacy_out
from .legacy_ppp import import_legacy_ppp


def health_response():
    return 200, "application/json", {"status": "ok"}


def evaluate_response(body):
    payload = json.loads(body.decode("utf-8"))
    point_count = payload.get("point_count", 1)
    case = payload["case"]
    return 200, "application/json", evaluate_case(case, point_count)


def csv_response(body):
    payload = json.loads(body.decode("utf-8"))
    point_count = payload.get("point_count", 1)
    case = payload["case"]
    result = evaluate_case(case, point_count)
    return 200, "text/csv", speeds_to_csv(result)


def json_export_response(body):
    payload = json.loads(body.decode("utf-8"))
    point_count = payload.get("point_count", 1)
    case = payload["case"]
    return 200, "application/json", evaluate_case(case, point_count)


def legacy_in_export_response(body):
    payload = json.loads(body.decode("utf-8"))
    case = payload["case"]
    options = payload.get("options", {})
    return 200, "text/plain", generate_candidate_legacy_in(case, options)


def import_response(body):
    return 200, "application/json", import_legacy_ppp(body, "upload.ppp")


def import_out_response(body):
    return 200, "application/json", parse_legacy_out(body.decode("utf-8", errors="replace"), "upload.OUT")


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
        if method == "POST" and path == "/api/export/legacy-in-candidate":
            return legacy_in_export_response(body)
        if method == "POST" and path == "/api/import/ppp":
            return import_response(body)
        if method == "POST" and path == "/api/import/out":
            return import_out_response(body)
        return 404, "application/json", {"error": "not found"}
    except (KeyError, ValueError, json.JSONDecodeError, struct.error) as error:
        return 400, "application/json", {"error": str(error)}
