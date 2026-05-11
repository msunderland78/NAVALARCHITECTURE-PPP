import argparse
import json
import sys
from pathlib import Path

from .case_io import load_case_json
from .core import DEFAULT_POINT_COUNT, evaluate_case


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("case_json")
    parser.add_argument("--point-count", type=int, default=DEFAULT_POINT_COUNT)
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    case = load_case_json(args.case_json)
    result = evaluate_case(case, args.point_count)
    text = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
