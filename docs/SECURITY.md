# Security & Safety Model

## 1. Dual-Boot Safety Invariants (Rule 1.5)
Tejas OS runs in a dual-boot environment with Windows 11 on UEFI. The installer and desktop daemons operate under strict non-negotiable safety rules:
1. **Zero Disk Partitioning:** Under no circumstance will any script or tool execute `mkfs`, `fdisk`, `parted`, or partition manipulation commands.
2. **NTFS Isolation:** The Windows partition (NTFS) is completely isolated from modification or deletion.
3. **EFI Protection:** The EFI System Partition (ESP) and the Windows bootloader (`bootmgfw.efi`) are protected and never overwritten.
4. **Explicit Permissions:** No script silently executes destructive commands without user consent.

---

## 2. June AI Execution Sandbox & Permission Engine
AI-generated system actions are treated as **untrusted input**.
- Execution passes through a strictly allowlisted `ActionPlanner` and `ControlledExecutor`.
- Any system-modifying operation (file deletions, network modifications, package installations) triggers an explicit user confirmation modal.
- An instantaneous **Emergency Stop** (`Super + Escape`) aborts active execution plans within milliseconds.

---

## 3. Credential & Secrets Management
- API keys, OAuth tokens, and passwords are **never** stored in plain files, environment files committed to Git, or shell histories.
- Secrets are securely managed via system secret services (`libsecret` / `secret-tool` / Wayland secure keyrings).
- The memory engine automatically sanitizes sensitive tokens before persisting conversation history to SQLite.
