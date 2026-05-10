import json
import tempfile
import unittest
from pathlib import Path

from ppp_core.legacy_in_cli import main


ROOT = Path(__file__).resolve().parents[3]


class LegacyInCliTest(unittest.TestCase):
    def test_main_writes_candidate_in(self):
        case_path = ROOT / "tests" / "fixtures" / "pppin_sample_import.json"
        fixture = (ROOT / "tests" / "fixtures" / "pppin_sample_candidate.IN").read_text()
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "candidate.IN"
            code = main([str(case_path), "--output", str(output)])

            self.assertEqual(code, 0)
            self.assertEqual(output.read_text(), fixture)

    def test_main_writes_option_variant(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            case_path = temp / "case.json"
            output = temp / "candidate.IN"
            case_path.write_text(json.dumps({"case": case}))
            code = main([
                str(case_path),
                "--first-record-order",
                "drafts_before_depth",
                "--stern-correction",
                "-10",
                "--pitch-diameter-ratio",
                "0.8",
                "--water-type-code",
                "2",
                "--appendage-primary-value",
                "5",
                "--appendage-model-total",
                "0.05",
                "--propeller-record-order",
                "dp_wetted_half",
                "--output",
                str(output)
            ])
            lines = output.read_text().splitlines()

            self.assertEqual(code, 0)
            self.assertEqual(lines[0], "212 32 11 11 21 321")
            self.assertEqual(lines[2], "5 0.05 21 4 16 -10 1")
            self.assertEqual(lines[4], "8 7890 12.11")
            self.assertEqual(lines[5], "0.8 0.8 2")


if __name__ == "__main__":
    unittest.main()
