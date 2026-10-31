"""
Static syntax and schema validator for Quickshell QML files and Theme JSON presets.
"""

import glob
import json
import os
import sys


def validate_json_themes():
    theme_files = glob.glob("themes/**/*.json", recursive=True)
    if not theme_files:
        print("[FAIL] No theme JSON files found!")
        return False

    required_keys = ["name", "type", "colors", "metrics", "typography", "effects"]
    required_colors = [
        "background",
        "surface",
        "border",
        "accent",
        "textPrimary",
        "textSecondary",
    ]

    for f in theme_files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            for k in required_keys:
                if k not in data:
                    print(f"[FAIL] {f} missing required key '{k}'")
                    return False
            for c in required_colors:
                if c not in data["colors"]:
                    print(f"[FAIL] {f} missing color token '{c}'")
                    return False
            print(
                f"  [OK JSON] {f} -> Preset: '{data['name']}' ({data['type']} mode)"
            )
        except Exception as e:
            print(f"[FAIL] {f} JSON error: {e}")
            return False
    return True


def validate_qml_file(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    # Check balanced braces, brackets, and parentheses
    delimiters = {"(": ")", "{": "}", "[": "]"}
    stack = []
    in_string = False
    string_char = ""
    in_line_comment = False
    in_block_comment = False

    i = 0
    n = len(code)
    while i < n:
        if (
            not in_string
            and not in_line_comment
            and not in_block_comment
            and code[i : i + 2] == "/*"
        ):
            in_block_comment = True
            i += 2
            continue
        if in_block_comment:
            if code[i : i + 2] == "*/":
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue

        if (
            not in_string
            and not in_line_comment
            and not in_block_comment
            and code[i : i + 2] == "//"
        ):
            in_line_comment = True
            i += 2
            continue
        if in_line_comment:
            if code[i] == "\n":
                in_line_comment = False
            i += 1
            continue

        char = code[i]

        if char in ('"', "'", "`") and not in_string:
            in_string = True
            string_char = char
            i += 1
            continue
        elif in_string and char == string_char:
            if i > 0 and code[i - 1] != "\\":
                in_string = False
            i += 1
            continue
        elif in_string:
            i += 1
            continue

        if char in delimiters:
            stack.append((char, i))
        elif char in delimiters.values():
            if not stack:
                print(
                    f"[ERROR] {path}:{i} Unexpected closing delimiter '{char}'"
                )
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


def test_theme_json_schemas():
    assert validate_json_themes(), "Theme JSON schema validation failed"


def test_quickshell_qml_syntax():
    qml_files = (
        glob.glob("shell/**/*.qml", recursive=True)
        + glob.glob("system/**/*.qml", recursive=True)
        + glob.glob("productivity/**/*.qml", recursive=True)
        + glob.glob("assistant/**/*.qml", recursive=True)
        + glob.glob("developer/**/*.qml", recursive=True)
    )
    assert qml_files, "No QML files found"
    for f in qml_files:
        assert validate_qml_file(f), f"QML syntax validation failed for file: {f}"


def main():
    print("1. Validating Theme JSON Files...")
    if not validate_json_themes():
        sys.exit(1)

    print("\n2. Validating Quickshell QML Component Syntax...")
    qml_files = (
        glob.glob("shell/**/*.qml", recursive=True)
        + glob.glob("system/**/*.qml", recursive=True)
        + glob.glob("productivity/**/*.qml", recursive=True)
        + glob.glob("assistant/**/*.qml", recursive=True)
        + glob.glob("developer/**/*.qml", recursive=True)
    )
    if not qml_files:
        print("[FAIL] No QML files found in shell/")
        sys.exit(1)

    all_passed = True
    for f in qml_files:
        if validate_qml_file(f):
            print(f"  [OK QML] {f}")
        else:
            all_passed = False

    if not all_passed:
        sys.exit(1)

    print("\nAll Quickshell QML and Theme files passed static verification!")


if __name__ == "__main__":
    main()
