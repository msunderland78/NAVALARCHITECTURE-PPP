import argparse
import json
import sys
from pathlib import Path

from .core import DEFAULT_POINT_COUNT, evaluate_case
from .legacy_compare import compare_legacy_out_to_result
from .legacy_out import parse_legacy_out


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("case_json")
    parser.add_argument("legacy_out")
    parser.add_argument("--point-count", type=int, default=DEFAULT_POINT_COUNT)
    parser.add_argument("--field", action="append")
    parser.add_argument("--output")
    parser.add_argument("--speed-tolerance", type=float, default=1e-6)
    parser.add_argument("--max-absolute-delta", type=float)
    parser.add_argument("--max-relative-delta", type=float)
    parser.add_argument("--fail-on-missing-modern", action="store_true")
    parser.add_argument("--require-matched-speed-count", type=int)
    args = parser.parse_args(argv)

    payload = json.loads(Path(args.case_json).read_text())
    case = payload.get("case", payload)
    modern_result = evaluate_case(case, args.point_count)
    legacy_out_path = Path(args.legacy_out)
    parsed_out = parse_legacy_out(legacy_out_path.read_text(errors="replace"), legacy_out_path.name)
    result = compare_legacy_out_to_result(parsed_out, modern_result, args.field, args.speed_tolerance)
    result["case_json"] = str(Path(args.case_json))
    result["legacy_out"] = str(legacy_out_path)
    failures = comparison_failures(result, args.max_absolute_delta, args.max_relative_delta, args.fail_on_missing_modern, args.require_matched_speed_count)
    result["passed"] = not failures
    result["failures"] = failures
    text = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n")
    else:
        sys.stdout.write(text + "\n")
    return 0 if result["passed"] else 1


def comparison_failures(result, max_absolute_delta, max_relative_delta, fail_on_missing_modern, require_matched_speed_count):
    failures = []
    if require_matched_speed_count is not None and result["matched_speed_count"] != require_matched_speed_count:
        failures.append({
            "rule": "require_matched_speed_count",
            "expected": require_matched_speed_count,
            "actual": result["matched_speed_count"]
        })
    if max_absolute_delta is not None:
        max_delta = result["summary"]["max_absolute_delta"]
        if max_delta and max_delta["absolute_delta"] > max_absolute_delta:
            failures.append({
                "rule": "max_absolute_delta",
                "limit": max_absolute_delta,
                "actual": max_delta
            })
    if max_relative_delta is not None:
        max_delta = result["summary"]["max_relative_delta"]
        if max_delta and max_delta["absolute_relative_delta"] > max_relative_delta:
            failures.append({
                "rule": "max_relative_delta",
                "limit": max_relative_delta,
                "actual": max_delta
            })
    missing_modern = result["summary"]["status_counts"].get("missing_modern", 0)
    if fail_on_missing_modern and missing_modern:
        failures.append({
            "rule": "fail_on_missing_modern",
            "actual": missing_modern
        })
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
