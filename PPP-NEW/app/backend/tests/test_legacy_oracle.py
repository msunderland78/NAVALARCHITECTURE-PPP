import json
import tempfile
import unittest
from pathlib import Path

from ppp_core.legacy_oracle import run_oracle, stage_oracle_run


ROOT = Path(__file__).resolve().parents[3]


class LegacyOracleTest(unittest.TestCase):
    def test_stage_oracle_run(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            fake_exe = temp / "fake.exe"
            fake_exe.write_bytes(b"legacy")
            paths = stage_oracle_run(case, fake_exe, temp / "work")

            self.assertEqual(paths["exe"].read_bytes(), b"legacy")
            self.assertEqual(paths["input"].read_text(), (ROOT / "tests" / "fixtures" / "pppin_sample_candidate.IN").read_text())

    def test_run_oracle_with_fake_wine(self):
        case = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            fake_exe = temp / "fake.exe"
            fake_exe.write_bytes(b"legacy")
            fake_wine = temp / "fake_wine.sh"
            fake_wine.write_text("#!/bin/sh\nprintf 'fake stdout'\nprintf 'fake stderr' >&2\nexit 7\n")
            fake_wine.chmod(0o755)
            result = run_oracle(case, fake_exe, temp / "work", wine=str(fake_wine), timeout_seconds=5)

            self.assertEqual(result["returncode"], 7)
            self.assertIn("212 32 21 11 11 321", result["input"])
            self.assertEqual(result["stdout"], "fake stdout")
            self.assertEqual(result["stderr"], "fake stderr")
            self.assertFalse(result["out_exists"])


if __name__ == "__main__":
    unittest.main()
