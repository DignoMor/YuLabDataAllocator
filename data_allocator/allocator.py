
import os
import shutil

import numpy as np

from data_allocator.config_handler import ConfigHandler
from data_allocator.storage_manager import StorageManager
from data_allocator.exceptions import AllocatorException

class Allocator:
    def __init__(self, config_path, db_path):
        """
        Initialize the Allocator with ConfigHandler and StorageManager.
        """
        self.config = ConfigHandler(config_path=config_path)
        self.storage = StorageManager(db_path=db_path)

    def make_directory(self, path):
        '''
        Create a directory if it does not exist.
        Also perform sanity checks.
        '''
        drive_paths = self.config.get_drive_paths().values()
        if not np.any([path.startswith(drive_path) for drive_path in drive_paths]):
            raise AllocatorException(f"[ERROR] Path '{path}' is not in any of the configured drives.")

        os.makedirs(path, exist_ok=True)
    
    def remove_directory(self, path):
        '''
        Remove a directory if it exists.
        Also perform sanity checks.
        '''
        drive_paths = self.config.get_drive_paths().values()
        if not np.any([path.startswith(drive_path) for drive_path in drive_paths]):
            raise AllocatorException(f"[ERROR] Path '{path}' is not in any of the configured drives.")

        if os.path.exists(path):
            shutil.rmtree(path)
        else:
            raise AllocatorException(f"[ERROR] Path '{path}' does not exist.")

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
            raise AllocatorException(f"[ERROR] Duplicate entry for '{branch_name}' exists.")
        
        space_info = self.check_space()
        target_drive = max(space_info, key=space_info.get)
        target_path = os.path.join(self.config.get_drive_paths()[target_drive], 
                                   branch_name, 
                                   )

        # Create the directory with all parent directories
        self.make_directory(target_path)

        # Record the location
        self.storage.record_location(branch_name, target_drive)

        return target_path

    def get_path(self, branch_name):
        """
        Retrieve the full path for a given branch name.
        """
        drive = self.storage.get_drive(branch_name)
        if drive:
            path = os.path.join(self.config.get_drive_paths()[drive], branch_name)
            return path
        else:
            raise AllocatorException(f"[ERROR] No location found for '{branch_name}'")

    def delete_branch(self, branch_name):
        """
        Delete the branch and its record from storage.
        """
        path = self.get_path(branch_name)
        self.remove_directory(path)
        self.storage.delete_location(branch_name)

    def calculate_branch_disk_usage(self, branch_name):
        """
        Calculate the total disk usage of a branch directory.

        Keyword arguments:
        - branch_name: The branch name as stored in the database.

        Returns:
        - int: Total size in bytes.
        
        Raises:
        - AllocatorException: If the branch is not found in the database 
                              or path is not a directory.
        """
        path = self.get_path(branch_name)
        
        if not os.path.exists(path):
            raise AllocatorException(f"[ERROR] Path '{path}' does not exist.")
        
        if not os.path.isdir(path):
            raise AllocatorException(f"[ERROR] Path '{path}' is not a directory.")
        
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, IOError):
                        # Skip files that can't be accessed
                        pass
        except (OSError, IOError) as e:
            raise AllocatorException(f"[ERROR] Unable to calculate disk usage for '{path}': {e}")
        
        return total_size
        
    @staticmethod
    def format_size(size):
        """
        Format the size in bytes to a human readable string.
        """
        if size < 1024:
            return f"{size} B"
        elif size < 1024**2:
            return f"{size / 1024} KB"
        elif size < 1024**3:
            return f"{size / 1024**2} MB"
        else:
            return f"{size / 1024**3} GB"