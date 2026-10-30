"""
Unit tests for Productivity Suite backends (Clipboard, Screenshots, Notes & Tasks).
"""

import json
import os
import unittest
from unittest.mock import MagicMock, patch

from productivity.clipboard.clipboard_manager import ClipboardManager
from productivity.notes.notes_manager import NotesManager
from productivity.screenshots.screenshot_manager import ScreenshotManager


class TestProductivityBackends(unittest.TestCase):

    def test_clipboard_manager_pinning(self):
        cm = ClipboardManager()
        test_content = "Special test clip string"
        # Toggle pin on
        pinned = cm.toggle_pin(test_content)
        self.assertTrue(pinned)
        # Toggle pin off
        unpinned = cm.toggle_pin(test_content)
        self.assertFalse(unpinned)

    def test_clipboard_history_fallback(self):
        cm = ClipboardManager()
        hist = cm.get_history()
        self.assertIsInstance(hist, list)

    def test_screenshot_filename_timestamp(self):
        sm = ScreenshotManager()
        fn = sm._get_timestamp_filename("png")
        self.assertTrue(fn.endswith(".png"))
        self.assertIn("screenshot_", fn)

    def test_notes_and_tasks_crud(self):
        nm = NotesManager()
        data = nm.get_data()
        self.assertIn("notes", data)
        self.assertIn("tasks", data)

        # Add note
        note = nm.add_note("Test Title", "Test Content")
        self.assertEqual(note["title"], "Test Title")

        # Delete note
        deleted = nm.delete_note(note["id"])
        self.assertTrue(deleted)

        # Add task
        task = nm.add_task("Test Task Item")
        self.assertFalse(task["completed"])

        # Toggle task
        toggled = nm.toggle_task(task["id"])
        self.assertTrue(toggled)

        # Delete task
        del_task = nm.delete_task(task["id"])
        self.assertTrue(del_task)


if __name__ == "__main__":
    unittest.main()
