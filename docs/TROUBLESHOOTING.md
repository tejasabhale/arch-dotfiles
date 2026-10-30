# Troubleshooting Guide — Tejas OS

## 1. Dual-Boot & Bootloader Recovery
If the system ever boots directly into Windows without displaying the GRUB/systemd-boot menu:
1. Boot into UEFI BIOS settings (Press **F10** or **Esc** at the HP startup logo).
2. Navigate to **Boot Options** -> **UEFI Boot Order**.
3. Move `Arch Linux` above `Windows Boot Manager`.
4. Ensure Secure Boot is disabled if custom kernel modules are in use.

---

## 2. PipeWire Audio Issues
If audio is muted or no output devices are listed:
```bash
# Check status of PipeWire and WirePlumber
systemctl --user status pipewire wireplumber

# Restart audio subsystem
systemctl --user restart pipewire pipewire-pulse wireplumber
```

---

## 3. Wi-Fi & Hotspot Access Point
If Wi-Fi fails to scan or Hotspot fails to start:
1. Ensure the Wi-Fi physical radio switch is ON.
2. Verify NetworkManager service is active:
   ```bash
   sudo systemctl status NetworkManager
   ```
3. Check for AP mode support:
   ```bash
   iw list | grep "Supported interface modes" -A 8
   ```

---

## 4. Fonts & Icons (Devanagari & Nerd Fonts)
If icons appear as missing rectangles or Hindi/Marathi text does not render:
```bash
# Install required Nerd Fonts and Devanagari fonts
sudo pacman -S --needed ttf-jetbrains-mono-nerd noto-fonts noto-fonts-cjk noto-fonts-emoji

# Refresh font cache
fc-cache -fv
```

---

## 5. June AI Daemon Status
If pressing `Super + Space` does not respond:
```bash
# Check if June daemon is running
ps aux | grep "assistant.core.daemon"

# Test local IPC connection
python3 -m assistant.core.cli ping

# Start daemon in verbose debug mode
python3 -m assistant.core.daemon --debug
```
