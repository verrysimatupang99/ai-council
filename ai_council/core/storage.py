"""
Storage Manager for AI Council - Handles persistent session history using SQLite
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class StorageManager:
    """Manages persistent storage for AI Council sessions"""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            # Default to a .ai_council directory in the user's home
            storage_dir = Path.home() / ".ai_council"
            storage_dir.mkdir(exist_ok=True)
            self.db_path = storage_dir / "history.db"
        else:
            self.db_path = db_path
            
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    final_synthesis TEXT,
                    rounds INTEGER,
                    agents_json TEXT
                )
            ''')
            
            # Responses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    agent_name TEXT,
                    round INTEGER,
                    content TEXT,
                    provider TEXT,
                    model TEXT,
                    latency_ms REAL,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            conn.commit()
    
    def save_session(self, session_id: str, query: str, rounds: int, agents: List[str], 
                     all_responses: List[Dict[str, Any]], final_synthesis: Optional[str] = None):
        """Save a complete session to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert session
            cursor.execute('''
                INSERT INTO sessions (id, query, rounds, agents_json, final_synthesis)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, query, rounds, json.dumps(agents), final_synthesis))
            
            # Insert individual responses
            for resp in all_responses:
                cursor.execute('''
                    INSERT INTO responses (session_id, agent_name, round, content, provider, model, latency_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, 
                    resp.get('agent'), 
                    resp.get('round', 0), 
                    resp.get('content'),
                    resp.get('provider'),
                    resp.get('model'),
                    resp.get('latency_ms', 0)
                ))
            
            conn.commit()
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent session history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sessions ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full details for a specific session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get session
            cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
            session_row = cursor.fetchone()
            
            if not session_row:
                return None
            
            session = dict(session_row)
            
            # Get responses
            cursor.execute('SELECT * FROM responses WHERE session_id = ? ORDER BY round, agent_name', (session_id,))
            session['responses'] = [dict(row) for row in cursor.fetchall()]
            
            return session
    
    def clear_history(self):
        """Delete all history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM responses')
            cursor.execute('DELETE FROM sessions')
            conn.commit()
