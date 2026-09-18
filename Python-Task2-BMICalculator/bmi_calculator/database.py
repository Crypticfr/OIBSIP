# -*- coding: utf-8 -*-
"""
SQLite database storage for BMI history and trend tracking.
Features:
- Multi-user record partitioning by username
- Explicit connection closure to prevent Windows file locking
- Robust error handling for database read/write failures
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bmi_history.db")

class DatabaseError(Exception):
    """Raised when an SQLite read or write operation fails."""
    pass

class BMIDatabase:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path if db_path else os.path.abspath(DEFAULT_DB_PATH)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to connect to database at '{self.db_path}': {e}")

    def init_db(self):
        """Creates the bmi_records table and ensures user_name column exists."""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT NOT NULL DEFAULT 'Default User',
                    timestamp TEXT NOT NULL,
                    weight_kg REAL NOT NULL,
                    height_m REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    notes TEXT
                )
            ''')
            conn.commit()

            # Schema migration check: ensure user_name exists if created previously
            cursor.execute("PRAGMA table_info(bmi_records)")
            columns = [info[1] for info in cursor.fetchall()]
            if "user_name" not in columns:
                cursor.execute("ALTER TABLE bmi_records ADD COLUMN user_name TEXT NOT NULL DEFAULT 'Default User'")
                conn.commit()

        except sqlite3.Error as e:
            raise DatabaseError(f"Database initialization failed: {e}")
        finally:
            if conn:
                conn.close()

    def add_record(
        self,
        weight_kg: float,
        height_m: float,
        bmi: float,
        category: str,
        user_name: str = "Default User",
        notes: str = ""
    ) -> int:
        """Inserts a new BMI measurement for a specific user into the database."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clean_user = user_name.strip() if user_name and user_name.strip() else "Default User"
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bmi_records (user_name, timestamp, weight_kg, height_m, bmi, category, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (clean_user, timestamp, weight_kg, height_m, bmi, category, notes))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to write record to database: {e}")
        finally:
            if conn:
                conn.close()

    def get_users(self) -> List[str]:
        """Retrieves a list of all distinct user names in the database."""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT user_name FROM bmi_records
                ORDER BY user_name ASC
            ''')
            rows = cursor.fetchall()
            return [r[0] for r in rows if r[0]]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to read users from database: {e}")
        finally:
            if conn:
                conn.close()

    def get_all_records(self, user_name: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves records (optionally filtered by user) ordered from newest to oldest."""
        conn = None
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if user_name and user_name != "All Users":
                cursor.execute('''
                    SELECT id, user_name, timestamp, weight_kg, height_m, bmi, category, notes
                    FROM bmi_records
                    WHERE user_name = ?
                    ORDER BY id DESC
                    LIMIT ?
                ''', (user_name, limit))
            else:
                cursor.execute('''
                    SELECT id, user_name, timestamp, weight_kg, height_m, bmi, category, notes
                    FROM bmi_records
                    ORDER BY id DESC
                    LIMIT ?
                ''', (limit,))
                
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to read records from database: {e}")
        finally:
            if conn:
                conn.close()

    def get_chronological_records(self, user_name: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves records ordered chronologically for plotting trends."""
        conn = None
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if user_name and user_name != "All Users":
                cursor.execute('''
                    SELECT id, user_name, timestamp, weight_kg, height_m, bmi, category, notes
                    FROM bmi_records
                    WHERE user_name = ?
                    ORDER BY id ASC
                    LIMIT ?
                ''', (user_name, limit))
            else:
                cursor.execute('''
                    SELECT id, user_name, timestamp, weight_kg, height_m, bmi, category, notes
                    FROM bmi_records
                    ORDER BY id ASC
                    LIMIT ?
                ''', (limit,))
                
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to read chronological records from database: {e}")
        finally:
            if conn:
                conn.close()

    def delete_record(self, record_id: int) -> bool:
        """Deletes a specific record by ID."""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM bmi_records WHERE id = ?', (record_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to delete record ID {record_id}: {e}")
        finally:
            if conn:
                conn.close()

    def clear_history(self, user_name: Optional[str] = None):
        """Clears records from database (optionally filtered by user)."""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if user_name and user_name != "All Users":
                cursor.execute('DELETE FROM bmi_records WHERE user_name = ?', (user_name,))
            else:
                cursor.execute('DELETE FROM bmi_records')
            conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to clear history: {e}")
        finally:
            if conn:
                conn.close()