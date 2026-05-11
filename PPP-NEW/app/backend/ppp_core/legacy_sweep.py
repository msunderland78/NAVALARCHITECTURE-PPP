from hashlib import sha256
from pathlib import Path

from .legacy_oracle import run_oracle


DEFAULT_STERN_CORRECTIONS = [0, -10, 10]
DEFAULT_PITCH_DIAMETER_RATIOS = [0, 0.8, 1.0]
DEFAULT_WATER_TYPE_CODES = [1, 2, 3]
DEFAULT_APPENDAGE_PRIMARY_VALUES = [None]
DEFAULT_APPENDAGE_MODEL_TOTALS = [None]
DEFAULT_FIRST_RECORD_ORDERS = [None]
DEFAULT_PROPELLER_RECORD_ORDERS = [None]
FORTRAN_FAILURE_PATTERNS = {
    "DOMAIN error": "domain_error",
    "CONOUT$": "console_output_error",
    "SING error": "sing_error",
    "TLOSS error": "tloss_error",
    "end-of-file": "end_of_file",
    "severe": "fortran_runtime_error"
}


def candidate_option_sets(stern_corrections=None, pitch_diameter_ratios=None, water_type_codes=None, appendage_primary_values=None, appendage_model_totals=None, first_record_orders=None, propeller_record_orders=None):
    stern_values = defaulted(stern_corrections, DEFAULT_STERN_CORRECTIONS)
    pitch_values = defaulted(pitch_diameter_ratios, DEFAULT_PITCH_DIAMETER_RATIOS)
    water_values = defaulted(water_type_codes, DEFAULT_WATER_TYPE_CODES)
    appendage_primary = defaulted(appendage_primary_values, DEFAULT_APPENDAGE_PRIMARY_VALUES)
    appendage_model = defaulted(appendage_model_totals, DEFAULT_APPENDAGE_MODEL_TOTALS)
    first_orders = defaulted(first_record_orders, DEFAULT_FIRST_RECORD_ORDERS)
    propeller_orders = defaulted(propeller_record_orders, DEFAULT_PROPELLER_RECORD_ORDERS)
    return [
        clean_options({
            "stern_correction": stern,
            "pitch_diameter_ratio": pitch,
            "water_type_code": water,
            "appendage_primary_value": primary,
            "appendage_model_total": model,
            "first_record_order": first_order,
            "propeller_record_order": propeller_order
        })
        for stern in stern_values
        for pitch in pitch_values
        for water in water_values
        for primary in appendage_primary
        for model in appendage_model
        for first_order in first_orders
        for propeller_order in propeller_orders
    ]


def run_oracle_sweep(case, legacy_exe_path, workdir, option_sets=None, wine="wine", wine_args=None, timeout_seconds=20, wineprefix=None, use_pty=False, stop_on_out=True):
    option_sets = validate_option_sets(option_sets)
    root = Path(workdir)
    root.mkdir(parents=True, exist_ok=True)
    attempts = []
    for index, options in enumerate(option_sets, start=1):
        result = run_oracle(
            case,
            legacy_exe_path,
            root / f"attempt-{index:03d}",
            options,
            wine=wine,
            wine_args=wine_args,
            timeout_seconds=timeout_seconds,
            wineprefix=wineprefix,
            use_pty=use_pty
        )
        attempts.append(summarize_attempt(index, options, result))
        if stop_on_out and result["out_exists"]:
            break
    return {
        "attempt_count": len(attempts),
        "out_count": sum(1 for attempt in attempts if attempt["out_exists"]),
        "successful_attempts": [attempt for attempt in attempts if attempt["out_exists"]],
        "attempts": attempts
    }


def summarize_attempt(index, options, result):
    return {
        "index": index,
        "options": dict(options),
        "command": result["command"],
        "workdir": result["workdir"],
        "returncode": result["returncode"],
        "timed_out": result["timed_out"],
        "out_exists": result["out_exists"],
        "calculation_completed": bool(result["parsed_out"] and result["parsed_out"].get("calculation_completed")),
        "input_sha256": sha256(result["input"].encode("ascii")).hexdigest(),
        "input_line_count": len(result["input"].splitlines()),
        "input_first_record": first_line(result["input"]),
        "failure_kind": "timeout" if result["timed_out"] else failure_kind(result["stderr"], result["stdout"]),
        "stderr_tail": tail_text(result["stderr"]),
        "stdout_tail": tail_text(result["stdout"])
    }


def failure_kind(stderr, stdout):
    text = f"{stderr}\n{stdout}"
    for pattern, kind in FORTRAN_FAILURE_PATTERNS.items():
        if pattern.lower() in text.lower():
            return kind
    return None


def first_line(text):
    return text.splitlines()[0] if text.splitlines() else ""


def tail_text(text, max_lines=8):
    return "\n".join(text.splitlines()[-max_lines:])


def clean_options(options):
    return {key: value for key, value in options.items() if value is not None}


def defaulted(values, defaults):
    if values is None:
        return defaults
    if not isinstance(values, list):
        raise ValueError("sweep option values must be lists")
    return values


def validate_option_sets(option_sets):
    if option_sets is None:
        return candidate_option_sets()
    if not isinstance(option_sets, list):
        raise ValueError("option_sets must be a list")
    for options in option_sets:
        if not isinstance(options, dict):
            raise ValueError("option_sets entries must be objects")
    return option_sets
