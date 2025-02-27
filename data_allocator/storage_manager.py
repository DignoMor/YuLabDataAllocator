# data_allocator/storage_manager.py

import sqlite3
import os

class StorageManager:
    def __init__(self, db_path):
        """
        Initialize the StorageManager with the database path.
        """
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """
        Initialize the database and create the table if it doesn't exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_location (
                    branch_path TEXT PRIMARY KEY,
                    drive_path TEXT,
                    path TEXT
                );
            ''')
            conn.commit()

    def record_location(self, branch_path, drive_path):
        """
        Record the storage location of a branch.
        """
        if self.check_duplicates(branch_path):
            raise Exception(f"[ERROR] Duplicate entry for '{branch_path}' exists.")
        
        full_branch_path = os.path.join(drive_path, branch_path)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO data_location (branch_path, drive_path, path)
                VALUES (?, ?, ?);
            ''', (branch_path, drive_path, full_branch_path))
            conn.commit()

    def get_location(self, branch_path):
        """
        Retrieve the stored path for a branch.
        Return None if the branch is not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT path FROM data_location
                WHERE branch_path= ?;
            ''', (branch_path,))
            result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            return None

    def check_duplicates(self, branch_path):
        """
        Check if a branch is already recorded.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM data_location
                WHERE branch_path = ?;
            ''', (branch_path, ))
            count = cursor.fetchone()[0]
        
        return count > 0

    def delete_location(self, branch_path):
        """
        Delete the record of a branch location.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM data_location
                WHERE branch_path = ?;
            ''', (branch_path, ))
            conn.commit()
        
