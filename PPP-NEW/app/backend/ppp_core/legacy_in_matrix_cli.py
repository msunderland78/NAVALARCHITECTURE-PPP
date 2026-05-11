import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

from .case_io import load_case_json
from .legacy_in import generate_candidate_legacy_in
from .legacy_sweep import candidate_option_sets


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("case_json")
    parser.add_argument("workdir")
    parser.add_argument("--output")
    parser.add_argument("--stern-correction", action="append", type=int)
    parser.add_argument("--pitch-diameter-ratio", action="append", type=float)
    parser.add_argument("--water-type-code", action="append", type=int)
    parser.add_argument("--appendage-primary-value", action="append", type=float)
    parser.add_argument("--appendage-model-total", action="append", type=float)
    parser.add_argument("--first-record-order", action="append", choices=["depth_before_drafts", "drafts_before_depth"])
    parser.add_argument("--propeller-record-order", action="append", choices=["wetted_half_dp", "dp_wetted_half"])
    args = parser.parse_args(argv)

    case = load_case_json(args.case_json)
    option_sets = candidate_option_sets(
        args.stern_correction,
        args.pitch_diameter_ratio,
        args.water_type_code,
        args.appendage_primary_value,
        args.appendage_model_total,
        args.first_record_order,
        args.propeller_record_order
    )
    result = write_matrix(case, args.workdir, option_sets)
    result["case_json"] = str(Path(args.case_json))
    text = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


def write_matrix(case, workdir, option_sets):
    root = Path(workdir)
    root.mkdir(parents=True, exist_ok=True)
    attempts = []
    for index, options in enumerate(option_sets, start=1):
        attempt_dir = root / f"attempt-{index:03d}"
        attempt_dir.mkdir(parents=True, exist_ok=True)
        text = generate_candidate_legacy_in(case, options)
        input_path = attempt_dir / "IN"
        input_path.write_text(text, encoding="ascii")
        attempts.append({
            "index": index,
            "options": dict(options),
            "input": str(input_path),
            "input_sha256": sha256(text.encode("ascii")).hexdigest(),
            "input_line_count": len(text.splitlines()),
            "input_first_record": first_line(text)
        })
    return {
        "attempt_count": len(attempts),
        "workdir": str(root),
        "attempts": attempts
    }


def first_line(text):
    return text.splitlines()[0] if text.splitlines() else ""


if __name__ == "__main__":
    raise SystemExit(main())
