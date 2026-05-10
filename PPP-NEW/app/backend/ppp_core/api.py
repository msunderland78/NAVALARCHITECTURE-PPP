import json

from .core import evaluate_case
from .export import speeds_to_csv


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


def route(method, path, body=b""):
    if method == "GET" and path == "/health":
        return health_response()
    if method == "POST" and path == "/api/evaluate":
        return evaluate_response(body)
    if method == "POST" and path == "/api/export/csv":
        return csv_response(body)
    return 404, "application/json", {"error": "not found"}
