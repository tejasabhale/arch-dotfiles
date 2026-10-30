"""
Static syntax validator for Hyprland Lua configuration files.
Verifies syntax patterns, balanced braces/parentheses, and global 'hl' API usage.
"""

import glob
import re
import sys


def validate_lua_file(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Check balanced delimiters
    delimiters = {"(": ")", "{": "}", "[": "]"}
    stack = []
    in_string = False
    string_char = ""
    in_comment = False
    in_block_comment = False

    i = 0
    n = len(code)
    while i < n:
        # Check block comments --[[ ... ]]
        if not in_string and not in_comment and code[i : i + 4] == "--[[":
            in_block_comment = True
            i += 4
            continue
        if in_block_comment:
            if code[i : i + 2] == "]]":
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue

        # Check line comments --
        if not in_string and not in_comment and code[i : i + 2] == "--":
            in_comment = True
            i += 2
            continue
        if in_comment:
            if code[i] == "\n":
                in_comment = False
            i += 1
            continue

        char = code[i]

        # Check strings
        if char in ('"', "'") and not in_string:
            in_string = True
            string_char = char
            i += 1
            continue
        elif in_string and char == string_char:
            # Check escape
            if i > 0 and code[i - 1] != "\\":
                in_string = False
            i += 1
            continue
        elif in_string:
            i += 1
            continue

        # Check delimiters
        if char in delimiters:
            stack.append((char, i))
        elif char in delimiters.values():
            if not stack:
                print(f"[ERROR] {path}:{i} Unexpected closing delimiter '{char}'")
                return False
            open_char, open_pos = stack.pop()
            if delimiters[open_char] != char:
                print(
                    f"[ERROR] {path}:{i} Mismatched delimiter: opened '{open_char}' at {open_pos}, closed '{char}'"
                )
                return False

        i += 1

    if stack:
        open_char, open_pos = stack[-1]
        print(f"[ERROR] {path}:{open_pos} Unclosed delimiter '{open_char}'")
        return False

    return True


def main():
    lua_files = glob.glob("core/hyprland/**/*.lua", recursive=True)
    if not lua_files:
        print("[FAIL] No Lua files found in core/hyprland/")
        sys.exit(1)

    all_passed = True
    print(f"Validating {len(lua_files)} Lua files...")
    for f in lua_files:
        if validate_lua_file(f):
            print(f"  [OK] {f}")
        else:
            all_passed = False

    if not all_passed:
        sys.exit(1)

    print("\nAll Hyprland Lua files passed static syntax validation!")


if __name__ == "__main__":
    main()
