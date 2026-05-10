import argparse
import json
import sys
from pathlib import Path

from .legacy_in import generate_candidate_legacy_in


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("case_json")
    parser.add_argument("--output")
    parser.add_argument("--stern-correction", type=int)
    parser.add_argument("--pitch-diameter-ratio", type=float)
    parser.add_argument("--water-type-code", type=int)
    parser.add_argument("--appendage-primary-value", type=float)
    parser.add_argument("--appendage-model-total", type=float)
    parser.add_argument("--first-record-order", choices=["depth_before_drafts", "drafts_before_depth"])
    args = parser.parse_args(argv)

    payload = json.loads(Path(args.case_json).read_text())
    case = payload.get("case", payload)
    text = generate_candidate_legacy_in(case, clean_options({
        "stern_correction": args.stern_correction,
        "pitch_diameter_ratio": args.pitch_diameter_ratio,
        "water_type_code": args.water_type_code,
        "appendage_primary_value": args.appendage_primary_value,
        "appendage_model_total": args.appendage_model_total,
        "first_record_order": args.first_record_order
    }))
    if args.output:
        Path(args.output).write_text(text)
    else:
        sys.stdout.write(text)
    return 0


def clean_options(options):
    return {key: value for key, value in options.items() if value is not None}


if __name__ == "__main__":
    raise SystemExit(main())
