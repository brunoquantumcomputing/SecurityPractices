import sqlite3
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class DatabaseConnection:
    connection: sqlite3.Connection
    cursor: sqlite3.Cursor
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()

class SecureDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def _execute_query(self, query: str, params: tuple) -> List[tuple]:
        """Execute a parameterized query safely"""
        with DatabaseConnection(
            connection=sqlite3.connect(self.db_path),
            cursor=sqlite3.connect(self.db_path).cursor()
        ) as db:
            db.cursor.execute(query, params)
            return db.cursor.fetchall()
            
    def _execute_update(self, query: str, params: tuple) -> None:
        """Execute an update query safely"""
        with DatabaseConnection(
            connection=sqlite3.connect(self.db_path),
            cursor=sqlite3.connect(self.db_path).cursor()
        ) as db:
            db.cursor.execute(query, params)
            
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a user by ID with type checking"""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Invalid user ID")
            
        result = self._execute_query(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        if not result:
            return None
            
        columns = [description[0] for description in self._get_column_names()]
        return dict(zip(columns, result[0]))
        
    def _get_column_names(self) -> List[str]:
        """Get column names from the users table"""
        with DatabaseConnection(
            connection=sqlite3.connect(self.db_path),
            cursor=sqlite3.connect(self.db_path).cursor()
        ) as db:
            db.cursor.execute("PRAGMA table_info(users)")
            return [row[1] for row in db.cursor.fetchall()]

# Usage example
db = SecureDatabase("example.db")
user = db.get_user_by_id(1)
print(user)