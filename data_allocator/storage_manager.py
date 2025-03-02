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
                    drive_name TEXT
                );
            ''')
            conn.commit()

    def record_location(self, branch_path, drive_name):
        """
        Record the storage location of a branch.

        Keyword arguments:
        - branch_path: The path of the branch.
        - drive_name: The name of the drive.
        """
        if self.check_duplicates(branch_path):
            raise Exception(f"[ERROR] Duplicate entry for '{branch_path}' exists.")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO data_location (branch_path, drive_name)
                VALUES (?, ?);
            ''', (branch_path, drive_name))
            conn.commit()

    def get_drive(self, branch_path):
        """
        Retrieve the drive a given branch is stored in.
        Return None if the branch is not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT drive_name FROM data_location
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
        
    def get_all_locations2drive(self):
        '''
        Return a dictionary of all branch locations 
        and their corresponding drive names.

        Return: 
        - locations2drive: dictionary of branch and drive names
        '''
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM data_location;
            ''')
            locations = {row[0]: row[1] for row in cursor.fetchall()}
        
        return locations

