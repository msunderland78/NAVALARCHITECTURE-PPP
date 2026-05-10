import json
import tempfile
import unittest
from pathlib import Path

from ppp_core.legacy_sweep_cli import main


ROOT = Path(__file__).resolve().parents[3]


class LegacySweepCliTest(unittest.TestCase):
    def test_main_writes_sweep_summary(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            case_path = temp / "case.json"
            fake_exe = temp / "PPPFTRN.EXE"
            fake_wine = temp / "fake_wine.sh"
            output = temp / "summary.json"
            captured_out = temp / "captured.OUT"
            captured_parsed = temp / "captured-out.json"
            case_path.write_text(json.dumps({"case": case}))
            fake_exe.write_bytes(b"legacy")
            fake_wine.write_text("#!/bin/sh\nif grep -q '0.8 0.8 1' IN; then printf 'Power Prediction Program (PPP-1.8) by M. G. Parsons\\nCalculation Completed Successfully!' > OUT; fi\nexit 0\n")
            fake_wine.chmod(0o755)

            code = main([
                str(case_path),
                str(fake_exe),
                str(temp / "sweep"),
                "--wine",
                str(fake_wine),
                "--wine-arg=--backend=curses",
                "--timeout-seconds",
                "5",
                "--stern-correction",
                "0",
                "--pitch-diameter-ratio",
                "0",
                "--pitch-diameter-ratio",
                "0.8",
                "--water-type-code",
                "1",
                "--first-record-order",
                "drafts_before_depth",
                "--appendage-primary-value",
                "0.05",
                "--appendage-model-total",
                "0",
                "--capture-out",
                str(captured_out),
                "--capture-parsed-out",
                str(captured_parsed),
                "--output",
                str(output)
            ])
            result = json.loads(output.read_text())

            self.assertEqual(code, 0)
            self.assertEqual(result["attempt_count"], 2)
            self.assertEqual(result["out_count"], 1)
            self.assertEqual(result["successful_attempts"][0]["options"]["pitch_diameter_ratio"], 0.8)
            self.assertIn("--backend=curses", result["successful_attempts"][0]["command"])
            self.assertEqual(result["successful_attempts"][0]["options"]["first_record_order"], "drafts_before_depth")
            self.assertEqual(result["case_json"], str(case_path))
            self.assertEqual(result["legacy_exe"], str(fake_exe))
            self.assertEqual(result["captured_out"], str(captured_out))
            self.assertEqual(result["captured_parsed_out"], str(captured_parsed))
            self.assertIn("Power Prediction Program", captured_out.read_text())
            self.assertTrue(json.loads(captured_parsed.read_text())["calculation_completed"])


if __name__ == "__main__":
    unittest.main()
