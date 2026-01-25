# Govee H5198 Temperature Monitor & Logger

A Python-based toolset for monitoring and logging data from the **Govee H5198 WiFi Meat Thermometer** using Bluetooth Low Energy (BLE).

This project reverse-engineers the BLE advertisement packets to provide real-time temperature readings and CSV/TXT logging without requiring the official Govee app or cloud service.

## Features

*   **Auto-Discovery:** Automatically finds your H5198 device (looks for Manufacturer ID `0x2331`), so you don't need to hardcode a MAC address.
*   **Real-Time Monitoring:** Console-based live view of all 4 probes.
*   **Data Logging:** Logs temperature data to timestamped CSV and TXT files.
*   **Robust Syncing:** Waits for all connected probes to report data before starting logs to ensure complete datasets.

## Prerequisites

*   Python 3.7+
*   A Bluetooth Adapter (BLE capable)

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/temperature_monitor.git
    cd temperature_monitor
    ```

2.  Install the required Python library (`bleak`):
    ```bash
    pip install bleak
    ```

## Usage

### 1. Live Monitor (`govee_live_view.py`)
View current temperatures in your terminal. This script scans for the device, syncs all probes, and then displays a live-updating status line.

```bash
python govee_live_view.py
```

### 2. Data Logger (`govee_logger.py`)
Logs temperature data to the `temperature_logs/` directory.

**Run indefinitely (until Ctrl+C):**
```bash
python govee_logger.py
```

**Run for a specific duration (in minutes):**
```bash
python govee_logger.py 60       # Run for 1 hour
python govee_logger.py 10       # Run for 10 minutes
python govee_logger.py 0.5      # Run for 30 seconds
```

## Output

Log files are saved in the `temperature_logs/` folder with unique timestamps:

*   `temperature_log_YYYY-MM-DD_HH-MM-SS.csv` (Easy to import into Excel)
*   `temperature_log_YYYY-MM-DD_HH-MM-SS.txt` (Human-readable format)

## Troubleshooting

*   **Sync Timeout:** If some probes are unplugged, the "Syncing" phase will time out after 60 seconds and proceed with whichever probes were found.
*   **Bluetooth Permissions:** On Linux/Raspberry Pi, you may need to run with `sudo` or configure bluetooth permissions.
