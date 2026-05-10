import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ppp_core.api import route


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.respond(*route("GET", self.path))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        self.respond(*route("POST", self.path, body))

    def respond(self, status, content_type, payload):
        if content_type == "application/json":
            body = json.dumps(payload).encode("utf-8")
        else:
            body = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    run()
