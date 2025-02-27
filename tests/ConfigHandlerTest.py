# tests/ConfigHandlerTest.py

import unittest
import shutil
import os
from data_allocator.config_handler import ConfigHandler

class TestConfigHandler(unittest.TestCase):
    @classmethod
    def setUp(cls):
        """
        Create temporary directories and mount them for testing.
        """
        cls.example_config = os.path.join("example_config", "config.json")
        cls.drive1 = "wdir/drive1"
        cls.drive2 = "wdir/drive2"

        # Create directories
        os.makedirs(cls.drive1, exist_ok=True)
        os.makedirs(cls.drive2, exist_ok=True)

    @classmethod
    def tearDown(cls):
        """
        Clean up by unmounting and removing temporary directories.
        """
        shutil.rmtree(cls.drive1)
        shutil.rmtree(cls.drive2)

    def test_load_config(self):
        """
        Test if configuration loads correctly.
        """
        config = ConfigHandler(self.example_config)
        self.assertIsNotNone(config)
        self.assertIn("drive1", config.get_drive_paths())
        self.assertIn("drive2", config.get_drive_paths())

    def test_reload_config(self):
        """
        Test configuration reload functionality.
        """
        config = ConfigHandler(self.example_config)
        config.reload_config()
        drive_paths = config.get_drive_paths()
        
        self.assertIn("drive1", drive_paths)
        self.assertIn("drive2", drive_paths)

if __name__ == "__main__":
    unittest.main()
