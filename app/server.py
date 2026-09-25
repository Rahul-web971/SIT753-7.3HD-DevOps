"""Small task API with health and Prometheus metrics endpoints."""
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

START = time.time()
TASKS = {}
COUNTERS = {"requests": 0, "errors": 0}


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        COUNTERS["requests"] += 1
        path = urlparse(self.path).path
        if path == "/health":
            self.respond(200, {"status": "ok", "version": os.getenv("APP_VERSION", "local")})
        elif path == "/tasks":
            self.respond(200, {"tasks": list(TASKS.values())})
        elif path == "/metrics":
            body = (
                f"app_requests_total {COUNTERS['requests']}\n"
                f"app_errors_total {COUNTERS['errors']}\n"
                f"app_uptime_seconds {time.time() - START:.1f}\n"
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            COUNTERS["errors"] += 1
            self.respond(404, {"error": "not found"})

    def do_POST(self):
        COUNTERS["requests"] += 1
        if urlparse(self.path).path != "/tasks":
            COUNTERS["errors"] += 1
            return self.respond(404, {"error": "not found"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > 2048:
                raise ValueError("invalid body size")
            payload = json.loads(self.rfile.read(size))
            title = payload.get("title")
            if not isinstance(title, str) or not title.strip() or len(title) > 120:
                raise ValueError("title must be 1 to 120 characters")
        except (ValueError, TypeError, json.JSONDecodeError):
            COUNTERS["errors"] += 1
            return self.respond(400, {"error": "invalid task"})
        task_id = str(len(TASKS) + 1)
        task = {"id": task_id, "title": title.strip(), "done": False}
        TASKS[task_id] = task
        self.respond(201, task)

    def do_PATCH(self):
        COUNTERS["requests"] += 1
        parts = urlparse(self.path).path.split("/")
        if len(parts) != 3 or parts[1] != "tasks" or parts[2] not in TASKS:
            COUNTERS["errors"] += 1
            return self.respond(404, {"error": "task not found"})
        TASKS[parts[2]]["done"] = True
        self.respond(200, TASKS[parts[2]])


if __name__ == "__main__":
        ThreadingHTTPServer((os.getenv("HOST", "127.0.0.1"), int(os.getenv("PORT", "8000"))), Handler).serve_forever()
