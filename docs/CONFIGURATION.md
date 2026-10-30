# Centralized Configuration & Tokenized Theming

## 1. Centralized Storage Architecture
In compliance with **AGENTS.md Rule 1.3**, all persistent user configurations, settings, feature toggles, and state files live under:
```
~/.config/tejas-os/
```

### Managed Configuration Files:
| File | Purpose | Managed By |
|---|---|---|
| `features.json` | Granular module enable/disable states and daemon mappings | `config/manager.py` |
| `settings.json` | System preferences (theme, fonts, gaps, sensitivity, volume) | `config/manager.py` |
| `profiles.json` | Definitions for 4 performance profiles | `config/manager.py` |
| `projects.json` | Pinned developer workspaces and recent projects | `developer/project_launcher/project_manager.py` |
| `assistant.json`| June AI identity, active provider, voice & language preferences | `assistant/core/identity.py` |
| `themes/`       | Tokenized JSON theme presets (Midnight, Nordic Light, Forest, Violet) | `shell/services/ThemeService.qml` |

All writes are performed **atomically** using temporary files and `os.replace` to eliminate file corruption.

---

## 2. Tokenized Theming & Presets

UI components never use hardcoded hex codes or pixel metrics. Instead, components read directly from `ThemeService.qml`:

```qml
// Example Theme Token Usage in QML
Rectangle {
    color: ThemeService.colors.surface
    border.color: ThemeService.colors.border
    radius: ThemeService.metrics.radiusSmall
}
```

### The 4 Supported Theme Presets:
1. **Midnight (Default):**
   - Palette: Deep night blue & dark indigo background (`#0f141c`), vibrant ice-blue accents (`#7aa2f7`).
2. **Nordic Light:**
   - Palette: Warm light blue & clean snow (`#eceff4`), deep frost blue accents (`#5e81ac`).
3. **Forest:**
   - Palette: Earthy pine & muted dark green (`#141b18`), soft sage accents (`#a3be8c`).
4. **Violet:**
   - Palette: Deep royal dark purple (`#161320`), luminous violet accents (`#bb9af7`).

To switch themes via CLI:
```bash
python3 -m config.manager --theme violet
```

---

## 3. Modular Feature Isolation (Rule 1.4)

Each feature in `features.json` is independently toggleable:

```json
{
  "dock": { "enabled": true, "daemons": [] },
  "clipboard_history": { "enabled": true, "daemons": ["productivity.clipboard.clipboard_manager"] },
  "june_assistant": { "enabled": true, "daemons": ["assistant.core.daemon"] }
}
```

Disabling a feature will **actively terminate** the associated daemons and free memory. Re-enabling restores the previous state without loss of data.
