# tests/AllocatorTest.py

import unittest
import os
from data_allocator.allocator import Allocator
from data_allocator.config_handler import ConfigHandler

class TestAllocator(unittest.TestCase):
    @classmethod
    def setUp(cls):
        """
        Create test directories for drive1 and drive2 in wdir.
        """
        cls.wdir = "wdir"
        cls.drive1 = os.path.join(cls.wdir, "drive1")
        cls.drive2 = os.path.join(cls.wdir, "drive2")

        # Create working directory and drives
        os.makedirs(cls.drive1, exist_ok=True)
        os.makedirs(cls.drive2, exist_ok=True)

        cls.config_path = os.path.join("example_config", "config.json")
        cls.db_path = os.path.join(cls.wdir, "test.db")
        cls.allocator = Allocator(config_path=cls.config_path, 
                                  db_path=cls.db_path, 
                                  )

    @classmethod
    def tearDown(cls):
        """
        Clean up by removing the test directories.
        """
        if os.path.exists(cls.wdir):
            for root, dirs, files in os.walk(cls.wdir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(cls.wdir)

    def test_allocate(self):
        """
        Test allocating a new branch.
        """
        path = self.allocator.allocate("test_branch")
        self.assertTrue(os.path.exists(path))

        self.allocator.delete_branch("test_branch")

    def test_get_path(self):
        """
        Test retrieving the path for an existing branch.
        """
        self.allocator.allocate("test_branch")
        path = self.allocator.get_path("test_branch")
        self.assertTrue(os.path.exists(path))
        self.assertIn("test_branch", path)

    def test_delete_branch(self):
        """
        Test deleting a branch and its record.
        """
        self.allocator.allocate("test_branch")
        self.allocator.delete_branch("test_branch")
        with self.assertRaises(Exception):
            self.allocator.get_path("test_branch")

if __name__ == "__main__":
    unittest.main()
