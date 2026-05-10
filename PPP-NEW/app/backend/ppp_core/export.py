import csv
from io import StringIO


SPEED_COLUMNS = [
    "speed_knots",
    "speed_mps",
    "froude_number",
    "speed_length_ratio",
    "reynolds_number",
    "friction_coefficient",
    "frictional_resistance_n"
]


def speeds_to_csv(result):
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=SPEED_COLUMNS)
    writer.writeheader()
    for row in result["speeds"]:
        writer.writerow({column: row[column] for column in SPEED_COLUMNS})
    return output.getvalue()
