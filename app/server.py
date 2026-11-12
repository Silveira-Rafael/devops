"""Servidor HTTP da Task API (somente biblioteca padrão do Python)."""

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from app import __version__
from app.store import TaskStore, ValidationError

LOGGER = logging.getLogger("taskapi")
MAX_BODY_BYTES = 10_000


def make_handler(store):
    """Cria a classe de tratamento de requisições ligada a um TaskStore."""

    class Handler(BaseHTTPRequestHandler):
        server_version = f"TaskAPI/{__version__}"

        # ----- utilitários -------------------------------------------------
        def log_message(self, fmt, *args):
            LOGGER.info("%s - %s", self.address_string(), fmt % args)

        def _send(self, status, payload=None):
            body = b"" if payload is None else json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def _read_json(self):
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                raise ValidationError("Cabeçalho Content-Length inválido.")
            if length <= 0 or length > MAX_BODY_BYTES:
                raise ValidationError("Corpo da requisição ausente ou grande demais.")
            try:
                data = json.loads(self.rfile.read(length))
            except (ValueError, UnicodeDecodeError):
                raise ValidationError("O corpo da requisição não é um JSON válido.")
            if not isinstance(data, dict):
                raise ValidationError("O corpo da requisição deve ser um objeto JSON.")
            return data

        # ----- roteamento --------------------------------------------------
        def _dispatch(self, method):
            path = urlparse(self.path).path.rstrip("/") or "/"
            try:
                if path == "/health":
                    return self._health(method)
                if path == "/tasks":
                    return self._collection(method)
                prefix = "/tasks/"
                if path.startswith(prefix) and path[len(prefix):].isdigit():
                    return self._item(method, int(path[len(prefix):]))
                return self._send(404, {"error": "Rota não encontrada."})
            except ValidationError as exc:
                return self._send(400, {"error": str(exc)})

        def _health(self, method):
            if method != "GET":
                return self._send(405, {"error": "Método não permitido."})
            return self._send(200, {"status": "ok", "version": __version__})

        def _collection(self, method):
            if method == "GET":
                return self._send(200, store.list())
            if method == "POST":
                body = self._read_json()
                return self._send(201, store.create(body.get("title")))
            return self._send(405, {"error": "Método não permitido."})

        def _item(self, method, task_id):
            if method == "GET":
                task = store.get(task_id)
            elif method == "PUT":
                task = store.update(task_id, self._read_json())
            elif method == "DELETE":
                if store.delete(task_id):
                    return self._send(204)
                task = None
            else:
                return self._send(405, {"error": "Método não permitido."})
            if task is None:
                return self._send(404, {"error": "Tarefa não encontrada."})
            return self._send(200, task)

        # ----- métodos HTTP ------------------------------------------------
        def do_GET(self):
            self._dispatch("GET")

        def do_POST(self):
            self._dispatch("POST")

        def do_PUT(self):
            self._dispatch("PUT")

        def do_DELETE(self):
            self._dispatch("DELETE")

    return Handler


def create_server(host="127.0.0.1", port=0, store=None):
    """Cria (sem iniciar) o servidor. Use port=0 para uma porta livre."""
    store = store or TaskStore()
    server = ThreadingHTTPServer((host, port), make_handler(store))
    server.store = store
    return server
