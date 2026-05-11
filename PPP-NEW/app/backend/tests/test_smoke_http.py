import contextlib
import importlib.util
import io
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

from server import Handler


ROOT = Path(__file__).resolve().parents[3]
SMOKE_PATH = ROOT / "tools" / "smoke_http.py"


def load_smoke_http():
    spec = importlib.util.spec_from_file_location("smoke_http", SMOKE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class QuietHandler(Handler):
    def log_message(self, format, *args):
        pass


class SmokeHttpTest(unittest.TestCase):
    def test_smoke_http_passes_against_backend_server(self):
        smoke_http = load_smoke_http()
        server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base_url = f"http://127.0.0.1:{server.server_address[1]}"
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = smoke_http.main(["--base-url", base_url])
            payload = json.loads(stream.getvalue())
            self.assertEqual(0, code)
            self.assertTrue(payload["passed"])
            self.assertEqual([True] * len(payload["checks"]), [check["passed"] for check in payload["checks"]])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
