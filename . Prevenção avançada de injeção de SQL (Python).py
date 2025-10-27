import sqlite3
from typing import Dict, Any, List, Optional, Tuple
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
        self._initialize_db()
        
    def _initialize_db(self):
        """Initialize the database schema"""
        with DatabaseConnection(
            connection=sqlite3.connect(self.db_path),
            cursor=sqlite3.connect(self.db_path).cursor()
        ) as db:
            db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL
                )
            """)
            
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
            
    def add_user(self, username: str, email: str, password_hash: str) -> int:
        """Add a new user to the database"""
        if not username or not email or not password_hash:
            raise ValueError("All fields are required")
            
        result = self._execute_query(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        return result.lastrowid
        
    def update_user(self, user_id: int, **kwargs) -> None:
        """Update an existing user"""
        if not kwargs:
            return
            
        updates = []
        params = []
        for key, value in kwargs.items():
            updates.append(f"{key} = ?")
            params.append(value)
            
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        params.append(user_id)
        
        self._execute_update(query, tuple(params))
        
    def delete_user(self, user_id: int) -> None:
        """Delete a user from the database"""
        self._execute_update(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )

# Usage example
db = SecureDatabase("example.db")
db.add_user("john_doe", "john@example.com", "password_hash_here")
user = db.get_user_by_id(1)
print(user)