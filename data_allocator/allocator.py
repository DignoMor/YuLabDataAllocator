
import os
import shutil

import numpy as np

from data_allocator.config_handler import ConfigHandler
from data_allocator.storage_manager import StorageManager

class Allocator:
    def __init__(self, config_path, db_path):
        """
        Initialize the Allocator with ConfigHandler and StorageManager.
        """
        self.config = ConfigHandler(config_path=config_path)
        self.storage = StorageManager(db_path=db_path)

    def check_space(self):
        """
        Check available space on each drive.
        """
        space_info = {}
        for drive, path in self.config.get_drive_paths().items():
            usage = shutil.disk_usage(path)
            space_info[drive] = int(usage.free)
        return space_info

    def allocate(self, branch_name):
        """
        Allocate the branch to the appropriate drive based on available space.
        """
        if self.storage.check_duplicates(branch_name):
            raise Exception(f"[ERROR] Duplicate entry for '{branch_name}' exists.")
        
        space_info = self.check_space()
        target_drive = max(space_info, key=space_info.get)
        target_path = os.path.join(self.config.get_drive_paths()[target_drive], 
                                   branch_name, 
                                   )

        # Create the directory with all parent directories
        os.makedirs(target_path, exist_ok=True)

        # Record the location
        self.storage.record_location(branch_name, self.config.get_drive_paths()[target_drive])

        return target_path

    def get_path(self, branch_name):
        """
        Retrieve the full path for a given branch name.
        """
        path = self.storage.get_location(branch_name)
        if path:
            return path
        else:
            raise Exception(f"[ERROR] No location found for '{branch_name}'")

    def delete_branch(self, branch_name):
        """
        Delete the branch and its record from storage.
        """
        path = self.get_path(branch_name)
        if os.path.exists(path):
            shutil.rmtree(path)
            self.storage.delete_location(branch_name)
        else:
            raise Exception(f"[ERROR] No location found for '{branch_name}'")
        
