import unittest
from pathlib import Path

from ppp_core.legacy_out import parse_legacy_out


ROOT = Path(__file__).resolve().parents[3]


class LegacyOutTest(unittest.TestCase):
    def test_parse_legacy_out(self):
        parsed = parse_legacy_out(sample_out(), "OUT")

        self.assertEqual(parsed["program"], "Power Prediction Program (PPP-1.8) by M. G. Parsons")
        self.assertTrue(parsed["calculation_completed"])
        self.assertAlmostEqual(parsed["input_verification"]["length_of_waterline_lwl_m"]["numeric_value"], 212.0)
        self.assertAlmostEqual(parsed["input_verification"]["kinematic_viscosity_m_2_s"]["numeric_value"], 1.18831e-6)
        self.assertEqual(len(parsed["coefficient_rows"]), 2)
        self.assertEqual(len(parsed["component_rows"]), 2)
        self.assertEqual(len(parsed["powering_rows"]), 2)
        self.assertAlmostEqual(parsed["coefficient_rows"][0]["friction_coefficient"], 0.00147166)
        self.assertAlmostEqual(parsed["component_rows"][1]["wave_resistance_n"], 82000.0)
        self.assertAlmostEqual(parsed["powering_rows"][0]["required_thrust_n"], 430000.0)

    def test_fortran_d_exponents(self):
        parsed = parse_legacy_out("Input Verification:\nKinematic Viscosity (m^2/s) = 1.188310D-006\n")

        self.assertAlmostEqual(parsed["input_verification"]["kinematic_viscosity_m_2_s"]["numeric_value"], 1.18831e-6)


def sample_out():
    return (ROOT / "tests" / "fixtures" / "representative_legacy.OUT").read_text()


if __name__ == "__main__":
    unittest.main()
