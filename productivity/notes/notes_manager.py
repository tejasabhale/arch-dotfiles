#!/usr/bin/env python3
"""
Quick Notes & Tasks Backend Service.
Persists markdown notes and todo lists under ~/.local/share/tejas-os/notes.json.
"""

from datetime import datetime
import json
import os
import sys
import uuid
from typing import Any, Dict, List


class NotesManager:
    DATA_PATH = os.path.expanduser("~/.local/share/tejas-os/notes.json")

    def __init__(self):
        os.makedirs(os.path.dirname(self.DATA_PATH), exist_ok=True)
        if not os.path.exists(self.DATA_PATH):
            default_data = {
                "notes": [
                    {
                        "id": "1",
                        "title": "Welcome to June Desktop",
                        "content": "A high-performance modular Linux desktop built with Hyprland and Quickshell.",
                        "updated_at": datetime.now().isoformat(),
                    }
                ],
                "tasks": [
                    {
                        "id": "1",
                        "text": "Explore June AI features with Super+J",
                        "completed": False,
                    },
                    {
                        "id": "2",
                        "text": "Configure development projects",
                        "completed": False,
                    },
                    {
                        "id": "3",
                        "text": "Try switching themes from Control Center",
                        "completed": True,
                    },
                ],
            }
            with open(self.DATA_PATH, "w") as f:
                json.dump(default_data, f, indent=2)

    def _load(self) -> Dict[str, Any]:
        try:
            with open(self.DATA_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {"notes": [], "tasks": []}

    def _save(self, data: Dict[str, Any]):
        try:
            with open(self.DATA_PATH, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def get_data(self) -> Dict[str, Any]:
        return self._load()

    def add_note(self, title: str, content: str) -> Dict[str, Any]:
        data = self._load()
        note = {
            "id": str(uuid.uuid4())[:8],
            "title": title or "Untitled Note",
            "content": content,
            "updated_at": datetime.now().isoformat(),
        }
        data["notes"].insert(0, note)
        self._save(data)
        return note

    def delete_note(self, note_id: str) -> bool:
        data = self._load()
        data["notes"] = [n for n in data["notes"] if n["id"] != note_id]
        self._save(data)
        return True

    def add_task(self, text: str) -> Dict[str, Any]:
        data = self._load()
        task = {
            "id": str(uuid.uuid4())[:8],
            "text": text,
            "completed": False,
        }
        data["tasks"].append(task)
        self._save(data)
        return task

    def toggle_task(self, task_id: str) -> bool:
        data = self._load()
        for t in data["tasks"]:
            if t["id"] == task_id:
                t["completed"] = not t["completed"]
                break
        self._save(data)
        return True

    def delete_task(self, task_id: str) -> bool:
        data = self._load()
        data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
        self._save(data)
        return True


def main():
    nm = NotesManager()
    if len(sys.argv) < 2 or sys.argv[1] == "get":
        print(json.dumps(nm.get_data(), indent=2))
    elif sys.argv[1] == "add-note" and len(sys.argv) > 3:
        print(json.dumps(nm.add_note(sys.argv[2], sys.argv[3]), indent=2))
    elif sys.argv[1] == "del-note" and len(sys.argv) > 2:
        print(json.dumps({"success": nm.delete_note(sys.argv[2])}, indent=2))
    elif sys.argv[1] == "add-task" and len(sys.argv) > 2:
        print(json.dumps(nm.add_task(sys.argv[2]), indent=2))
    elif sys.argv[1] == "toggle-task" and len(sys.argv) > 2:
        print(json.dumps({"success": nm.toggle_task(sys.argv[2])}, indent=2))
    elif sys.argv[1] == "del-task" and len(sys.argv) > 2:
        print(json.dumps({"success": nm.delete_task(sys.argv[2])}, indent=2))


if __name__ == "__main__":
    main()
