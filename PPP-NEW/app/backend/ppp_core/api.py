import json
import struct

from .core import evaluate_case
from .export import speeds_to_csv
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


def import_response(body):
    return 200, "application/json", import_legacy_ppp(body, "upload.ppp")


def route(method, path, body=b""):
    try:
        if method == "GET" and path == "/health":
            return health_response()
        if method == "POST" and path == "/api/evaluate":
            return evaluate_response(body)
        if method == "POST" and path == "/api/export/csv":
            return csv_response(body)
        if method == "POST" and path == "/api/import/ppp":
            return import_response(body)
        return 404, "application/json", {"error": "not found"}
    except (KeyError, ValueError, json.JSONDecodeError, struct.error) as error:
        return 400, "application/json", {"error": str(error)}
