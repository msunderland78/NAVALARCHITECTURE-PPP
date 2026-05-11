import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from ppp_core.api import route


FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
STATIC_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript"
}
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer"
}


class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        path = request_path(self.path)
        if path == "/" or path in ("/app.js", "/styles.css"):
            self.serve_static(path, head_only=True)
        else:
            self.respond(*route("GET", path), head_only=True)

    def do_GET(self):
        path = request_path(self.path)
        if path == "/" or path in ("/app.js", "/styles.css"):
            self.serve_static(path)
        else:
            self.respond(*route("GET", path))

    def do_POST(self):
        path = request_path(self.path)
        try:
            length = request_content_length(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            self.respond(400, "application/json", {"error": str(error)})
            return
        body = self.rfile.read(length)
        self.respond(*route("POST", path, body))

    def respond(self, status, content_type, payload, head_only=False):
        if content_type == "application/json":
            body = json.dumps(payload).encode("utf-8")
        else:
            body = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_security_headers()
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def serve_static(self, request_path_value, head_only=False):
        if request_path_value == "/":
            path = FRONTEND / "index.html"
        else:
            path = FRONTEND / request_path_value.lstrip("/")
        if not path.exists() or path.parent != FRONTEND:
            self.respond(404, "application/json", {"error": "not found"}, head_only)
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", STATIC_TYPES.get(path.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.send_security_headers()
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def send_security_headers(self):
        for name, value in SECURITY_HEADERS.items():
            self.send_header(name, value)


def request_path(target):
    return urlsplit(target).path


def request_content_length(value):
    try:
        length = int(value)
    except (TypeError, ValueError):
        raise ValueError("Content-Length must be a non-negative integer")
    if length < 0:
        raise ValueError("Content-Length must be a non-negative integer")
    return length


def run(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    run(os.getenv("PPP_HOST", "127.0.0.1"), int(os.getenv("PPP_PORT", "8000")))
