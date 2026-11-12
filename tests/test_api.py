import json
import threading
import unittest
import urllib.error
import urllib.request

from app.server import create_server


class ApiTests(unittest.TestCase):
    """Testes de integração"""

    def setUp(self):
        self.server = create_server("127.0.0.1", 0)
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def call(self, method, path, body=None, raw=None):
        data = raw if raw is not None else (
            json.dumps(body).encode("utf-8") if body is not None else None
        )
        request = urllib.request.Request(
            self.base + path,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                status, content = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, content = error.code, error.read()
            error.close()
        return status, (json.loads(content) if content else None)

    def test_health(self):
        status, body = self.call("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_health_rejects_post(self):
        status, _ = self.call("POST", "/health", {})
        self.assertEqual(status, 405)

    def test_unknown_route_returns_404(self):
        self.assertEqual(self.call("GET", "/nada")[0], 404)
        self.assertEqual(self.call("GET", "/tasks/abc")[0], 404)

    def test_empty_list(self):
        self.assertEqual(self.call("GET", "/tasks"), (200, []))

    def test_create_and_get_task(self):
        status, created = self.call("POST", "/tasks", {"title": "Configurar CI"})
        self.assertEqual(status, 201)
        self.assertEqual(created["title"], "Configurar CI")
        status, fetched = self.call("GET", f"/tasks/{created['id']}")
        self.assertEqual((status, fetched), (200, created))

    def test_trailing_slash_is_accepted(self):
        self.assertEqual(self.call("GET", "/tasks/")[0], 200)

    def test_create_without_title_returns_400(self):
        status, body = self.call("POST", "/tasks", {"outro": 1})
        self.assertEqual(status, 400)
        self.assertIn("title", body["error"])

    def test_invalid_json_returns_400(self):
        status, _ = self.call("POST", "/tasks", raw=b"{isso nao e json")
        self.assertEqual(status, 400)

    def test_json_must_be_an_object(self):
        status, _ = self.call("POST", "/tasks", raw=b"[1, 2, 3]")
        self.assertEqual(status, 400)

    def test_missing_body_returns_400(self):
        self.assertEqual(self.call("POST", "/tasks")[0], 400)

    def test_update_task(self):
        self.call("POST", "/tasks", {"title": "A"})
        status, body = self.call("PUT", "/tasks/1", {"done": True})
        self.assertEqual(status, 200)
        self.assertTrue(body["done"])

    def test_update_invalid_value_returns_400(self):
        self.call("POST", "/tasks", {"title": "A"})
        self.assertEqual(self.call("PUT", "/tasks/1", {"done": "talvez"})[0], 400)

    def test_update_missing_task_returns_404(self):
        self.assertEqual(self.call("PUT", "/tasks/99", {"done": True})[0], 404)

    def test_delete_task(self):
        self.call("POST", "/tasks", {"title": "A"})
        self.assertEqual(self.call("DELETE", "/tasks/1")[0], 204)
        self.assertEqual(self.call("GET", "/tasks/1")[0], 404)
        self.assertEqual(self.call("DELETE", "/tasks/1")[0], 404)

    def test_method_not_allowed(self):
        self.assertEqual(self.call("DELETE", "/tasks")[0], 405)
        self.assertEqual(self.call("POST", "/tasks/1", {})[0], 405)


if __name__ == "__main__":
    unittest.main()
