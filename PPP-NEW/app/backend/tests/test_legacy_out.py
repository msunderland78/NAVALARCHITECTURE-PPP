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

    def test_rejects_non_finite_numbers(self):
        with self.assertRaisesRegex(ValueError, "legacy OUT numeric value must be finite"):
            parse_legacy_out("Input Verification:\nKinematic Viscosity (m^2/s) = 1.0D+999\n")

    def test_powering_rows_without_speed_mps(self):
        text = "\n".join([
            "Resistance, Effective Power, Propulsion Factors and Required Thrust",
            "V(kts) RT(N) PE(kW) w t REQ.THR(N) etaH etaRR",
            "15.00 610068.1 4707.65 0.2440 0.1841 747752.3 1.0792 0.9916"
        ])
        parsed = parse_legacy_out(text, "OUT")

        self.assertTrue(parsed["calculation_completed"])
        self.assertEqual(len(parsed["powering_rows"]), 1)
        self.assertNotIn("speed_mps", parsed["powering_rows"][0])
        self.assertAlmostEqual(parsed["powering_rows"][0]["total_resistance_n"], 610068.1)

    def test_input_label_with_equals(self):
        parsed = parse_legacy_out("Input Verification:\nMidship Coefficient to LWL CM=CX       =    0.9800\n")

        value = parsed["input_verification"]["midship_coefficient_to_lwl_cm_cx"]
        self.assertAlmostEqual(value["numeric_value"], 0.98)
        self.assertEqual(value["raw_value"], "0.9800")

    def test_parse_captured_oracle_fixture(self):
        parsed = parse_legacy_out((ROOT / "tests" / "fixtures" / "pppin_sample_legacy_oracle.OUT").read_text(), "OUT")

        self.assertTrue(parsed["calculation_completed"])
        self.assertEqual(len(parsed["coefficient_rows"]), 8)
        self.assertEqual(len(parsed["component_rows"]), 8)
        self.assertEqual(len(parsed["powering_rows"]), 8)
        self.assertAlmostEqual(parsed["coefficient_rows"][0]["frictional_resistance_n"], 354648.6)
        self.assertAlmostEqual(parsed["component_rows"][0]["wave_resistance_n"], 14254.6)
        self.assertAlmostEqual(parsed["powering_rows"][0]["total_resistance_n"], 610068.1)


def sample_out():
    return (ROOT / "tests" / "fixtures" / "representative_legacy.OUT").read_text()


if __name__ == "__main__":
    unittest.main()
