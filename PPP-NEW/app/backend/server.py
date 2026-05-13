import json
import os
import sys
import time
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
MAX_REQUEST_BYTES = 16 * 1024 * 1024


class RequestTooLarge(ValueError):
    pass


class Handler(BaseHTTPRequestHandler):
    server_version = "PPPBackend"
    sys_version = ""

    def log_message(self, format, *args):
        method = getattr(self, "command", "") or ""
        path = getattr(self, "path", "") or ""
        status = ""
        size = ""
        if format == '"%s" %s %s' and len(args) == 3:
            status = str(args[1])
            size = str(args[2])
        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "remote": self.address_string(),
            "method": method,
            "path": path,
            "status": status,
            "size": size
        }
        sys.stdout.write(json.dumps(record) + "\n")
        sys.stdout.flush()

    def log_error(self, format, *args):
        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "remote": self.address_string(),
            "level": "error",
            "message": format % args if args else format
        }
        sys.stderr.write(json.dumps(record) + "\n")
        sys.stderr.flush()

    def do_OPTIONS(self):
        self.respond(204, "application/json", {}, headers={"Allow": "GET, HEAD, POST, OPTIONS"})

    def do_PUT(self):
        self.respond_method_not_allowed()

    def do_DELETE(self):
        self.respond_method_not_allowed()

    def do_PATCH(self):
        self.respond_method_not_allowed()

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
        except RequestTooLarge as error:
            self.respond(413, "application/json", {"error": str(error)})
            return
        except ValueError as error:
            self.respond(400, "application/json", {"error": str(error)})
            return
        body = self.rfile.read(length)
        if len(body) != length:
            self.respond(400, "application/json", {"error": "Content-Length did not match body length"})
            return
        self.respond(*route("POST", path, body))

    def respond_method_not_allowed(self):
        self.respond(405, "application/json", {"error": "method not allowed"}, headers={"Allow": "GET, HEAD, POST, OPTIONS"})

    def respond(self, status, content_type, payload, head_only=False, headers=None):
        if content_type == "application/json":
            body = json.dumps(payload).encode("utf-8")
        else:
            body = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_security_headers()
        for name, value in (headers or {}).items():
            self.send_header(name, value)
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
    if length > MAX_REQUEST_BYTES:
        raise RequestTooLarge(f"Content-Length exceeds maximum of {MAX_REQUEST_BYTES} bytes")
    return length


def run(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    run(os.getenv("PPP_HOST", "127.0.0.1"), int(os.getenv("PPP_PORT", "8000")))
