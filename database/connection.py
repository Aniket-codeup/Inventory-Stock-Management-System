import sqlite3
import os

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "inventory.db")
_active_db_path = DEFAULT_DB_PATH

def set_db_path(path: str):
    """Set the active database path (useful for testing)."""
    global _active_db_path
    _active_db_path = path

def get_db_path() -> str:
    """Return the currently configured database path."""
    return _active_db_path

def get_db_connection(db_path: str = None) -> sqlite3.Connection:
    """Create and return a database connection with foreign keys enabled."""
    target_path = db_path if db_path is not None else _active_db_path
    conn = sqlite3.connect(target_path)
    # Enable foreign key support as required by PRD Section 6.2 & 7.8
    conn.execute("PRAGMA foreign_keys = ON;")
    # Return rows as dictionaries for easier data handling
    conn.row_factory = sqlite3.Row
    return conn