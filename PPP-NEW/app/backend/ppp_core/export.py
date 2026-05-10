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
