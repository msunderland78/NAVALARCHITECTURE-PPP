import shutil
import subprocess
import unittest
from pathlib import Path

FRONTEND_TEST = Path(__file__).resolve().parents[2] / "frontend" / "tests" / "pure.test.js"


class FrontendPureTest(unittest.TestCase):
    def test_node_pure_helpers_pass(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node not installed")
        result = subprocess.run(
            [node, "--test", str(FRONTEND_TEST)],
            capture_output=True,
            text=True,
            timeout=30
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout={result.stdout}\nstderr={result.stderr}")
        self.assertIn("# pass 15", result.stdout)
        self.assertIn("# fail 0", result.stdout)
