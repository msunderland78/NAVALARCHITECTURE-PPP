from math import isfinite
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Result


DEFAULT_COMPARE_FIELDS = [
    "speed_mps",
    "froude_number",
    "speed_length_ratio",
    "friction_coefficient",
    "residual_resistance_coefficient",
    "correlation_allowance_coefficient",
    "frictional_resistance_n",
    "rf_form_resistance_n",
    "appendage_resistance_n",
    "wave_resistance_n",
    "bulb_resistance_n",
    "transom_resistance_n",
    "correlation_allowance_resistance_n",
    "air_resistance_n",
    "total_resistance_n",
    "effective_power_kw",
    "wake_fraction",
    "thrust_deduction",
    "required_thrust_n",
    "hull_efficiency",
    "relative_rotative_efficiency"
]


def merge_legacy_out_rows(parsed_out):
    if not isinstance(parsed_out, dict):
        raise ValueError("parsed_out must be an object")
    rows_by_speed = {}
    for table_name in ["coefficient_rows", "component_rows", "powering_rows"]:
        table_rows = parsed_out.get(table_name, [])
        if not isinstance(table_rows, list):
            raise ValueError(f"{table_name} must be a list")
        for source_row in table_rows:
            speed = speed_from_row(source_row, table_name)
            target_row = rows_by_speed.setdefault(speed, {"speed_knots": speed})
            target_row.update(source_row)
    return [rows_by_speed[speed] for speed in sorted(rows_by_speed)]


def compare_legacy_out_to_result(
    parsed_out: dict,
    modern_result: "Result",
    fields: list[str] | None = None,
    speed_tolerance: float = 1e-6,
) -> dict:
    compare_fields, speed_tolerance = validate_compare_options(fields, speed_tolerance)
    legacy_rows = merge_legacy_out_rows(parsed_out)
    modern_rows = validate_modern_rows(modern_result)
    matches = []
    unmatched_legacy = []
    matched_modern_indexes = set()

    for legacy_row in legacy_rows:
        speed = speed_from_row(legacy_row, "legacy_rows")
        match_index, modern_row = find_speed_match(speed, modern_rows, speed_tolerance, matched_modern_indexes)
        if modern_row is None:
            unmatched_legacy.append(speed)
            continue
        matched_modern_indexes.add(match_index)
        matches.append({
            "speed_knots": speed,
            "modern_speed_knots": speed_from_row(modern_row, "modern_result.speeds"),
            "fields": compare_fields_for_row(legacy_row, modern_row, compare_fields)
        })

    unmatched_modern = [
        speed_from_row(row, "modern_result.speeds")
        for index, row in enumerate(modern_rows)
        if index not in matched_modern_indexes
    ]
    summary = comparison_summary(matches)

    return {
        "legacy_program": parsed_out.get("program"),
        "legacy_calculation_completed": parsed_out.get("calculation_completed"),
        "matched_speed_count": len(matches),
        "unmatched_legacy_speeds": unmatched_legacy,
        "unmatched_modern_speeds": unmatched_modern,
        "summary": summary,
        "comparisons": matches
    }


def find_speed_match(speed, rows, tolerance, excluded_indexes):
    speed = validate_speed(speed, "legacy_rows.speed_knots")
    best_index = None
    best_row = None
    best_delta = None
    for index, row in enumerate(rows):
        if index in excluded_indexes:
            continue
        delta = abs(speed_from_row(row, "modern_result.speeds") - speed)
        if delta <= tolerance and (best_delta is None or delta < best_delta):
            best_index = index
            best_row = row
            best_delta = delta
    return best_index, best_row


def validate_modern_rows(modern_result):
    if not isinstance(modern_result, dict):
        raise ValueError("modern_result must be an object")
    modern_rows = modern_result.get("speeds", [])
    if not isinstance(modern_rows, list):
        raise ValueError("modern_result.speeds must be a list")
    return modern_rows


def speed_from_row(row, source):
    if not isinstance(row, dict):
        raise ValueError(f"{source} row must be an object")
    return validate_speed(row.get("speed_knots"), f"{source}.speed_knots")


def validate_speed(speed, source):
    if isinstance(speed, bool) or not isinstance(speed, (int, float)) or not isfinite(speed):
        raise ValueError(f"{source} must be finite")
    return speed


def validate_compare_options(fields, speed_tolerance):
    if isinstance(speed_tolerance, bool) or not isinstance(speed_tolerance, (int, float)) or not isfinite(speed_tolerance) or speed_tolerance < 0:
        raise ValueError("speed_tolerance must be a non-negative finite number")
    if fields is not None and (not isinstance(fields, list) or not all(isinstance(field, str) for field in fields)):
        raise ValueError("fields must be a list of strings")
    return fields or DEFAULT_COMPARE_FIELDS, speed_tolerance


def compare_fields_for_row(legacy_row, modern_row, fields):
    return [
        compare_field(field, legacy_row.get(field), modern_row.get(field))
        for field in fields
    ]


def compare_field(field, legacy_value, modern_value):
    comparison = {
        "field": field,
        "legacy": legacy_value,
        "modern": modern_value
    }
    if legacy_value is None and modern_value is None:
        comparison["status"] = "no_data"
        return comparison
    if legacy_value is None:
        comparison["status"] = "missing_legacy"
        return comparison
    if modern_value is None:
        comparison["status"] = "missing_modern"
        return comparison
    if (
        isinstance(legacy_value, bool)
        or isinstance(modern_value, bool)
        or not isinstance(legacy_value, (int, float))
        or not isinstance(modern_value, (int, float))
    ):
        comparison["status"] = "non_numeric"
        return comparison

    delta = modern_value - legacy_value
    comparison["delta"] = delta
    comparison["absolute_delta"] = abs(delta)
    comparison["relative_delta"] = None if legacy_value == 0 else delta / legacy_value
    comparison["status"] = "numeric_delta"
    return comparison


def comparison_summary(matches):
    status_counts = {}
    max_absolute_delta = None
    max_absolute_delta_field = None
    max_relative_delta = None
    max_relative_delta_field = None
    for match in matches:
        for field in match["fields"]:
            status = field["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
            absolute_delta = field.get("absolute_delta")
            if absolute_delta is not None and (max_absolute_delta is None or absolute_delta > max_absolute_delta):
                max_absolute_delta = absolute_delta
                max_absolute_delta_field = {
                    "speed_knots": match["speed_knots"],
                    "field": field["field"],
                    "absolute_delta": absolute_delta
                }
            relative_delta = field.get("relative_delta")
            if relative_delta is not None:
                absolute_relative_delta = abs(relative_delta)
                if max_relative_delta is None or absolute_relative_delta > max_relative_delta:
                    max_relative_delta = absolute_relative_delta
                    max_relative_delta_field = {
                        "speed_knots": match["speed_knots"],
                        "field": field["field"],
                        "relative_delta": relative_delta,
                        "absolute_relative_delta": absolute_relative_delta
                    }
    return {
        "status_counts": status_counts,
        "max_absolute_delta": max_absolute_delta_field,
        "max_relative_delta": max_relative_delta_field
    }
