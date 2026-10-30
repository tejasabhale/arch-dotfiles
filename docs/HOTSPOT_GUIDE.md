# Dedicated Wi-Fi Hotspot & Access Point Guide

## 1. Overview
The **Hotspot Manager** (`system/hotspot/`) turns your HP EliteBook 840 G5 into a standalone Access Point (AP). It communicates directly with **NetworkManager** via D-Bus and includes an interactive graphical control panel (`HotspotPanel.qml`).

---

## 2. Hardware Compatibility Check
HP EliteBook 840 G5 utilizes an **Intel Dual Band Wireless-AC 8265** Wi-Fi adapter.
The Hotspot Manager executes hardware inspection via `iw list` to confirm:
- AP interface mode support.
- Simultaneous STA/AP concurrence (Wi-Fi client + Hotspot active simultaneously).
- 2.4 GHz (Channels 1–11) and 5 GHz (Channels 36–165) availability.

---

## 3. Features
1. **One-Click Hotspot Toggle:** Instantly start or stop the AP connection.
2. **Ambiguity-Free Password Generator:** Generates high-entropy passwords omitting easily confused characters (`l`, `1`, `I`, `0`, `O`).
3. **QR Code Sharing:** Generates a standard Wi-Fi QR code (`WIFI:S:<SSID>;T:WPA;P:<PASSWORD>;;`) for camera scanning by smartphones.
4. **Client Device Tracking:** Inspects `/proc/net/arp` and DHCP leases to display connected client hostnames and IP/MAC addresses.
5. **Security Protocols:** Supports WPA2-Personal (AES) and WPA3-SAE.

---

## 4. Usage

### Launching Hotspot Panel
- Open Control Center (**Super + C**) and click the **Hotspot** toggle.
- Or launch directly from the terminal:
  ```bash
  python3 -m system.hotspot.hotspot_manager start --ssid "Tejas-Hotspot" --password "supersecretpass"
  ```
