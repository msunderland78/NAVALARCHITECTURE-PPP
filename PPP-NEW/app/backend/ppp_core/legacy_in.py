PROPULSION_CODES = {
    "single_screw_conventional_stern": 1,
    "single_screw_open_flow_stern": 2,
    "twin_screw": 3
}

WATER_CODES = {
    "custom": 1,
    "fresh_water_15_c": 2,
    "salt_water_15_c": 3
}

STERN_CORRECTION_CANDIDATES = {
    "normal_shaped_sections": 0,
    "v_shaped_sections": -10,
    "u_shaped_sections_with_hogner_stern": 10,
    "pram_with_gondola": 0
}


def generate_candidate_legacy_in(case, options=None):
    options = options or {}
    hull = case["hull"]
    features = case["features"]
    propulsion = case["propulsion"]
    appendages = case["appendages"]
    modeling = case["modeling"]
    water = case["water"]
    margin = case["margin"]
    speed_sweep = case["speed_sweep"]
    rows = [
        [
            hull["lwl_m"],
            hull["beam_lwl_m"],
            modeling["depth_at_bow_m"],
            hull["draft_forward_m"],
            hull["draft_aft_m"],
            modeling["deckhouse_cargo_frontal_area_m2"]
        ],
        [
            hull["block_coefficient"],
            hull["midship_coefficient"],
            hull["waterplane_coefficient"],
            margin["design_margin_percent"] / 100
        ],
        [
            appendage_primary_value(appendages),
            appendage_model_total(appendages),
            features["bulb_area_station_0_m2"],
            features["bulb_vertical_center_m"],
            features["transom_immersed_area_zero_speed_m2"],
            options.get("stern_correction", stern_correction(features["stern_type"])),
            options.get("propulsion_type_code", propulsion_code(propulsion["type"]))
        ],
        [hull["lcb_percent_lwl_from_midships_forward_positive"]],
        [
            propulsion["propeller_diameter_m"],
            modeling["wetted_surface_m2"],
            modeling["half_angle_entrance_degrees"]
        ],
        [
            propulsion["expanded_area_ratio"],
            propulsion.get("pitch_diameter_ratio") or options.get("pitch_diameter_ratio", 0),
            options.get("water_type_code", water_code(water["type"]))
        ],
        [
            speed_sweep["initial_speed_knots"],
            speed_sweep["speed_increment_knots"]
        ],
        [
            water["density_kg_m3"],
            water["kinematic_viscosity_m2_s"]
        ]
    ]
    return "".join(" ".join(format_legacy_number(value) for value in row) + "\n" for row in rows)


def appendage_primary_value(appendages):
    if appendages.get("mode") == "equivalent_area_form_factor":
        return appendages.get("equivalent_wetted_area_form_factor_m2") or 0
    return appendages.get("percent_bare_hull_resistance", 0) / 100


def appendage_model_total(appendages):
    if appendages.get("mode") == "equivalent_area_form_factor":
        return appendages.get("equivalent_wetted_area_form_factor_m2") or 0
    return 0


def propulsion_code(value):
    return PROPULSION_CODES.get(value, 1)


def water_code(value):
    return WATER_CODES.get(value, 1)


def stern_correction(value):
    return STERN_CORRECTION_CANDIDATES.get(value, 0)


def format_legacy_number(value):
    return f"{float(value):.12g}"
