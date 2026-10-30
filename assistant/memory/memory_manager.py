#!/usr/bin/env python3
"""
Personal AI Memory Engine.
Maintains persistent user preferences, project shortcuts, and workflows in SQLite
at ~/.local/share/tejas-os/june/memory.db.

Complies with AGENTS.md Rule 2.2:
Strictly filters and rejects credentials, secrets, passwords, or tokens from memory.
"""

from datetime import datetime
import json
import os
import re
import sqlite3
from typing import Any, Dict, List, Optional, Tuple


class MemoryManager:
    """Manages long-term personal memory with strict security sanitation."""

    DEFAULT_DB_DIR = os.path.expanduser("~/.local/share/tejas-os/june")
    DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "memory.db")

    # Sensitive key/value rejection regex
    CREDENTIAL_FILTER = re.compile(
        r"(password|passwd|api[-_]?key|secret|token|bearer|credential|auth_header|private[-_]?key)",
        re.IGNORECASE,
    )

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or self.DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
                CREATE INDEX IF NOT EXISTS idx_memories_cat ON memories(category);
            """)

    def _is_sensitive(self, text: str) -> bool:
        return bool(self.CREDENTIAL_FILTER.search(text))

    def remember(self, key: str, value: str, category: str = "general") -> Tuple[bool, Optional[str]]:
        """
        Stores or updates a memory key-value pair.
        Rejects credentials, tokens, or passwords to comply with security rules.
        """
        k = key.strip()
        v = value.strip()
        cat = category.strip()

        if not k or not v:
            return False, "Key and value cannot be empty."

        # Security check: Never store credentials in memory
        if self._is_sensitive(k) or self._is_sensitive(v):
            return False, "Security Violation: Credentials, passwords, or API keys cannot be stored in personal memory."

        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO memories (key, value, category, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    category = excluded.category,
                    updated_at = excluded.updated_at
                """,
                (k, v, cat, now),
            )
        return True, None

    def recall(self, key: str) -> Optional[str]:
        """Retrieves a memory value by exact key match."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT value FROM memories WHERE key = ?", (key.strip(),))
            row = cursor.fetchone()
            return row["value"] if row else None

    def search_memories(self, query: str) -> List[Dict[str, Any]]:
        """Searches memories matching query in key or value."""
        q = f"%{query.strip()}%"
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, key, value, category, updated_at FROM memories WHERE key LIKE ? OR value LIKE ? ORDER BY updated_at DESC",
                (q, q),
            )
            return [dict(row) for row in cursor.fetchall()]

    def list_memories(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists stored memories, optionally filtered by category."""
        with self._get_connection() as conn:
            if category:
                cursor = conn.execute(
                    "SELECT id, key, value, category, updated_at FROM memories WHERE category = ? ORDER BY key ASC",
                    (category.strip(),),
                )
            else:
                cursor = conn.execute(
                    "SELECT id, key, value, category, updated_at FROM memories ORDER BY updated_at DESC"
                )
            return [dict(row) for row in cursor.fetchall()]

    def forget(self, key: str) -> bool:
        """Removes a memory key."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM memories WHERE key = ?", (key.strip(),))
            return cursor.rowcount > 0

    def clear_memories(self) -> bool:
        """Instant wipe of all personal memories."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM memories;")
            return True
