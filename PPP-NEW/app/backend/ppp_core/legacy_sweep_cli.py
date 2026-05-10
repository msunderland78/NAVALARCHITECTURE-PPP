import argparse
import json
import sys
from pathlib import Path

from .legacy_out import parse_legacy_out
from .legacy_sweep import candidate_option_sets, run_oracle_sweep


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("case_json")
    parser.add_argument("legacy_exe")
    parser.add_argument("workdir")
    parser.add_argument("--output")
    parser.add_argument("--wine", default="wine")
    parser.add_argument("--wine-arg", action="append", default=[])
    parser.add_argument("--wineprefix")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--keep-going", action="store_true")
    parser.add_argument("--stern-correction", action="append", type=int)
    parser.add_argument("--pitch-diameter-ratio", action="append", type=float)
    parser.add_argument("--water-type-code", action="append", type=int)
    parser.add_argument("--appendage-primary-value", action="append", type=float)
    parser.add_argument("--appendage-model-total", action="append", type=float)
    parser.add_argument("--first-record-order", action="append", choices=["depth_before_drafts", "drafts_before_depth"])
    parser.add_argument("--propeller-record-order", action="append", choices=["wetted_half_dp", "dp_wetted_half"])
    parser.add_argument("--capture-out")
    parser.add_argument("--capture-parsed-out")
    args = parser.parse_args(argv)

    payload = json.loads(Path(args.case_json).read_text())
    case = payload.get("case", payload)
    option_sets = candidate_option_sets(
        args.stern_correction,
        args.pitch_diameter_ratio,
        args.water_type_code,
        args.appendage_primary_value,
        args.appendage_model_total,
        args.first_record_order,
        args.propeller_record_order
    )
    result = run_oracle_sweep(
        case,
        args.legacy_exe,
        args.workdir,
        option_sets,
        wine=args.wine,
        wine_args=args.wine_arg,
        timeout_seconds=args.timeout_seconds,
        wineprefix=args.wineprefix,
        stop_on_out=not args.keep_going
    )
    result["case_json"] = str(Path(args.case_json))
    result["legacy_exe"] = str(Path(args.legacy_exe))
    capture_outputs(result, args.capture_out, args.capture_parsed_out)
    text = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


def capture_outputs(result, capture_out, capture_parsed_out):
    if not result["successful_attempts"]:
        return
    source = Path(result["successful_attempts"][0]["workdir"]) / "OUT"
    if not source.exists():
        return
    out_text = source.read_text(encoding="utf-8", errors="replace")
    if capture_out:
        target = Path(capture_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(out_text)
        result["captured_out"] = str(target)
    if capture_parsed_out:
        target = Path(capture_parsed_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(parse_legacy_out(out_text, "OUT"), indent=2) + "\n")
        result["captured_parsed_out"] = str(target)


if __name__ == "__main__":
    raise SystemExit(main())
