# Contributing to Tejas OS

Thank you for contributing to the Tejas OS project! Please read these guidelines before authoring code or submitting pull requests.

## 1. Code Standards & Invariants

### 1.1 Line Endings
All files (Lua configurations, QML components, shell scripts, Python files, JSON schemas) **MUST use LF line endings (`eol=lf`)**. Never commit CRLF line endings.

### 1.2 Hyprland 0.55+ Configuration
- Hyprland configurations must use **pure Lua** (`core/hyprland/modules/*.lua`).
- Always use the official global `hl` table API (`hl.config()`, `hl.bind()`, `hl.monitor()`, etc.).
- Never commit deprecated `hyprlang` files.

### 1.3 Quickshell & QML Standard
- Build components using verified Quickshell types: `ShellRoot`, `PanelWindow`, `WlrLayershell`, `Process`.
- Bind all colors, radii, and fonts to `ThemeService` tokens. Never hardcode hex codes or pixel numbers.

### 1.4 Dual-Boot Safety Guard (Rule 1.5)
- Under no circumstance may any script format disks, touch NTFS partitions, or alter `bootmgfw.efi`.

---

## 2. Testing & Static Verification Workflow

Before committing any changes, run the test suites:

```bash
# 1. Run all unit tests
python -m pytest tests/

# 2. Validate QML delimiters and theme JSON schemas
python tests/test_qml_syntax.py

# 3. Test installer dry-run
./install.sh --dry-run
```

All 70+ tests must pass with zero failures.

---

## 3. Commit Convention
Follow conventional commit formatting:
- `feat(<module>): ...`
- `fix(<module>): ...`
- `docs(<module>): ...`
- `test(<module>): ...`
