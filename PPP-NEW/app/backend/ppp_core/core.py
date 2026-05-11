from math import cos, exp, log10, sqrt


KNOT_TO_MPS = 0.514444
METER_TO_FOOT = 3.280839895
G = 9.80665
LEGACY_AIR_DRAG_PRESSURE_COEFFICIENT = 0.737223
STERN_CORRECTIONS = {
    "normal_shaped_sections": 0,
    "v_shaped_sections": -10,
    "u_shaped_sections_with_hogner_stern": 10,
    "pram_with_gondola": 10
}
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
    validate_speed_sweep(case["speed_sweep"], point_count)
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
    displacement_volume = lwl * beam * mean_draft * cb
    midship_area = beam * mean_draft * cm
    waterplane_area = lwl * beam * hull["waterplane_coefficient"]
    derived = {
        "mean_draft_m": mean_draft,
        "prismatic_coefficient": cp,
        "lcb_m_from_fp": lcb_m_from_fp,
        "lcb_percent_lwl_from_fp": lcb_m_from_fp / lwl * 100,
        "beam_draft_ratio": beam / mean_draft,
        "draft_beam_ratio": mean_draft / beam,
        "lwl_beam_ratio": lwl / beam,
        "beam_lwl_ratio": beam / lwl,
        "midship_area_m2": midship_area,
        "waterplane_area_m2": waterplane_area,
        "displacement_volume_m3": displacement_volume,
        "length_displacement_ratio": lwl / displacement_volume ** (1 / 3),
        "displacement_mass_tonnes": displacement_volume * water["density_kg_m3"] / 1000
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
            hull,
            features,
            modeling,
            derived,
            appendages,
            propulsion,
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
        "propulsion.propeller_diameter_m": propulsion["propeller_diameter_m"],
        "modeling.depth_at_bow_m": modeling["depth_at_bow_m"],
        "modeling.wetted_surface_m2": modeling["wetted_surface_m2"],
        "modeling.half_angle_entrance_degrees": modeling["half_angle_entrance_degrees"],
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
    non_negative = {
        "features.bulb_area_station_0_m2": features["bulb_area_station_0_m2"],
        "features.bulb_vertical_center_m": features["bulb_vertical_center_m"],
        "features.transom_immersed_area_zero_speed_m2": features["transom_immersed_area_zero_speed_m2"],
        "modeling.deckhouse_cargo_frontal_area_m2": modeling["deckhouse_cargo_frontal_area_m2"]
    }
    for name, value in non_negative.items():
        if value < 0:
            raise ValueError(f"{name} must be non-negative")
    if propulsion["expanded_area_ratio"] < 0 or propulsion["expanded_area_ratio"] > 1:
        raise ValueError("propulsion.expanded_area_ratio must be between 0 and 1")
    pitch_diameter_ratio = propulsion.get("pitch_diameter_ratio")
    if pitch_diameter_ratio is not None and pitch_diameter_ratio < 0:
        raise ValueError("propulsion.pitch_diameter_ratio must be non-negative")
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


def validate_speed_sweep(speed_sweep, point_count):
    if point_count > 1 and speed_sweep["speed_increment_knots"] <= 0:
        raise ValueError("speed_sweep.speed_increment_knots must be positive when point_count is greater than 1")


def evaluate_speed(lwl_m, speed_knots, nu, rho, wetted_surface, hull, features, modeling, derived, appendages, propulsion, margin):
    speed_mps = speed_knots * KNOT_TO_MPS
    reynolds = speed_mps * lwl_m / nu
    cf = 0.075 / ((log10(reynolds) - 2) ** 2)
    rf = 0.5 * rho * speed_mps ** 2 * wetted_surface * cf
    form_factor = holtrop_form_factor(hull, features, derived)
    ca = holtrop_correlation_allowance_coefficient(hull, features)
    wave_resistance = holtrop_wave_resistance(speed_mps, rho, hull, features, modeling, derived)
    bulb_resistance = holtrop_bulb_resistance(speed_mps, rho, hull, features)
    transom_resistance = holtrop_transom_resistance(speed_mps, rho, hull, features)
    components = resistance_components(speed_mps, rf, form_factor, wave_resistance, bulb_resistance, transom_resistance, ca, rho, wetted_surface, modeling, appendages, margin)
    dynamic_pressure_area = 0.5 * rho * speed_mps ** 2 * wetted_surface
    propulsion_factors = holtrop_propulsion_factors(cf, ca, form_factor, hull, features, propulsion, derived, wetted_surface)
    return {
        "speed_knots": speed_knots,
        "speed_mps": speed_mps,
        "froude_number": speed_mps / sqrt(G * lwl_m),
        "speed_length_ratio": speed_knots / sqrt(lwl_m * METER_TO_FOOT),
        "reynolds_number": reynolds,
        "friction_coefficient": cf,
        "residual_resistance_coefficient": (components["rf_form_resistance_n"] + wave_resistance + bulb_resistance + transom_resistance) / dynamic_pressure_area,
        "correlation_allowance_coefficient": ca,
        **components,
        "effective_power_kw": components["total_resistance_n"] * speed_mps / 1000,
        **propulsion_factors,
        "required_thrust_n": components["total_resistance_n"] / (1 - propulsion_factors["thrust_deduction"])
    }


def holtrop_form_factor(hull, features, derived):
    lwl = hull["lwl_m"]
    beam = hull["beam_lwl_m"]
    mean_draft = derived["mean_draft_m"]
    cp = derived["prismatic_coefficient"]
    displacement_volume = derived["displacement_volume_m3"]
    lcb_percent = hull["lcb_percent_lwl_from_midships_forward_positive"]
    stern_correction = STERN_CORRECTIONS[features["stern_type"]]
    c14 = 1 + 0.011 * stern_correction
    lr = lwl * (1 - cp + 0.06 * cp * lcb_percent / (4 * cp - 1))
    one_plus_k1 = 0.93 + 0.487118 * c14 * (beam / lwl) ** 1.06806 * (mean_draft / lwl) ** 0.46106 * (lwl / lr) ** 0.121563 * (lwl ** 3 / displacement_volume) ** 0.36486 * (1 - cp) ** -0.604247
    return one_plus_k1 - 1


def holtrop_correlation_allowance_coefficient(hull, features):
    lwl = hull["lwl_m"]
    beam = hull["beam_lwl_m"]
    mean_draft = (hull["draft_forward_m"] + hull["draft_aft_m"]) / 2
    cb = hull["block_coefficient"]
    bulb_area = features["bulb_area_station_0_m2"]
    bulb_center = features["bulb_vertical_center_m"]
    c3 = 0 if bulb_area == 0 else 0.56 * bulb_area ** 1.5 / (beam * mean_draft * (0.31 * sqrt(bulb_area) + hull["draft_forward_m"] - bulb_center))
    c2 = 1 if c3 == 0 else exp(-1.89 * sqrt(c3))
    c4 = min(hull["draft_forward_m"] / lwl, 0.04)
    return 0.006 * (lwl + 100) ** -0.16 - 0.00205 + 0.003 * sqrt(lwl / 7.5) * cb ** 4 * c2 * (0.04 - c4)


def holtrop_wave_resistance(speed_mps, rho, hull, features, modeling, derived):
    lwl = hull["lwl_m"]
    beam = hull["beam_lwl_m"]
    mean_draft = derived["mean_draft_m"]
    cp = derived["prismatic_coefficient"]
    displacement_volume = derived["displacement_volume_m3"]
    half_angle = modeling["half_angle_entrance_degrees"]
    length_displacement_ratio = derived["length_displacement_ratio"]
    c1 = 2223105 * holtrop_c7(beam / lwl) ** 3.78613 * (mean_draft / beam) ** 1.07961 * (90 - half_angle) ** -1.37565
    c2 = holtrop_bulb_shape_factor(hull, features)
    c5 = 1 - 0.8 * features["transom_immersed_area_zero_speed_m2"] / (beam * mean_draft * hull["midship_coefficient"])
    c15 = holtrop_c15(length_displacement_ratio)
    c16 = holtrop_c16(cp)
    m1 = 0.0140407 * lwl / mean_draft - 1.75254 * displacement_volume ** (1 / 3) / lwl - 4.79323 * beam / lwl - c16
    m2 = c15 * cp ** 2 * exp(-0.1 * froude_number(speed_mps, lwl) ** -2)
    wave_lambda = 1.446 * cp - 0.03 * lwl / beam if lwl / beam < 12 else 1.446 * cp - 0.36
    return c1 * c2 * c5 * rho * G * displacement_volume * exp(m1 * froude_number(speed_mps, lwl) ** -0.9 + m2 * cos(wave_lambda * froude_number(speed_mps, lwl) ** -2))


def holtrop_bulb_resistance(speed_mps, rho, hull, features):
    bulb_area = features["bulb_area_station_0_m2"]
    if bulb_area == 0:
        return 0
    draft_forward = hull["draft_forward_m"]
    bulb_center = features["bulb_vertical_center_m"]
    pb = 0.56 * sqrt(bulb_area) / (draft_forward - 1.5 * bulb_center)
    fni = speed_mps / sqrt(G * (draft_forward - bulb_center - 0.25 * sqrt(bulb_area)) + 0.15 * speed_mps ** 2)
    return 0.11 * exp(-3 * pb ** -2) * fni ** 3 * bulb_area ** 1.5 * rho * G / (1 + fni ** 2)


def holtrop_transom_resistance(speed_mps, rho, hull, features):
    transom_area = features["transom_immersed_area_zero_speed_m2"]
    if transom_area == 0:
        return 0
    beam = hull["beam_lwl_m"]
    cwp = hull["waterplane_coefficient"]
    fnt = speed_mps / sqrt(2 * G * transom_area / (beam * (1 + cwp)))
    c6 = 0 if fnt >= 5 else 0.2 * (1 - 0.2 * fnt)
    return 0.5 * rho * speed_mps ** 2 * transom_area * c6


def holtrop_bulb_shape_factor(hull, features):
    bulb_area = features["bulb_area_station_0_m2"]
    if bulb_area == 0:
        return 1
    mean_draft = (hull["draft_forward_m"] + hull["draft_aft_m"]) / 2
    c3 = 0.56 * bulb_area ** 1.5 / (hull["beam_lwl_m"] * mean_draft * (0.31 * sqrt(bulb_area) + hull["draft_forward_m"] - features["bulb_vertical_center_m"]))
    return exp(-1.89 * sqrt(c3))


def holtrop_c7(beam_lwl_ratio):
    if beam_lwl_ratio < 0.11:
        return 0.229577 * beam_lwl_ratio ** (1 / 3)
    if beam_lwl_ratio < 0.25:
        return beam_lwl_ratio
    return 0.5 - 0.0625 / beam_lwl_ratio


def holtrop_c15(length_displacement_ratio):
    if length_displacement_ratio < 8:
        return -1.69385
    if length_displacement_ratio < 12:
        return -1.69385 + (length_displacement_ratio - 8) / 2.36
    return 0


def holtrop_c16(cp):
    if cp < 0.8:
        return 8.07981 * cp - 13.8673 * cp ** 2 + 6.984388 * cp ** 3
    return 1.73014 - 0.7067 * cp


def holtrop_propulsion_factors(cf, ca, form_factor, hull, features, propulsion, derived, wetted_surface):
    lwl = hull["lwl_m"]
    beam = hull["beam_lwl_m"]
    mean_draft = derived["mean_draft_m"]
    cb = hull["block_coefficient"]
    cp = derived["prismatic_coefficient"]
    cm = hull["midship_coefficient"]
    lcb_percent = hull["lcb_percent_lwl_from_midships_forward_positive"]
    propeller_diameter = propulsion["propeller_diameter_m"]
    expanded_area_ratio = propulsion["expanded_area_ratio"]
    cstern = STERN_CORRECTIONS[features["stern_type"]]
    thrust_deduction = 0.25014 * (beam / lwl) ** 0.28956 * (sqrt(beam * mean_draft) / propeller_diameter) ** 0.2624 / (1 - cp + 0.0225 * lcb_percent) ** 0.01762 + 0.0015 * cstern
    c8 = holtrop_c8(beam, mean_draft, wetted_surface, lwl, propeller_diameter)
    c9 = c8 if c8 < 28 else 32 - 16 / (c8 - 24)
    draft_diameter_ratio = mean_draft / propeller_diameter
    c11 = draft_diameter_ratio if draft_diameter_ratio < 2 else 0.0833333 * draft_diameter_ratio ** 3 + 1.33333
    c19 = 0.12997 / (0.95 - cb) - 0.11056 / (0.95 - cp) if cp < 0.7 else 0.18567 / (1.3571 - cm) - 0.71276 + 0.38648 * cp
    c20 = 1 + 0.015 * cstern
    cp1 = 1.45 * cp - 0.315 - 0.0225 * lcb_percent
    cv = (1 + form_factor) * cf + ca
    wake_fraction = c9 * c20 * cv * lwl / mean_draft * (0.050776 + 0.93405 * c11 * cv / (1 - cp1)) + 0.27915 * c20 * sqrt(beam / (lwl * (1 - cp1))) + c19 * c20
    relative_rotative_efficiency = 0.9922 - 0.05908 * expanded_area_ratio + 0.07424 * (cp - 0.0225 * lcb_percent)
    return {
        "wake_fraction": wake_fraction,
        "thrust_deduction": thrust_deduction,
        "hull_efficiency": (1 - thrust_deduction) / (1 - wake_fraction),
        "relative_rotative_efficiency": relative_rotative_efficiency
    }


def holtrop_c8(beam, mean_draft, wetted_surface, lwl, propeller_diameter):
    beam_draft_ratio = beam / mean_draft
    if beam_draft_ratio < 5:
        return beam * wetted_surface / (lwl * propeller_diameter * mean_draft)
    return wetted_surface * (7 * beam_draft_ratio - 25) / (lwl * propeller_diameter * (beam_draft_ratio - 3))


def resistance_components(speed_mps, rf, form_factor, wave_resistance, bulb_resistance, transom_resistance, correlation_allowance_coefficient, rho, wetted_surface, modeling, appendages, margin):
    rf_form_resistance = rf * form_factor
    correlation_allowance_resistance = 0.5 * rho * speed_mps ** 2 * wetted_surface * correlation_allowance_coefficient
    air_resistance = LEGACY_AIR_DRAG_PRESSURE_COEFFICIENT * speed_mps ** 2 * modeling["deckhouse_cargo_frontal_area_m2"]
    implemented_bare_hull_resistance = rf + rf_form_resistance + wave_resistance + bulb_resistance + transom_resistance
    appendage_mode = appendages.get("mode", "percent_bare_hull_resistance")
    appendage_resistance = 0.0
    equivalent_area = appendages.get("equivalent_wetted_area_form_factor_m2")
    if appendage_mode == "percent_bare_hull_resistance":
        appendage_resistance = implemented_bare_hull_resistance * appendages.get("percent_bare_hull_resistance", 0) / 100
    if appendage_mode == "equivalent_area_form_factor":
        appendage_resistance = rf / wetted_surface * (appendages.get("equivalent_wetted_area_form_factor_m2") or 0)
    subtotal = implemented_bare_hull_resistance + appendage_resistance + correlation_allowance_resistance + air_resistance
    design_margin = subtotal * margin["design_margin_percent"] / 100
    total = subtotal + design_margin
    return {
        "appendage_mode": appendage_mode,
        "appendage_equivalent_wetted_area_form_factor_m2": equivalent_area,
        "frictional_resistance_n": rf,
        "rf_form_resistance_n": rf_form_resistance,
        "form_resistance_n": rf_form_resistance,
        "appendage_resistance_n": appendage_resistance,
        "wave_resistance_n": wave_resistance,
        "bulb_resistance_n": bulb_resistance,
        "transom_resistance_n": transom_resistance,
        "correlation_allowance_resistance_n": correlation_allowance_resistance,
        "air_resistance_n": air_resistance,
        "implemented_resistance_subtotal_n": subtotal,
        "design_margin_resistance_n": design_margin,
        "total_resistance_n": total,
        "resistance_status": "partial_source_safe_components"
    }


def froude_number(speed_mps, lwl_m):
    return speed_mps / sqrt(G * lwl_m)


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
