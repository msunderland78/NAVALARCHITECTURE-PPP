from math import log10, sqrt


KNOT_TO_MPS = 0.514444
METER_TO_FOOT = 3.280839895
G = 9.80665


def evaluate_case(case, point_count=1):
    hull = case["hull"]
    water = case["water"]
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
        speeds.append(evaluate_speed(lwl, speed_knots, water["kinematic_viscosity_m2_s"]))
    return {
        "project": case["project"],
        "derived": derived,
        "applicability": applicability(case, derived, speeds),
        "speeds": speeds
    }


def evaluate_speed(lwl_m, speed_knots, nu):
    speed_mps = speed_knots * KNOT_TO_MPS
    reynolds = speed_mps * lwl_m / nu
    cf = 0.075 / ((log10(reynolds) - 2) ** 2)
    return {
        "speed_knots": speed_knots,
        "speed_mps": speed_mps,
        "froude_number": speed_mps / sqrt(G * lwl_m),
        "speed_length_ratio": speed_knots / sqrt(lwl_m * METER_TO_FOOT),
        "reynolds_number": reynolds,
        "friction_coefficient": cf
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
