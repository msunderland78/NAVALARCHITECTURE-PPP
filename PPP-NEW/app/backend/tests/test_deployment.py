import unittest
from pathlib import Path


APP = Path(__file__).resolve().parents[2]


class DeploymentTest(unittest.TestCase):
    def test_dockerfile_copies_runtime_files_only(self):
        text = (APP / "Dockerfile").read_text()

        self.assertIn("COPY backend/server.py ./backend/server.py", text)
        self.assertIn("COPY backend/ppp_core ./backend/ppp_core", text)
        self.assertIn("COPY frontend ./frontend", text)
        self.assertNotIn("COPY backend ./backend", text)
        self.assertNotIn("PPP-OLD", text)

    def test_dockerignore_excludes_non_runtime_backend_tests(self):
        text = (APP / ".dockerignore").read_text()

        self.assertIn("backend/tests/", text)


if __name__ == "__main__":
    unittest.main()
