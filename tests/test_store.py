import unittest

from app.store import MAX_TITLE_LENGTH, TaskStore, ValidationError


class TaskStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = TaskStore()

    def test_create_returns_task_with_incremental_id(self):
        first = self.store.create("Estudar Docker")
        second = self.store.create("Estudar Terraform")
        self.assertEqual(first, {"id": 1, "title": "Estudar Docker", "done": False})
        self.assertEqual(second["id"], 2)

    def test_create_trims_title(self):
        self.assertEqual(self.store.create("  Revisar CI  ")["title"], "Revisar CI")

    def test_create_rejects_invalid_titles(self):
        for invalid in (None, "", "   ", 123, ["x"]):
            with self.subTest(title=invalid):
                with self.assertRaises(ValidationError):
                    self.store.create(invalid)

    def test_create_rejects_long_title(self):
        with self.assertRaises(ValidationError):
            self.store.create("a" * (MAX_TITLE_LENGTH + 1))

    def test_list_returns_all_tasks(self):
        self.store.create("A")
        self.store.create("B")
        self.assertEqual([t["title"] for t in self.store.list()], ["A", "B"])

    def test_get_existing_and_missing(self):
        task = self.store.create("A")
        self.assertEqual(self.store.get(task["id"]), task)
        self.assertIsNone(self.store.get(999))

    def test_returned_data_is_a_copy(self):
        task = self.store.create("A")
        task["title"] = "alterado fora do store"
        self.assertEqual(self.store.get(1)["title"], "A")

    def test_update_title_and_done(self):
        self.store.create("A")
        updated = self.store.update(1, {"title": "B", "done": True})
        self.assertEqual(updated, {"id": 1, "title": "B", "done": True})

    def test_update_ignores_unknown_fields(self):
        self.store.create("A")
        updated = self.store.update(1, {"id": 50, "qualquer": "coisa"})
        self.assertEqual(updated, {"id": 1, "title": "A", "done": False})

    def test_update_validates_values(self):
        self.store.create("A")
        with self.assertRaises(ValidationError):
            self.store.update(1, {"done": "sim"})
        with self.assertRaises(ValidationError):
            self.store.update(1, {"title": ""})

    def test_update_missing_returns_none(self):
        self.assertIsNone(self.store.update(42, {"done": True}))

    def test_delete(self):
        self.store.create("A")
        self.assertTrue(self.store.delete(1))
        self.assertFalse(self.store.delete(1))
        self.assertEqual(self.store.list(), [])


if __name__ == "__main__":
    unittest.main()
