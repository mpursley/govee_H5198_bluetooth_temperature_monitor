# Gemini Context & Project Knowledge Base

This document serves as a high-level technical reference for the **Govee H5198 Bluetooth Temperature Monitor** project. It contains discovered protocol details, architectural decisions, and build instructions to assist future development.

## 1. Technical Protocol Details

The Govee H5198 device broadcasts temperature data via Bluetooth Low Energy (BLE) Advertisement packets.

*   **Manufacturer ID:** `0x2331`
    *   *Usage:* Used for filtering devices during Auto-Discovery.
*   **Packet Structure:**
    *   The device alternates between two packet types identified by the byte at offset `6` of the manufacturer data.
    *   **Type `0xc1`:** Contains data for **Probe 1** and **Probe 2**.
    *   **Type `0xc2`:** Contains data for **Probe 3** and **Probe 4**.
*   **Data Decoding:**
    *   Temperature is encoded as a 2-byte integer (Big Endian).
    *   Value represents Celsius * 100.
    *   *Formula:* `Temp_F = ((Value / 100.0) * 1.8) + 32`

## 2. Key Architectural Decisions

### Auto-Discovery vs. Hardcoded MAC
*   **Problem:** The device may rotate its MAC address (Privacy feature) or get a new one upon reset.
*   **Solution:** Scripts do not rely on a hardcoded MAC. They scan for `Manufacturer ID 0x2331`. The first device found matches and the script "locks on" to that MAC for the session duration to avoid interference.

### Syncing Phase
*   **Problem:** Probes report in separate packets. Starting a logger immediately often resulted in `None` or `--` values for the first few seconds.
*   **Solution:** Both `govee_logger.py` and `govee_live_view.py` enter a "Syncing" loop at startup. They wait (up to 60s) for valid data from all 4 probes before transitioning to the main task.

## 3. Development & Build

### Environment
*   **Python:** 3.x
*   **Dependencies:** `bleak`, `pyinstaller`

### Building Windows Binaries
To create standalone `.exe` files for distribution:

```bash
# Build Logger
pyinstaller --onefile govee_logger.py

# Build Live Monitor
pyinstaller --onefile govee_live_view.py
```

### Building Linux Binaries
To create standalone executables for Linux:

```bash
# Build Logger
pyinstaller --onefile govee_logger.py

# Build Live Monitor
pyinstaller --onefile govee_live_view.py
```

*Artifacts are placed in the `dist/` directory.*

## 4. File Structure

*   `govee_live_view.py`: Real-time console monitor (Syncs -> Displays).
*   `govee_logger.py`: CSV/TXT file logger. Supports CLI args for duration (e.g., `python govee_logger.py 60`).
*   `temperature_logs/`: Directory where timestamped log files are saved.
*   `research/`: Archive of initial research and reverse-engineering scripts.
