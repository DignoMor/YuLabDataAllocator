# tests/AllocatorTest.py

import unittest
import os
import shutil
from data_allocator.allocator import Allocator
from data_allocator.config_handler import ConfigHandler
from data_allocator.exceptions import AllocatorException

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

    def test_calculate_branch_disk_usage_empty(self):
        """
        Test calculating disk usage for an empty branch.
        """
        self.allocator.allocate("empty_branch")
        size = self.allocator.calculate_branch_disk_usage("empty_branch")
        self.assertEqual(size, 0)
        self.allocator.delete_branch("empty_branch")

    def test_calculate_branch_disk_usage_single_file(self):
        """
        Test calculating disk usage for a branch with a single file.
        """
        self.allocator.allocate("single_file_branch")
        path = self.allocator.get_path("single_file_branch")
        
        # Create a file with known content
        test_content = b"Hello, World! This is a test file."
        test_file = os.path.join(path, "test.txt")
        with open(test_file, "wb") as f:
            f.write(test_content)
        
        expected_size = len(test_content)
        size = self.allocator.calculate_branch_disk_usage("single_file_branch")
        self.assertEqual(size, expected_size)
        
        self.allocator.delete_branch("single_file_branch")

    def test_calculate_branch_disk_usage_multiple_files(self):
        """
        Test calculating disk usage for a branch with multiple files.
        """
        self.allocator.allocate("multi_file_branch")
        path = self.allocator.get_path("multi_file_branch")
        
        # Create multiple files with known content
        files_content = {
            "file1.txt": b"Content of file 1",
            "file2.txt": b"Content of file 2 with more text",
            "file3.txt": b"Short"
        }
        
        expected_size = 0
        for filename, content in files_content.items():
            filepath = os.path.join(path, filename)
            with open(filepath, "wb") as f:
                f.write(content)
            expected_size += len(content)
        
        size = self.allocator.calculate_branch_disk_usage("multi_file_branch")
        self.assertEqual(size, expected_size)
        
        self.allocator.delete_branch("multi_file_branch")

    def test_calculate_branch_disk_usage_nested_directories(self):
        """
        Test calculating disk usage for a branch with nested directories and files.
        """
        self.allocator.allocate("nested_branch")
        path = self.allocator.get_path("nested_branch")
        
        # Create nested directory structure
        subdir1 = os.path.join(path, "subdir1")
        subdir2 = os.path.join(path, "subdir2", "nested")
        os.makedirs(subdir1, exist_ok=True)
        os.makedirs(subdir2, exist_ok=True)
        
        # Create files at different levels
        files_content = {
            "root_file.txt": b"Root level file",
            os.path.join("subdir1", "sub1_file.txt"): b"Subdirectory 1 file",
            os.path.join("subdir2", "nested", "deep_file.txt"): b"Deep nested file"
        }
        
        expected_size = 0
        for rel_path, content in files_content.items():
            filepath = os.path.join(path, rel_path)
            with open(filepath, "wb") as f:
                f.write(content)
            expected_size += len(content)
        
        size = self.allocator.calculate_branch_disk_usage("nested_branch")
        self.assertEqual(size, expected_size)
        
        self.allocator.delete_branch("nested_branch")

    def test_calculate_branch_disk_usage_nonexistent_branch(self):
        """
        Test that calculating disk usage for a non-existent branch raises an exception.
        """
        with self.assertRaises(AllocatorException) as context:
            self.allocator.calculate_branch_disk_usage("nonexistent_branch")
        self.assertIn("location found", str(context.exception).lower())

    def test_calculate_branch_disk_usage_missing_path(self):
        """
        Test that calculating disk usage for a branch whose path was deleted raises an exception.
        """
        self.allocator.allocate("deleted_path_branch")
        path = self.allocator.get_path("deleted_path_branch")
        
        # Manually delete the directory but keep the database record
        shutil.rmtree(path)
        
        with self.assertRaises(AllocatorException) as context:
            self.allocator.calculate_branch_disk_usage("deleted_path_branch")
        self.assertIn("does not exist", str(context.exception).lower())
        
        # Clean up database record
        self.allocator.storage.delete_location("deleted_path_branch")

if __name__ == "__main__":
    unittest.main()
