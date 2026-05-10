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
    rows_by_speed = {}
    for table_name in ["coefficient_rows", "component_rows", "powering_rows"]:
        for source_row in parsed_out.get(table_name, []):
            speed = source_row["speed_knots"]
            target_row = rows_by_speed.setdefault(speed, {"speed_knots": speed})
            target_row.update(source_row)
    return [rows_by_speed[speed] for speed in sorted(rows_by_speed)]


def compare_legacy_out_to_result(parsed_out, modern_result, fields=None, speed_tolerance=1e-6):
    compare_fields = fields or DEFAULT_COMPARE_FIELDS
    legacy_rows = merge_legacy_out_rows(parsed_out)
    modern_rows = modern_result.get("speeds", [])
    matches = []
    unmatched_legacy = []
    matched_modern_indexes = set()

    for legacy_row in legacy_rows:
        match_index, modern_row = find_speed_match(legacy_row["speed_knots"], modern_rows, speed_tolerance, matched_modern_indexes)
        if modern_row is None:
            unmatched_legacy.append(legacy_row["speed_knots"])
            continue
        matched_modern_indexes.add(match_index)
        matches.append({
            "speed_knots": legacy_row["speed_knots"],
            "modern_speed_knots": modern_row["speed_knots"],
            "fields": compare_fields_for_row(legacy_row, modern_row, compare_fields)
        })

    unmatched_modern = [
        row["speed_knots"]
        for index, row in enumerate(modern_rows)
        if index not in matched_modern_indexes
    ]

    return {
        "legacy_program": parsed_out.get("program"),
        "legacy_calculation_completed": parsed_out.get("calculation_completed"),
        "matched_speed_count": len(matches),
        "unmatched_legacy_speeds": unmatched_legacy,
        "unmatched_modern_speeds": unmatched_modern,
        "comparisons": matches
    }


def find_speed_match(speed, rows, tolerance, excluded_indexes):
    best_index = None
    best_row = None
    best_delta = None
    for index, row in enumerate(rows):
        if index in excluded_indexes:
            continue
        delta = abs(row["speed_knots"] - speed)
        if delta <= tolerance and (best_delta is None or delta < best_delta):
            best_index = index
            best_row = row
            best_delta = delta
    return best_index, best_row


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
    if not isinstance(legacy_value, (int, float)) or not isinstance(modern_value, (int, float)):
        comparison["status"] = "non_numeric"
        return comparison

    delta = modern_value - legacy_value
    comparison["delta"] = delta
    comparison["absolute_delta"] = abs(delta)
    comparison["relative_delta"] = None if legacy_value == 0 else delta / legacy_value
    comparison["status"] = "numeric_delta"
    return comparison
