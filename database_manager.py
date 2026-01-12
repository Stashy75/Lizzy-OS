import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="data/lizzy.db"):
        self.db_path = db_path
        # Ensure the data folder exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def init_db(self):
        """Creates tables if they don't exist and repairs them if they do."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 1. Memory Table: Stores what Lizzy 'remembers'
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    content TEXT
                )
            ''')
            
            # 2. Detection Table: Stores LENSCAST optic scans
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    identity TEXT,
                    confidence REAL
                )
            ''')
            conn.commit()

    def save_memory(self, text):
        """Saves a scrubbed thought to Lizzy's long-term memory with safety checks."""
        # Safety: Don't save empty strings or single characters
        if not text or len(str(text).strip()) < 2:
            return
            
        try:
            with sqlite3.connect(self.db_path, timeout=10) as conn:
                cursor = conn.cursor()
                # Use a parameterized query to prevent SQL injection and handle quotes
                cursor.execute(
                    'INSERT INTO memories (timestamp, content) VALUES (?, ?)',
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(text).strip())
                )
                conn.commit()
        except sqlite3.Error as e:
            # This ensures the dashboard keeps running even if the DB has a hiccup
            print(f"DATABASE_LOG_ERROR: {e}")

    def log_detection(self, identity, confidence):
        """Logs a LENSCAST optic scan."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO detections (timestamp, identity, confidence) VALUES (?, ?, ?)',
                           (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), identity, confidence))
            conn.commit()

    def get_all_memories(self):
        """Retrieves history for the MEMORY tab."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT content FROM memories ORDER BY id DESC LIMIT 50')
                return [row[0] for row in cursor.fetchall()]
        except:
            return []

    def purge_infected_memories(self):
        """The 'Nuclear Option' to clear glitches."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM memories')
            cursor.execute('DELETE FROM detections')
            conn.commit()
            