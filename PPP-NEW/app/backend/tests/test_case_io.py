import json
import tempfile
import unittest
from pathlib import Path

from ppp_core.case_io import load_case_json


class CaseIoTest(unittest.TestCase):
    def test_load_case_json_accepts_raw_case(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "case.json"
            path.write_text(json.dumps({"project": {"name": "Example"}}))

            self.assertEqual(load_case_json(path), {"project": {"name": "Example"}})

    def test_load_case_json_accepts_wrapped_case(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "case.json"
            path.write_text(json.dumps({"case": {"project": {"name": "Example"}}}))

            self.assertEqual(load_case_json(path), {"project": {"name": "Example"}})

    def test_load_case_json_rejects_bad_shapes(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "case.json"
            path.write_text("[]")
            with self.assertRaisesRegex(ValueError, "case JSON must be an object"):
                load_case_json(path)

            path.write_text(json.dumps({"case": []}))
            with self.assertRaisesRegex(ValueError, "case JSON case must be an object"):
                load_case_json(path)


if __name__ == "__main__":
    unittest.main()
