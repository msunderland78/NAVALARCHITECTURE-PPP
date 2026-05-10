from math import log10, sqrt


KNOT_TO_MPS = 0.514444
METER_TO_FOOT = 3.280839895
G = 9.80665
STERN_TYPES = {
    "normal_shaped_sections",
    "v_shaped_sections",
    "u_shaped_sections_with_hogner_stern",
    "pram_with_gondola"
}
PROPULSION_TYPES = {
    "single_screw_conventional_stern",
    "single_screw_open_flow_stern",
    "twin_screw"
}
WATER_TYPES = {
    "custom",
    "fresh_water_15_c",
    "salt_water_15_c"
}


def evaluate_case(case, point_count=1):
    point_count = validate_point_count(point_count)
    validate_case(case)
    hull = case["hull"]
    features = case["features"]
    propulsion = case["propulsion"]
    water = case["water"]
    modeling = case["modeling"]
    appendages = case["appendages"]
    margin = case["margin"]
    speed_sweep = case["speed_sweep"]
    lwl = hull["lwl_m"]
    beam = hull["beam_lwl_m"]
    tf = hull["draft_forward_m"]
    ta = hull["draft_aft_m"]
    mean_draft = (tf + ta) / 2
    cb = hull["block_coefficient"]
    cm = hull["midship_coefficient"]
    cp = cb / cm
    lcb_percent = hull["lcb_percent_lwl_from_midships_forward_positive"]
    lcb_m_from_fp = lwl * (0.5 - lcb_percent / 100)
    derived = {
        "mean_draft_m": mean_draft,
        "prismatic_coefficient": cp,
        "lcb_m_from_fp": lcb_m_from_fp,
        "beam_draft_ratio": beam / mean_draft,
        "lwl_beam_ratio": lwl / beam
    }
    speeds = []
    for index in range(point_count):
        speed_knots = speed_sweep["initial_speed_knots"] + speed_sweep["speed_increment_knots"] * index
        speeds.append(evaluate_speed(
            lwl,
            speed_knots,
            water["kinematic_viscosity_m2_s"],
            water["density_kg_m3"],
            modeling["wetted_surface_m2"],
            appendages,
            margin
        ))
    return {
        "project": case["project"],
        "derived": derived,
        "modeling": modeling_result(modeling),
        "applicability": applicability(case, derived, speeds),
        "speeds": speeds
    }


def modeling_result(modeling):
    return {
        "wetted_surface_mode": modeling.get("wetted_surface_mode", "user"),
        "wetted_surface_m2": modeling["wetted_surface_m2"],
        "half_angle_entrance_mode": modeling.get("half_angle_entrance_mode", "user"),
        "half_angle_entrance_degrees": modeling["half_angle_entrance_degrees"]
    }


def validate_point_count(point_count):
    value = int(point_count)
    if value < 1 or value > 100:
        raise ValueError("point_count must be between 1 and 100")
    return value


def validate_case(case):
    hull = case["hull"]
    features = case["features"]
    propulsion = case["propulsion"]
    water = case["water"]
    modeling = case["modeling"]
    speed_sweep = case["speed_sweep"]
    appendages = case["appendages"]
    margin = case["margin"]
    positive = {
        "hull.lwl_m": hull["lwl_m"],
        "hull.beam_lwl_m": hull["beam_lwl_m"],
        "hull.draft_forward_m": hull["draft_forward_m"],
        "hull.draft_aft_m": hull["draft_aft_m"],
        "hull.block_coefficient": hull["block_coefficient"],
        "hull.midship_coefficient": hull["midship_coefficient"],
        "modeling.wetted_surface_m2": modeling["wetted_surface_m2"],
        "water.density_kg_m3": water["density_kg_m3"],
        "water.kinematic_viscosity_m2_s": water["kinematic_viscosity_m2_s"],
        "speed_sweep.initial_speed_knots": speed_sweep["initial_speed_knots"]
    }
    for name, value in positive.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive")
    bounded = {
        "hull.block_coefficient": hull["block_coefficient"],
        "hull.midship_coefficient": hull["midship_coefficient"],
        "hull.waterplane_coefficient": hull["waterplane_coefficient"]
    }
    for name, value in bounded.items():
        if value > 1:
            raise ValueError(f"{name} must be less than or equal to 1")
    if speed_sweep["speed_increment_knots"] < 0:
        raise ValueError("speed_sweep.speed_increment_knots must be non-negative")
    if features["stern_type"] not in STERN_TYPES:
        raise ValueError("features.stern_type is not supported")
    if propulsion["type"] not in PROPULSION_TYPES:
        raise ValueError("propulsion.type is not supported")
    if water["type"] not in WATER_TYPES:
        raise ValueError("water.type is not supported")
    if modeling.get("wetted_surface_mode", "user") != "user":
        raise ValueError("modeling.wetted_surface_mode is not supported")
    if modeling.get("half_angle_entrance_mode", "user") != "user":
        raise ValueError("modeling.half_angle_entrance_mode is not supported")
    appendage_mode = appendages.get("mode", "percent_bare_hull_resistance")
    if appendage_mode not in ("percent_bare_hull_resistance", "equivalent_area_form_factor"):
        raise ValueError("appendages.mode is not supported")
    if appendages.get("percent_bare_hull_resistance", 0) < 0:
        raise ValueError("appendages.percent_bare_hull_resistance must be non-negative")
    if (appendages.get("equivalent_wetted_area_form_factor_m2") or 0) < 0:
        raise ValueError("appendages.equivalent_wetted_area_form_factor_m2 must be non-negative")
    if margin["design_margin_percent"] < 0:
        raise ValueError("margin.design_margin_percent must be non-negative")


def evaluate_speed(lwl_m, speed_knots, nu, rho, wetted_surface, appendages, margin):
    speed_mps = speed_knots * KNOT_TO_MPS
    reynolds = speed_mps * lwl_m / nu
    cf = 0.075 / ((log10(reynolds) - 2) ** 2)
    rf = 0.5 * rho * speed_mps ** 2 * wetted_surface * cf
    components = resistance_components(rf, wetted_surface, appendages, margin)
    return {
        "speed_knots": speed_knots,
        "speed_mps": speed_mps,
        "froude_number": speed_mps / sqrt(G * lwl_m),
        "speed_length_ratio": speed_knots / sqrt(lwl_m * METER_TO_FOOT),
        "reynolds_number": reynolds,
        "friction_coefficient": cf,
        "residual_resistance_coefficient": None,
        "correlation_allowance_coefficient": None,
        **components,
        "effective_power_kw": components["total_resistance_n"] * speed_mps / 1000,
        "wake_fraction": None,
        "thrust_deduction": None,
        "required_thrust_n": None,
        "hull_efficiency": None,
        "relative_rotative_efficiency": None
    }


def resistance_components(rf, wetted_surface, appendages, margin):
    appendage_mode = appendages.get("mode", "percent_bare_hull_resistance")
    appendage_resistance = 0.0
    equivalent_area = appendages.get("equivalent_wetted_area_form_factor_m2")
    if appendage_mode == "percent_bare_hull_resistance":
        appendage_resistance = rf * appendages.get("percent_bare_hull_resistance", 0) / 100
    if appendage_mode == "equivalent_area_form_factor":
        appendage_resistance = rf / wetted_surface * (appendages.get("equivalent_wetted_area_form_factor_m2") or 0)
    subtotal = rf + appendage_resistance
    design_margin = subtotal * margin["design_margin_percent"] / 100
    total = subtotal + design_margin
    return {
        "appendage_mode": appendage_mode,
        "appendage_equivalent_wetted_area_form_factor_m2": equivalent_area,
        "frictional_resistance_n": rf,
        "rf_form_resistance_n": None,
        "form_resistance_n": None,
        "appendage_resistance_n": appendage_resistance,
        "wave_resistance_n": None,
        "bulb_resistance_n": None,
        "transom_resistance_n": None,
        "correlation_allowance_resistance_n": None,
        "air_resistance_n": None,
        "implemented_resistance_subtotal_n": subtotal,
        "design_margin_resistance_n": design_margin,
        "total_resistance_n": total,
        "resistance_status": "partial_source_safe_components"
    }


def applicability(case, derived, speeds):
    checks = []
    for speed in speeds:
        checks.append(check_between(
            "froude_number",
            speed["froude_number"],
            0.0,
            1.0,
            f"Fn(Vk = {speed['speed_knots']:.2f})"
        ))
    checks.append(check_between("beam_draft_ratio", derived["beam_draft_ratio"], 2.10, 4.00, "B/T"))
    checks.append(check_between("lwl_beam_ratio", derived["lwl_beam_ratio"], 3.90, 14.9, "LWL/B"))
    checks.append(check_between("prismatic_coefficient", derived["prismatic_coefficient"], 0.55, 0.85, "Cp"))
    return checks


def check_between(name, value, lower, upper, label):
    return {
        "name": name,
        "label": label,
        "value": value,
        "lower": lower,
        "upper": upper,
        "ok": lower < value < upper
    }
