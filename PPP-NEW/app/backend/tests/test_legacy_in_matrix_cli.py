import json
import tempfile
import unittest
from pathlib import Path

from ppp_core.legacy_in_matrix_cli import main

ROOT = Path(__file__).resolve().parents[3]


class LegacyInMatrixCliTest(unittest.TestCase):
    def test_main_writes_candidate_matrix(self):
        case_path = ROOT / "tests" / "fixtures" / "pppin_sample_import.json"
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            output = temp / "summary.json"
            code = main([
                str(case_path),
                str(temp / "matrix"),
                "--stern-correction",
                "0",
                "--pitch-diameter-ratio",
                "0",
                "--pitch-diameter-ratio",
                "0.8",
                "--water-type-code",
                "3",
                "--first-record-order",
                "depth_before_drafts",
                "--first-record-order",
                "drafts_before_depth",
                "--output",
                str(output)
            ])
            result = json.loads(output.read_text())

            self.assertEqual(code, 0)
            self.assertEqual(result["attempt_count"], 4)
            self.assertEqual(result["attempts"][0]["input_first_record"], "212 32 21 11 11 321")
            self.assertEqual(result["attempts"][1]["input_first_record"], "212 32 11 11 21 321")
            self.assertTrue(Path(result["attempts"][0]["input"]).exists())
            self.assertEqual(Path(result["attempts"][0]["input"]).read_text(), (ROOT / "tests" / "fixtures" / "pppin_sample_candidate.IN").read_text())


if __name__ == "__main__":
    unittest.main()
