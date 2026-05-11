#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "app" / "backend"
sys.path.insert(0, str(BACKEND))

from ppp_core.case_io import load_case_json
from ppp_core.legacy_oracle import run_oracle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default=str(ROOT / "tests" / "fixtures" / "pppin_sample_import.json"))
    parser.add_argument("--exe", required=True)
    parser.add_argument("--workdir", default="/tmp/ppp-oracle-repro")
    parser.add_argument("--wine", default="wine")
    parser.add_argument("--wine-arg", action="append", default=[])
    parser.add_argument("--wineprefix", default=None)
    parser.add_argument("--use-pty", action="store_true")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--stern-correction", type=float, default=None)
    parser.add_argument("--pitch-diameter-ratio", type=float, default=None)
    parser.add_argument("--water-type-code", type=float, default=None)
    args = parser.parse_args()
    case = load_case_json(args.case)
    options = clean_options({
        "stern_correction": args.stern_correction,
        "pitch_diameter_ratio": args.pitch_diameter_ratio,
        "water_type_code": args.water_type_code
    })
    result = run_oracle(
        case,
        args.exe,
        args.workdir,
        options,
        wine=args.wine,
        wine_args=args.wine_arg,
        timeout_seconds=args.timeout,
        wineprefix=args.wineprefix,
        use_pty=args.use_pty
    )
    print(json.dumps(result, indent=2))


def clean_options(options):
    return {key: value for key, value in options.items() if value is not None}


if __name__ == "__main__":
    main()
