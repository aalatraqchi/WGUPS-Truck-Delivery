# Developed based off webinar 1 which referenced ZyBooks
class HashTable:
    # Constructor
    def __init__(self, capacity=10):
        self.table = []
        for i in range(capacity):
            self.table.append([])

    # Method to insert items into hash table
    def insert(self, key, item):
        # Hash function to find bucket to insert item
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        # If key exists, update value
        for keyVal in bucket_list:
            if keyVal[0] == key:
                keyVal[1] = item
                return True

        # Insert key item pair into bucket list if it isn't already present
        new_key_val = [key, item]
        bucket_list.append(new_key_val)
        return True

    def search(self, key):
        # Hash function to find bucket to insert item
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        # Search for matching keys
        for keyVal in bucket_list:
            # If key is found, return value/item
            if keyVal[0] == key:
                return keyVal[1]
        return None

    def remove(self, key):
        # Hash function to find bucket to insert item
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        # Remove value/item if key is present
        for keyVal in bucket_list:
            if keyVal[0] == key:
                bucket_list.remove([keyVal[0], keyVal[1]])
