import argparse
import json
import sys
from pathlib import Path

from .core import evaluate_case
from .legacy_compare import compare_legacy_out_to_result
from .legacy_out import parse_legacy_out


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("case_json")
    parser.add_argument("legacy_out")
    parser.add_argument("--point-count", type=int, default=1)
    parser.add_argument("--field", action="append")
    parser.add_argument("--output")
    parser.add_argument("--speed-tolerance", type=float, default=1e-6)
    args = parser.parse_args(argv)

    payload = json.loads(Path(args.case_json).read_text())
    case = payload.get("case", payload)
    modern_result = evaluate_case(case, args.point_count)
    legacy_out_path = Path(args.legacy_out)
    parsed_out = parse_legacy_out(legacy_out_path.read_text(errors="replace"), legacy_out_path.name)
    result = compare_legacy_out_to_result(parsed_out, modern_result, args.field, args.speed_tolerance)
    result["case_json"] = str(Path(args.case_json))
    result["legacy_out"] = str(legacy_out_path)
    text = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
