"""Armazenamento em memória das tarefas, com validação das entradas."""

from itertools import count
from threading import Lock

MAX_TITLE_LENGTH = 120


class ValidationError(ValueError):
    """Erro de validação de dados enviados pelo cliente."""


def _clean_title(title):
    if not isinstance(title, str) or not title.strip():
        raise ValidationError("O campo 'title' é obrigatório e deve ser um texto não vazio.")
    title = title.strip()
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError(
            f"O campo 'title' deve ter no máximo {MAX_TITLE_LENGTH} caracteres."
        )
    return title


class TaskStore:
    """Guarda as tarefas em memória (seguro para uso com várias threads)."""

    def __init__(self):
        self._tasks = {}
        self._ids = count(1)
        self._lock = Lock()

    def create(self, title):
        title = _clean_title(title)
        with self._lock:
            task_id = next(self._ids)
            task = {"id": task_id, "title": title, "done": False}
            self._tasks[task_id] = task
            return dict(task)

    def list(self):
        with self._lock:
            return [dict(task) for task in self._tasks.values()]

    def get(self, task_id):
        with self._lock:
            task = self._tasks.get(task_id)
            return dict(task) if task else None

    def update(self, task_id, changes):
        """Atualiza 'title' e/ou 'done'. Retorna None se a tarefa não existir."""
        if "title" in changes:
            changes = dict(changes, title=_clean_title(changes["title"]))
        if "done" in changes and not isinstance(changes["done"], bool):
            raise ValidationError("O campo 'done' deve ser verdadeiro ou falso.")
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            for key in ("title", "done"):
                if key in changes:
                    task[key] = changes[key]
            return dict(task)

    def delete(self, task_id):
        with self._lock:
            return self._tasks.pop(task_id, None) is not None
