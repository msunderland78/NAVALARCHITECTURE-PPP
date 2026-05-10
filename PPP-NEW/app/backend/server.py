import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ppp_core.api import route


FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
STATIC_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript"
}


class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        if self.path == "/" or self.path in ("/app.js", "/styles.css"):
            self.serve_static(head_only=True)
        else:
            self.respond(*route("GET", self.path), head_only=True)

    def do_GET(self):
        if self.path == "/" or self.path in ("/app.js", "/styles.css"):
            self.serve_static()
        else:
            self.respond(*route("GET", self.path))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        self.respond(*route("POST", self.path, body))

    def respond(self, status, content_type, payload, head_only=False):
        if content_type == "application/json":
            body = json.dumps(payload).encode("utf-8")
        else:
            body = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def serve_static(self, head_only=False):
        if self.path == "/":
            path = FRONTEND / "index.html"
        else:
            path = FRONTEND / self.path.lstrip("/")
        if not path.exists() or path.parent != FRONTEND:
            self.respond(404, "application/json", {"error": "not found"}, head_only)
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", STATIC_TYPES.get(path.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head_only:
            self.wfile.write(body)


def run(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    run(os.getenv("PPP_HOST", "127.0.0.1"), int(os.getenv("PPP_PORT", "8000")))
