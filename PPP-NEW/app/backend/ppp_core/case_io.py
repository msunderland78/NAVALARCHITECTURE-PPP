import json
from pathlib import Path


def load_case_json(path):
    payload = json.loads(Path(path).read_text())
    if not isinstance(payload, dict):
        raise ValueError("case JSON must be an object")
    case = payload.get("case", payload)
    if not isinstance(case, dict):
        raise ValueError("case JSON case must be an object")
    return case
