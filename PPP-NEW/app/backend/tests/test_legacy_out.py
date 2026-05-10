import unittest

from ppp_core.legacy_out import parse_legacy_out


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
    return """Power Prediction Program (PPP-1.8) by M. G. Parsons

 Input Verification:
 Length of Waterline LWL (m)            = 212.00
 Maximum Beam on LWL (m)                = 32.00
 Kinematic Viscosity (m^2/s)            = 1.188310e-006

 Speed, Resistance Coefficients
 and Frictional Resistance RF(N):
 V(kts) V(m/s) FN SLRATIO CF CR CA RF
 15.00 7.71666 0.16924 0.56876 0.00147166 0.00090 0.00040 354654.0
 17.00 8.74555 0.19180 0.64460 0.00145200 0.00105 0.00040 451000.0

 Remaining Resistance Components (N):
 V(kts) RF*K1 RAPP RW RB RTR RA RAIR
 15.00 410000.0 17732.7 60000.0 1200.0 500.0 9000.0 3400.0
 17.00 522000.0 22550.0 82000.0 1600.0 700.0 11200.0 4300.0

 Resistance, Effective Power, Propulsion Factors
 and Required Thrust
 V(kts) V(m/s) RT(N) PE(kW) w t REQ.THR(N) etaH etaRR
 15.00 7.71666 391006.0 3017.3 0.22 0.18 430000.0 1.05 0.99
 17.00 8.74555 490000.0 4285.3 0.23 0.19 548000.0 1.04 0.98

 Calculation Completed Successfully!
"""


if __name__ == "__main__":
    unittest.main()
