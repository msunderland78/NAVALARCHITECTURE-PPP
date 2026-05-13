import json
import tempfile
import unittest
from pathlib import Path

from ppp_core.evaluate_cli import main

ROOT = Path(__file__).resolve().parents[3]


class EvaluateCliTest(unittest.TestCase):
    def test_main_writes_result(self):
        case_path = ROOT / "tests" / "fixtures" / "pppin_sample_import.json"
        expected = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_modern_result.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "result.json"
            code = main([
                str(case_path),
                "--point-count",
                "2",
                "--output",
                str(output)
            ])

            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.read_text()), expected)


if __name__ == "__main__":
    unittest.main()
