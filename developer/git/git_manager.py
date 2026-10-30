#!/usr/bin/env python3
"""
Developer Git Dashboard & Operations Manager.
Provides status tracking, commit helpers, diff inspection, and safe staging operations.
"""

import json
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple


class GitManager:
    """Inspects and manages git operations for a local repository."""

    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = os.path.abspath(repo_path or ".")

    def is_git_repo(self) -> bool:
        return os.path.isdir(os.path.join(self.repo_path, ".git"))

    def _run_git(self, args: List[str]) -> Tuple[bool, str]:
        if not shutil.which("git"):
            return False, "git command not found in PATH"
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
                timeout=10.0,
            )
            return True, res.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip() or e.stdout.strip()
        except Exception as e:
            return False, str(e)

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive status of current branch, staged, unstaged, and untracked files."""
        if not self.is_git_repo():
            return {
                "is_repo": False,
                "path": self.repo_path,
                "error": "Directory is not a git repository",
            }

        # Branch name
        ok_b, branch = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        if not ok_b:
            branch = "unknown"

        # Commit hash
        ok_h, commit_hash = self._run_git(["rev-parse", "--short", "HEAD"])
        if not ok_h:
            commit_hash = "none"

        # Porcelain status
        ok_s, status_out = self._run_git(["status", "--porcelain"])
        staged = []
        unstaged = []
        untracked = []

        if ok_s and status_out:
            for line in status_out.split("\n"):
                if len(line) < 3:
                    continue
                code_x = line[0]
                code_y = line[1]
                file_name = line[3:].strip()

                if code_x in ("M", "A", "D", "R", "C"):
                    staged.append({"file": file_name, "status": code_x})
                if code_y in ("M", "D"):
                    unstaged.append({"file": file_name, "status": code_y})
                if code_x == "?" and code_y == "?":
                    untracked.append({"file": file_name, "status": "?"})

        # Ahead / Behind remote
        ok_ab, ab_out = self._run_git(["rev-list", "--left-right", "--count", f"{branch}...@{{upstream}}"])
        ahead = 0
        behind = 0
        if ok_ab and ab_out:
            parts = ab_out.split()
            if len(parts) == 2:
                ahead = int(parts[0])
                behind = int(parts[1])

        return {
            "is_repo": True,
            "path": self.repo_path,
            "branch": branch,
            "commit": commit_hash,
            "ahead": ahead,
            "behind": behind,
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked,
            "is_clean": len(staged) == 0 and len(unstaged) == 0 and len(untracked) == 0,
        }

    def get_log(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Returns recent commit history."""
        if not self.is_git_repo():
            return []

        ok, out = self._run_git([
            "log",
            f"-n{limit}",
            "--pretty=format:%h%x09%an%x09%ad%x09%s",
            "--date=short"
        ])
        if not ok or not out:
            return []

        commits = []
        for line in out.split("\n"):
            parts = line.split("\t")
            if len(parts) >= 4:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "message": parts[3],
                })
        return commits

    def get_diff(self, cached: bool = False) -> str:
        """Returns git diff (cached or working tree)."""
        args = ["diff", "--cached"] if cached else ["diff"]
        ok, out = self._run_git(args)
        return out if ok else ""

    def stage(self, path: str = ".") -> Tuple[bool, str]:
        """Stages file or all files."""
        return self._run_git(["add", path])

    def unstage(self, path: str) -> Tuple[bool, str]:
        """Unstages file."""
        return self._run_git(["reset", "HEAD", path])

    def commit(self, message: str) -> Tuple[bool, str]:
        """Creates a commit with the specified message."""
        clean_msg = message.strip()
        if not clean_msg:
            return False, "Commit message cannot be empty"
        return self._run_git(["commit", "-m", clean_msg])


def main():
    repo = sys.argv[2] if len(sys.argv) > 2 else "."
    gm = GitManager(repo)

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "status":
            print(json.dumps(gm.get_status(), indent=2))
            return
        elif cmd == "log":
            n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 5
            print(json.dumps(gm.get_log(limit=n), indent=2))
            return
        elif cmd == "diff":
            print(gm.get_diff())
            return
        elif cmd == "commit" and len(sys.argv) > 2:
            ok, out = gm.commit(sys.argv[2])
            print(json.dumps({"success": ok, "output": out}))
            return

    print(json.dumps(gm.get_status(), indent=2))


if __name__ == "__main__":
    main()
