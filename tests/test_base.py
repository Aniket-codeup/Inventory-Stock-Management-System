import os
import tempfile
import unittest
from database.connection import set_db_path, get_db_path
from database.schema import initialize_database

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Create a unique temporary database file for isolation
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)
        
        # Configure the system to use the test database
        self.original_db_path = get_db_path()
        set_db_path(self.temp_db_path)
        
        # Initialize full schema
        initialize_database()

    def tearDown(self):
        # Restore original database path and remove temporary database
        set_db_path(self.original_db_path)
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except PermissionError:
                pass
