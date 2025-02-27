# tests/StorageManagerTest.py

import unittest
import os
from data_allocator.storage_manager import StorageManager

class TestStorageManager(unittest.TestCase):
    @classmethod
    def setUp(cls):
        """
        Setup a temporary database for testing.
        """
        cls.db_path = "wdir/test.db"
        cls.storage = StorageManager(db_path=cls.db_path)

    @classmethod
    def tearDown(cls):
        """
        Clean up by removing the test database.
        """
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_record_location(self):
        """
        Test recording a new location.
        """
        self.storage.record_location("test_folder/test_branch", "wdir/drive1")
        location = self.storage.get_location("test_folder/test_branch")
        self.assertEqual(location, "wdir/drive1/test_folder/test_branch")

    def test_duplicate_check(self):
        """
        Test duplicate check for branch name.
        """
        self.storage.record_location("test_dup/dup", "drive2")
        with self.assertRaises(Exception):
            self.storage.record_location("test_dup/dup", "drive1")

    def test_delete_location(self):
        """
        Test deleting a location record.
        """
        self.storage.record_location("test_delete", "wdir/drive1")
        self.storage.delete_location("test_delete")
        location = self.storage.get_location("test_delete")
        self.assertIsNone(location)

if __name__ == "__main__":
    unittest.main()
