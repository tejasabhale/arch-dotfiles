#!/usr/bin/env python3
"""
Scoped File Intelligence & Log Diagnostic Engine.
Indexes user files and parses logs within strictly bounded allowed directories.
Complies with AGENTS.md: Never touches credentials (.ssh, .env, secrets) or Windows partitions.
"""

import glob
import os
import re
from typing import Any, Dict, List, Optional, Tuple


class FileIntelligence:
    """Scoped file search, source code inspection, and log diagnosis."""

    # Approved search root directories
    APPROVED_ROOTS = [
        os.path.abspath("."),
        os.path.expanduser("~/Projects"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/.config/tejas-os"),
    ]

    # Prohibited sensitive directories and patterns
    SENSITIVE_PATTERNS = [
        re.compile(r"[\\/]\.ssh([\\/]|$)", re.IGNORECASE),
        re.compile(r"[\\/]\.gnupg([\\/]|$)", re.IGNORECASE),
        re.compile(r"[\\/]\.env(\..+)?$", re.IGNORECASE),
        re.compile(r"\b(id_rsa|id_ed25519|secrets?\.json|credentials?\.json)\b", re.IGNORECASE),
        re.compile(r"\.pem$", re.IGNORECASE),
        re.compile(r"[\\/]Windows([\\/]|$)", re.IGNORECASE),
        re.compile(r"[\\/]EFI([\\/]|$)", re.IGNORECASE),
    ]

    def is_path_safe(self, path: str) -> Tuple[bool, Optional[str]]:
        """Validates that path is within approved directories and does not target sensitive files."""
        abs_path = os.path.abspath(os.path.expanduser(path))

        # Check for sensitive filename patterns
        for pat in self.SENSITIVE_PATTERNS:
            if pat.search(abs_path):
                return False, f"Access Denied: Path '{abs_path}' matches sensitive security filter."

        # Ensure path is inside at least one approved root
        inside_approved = any(
            abs_path.startswith(approved_root)
            for approved_root in self.APPROVED_ROOTS
        )

        if not inside_approved:
            return False, f"Access Denied: Path '{abs_path}' is outside approved user workspaces."

        return True, None

    def search_files(
        self,
        query: str,
        search_dir: Optional[str] = None,
        max_results: int = 25,
    ) -> List[Dict[str, Any]]:
        """Searches for files matching query within approved workspace directory."""
        root_dir = os.path.abspath(search_dir or ".")
        safe, err = self.is_path_safe(root_dir)
        if not safe:
            return [{"error": err}]

        results = []
        q_lower = query.lower()

        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip hidden and sensitive subdirs
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in ("node_modules", "target", "build", "__pycache__")]

            for fn in filenames:
                if q_lower in fn.lower():
                    full_p = os.path.join(dirpath, fn)
                    safe_f, _ = self.is_path_safe(full_p)
                    if safe_f:
                        stat = os.stat(full_p)
                        results.append({
                            "name": fn,
                            "path": full_p,
                            "size_bytes": stat.st_size,
                            "modified": stat.st_mtime,
                        })
                        if len(results) >= max_results:
                            return results

        return results

    def summarize_code(self, file_path: str) -> Dict[str, Any]:
        """Provides high-level statistics and structure for a source file."""
        safe, err = self.is_path_safe(file_path)
        if not safe:
            return {"error": err}

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return {"error": f"File '{file_path}' does not exist"}

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            total_lines = len(lines)
            blank_lines = sum(1 for line in lines if not line.strip())
            comment_lines = sum(1 for line in lines if line.strip().startswith(("#", "//", "/*", "*", "--")))
            code_lines = total_lines - blank_lines - comment_lines

            # Heuristic symbol detection
            classes = [line.strip() for line in lines if re.match(r"^(class\s+\w+|struct\s+\w+)", line.strip())]
            functions = [line.strip() for line in lines if re.match(r"^(def\s+\w+|function\s+\w+)", line.strip())]

            return {
                "file": file_path,
                "total_lines": total_lines,
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "blank_lines": blank_lines,
                "class_count": len(classes),
                "classes": classes[:10],
                "function_count": len(functions),
                "functions": functions[:15],
            }
        except Exception as e:
            return {"error": f"Error summarizing code: {e}"}

    def parse_recent_logs(self, log_path: Optional[str] = None, max_lines: int = 50) -> Dict[str, Any]:
        """Scans recent log lines for errors, warnings, and exceptions."""
        target_log = log_path
        if not target_log:
            # Check default systemd user or application log if exists
            possible_logs = glob.glob(os.path.expanduser("~/.local/state/**/*.log"), recursive=True)
            target_log = possible_logs[0] if possible_logs else None

        if not target_log or not os.path.exists(target_log):
            return {
                "log_file": target_log or "none",
                "status": "healthy",
                "errors": [],
                "warnings": [],
                "summary": "No active system error logs found. Desktop operating normally.",
            }

        safe, err = self.is_path_safe(target_log)
        if not safe:
            return {"error": err}

        errors = []
        warnings = []
        try:
            with open(target_log, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()[-max_lines:]

            for line in lines:
                l_lower = line.lower()
                if "error" in l_lower or "exception" in l_lower or "critical" in l_lower or "fail" in l_lower:
                    errors.append(line.strip())
                elif "warn" in l_lower:
                    warnings.append(line.strip())

            return {
                "log_file": target_log,
                "lines_scanned": len(lines),
                "error_count": len(errors),
                "warning_count": len(warnings),
                "errors": errors[:10],
                "warnings": warnings[:10],
                "status": "critical" if errors else "warning" if warnings else "healthy",
            }
        except Exception as e:
            return {"error": f"Log parsing error: {e}"}
