import re


NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[deDE][-+]?\d+)?")

COEFFICIENT_COLUMNS = [
    "speed_knots",
    "speed_mps",
    "froude_number",
    "speed_length_ratio",
    "friction_coefficient",
    "residual_resistance_coefficient",
    "correlation_allowance_coefficient",
    "frictional_resistance_n"
]

COMPONENT_COLUMNS = [
    "speed_knots",
    "rf_form_resistance_n",
    "appendage_resistance_n",
    "wave_resistance_n",
    "bulb_resistance_n",
    "transom_resistance_n",
    "correlation_allowance_resistance_n",
    "air_resistance_n"
]

POWERING_COLUMNS = [
    "speed_knots",
    "speed_mps",
    "total_resistance_n",
    "effective_power_kw",
    "wake_fraction",
    "thrust_deduction",
    "required_thrust_n",
    "hull_efficiency",
    "relative_rotative_efficiency"
]


def parse_legacy_out(text, filename="OUT"):
    result = {
        "source": {
            "legacy_file": filename,
            "format": "PPP legacy OUT text"
        },
        "program": None,
        "input_verification": {},
        "coefficient_rows": [],
        "component_rows": [],
        "powering_rows": [],
        "calculation_completed": "Calculation Completed Successfully" in text
    }
    section = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower()
        if "power prediction program" in lowered:
            result["program"] = line
            continue
        if "input verification" in lowered:
            section = "input"
            continue
        if "speed, resistance coefficients" in lowered:
            section = "coefficients"
            continue
        if "remaining resistance components" in lowered:
            section = "components"
            continue
        if "resistance, effective power" in lowered:
            section = "powering"
            continue
        if section == "input" and "=" in line:
            parse_input_line(result["input_verification"], line)
            continue
        values = numeric_values(line)
        if not values or not starts_with_number(line):
            continue
        if section == "coefficients" and len(values) >= len(COEFFICIENT_COLUMNS):
            result["coefficient_rows"].append(row_from_values(COEFFICIENT_COLUMNS, values))
        if section == "components" and len(values) >= len(COMPONENT_COLUMNS):
            result["component_rows"].append(row_from_values(COMPONENT_COLUMNS, values))
        if section == "powering" and len(values) >= len(POWERING_COLUMNS):
            result["powering_rows"].append(row_from_values(POWERING_COLUMNS, values))
    return result


def parse_input_line(target, line):
    label, raw_value = line.split("=", 1)
    key = normalize_label(label)
    numbers = numeric_values(raw_value)
    target[key] = {
        "label": " ".join(label.split()),
        "raw_value": raw_value.strip(),
        "numeric_value": numbers[0] if numbers else None
    }


def numeric_values(text):
    return [float(match.group(0).replace("D", "E").replace("d", "e")) for match in NUMBER_RE.finditer(text)]


def starts_with_number(text):
    return NUMBER_RE.match(text.lstrip()) is not None


def row_from_values(columns, values):
    return {column: values[index] for index, column in enumerate(columns)}


def normalize_label(label):
    value = label.lower()
    value = value.replace("%", " percent ")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")
