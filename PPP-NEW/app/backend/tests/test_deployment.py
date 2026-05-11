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

    def test_dockerfile_runs_as_unprivileged_user(self):
        text = (APP / "Dockerfile").read_text()

        self.assertIn("RUN useradd --create-home --shell /usr/sbin/nologin ppp", text)
        self.assertIn("USER ppp", text)

    def test_dockerfile_disables_bytecode_writes(self):
        text = (APP / "Dockerfile").read_text()

        self.assertIn("ENV PYTHONDONTWRITEBYTECODE=1", text)

    def test_dockerignore_excludes_non_runtime_backend_tests(self):
        text = (APP / ".dockerignore").read_text()

        self.assertIn("backend/tests/", text)

    def test_compose_services_use_restart_policy(self):
        text = (APP / "docker-compose.yml").read_text()

        self.assertEqual(text.count("restart: unless-stopped"), 2)

    def test_compose_nginx_waits_for_backend_health(self):
        text = (APP / "docker-compose.yml").read_text()

        self.assertIn("condition: service_healthy", text)

    def test_nginx_proxy_has_basic_hardening(self):
        text = (APP / "nginx" / "default.conf").read_text()

        self.assertIn("client_max_body_size 10m;", text)
        self.assertIn("add_header X-Content-Type-Options nosniff always;", text)
        self.assertIn("add_header Referrer-Policy no-referrer always;", text)
        self.assertIn("proxy_connect_timeout 5s;", text)
        self.assertIn("proxy_send_timeout 30s;", text)
        self.assertIn("proxy_read_timeout 30s;", text)


if __name__ == "__main__":
    unittest.main()
