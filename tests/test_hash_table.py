import unittest

from wgups.hash_table import HashTable


class HashTableTest(unittest.TestCase):
    def test_insert_and_search(self):
        table = HashTable()
        table.insert(1, "one")
        table.insert(2, "two")
        self.assertEqual(table.search(1), "one")
        self.assertEqual(table.search(2), "two")
        self.assertIsNone(table.search(3))

    def test_insert_existing_key_replaces_value(self):
        table = HashTable()
        table.insert(1, "one")
        table.insert(1, "uno")
        self.assertEqual(table.search(1), "uno")
        self.assertEqual(len(table), 1)

    def test_remove(self):
        table = HashTable()
        table.insert(1, "one")
        self.assertTrue(table.remove(1))
        self.assertFalse(table.remove(1))
        self.assertIsNone(table.search(1))
        self.assertEqual(len(table), 0)

    def test_colliding_keys_are_kept_apart(self):
        table = HashTable(capacity=4, max_load_factor=10)
        for key in (1, 5, 9):  # all land in bucket 1
            table.insert(key, key * 10)
        self.assertEqual([table.search(k) for k in (1, 5, 9)], [10, 50, 90])

    def test_grows_and_keeps_every_item(self):
        table = HashTable(capacity=2)
        for key in range(100):
            table.insert(key, str(key))
        self.assertEqual(len(table), 100)
        self.assertGreaterEqual(len(table._buckets), 100)
        self.assertTrue(all(table.search(k) == str(k) for k in range(100)))
        self.assertEqual(sorted(table.values(), key=int), [str(k) for k in range(100)])

    def test_contains_finds_keys_stored_with_none(self):
        table = HashTable()
        table.insert(1, None)
        self.assertIn(1, table)
        self.assertNotIn(2, table)

    def test_rejects_invalid_settings(self):
        with self.assertRaises(ValueError):
            HashTable(capacity=0)
        with self.assertRaises(ValueError):
            HashTable(max_load_factor=0)


if __name__ == "__main__":
    unittest.main()
