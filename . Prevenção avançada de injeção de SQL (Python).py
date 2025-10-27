import sqlite3
from typing import Dict, Any
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
        
    def execute_query(self, query: str, params: tuple) -> list:
        """Execute a parameterized query safely"""
        with DatabaseConnection(
            connection=sqlite3.connect(self.db_path),
            cursor=sqlite3.connect(self.db_path).cursor()
        ) as db:
            db.cursor.execute(query, params)
            return db.cursor.fetchall()
            
    def execute_update(self, query: str, params: tuple) -> None:
        """Execute an update query safely"""
        with DatabaseConnection(
            connection=sqlite3.connect(self.db_path),
            cursor=sqlite3.connect(self.db_path).cursor()
        ) as db:
            db.cursor.execute(query, params)
            
    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Get a user by ID with type checking"""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Invalid user ID")
            
        result = self.execute_query(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        return result[0] if result else None