"""A chaining hash table used to store and look up packages by ID.

Based on the chaining hash table from the course's zyBooks material, extended
with automatic resizing so lookups stay O(1) on average as the package count
grows.
"""

from __future__ import annotations

from typing import Any, Iterator


class HashTable:
    """Maps keys to values using separate chaining.

    Each bucket is a list of ``[key, value]`` pairs. When the number of stored
    items exceeds ``capacity * max_load_factor``, the table doubles its bucket
    count and rehashes every item.
    """

    def __init__(self, capacity: int = 10, max_load_factor: float = 1.0) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if max_load_factor <= 0:
            raise ValueError("max_load_factor must be greater than 0")
        self._buckets: list[list[list[Any]]] = [[] for _ in range(capacity)]
        self._max_load_factor = max_load_factor
        self._size = 0

    def _bucket(self, key: Any) -> list[list[Any]]:
        return self._buckets[hash(key) % len(self._buckets)]

    def insert(self, key: Any, value: Any) -> None:
        """Adds a key/value pair, or replaces the value if the key exists. O(1) average."""
        bucket = self._bucket(key)
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])
        self._size += 1
        if self._size > len(self._buckets) * self._max_load_factor:
            self._resize(len(self._buckets) * 2)

    def search(self, key: Any) -> Any | None:
        """Returns the value stored for ``key``, or ``None``. O(1) average."""
        for stored_key, value in self._bucket(key):
            if stored_key == key:
                return value
        return None

    def remove(self, key: Any) -> bool:
        """Removes ``key`` and returns whether it was present. O(1) average."""
        bucket = self._bucket(key)
        for index, pair in enumerate(bucket):
            if pair[0] == key:
                del bucket[index]
                self._size -= 1
                return True
        return False

    def values(self) -> Iterator[Any]:
        """Yields every stored value, in no particular order."""
        for bucket in self._buckets:
            for _, value in bucket:
                yield value

    def _resize(self, capacity: int) -> None:
        old_pairs = [pair for bucket in self._buckets for pair in bucket]
        self._buckets = [[] for _ in range(capacity)]
        for key, value in old_pairs:
            self._bucket(key).append([key, value])

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: Any) -> bool:
        return any(stored_key == key for stored_key, _ in self._bucket(key))
