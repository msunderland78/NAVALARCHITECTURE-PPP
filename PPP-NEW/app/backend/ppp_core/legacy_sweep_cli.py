import argparse
import json
import sys
from pathlib import Path

from .legacy_sweep import candidate_option_sets, run_oracle_sweep


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("case_json")
    parser.add_argument("legacy_exe")
    parser.add_argument("workdir")
    parser.add_argument("--output")
    parser.add_argument("--wine", default="wine")
    parser.add_argument("--wineprefix")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--keep-going", action="store_true")
    parser.add_argument("--stern-correction", action="append", type=int)
    parser.add_argument("--pitch-diameter-ratio", action="append", type=float)
    parser.add_argument("--water-type-code", action="append", type=int)
    parser.add_argument("--appendage-primary-value", action="append", type=float)
    parser.add_argument("--appendage-model-total", action="append", type=float)
    args = parser.parse_args(argv)

    payload = json.loads(Path(args.case_json).read_text())
    case = payload.get("case", payload)
    option_sets = candidate_option_sets(
        args.stern_correction,
        args.pitch_diameter_ratio,
        args.water_type_code,
        args.appendage_primary_value,
        args.appendage_model_total
    )
    result = run_oracle_sweep(
        case,
        args.legacy_exe,
        args.workdir,
        option_sets,
        wine=args.wine,
        timeout_seconds=args.timeout_seconds,
        wineprefix=args.wineprefix,
        stop_on_out=not args.keep_going
    )
    result["case_json"] = str(Path(args.case_json))
    result["legacy_exe"] = str(Path(args.legacy_exe))
    text = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
