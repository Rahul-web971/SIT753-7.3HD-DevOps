"""API integration tests against an ephemeral local server."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app.server import TASKS, Handler


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        TASKS.clear()

    def request(self, path, method="GET", payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        req = Request(self.base + path, data=data, method=method)
        with urlopen(req, timeout=3) as response:
            return response.status, response.read().decode()

    def test_health_and_metrics(self):
        self.assertEqual(self.request("/health")[0], 200)
        self.assertIn("app_requests_total", self.request("/metrics")[1])

    def test_create_list_and_complete(self):
        status, body = self.request("/tasks", "POST", {"title": "Demo"})
        self.assertEqual(status, 201)
        task_id = json.loads(body)["id"]
        self.assertIn("Demo", self.request("/tasks")[1])
        self.assertTrue(json.loads(self.request(f"/tasks/{task_id}", "PATCH")[1])["done"])

    def test_invalid_title_rejected(self):
        with self.assertRaises(HTTPError) as error:
            self.request("/tasks", "POST", {"title": " "})
        self.assertEqual(error.exception.code, 400)
