#!/usr/bin/env python3
"""
Persistent Conversation Storage Engine.
Stores multi-turn chat sessions, messages, and metadata in SQLite at
~/.local/share/tejas-os/june/conversations.db.
"""

from datetime import datetime
import json
import os
import sqlite3
import sys
from typing import Any, Dict, List, Optional
import uuid


class ConversationStore:
    """SQLite-backed conversation session and message store."""

    DEFAULT_DB_DIR = os.path.expanduser("~/.local/share/tejas-os/june")
    DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "conversations.db")

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or self.DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        """Initializes tables and indexes."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    provider TEXT,
                    model TEXT
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    tokens INTEGER DEFAULT 0,
                    metadata TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
                CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(updated_at);
            """)

    def create_session(
        self,
        title: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        sid = session_id or str(uuid.uuid4())[:12]
        now = datetime.now().isoformat()
        session_title = title or f"Session {now[:10]}"

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO sessions (id, title, created_at, updated_at, provider, model)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (sid, session_title, now, now, provider or "default", model or "default"),
            )
        return sid

    def get_or_create_default_session(self) -> str:
        sessions = self.list_sessions(limit=1)
        if sessions:
            return sessions[0]["id"]
        return self.create_session(title="Main Workspace Chat")

    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, title, created_at, updated_at, provider, model
                FROM sessions
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, created_at, updated_at, provider, model FROM sessions WHERE id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_session_title(self, session_id: str, title: str) -> bool:
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
                (title.strip(), now, session_id),
            )
            return cursor.rowcount > 0

    def delete_session(self, session_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            return cursor.rowcount > 0

    def clear_all_sessions(self) -> bool:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM messages;")
            conn.execute("DELETE FROM sessions;")
            return True

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tokens: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        # Ensure session exists
        if not self.get_session(session_id):
            self.create_session(session_id=session_id)

        now = datetime.now().isoformat()
        meta_json = json.dumps(metadata or {})

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO messages (session_id, role, content, timestamp, tokens, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (session_id, role, content, now, tokens, meta_json),
            )
            msg_id = cursor.lastrowid

            # Update session's updated_at timestamp
            conn.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (now, session_id),
            )
            return msg_id

    def get_messages(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, session_id, role, content, timestamp, tokens, metadata
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (session_id, limit),
            )
            results = []
            for row in cursor.fetchall():
                d = dict(row)
                try:
                    d["metadata"] = json.loads(d["metadata"]) if d["metadata"] else {}
                except Exception:
                    d["metadata"] = {}
                results.append(d)
            return results

    def get_recent_context(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Returns the most recent messages formatted as [{'role': ..., 'content': ...}] for LLM context."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT role, content
                FROM (
                    SELECT id, role, content
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                )
                ORDER BY id ASC
                """,
                (session_id, limit),
            )
            return [{"role": row["role"], "content": row["content"]} for row in cursor.fetchall()]

    def search_messages(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, session_id, role, content, timestamp
                FROM messages
                WHERE content LIKE ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (f"%{query}%", limit),
            )
            return [dict(row) for row in cursor.fetchall()]

    def export_session_markdown(self, session_id: str) -> str:
        session = self.get_session(session_id)
        if not session:
            return "# Session Not Found\n"

        messages = self.get_messages(session_id)
        md = [f"# {session['title']}\n"]
        md.append(f"- **Session ID:** `{session['id']}`")
        md.append(f"- **Created:** {session['created_at']}")
        md.append(f"- **Provider:** {session['provider']} ({session['model']})\n\n---\n")

        for msg in messages:
            role_header = "**User**" if msg["role"] == "user" else "**June**" if msg["role"] == "assistant" else f"**{msg['role'].capitalize()}**"
            md.append(f"{role_header} *({msg['timestamp']})*:\n\n{msg['content']}\n\n---\n")

        return "\n".join(md)
