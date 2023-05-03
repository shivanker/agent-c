#! /usr/bin/python3 -m unittest

import unittest
from memory.inplace import InPlaceMemory
import copy


class MemoryTest(unittest.TestCase):
    def setUp(self):
        self.memory = InPlaceMemory(
            lambda a, b, c, d: True, lambda x: len(x["content"])
        )

    def test_missing_get(self):
        self.assertEqual(self.memory.get("user1"), None)

    def test_basic_get(self):
        test_msg = {"role": "user", "content": "Test message"}
        self.memory.append("user1", copy.deepcopy(test_msg))
        self.assertEqual(self.memory.get("user1"), [test_msg])

    def test_multiple_users(self):
        self.memory.append("user1", {"role": "user", "content": "Test message 1"})
        self.memory.append("user2", {"role": "user", "content": "Test message 2"})
        self.memory.append("user1", {"role": "user", "content": "Test message 3"})
        self.assertEqual(len(self.memory.get("user1")), 2)
        self.assertEqual(self.memory.get("user1")[0]["content"], "Test message 1")
        self.assertEqual(self.memory.get("user1")[1]["content"], "Test message 3")
        self.assertEqual(len(self.memory.get("user2")), 1)
        self.assertEqual(self.memory.get("user2")[0]["content"], "Test message 2")

    def test_pop(self):
        self.memory.append("user1", {"role": "user", "content": "Test message 1"})
        self.memory.append("user2", {"role": "user", "content": "Test message 2"})
        self.memory.append("user1", {"role": "user", "content": "Test message 3"})
        self.assertEqual(len(self.memory.get("user1")), 2)
        self.memory.pop("user1")
        self.assertEqual(self.memory.get("user1"), None)
        self.assertEqual(len(self.memory.get("user2")), 1)
        self.memory.pop("user2")
        self.assertEqual(self.memory.get("user2"), None)

    def test_limit_idx(self):
        self.memory = InPlaceMemory(
            lambda idx, ts, size, msg: True if idx < 2 else False,
            lambda x: len(x["content"]),
        )
        self.memory.append("user1", {"role": "user", "content": "Test message 1"})
        self.memory.append("user1", {"role": "user", "content": "Test message 2"})
        self.memory.append("user2", {"role": "user", "content": "Test message _"})
        self.assertEqual(len(self.memory.get("user1")), 2)
        self.assertEqual(self.memory.get("user1")[1]["content"], "Test message 2")
        self.memory.append("user1", {"role": "user", "content": "Test message 3"})
        self.assertEqual(len(self.memory.get("user1")), 2)
        self.assertEqual(self.memory.get("user1")[0]["content"], "Test message 2")
        self.assertEqual(self.memory.get("user1")[1]["content"], "Test message 3")

    def test_limit_msg(self):
        self.memory = InPlaceMemory(
            lambda idx, ts, size, msg: True if msg["role"] == "user" else False,
            lambda x: len(x["content"]),
        )
        self.memory.append("user1", {"role": "user", "content": "Test message 1"})
        self.memory.append("user1", {"role": "system", "content": "Test message 2"})
        self.memory.append("user1", {"role": "user", "content": "Test message 3"})
        self.assertEqual(len(self.memory.get("user1")), 2)
        self.assertEqual(self.memory.get("user1")[0]["content"], "Test message 1")
        self.assertEqual(self.memory.get("user1")[1]["content"], "Test message 3")

    def test_limit_size(self):
        self.memory = InPlaceMemory(
            lambda idx, ts, size, msg: True if size < 2 * 15 else False,
            lambda x: len(x["content"]),
        )
        self.memory.append("user1", {"role": "user", "content": "Test message 1"})
        self.memory.append("user1", {"role": "user", "content": "Test message 2"})
        self.memory.append("user2", {"role": "user", "content": "Test message _"})
        self.assertEqual(len(self.memory.get("user1")), 2)
        self.assertEqual(self.memory.get("user1")[1]["content"], "Test message 2")
        self.memory.append("user1", {"role": "user", "content": "Test message 3"})
        self.assertEqual(len(self.memory.get("user1")), 2)
        self.assertEqual(self.memory.get("user1")[0]["content"], "Test message 2")
        self.assertEqual(self.memory.get("user1")[1]["content"], "Test message 3")


# Define a main method to run the tests
if __name__ == "__main__":
    unittest.main()
