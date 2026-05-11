import csv
from io import StringIO


SPEED_COLUMNS = [
    "speed_knots",
    "speed_mps",
    "froude_number",
    "speed_length_ratio",
    "reynolds_number",
    "friction_coefficient",
    "residual_resistance_coefficient",
    "correlation_allowance_coefficient",
    "appendage_mode",
    "appendage_equivalent_wetted_area_form_factor_m2",
    "frictional_resistance_n",
    "rf_form_resistance_n",
    "form_resistance_n",
    "appendage_resistance_n",
    "wave_resistance_n",
    "bulb_resistance_n",
    "transom_resistance_n",
    "correlation_allowance_resistance_n",
    "air_resistance_n",
    "implemented_resistance_subtotal_n",
    "design_margin_resistance_n",
    "total_resistance_n",
    "effective_power_kw",
    "wake_fraction",
    "thrust_deduction",
    "required_thrust_n",
    "hull_efficiency",
    "relative_rotative_efficiency",
    "resistance_status"
]


def speeds_to_csv(result):
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=SPEED_COLUMNS)
    writer.writeheader()
    for row in result["speeds"]:
        writer.writerow({column: row[column] for column in SPEED_COLUMNS})
    return output.getvalue()


def result_to_markdown(result, case=None):
    lines = [
        f"# {result['project']['name']}",
        "",
        f"Run ID: {result['project']['run_id']}",
        "",
        "## Engineering Review",
        "",
        result["engineering_review"]["note"],
        "",
        f"Calculation status: `{result['engineering_review']['status']}`",
        "",
    ]
    warnings = result["engineering_review"].get("warnings", [])
    if warnings:
        lines.extend(["Warnings:", ""])
        for warning in warnings:
            lines.append(f"- {warning}")
        lines.append("")
    if case is not None:
        lines.extend(input_summary_lines(case))
    lines.extend([
        "## Derived Hull Summary",
        "",
        "| Item | Value |",
        "|---|---:|",
        f"| Mean draft, m | {format_report_number(result['derived']['mean_draft_m'])} |",
        f"| Prismatic coefficient | {format_report_number(result['derived']['prismatic_coefficient'])} |",
        f"| Displacement, tonnes | {format_report_number(result['derived']['displacement_mass_tonnes'])} |",
        f"| L/V^(1/3) | {format_report_number(result['derived']['length_displacement_ratio'])} |",
        f"| Active wetted surface, m2 | {format_report_number(result['modeling']['wetted_surface_m2'])} |",
        f"| Active half angle, deg | {format_report_number(result['modeling']['half_angle_entrance_degrees'])} |",
        "",
        "## Applicability",
        "",
        "| Check | Value | Range | Status |",
        "|---|---:|---:|---|"
    ])
    for check in result["applicability"]:
        status = "OK" if check["ok"] else "Review"
        lines.append(f"| {check['label']} | {format_report_number(check['value'])} | {check['lower']} to {check['upper']} | {status} |")
    lines.extend([
        "",
        "## Speed Results",
        "",
        "| V, kn | Fn | RT, kN | PE, kW | Required thrust, kN | Status |",
        "|---:|---:|---:|---:|---:|---|"
    ])
    for row in result["speeds"]:
        lines.append(
            f"| {format_report_number(row['speed_knots'])} | "
            f"{format_report_number(row['froude_number'])} | "
            f"{format_report_number(row['total_resistance_n'] / 1000)} | "
            f"{format_report_number(row['effective_power_kw'])} | "
            f"{format_report_number(row['required_thrust_n'] / 1000)} | "
            f"`{row['resistance_status']}` |"
        )
    return "\n".join(lines) + "\n"


def input_summary_lines(case):
    return [
        "## Input Summary",
        "",
        "| Item | Value |",
        "|---|---:|",
        f"| Initial speed, kn | {format_report_number(case['speed_sweep']['initial_speed_knots'])} |",
        f"| Speed increment, kn | {format_report_number(case['speed_sweep']['speed_increment_knots'])} |",
        f"| Water type | {case['water']['type']} |",
        f"| Water density, kg/m3 | {format_report_number(case['water']['density_kg_m3'])} |",
        f"| Kinematic viscosity, m2/s | {format_scientific(case['water']['kinematic_viscosity_m2_s'])} |",
        f"| Propulsion type | {case['propulsion']['type']} |",
        f"| Appendage mode | {case['appendages']['mode']} |",
        f"| Wetted surface mode | {case['modeling']['wetted_surface_mode']} |",
        f"| Half angle mode | {case['modeling']['half_angle_entrance_mode']} |",
        f"| Air drag | {'yes' if case['modeling']['air_drag'] else 'no'} |",
        f"| Design margin, percent | {format_report_number(case['margin']['design_margin_percent'])} |",
        "",
    ]


def format_report_number(value):
    if abs(value) >= 100:
        return f"{value:.2f}"
    return f"{value:.4f}"


def format_scientific(value):
    return f"{value:.6g}"
